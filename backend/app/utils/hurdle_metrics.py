from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# Interval utilities


@dataclass(frozen=True)
class Interval:
    start: int
    end: int  # end is exclusive, duration is end - start


def _compute_gaps(contacts_sorted: list[Interval]) -> list[Interval]:
    """
    Return gaps between consecutive contact intervals, representing time when neither foot is on the ground.
    """
    gaps: list[Interval] = []
    if len(contacts_sorted) < 2:
        return gaps

    for a, b in zip(contacts_sorted[:-1], contacts_sorted[1:], strict=True):
        if b.start > a.end:
            gaps.append(Interval(start=a.end, end=b.start))

    return gaps


def _filter_hurdle_gaps(
    gaps: list[Interval],
    min_ms: int,
    max_ms: int | None = None,
) -> list[Interval]:
    """
    Keep only gaps long enough to be treated as hurdle clearances.
    """
    out: list[Interval] = []

    for g in gaps:
        dur = g.end - g.start
        if dur < min_ms:
            continue
        if max_ms is not None and dur > max_ms:
            continue
        out.append(g)

    return out


# Step lookup helpers


def _last_contact_before(df: pd.DataFrame, t_ms: int) -> pd.Series | None:
    """
    Return the contact step that ends (to_time) closest to but not after t_ms.
    """
    cand = df[df["to_time"] <= t_ms]

    if cand.empty:
        return None

    return cand.iloc[cand["to_time"].argmax()]


def _first_contact_after(df: pd.DataFrame, t_ms: int) -> pd.Series | None:
    """
    Return the contact step that starts (ic_time) closest to but not before t_ms.
    """
    cand = df[df["ic_time"] >= t_ms]

    if cand.empty:
        return None

    return cand.iloc[cand["ic_time"].argmin()]


def _count_steps_between(
    df: pd.DataFrame, t_start_exclusive: int, t_end_exclusive: int
) -> int:
    """
    Count step initial contacts (ic_time) strictly between two timestamps.
    """
    mask = (df["ic_time"] > t_start_exclusive) & (df["ic_time"] < t_end_exclusive)

    return int(mask.sum())


# Individual hurdle metric accessors


def calc_hurdle_split_ms(
    df_steps: pd.DataFrame,
    hurdle_min_ft_ms: int = 260,
    hurdle_max_ft_ms: int | None = None,
) -> pd.DataFrame:
    """
    Hurdle Split: time between consecutive hurdle clearances. DataFrame with columns: hurdle_num, hurdle_split_ms
    """
    out = transform_stride_cycles_to_hurdle_metrics(
        df_steps, hurdle_min_ft_ms=hurdle_min_ft_ms, hurdle_max_ft_ms=hurdle_max_ft_ms
    )
    return out[["hurdle_num", "hurdle_split_ms"]]


def calc_steps_between_hurdles(
    df_steps: pd.DataFrame,
    hurdle_min_ft_ms: int = 260,
    hurdle_max_ft_ms: int | None = None,
) -> pd.DataFrame:
    """
    Steps Between Hurdles: count of ground contacts between hurdles. DataFrame with columns: hurdle_num,
    steps_between_hurdles
    """
    out = transform_stride_cycles_to_hurdle_metrics(
        df_steps, hurdle_min_ft_ms=hurdle_min_ft_ms, hurdle_max_ft_ms=hurdle_max_ft_ms
    )
    return out[["hurdle_num", "steps_between_hurdles"]]


def calc_takeoff_gct_ms(
    df_steps: pd.DataFrame,
    hurdle_min_ft_ms: int = 260,
    hurdle_max_ft_ms: int | None = None,
) -> pd.DataFrame:
    """
    Take-off GCT: GCT of the last step before hurdle clearance. DataFrame with columns: hurdle_num, takeoff_gct_ms
    """
    out = transform_stride_cycles_to_hurdle_metrics(
        df_steps, hurdle_min_ft_ms=hurdle_min_ft_ms, hurdle_max_ft_ms=hurdle_max_ft_ms
    )
    return out[["hurdle_num", "takeoff_gct_ms"]]


def calc_landing_gct_ms(
    df_steps: pd.DataFrame,
    hurdle_min_ft_ms: int = 260,
    hurdle_max_ft_ms: int | None = None,
) -> pd.DataFrame:
    """
    Landing GCT: GCT of the first step after hurdle clearance. DataFrame with columns: hurdle_num, landing_gct_ms
    """
    out = transform_stride_cycles_to_hurdle_metrics(
        df_steps, hurdle_min_ft_ms=hurdle_min_ft_ms, hurdle_max_ft_ms=hurdle_max_ft_ms
    )
    return out[["hurdle_num", "landing_gct_ms"]]


