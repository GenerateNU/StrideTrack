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


def transform_stride_cycles_to_triple_jump_metrics(
    df_steps: pd.DataFrame,
    phase_min_ft_ms: int = 250,
    phase_max_ft_ms: int | None = None,
) -> pd.DataFrame:
    required = {"foot", "ic_time", "to_time", "gct_ms"}
    missing = required - set(df_steps.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out_cols = [
        "hop_gct_ms",
        "hop_ft_ms",
        "hop_takeoff_foot",
        "step_gct_ms",
        "step_ft_ms",
        "jump_gct_ms",
        "jump_ft_ms",
        "phase_ratio_hop",
        "phase_ratio_step",
        "phase_ratio_jump",
        "contact_time_efficiency",
        "hop_clearance_start_ms",
        "hop_clearance_end_ms",
        "step_clearance_start_ms",
        "step_clearance_end_ms",
        "jump_clearance_start_ms",
        "jump_clearance_end_ms",
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
    phase_gaps = _filter_gaps(gaps, min_ms=phase_min_ft_ms, max_ms=phase_max_ft_ms)

    if len(phase_gaps) < 3:
        return pd.DataFrame(columns=out_cols)

    ordered = sorted(phase_gaps, key=lambda g: g.start)[:3]
    hop_gap, step_gap, jump_gap = ordered

    hop_ft = hop_gap.end - hop_gap.start
    step_ft = step_gap.end - step_gap.start
    jump_ft = jump_gap.end - jump_gap.start
    total_ft = hop_ft + step_ft + jump_ft

    hop_takeoff = _last_contact_before(steps, hop_gap.start)
    step_takeoff = _last_contact_before(steps, step_gap.start)
    jump_takeoff = _last_contact_before(steps, jump_gap.start)

    total_gct = sum(
        int(s["gct_ms"])
        for s in [hop_takeoff, step_takeoff, jump_takeoff]
        if s is not None
    )

    def _gct(s: pd.Series | None) -> int | None:
        return None if s is None else int(s["gct_ms"])

    def _foot(s: pd.Series | None) -> str | None:
        return None if s is None else str(s["foot"])

    row = {
        "hop_gct_ms": _gct(hop_takeoff),
        "hop_ft_ms": int(hop_ft),
        "hop_takeoff_foot": _foot(hop_takeoff),
        "step_gct_ms": _gct(step_takeoff),
        "step_ft_ms": int(step_ft),
        "jump_gct_ms": _gct(jump_takeoff),
        "jump_ft_ms": int(jump_ft),
        "phase_ratio_hop": round(hop_ft / total_ft * 100, 2) if total_ft > 0 else None,
        "phase_ratio_step": round(step_ft / total_ft * 100, 2)
        if total_ft > 0
        else None,
        "phase_ratio_jump": round(jump_ft / total_ft * 100, 2)
        if total_ft > 0
        else None,
        "contact_time_efficiency": round(total_ft / total_gct, 4)
        if total_gct > 0
        else None,
        "hop_clearance_start_ms": int(hop_gap.start),
        "hop_clearance_end_ms": int(hop_gap.end),
        "step_clearance_start_ms": int(step_gap.start),
        "step_clearance_end_ms": int(step_gap.end),
        "jump_clearance_start_ms": int(jump_gap.start),
        "jump_clearance_end_ms": int(jump_gap.end),
    }

    return pd.DataFrame([row])[out_cols]
