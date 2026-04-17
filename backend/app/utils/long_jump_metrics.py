from __future__ import annotations

import pandas as pd

from app.utils.interval import Interval


def _compute_gaps(contacts_sorted: list[Interval]) -> list[Interval]:
    gaps: list[Interval] = []
    if len(contacts_sorted) < 2:
        return gaps
    for a, b in zip(contacts_sorted[:-1], contacts_sorted[1:], strict=True):
        if b.start > a.end:
            gaps.append(Interval(start=a.end, end=b.start))
    return gaps


def _filter_gaps(
    gaps: list[Interval],
    min_ms: int,
    max_ms: int | None = None,
) -> list[Interval]:
    out: list[Interval] = []
    for g in gaps:
        dur = g.end - g.start
        if dur < min_ms:
            continue
        if max_ms is not None and dur > max_ms:
            continue
        out.append(g)
    return out


def _last_contact_before(df: pd.DataFrame, t_ms: int) -> pd.Series | None:
    cand = df[df["to_time"] <= t_ms]
    return None if cand.empty else cand.iloc[cand["to_time"].argmax()]


def transform_stride_cycles_to_long_jump_metrics(
    df_steps: pd.DataFrame,
    jump_min_ft_ms: int = 500,
    jump_max_ft_ms: int | None = None,
) -> pd.DataFrame:
    required = {"foot", "ic_time", "to_time", "gct_ms"}
    missing = required - set(df_steps.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out_cols = [
        "takeoff_foot",
        "takeoff_gct_ms",
        "penultimate_foot",
        "penultimate_gct_ms",
        "jump_ft_ms",
        "clearance_start_ms",
        "clearance_end_ms",
        "approach_mean_gct_ms",
        "approach_mean_ft_ms",
        "approach_cv_pct",
        "approach_rsi",
    ]

    if df_steps.empty:
        return pd.DataFrame(columns=out_cols)

    steps = (
        df_steps.sort_values(["ic_time", "foot", "to_time"])
        .reset_index(drop=True)
        .copy()
    )

    contacts = [
        Interval(int(r.ic_time), int(r.to_time))
        for r in steps.itertuples(index=False)
        if int(r.to_time) > int(r.ic_time)
    ]
    contacts_sorted = sorted(contacts, key=lambda x: x.start)
    gaps = _compute_gaps(contacts_sorted)
    jump_gaps = _filter_gaps(gaps, min_ms=jump_min_ft_ms, max_ms=jump_max_ft_ms)

    if not jump_gaps:
        return pd.DataFrame(columns=out_cols)

    jump_gap = max(jump_gaps, key=lambda g: g.end - g.start)

    takeoff_step = _last_contact_before(steps, jump_gap.start)
    penultimate_step = (
        _last_contact_before(steps, int(takeoff_step["ic_time"]) - 1)
        if takeoff_step is not None
        else None
    )

    approach = steps[steps["to_time"] <= jump_gap.start].copy()
    approach_run = approach.iloc[:-2] if len(approach) >= 4 else approach

    mean_gct = float(approach_run["gct_ms"].mean()) if not approach_run.empty else None
    cv_pct = None
    if mean_gct and mean_gct > 0 and len(approach_run) > 1:
        cv_pct = float(approach_run["gct_ms"].std() / mean_gct * 100)

    mean_ft = rsi = None
    if "flight_ms" in steps.columns and not approach_run.empty:
        ft_vals = approach_run["flight_ms"].dropna()
        if not ft_vals.empty:
            mean_ft = float(ft_vals.mean())
        valid = approach_run.dropna(subset=["flight_ms"])
        valid = valid[valid["gct_ms"] > 0]
        if not valid.empty:
            rsi = float((valid["flight_ms"] / valid["gct_ms"]).mean())

    row = {
        "takeoff_foot": None if takeoff_step is None else str(takeoff_step["foot"]),
        "takeoff_gct_ms": None if takeoff_step is None else int(takeoff_step["gct_ms"]),
        "penultimate_foot": None
        if penultimate_step is None
        else str(penultimate_step["foot"]),
        "penultimate_gct_ms": None
        if penultimate_step is None
        else int(penultimate_step["gct_ms"]),
        "jump_ft_ms": int(jump_gap.end - jump_gap.start),
        "clearance_start_ms": int(jump_gap.start),
        "clearance_end_ms": int(jump_gap.end),
        "approach_mean_gct_ms": round(mean_gct, 2) if mean_gct is not None else None,
        "approach_mean_ft_ms": round(mean_ft, 2) if mean_ft is not None else None,
        "approach_cv_pct": round(cv_pct, 2) if cv_pct is not None else None,
        "approach_rsi": round(rsi, 4) if rsi is not None else None,
    }

    return pd.DataFrame([row])[out_cols]