def calc_takeoff_ft_ms(
    df_steps: pd.DataFrame,
    hurdle_min_ft_ms: int = 260,
    hurdle_max_ft_ms: int | None = None,
) -> pd.DataFrame:
    """
    Take-off FT: FT during hurdle clearance. DataFrame with columns: hurdle_num, takeoff_ft_ms
    """
    out = transform_stride_cycles_to_hurdle_metrics(
        df_steps, hurdle_min_ft_ms=hurdle_min_ft_ms, hurdle_max_ft_ms=hurdle_max_ft_ms
    )
    return out[["hurdle_num", "takeoff_ft_ms"]]


def calc_gct_increase_hurdle_to_hurdle_pct(
    df_steps: pd.DataFrame,
    hurdle_min_ft_ms: int = 260,
    hurdle_max_ft_ms: int | None = None,
) -> pd.DataFrame:
    """
    GCT Increase Hurdle-to-Hurdle: (GCT_hurdle_N - GCT_hurdle_1) / GCT_hurdle_1 * 100 DataFrame with columns:
    hurdle_num, gct_increase_hurdle_to_hurdle_pct
    """
    out = transform_stride_cycles_to_hurdle_metrics(
        df_steps, hurdle_min_ft_ms=hurdle_min_ft_ms, hurdle_max_ft_ms=hurdle_max_ft_ms
    )
    return out[["hurdle_num", "gct_increase_hurdle_to_hurdle_pct"]]


# Main transformation


def transform_stride_cycles_to_hurdle_metrics(
    df_steps: pd.DataFrame,
    hurdle_min_ft_ms: int = 260,
    hurdle_max_ft_ms: int | None = None,
) -> pd.DataFrame:
    """
    Compute hurdle metrics from stride-cycle rows.
    """
    required = {"foot", "ic_time", "to_time", "gct_ms"}
    missing = required - set(df_steps.columns)
    if missing:
        raise ValueError(f"Missing required columns in df_steps: {sorted(missing)}")

    out_cols = [
        "hurdle_num",
        "clearance_start_ms",
        "clearance_end_ms",
        "takeoff_ft_ms",
        "hurdle_split_ms",
        "steps_between_hurdles",
        "takeoff_foot",
        "takeoff_gct_ms",
        "landing_foot",
        "landing_gct_ms",
        "gct_increase_hurdle_to_hurdle_pct",
    ]

    if df_steps.empty:
        return pd.DataFrame(columns=out_cols)

    # Sort again just in case
    steps = (
        df_steps.sort_values(["ic_time", "foot", "to_time"])
        .reset_index(drop=True)
        .copy()
    )

    # Build contact intervals across both feet
    contacts = [
        Interval(int(r.ic_time), int(r.to_time))
        for r in steps.itertuples(index=False)
        if int(r.to_time) > int(r.ic_time)
    ]
    contacts_sorted = sorted(contacts, key=lambda x: (x.start, x.end))

    # Gaps between contacts
    gaps = _compute_gaps(contacts_sorted)

    # Hurdle gaps where neither foot is on ground
    hurdle_gaps = _filter_hurdle_gaps(
        gaps, min_ms=hurdle_min_ft_ms, max_ms=hurdle_max_ft_ms
    )
    if not hurdle_gaps:
        return pd.DataFrame(columns=out_cols)

    # Compute per-hurdle metrics
    rows: list[dict] = []
    for i, hg in enumerate(hurdle_gaps, start=1):
        start_ms = hg.start
        end_ms = hg.end
        takeoff_ft = end_ms - start_ms

        takeoff_step = _last_contact_before(steps, start_ms)
        landing_step = _first_contact_after(steps, end_ms)

        # Split + steps between hurdles requires looking at next hurdle
        if i < len(hurdle_gaps):
            next_start = hurdle_gaps[i].start
            split_ms = int(next_start - start_ms)
            steps_between = _count_steps_between(steps, end_ms, next_start)
        else:
            split_ms = np.nan
            steps_between = np.nan

        rows.append(
            {
                "hurdle_num": i,
                "clearance_start_ms": int(start_ms),
                "clearance_end_ms": int(end_ms),
                "takeoff_ft_ms": int(takeoff_ft),
                "hurdle_split_ms": split_ms,
                "steps_between_hurdles": steps_between,
                "takeoff_foot": None
                if takeoff_step is None
                else str(takeoff_step["foot"]),
                "takeoff_gct_ms": None
                if takeoff_step is None
                else int(takeoff_step["gct_ms"]),
                "landing_foot": None
                if landing_step is None
                else str(landing_step["foot"]),
                "landing_gct_ms": None
                if landing_step is None
                else int(landing_step["gct_ms"]),
            }
        )

    out = pd.DataFrame(rows)

    if out["takeoff_gct_ms"].notna().any():
        gct0 = out["takeoff_gct_ms"].dropna().iloc[0]
        if gct0 and gct0 > 0:
            out["gct_increase_hurdle_to_hurdle_pct"] = (
                (out["takeoff_gct_ms"] - gct0) / gct0 * 100.0
            )
        else:
            out["gct_increase_hurdle_to_hurdle_pct"] = np.nan
    else:
        out["gct_increase_hurdle_to_hurdle_pct"] = np.nan

    return out[out_cols]
