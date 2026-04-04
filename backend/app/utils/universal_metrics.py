"""
universal_metrics.py
====================
Computes every Universal Metric defined in StrideTrack Metrics Reference.

All metrics operate on the APPROACH portion of a run.
For jump events the caller passes approach_end_ms (= clearance_start_ms
from the event-specific transform) so jump-phase steps are excluded.
For sprinting the caller passes approach_end_ms=None to include all steps.

Two output shapes
-----------------
1. Per-step series  → fed to line charts / stacked-bar charts on the frontend.
2. Summary KPIs     → fed to KPI cards and gauges.

Formula reference (StrideTrack Metrics Reference)
--------------------------------------------------
Step Time         = GCT + FT
Stride Time       = Step_Time_L + Step_Time_R   (same stride_num)
RSI               = FT / GCT
Duty Factor       = GCT / Step_Time
Contact-Flight    = (FT − GCT) / Step_Time
Step Frequency    = 1000 / Step_Time_ms          (Hz)
Mean *            = Σ(metric) / n
GCT Asymmetry %   = |mean_GCT_L − mean_GCT_R| / ((mean_GCT_L + mean_GCT_R) / 2) × 100
FT  Asymmetry %   = |mean_FT_L  − mean_FT_R|  / ((mean_FT_L  + mean_FT_R)  / 2) × 100
ΔGCT L-R          = mean_GCT_L − mean_GCT_R    (ms, signed)
ΔFT  L-R          = mean_FT_L  − mean_FT_R     (ms, signed)
GCT Drift %       = (mean_GCT_last5 − mean_GCT_first5) / mean_GCT_first5 × 100
FT  Drift %       = (mean_FT_last5  − mean_FT_first5)  / mean_FT_first5  × 100
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

# ── helpers ───────────────────────────────────────────────────────────────────


def _safe_div(num: float, denom: float) -> float | None:
    if denom == 0 or np.isnan(num) or np.isnan(denom):
        return None
    return float(num / denom)


def _asym_pct(a: float, b: float) -> float | None:
    """|a − b| / ((a + b) / 2) × 100"""
    denom = (a + b) / 2
    return None if denom == 0 else round(abs(a - b) / denom * 100, 2)


def _drift_pct(first: float, last: float) -> float | None:
    return None if first == 0 else round((last - first) / first * 100, 2)


# ── approach filter ───────────────────────────────────────────────────────────


def _approach_steps(df: pd.DataFrame, approach_end_ms: int | None) -> pd.DataFrame:
    """
    Return only approach-phase contacts.

    approach_end_ms: to_time of the last approach ground contact
        (= clearance_start_ms from the event-specific transform).
        None → use all rows (e.g. sprinting).

    We exclude any contact whose ic_time >= approach_end_ms to drop
    sand landings and jump-phase contacts cleanly.
    """
    if approach_end_ms is None:
        return df.copy()
    return df[df["ic_time"] < approach_end_ms].copy()


# ── 1. Per-step series ────────────────────────────────────────────────────────


def compute_step_series(
    df: pd.DataFrame,
    approach_end_ms: int | None = None,
) -> list[dict[str, Any]]:
    """
    One row per approach ground contact.
    Columns returned:
        stride_num, foot, ic_time, gct_ms, flight_ms, step_time_ms,
        rsi, duty_factor, contact_flight_index, step_frequency_hz

    Used by:
        • GCT L/R overlay line chart
        • FT L/R overlay line chart
        • Step Time stacked bar chart
        • RSI per-step line chart
        • Step Frequency line chart
    """
    app = _approach_steps(df, approach_end_ms).sort_values("ic_time")
    rows: list[dict[str, Any]] = []

    for _, r in app.iterrows():
        gct = int(r["gct_ms"])
        ft = int(r["flight_ms"]) if not pd.isna(r.get("flight_ms", np.nan)) else None
        st = (
            int(r["step_time_ms"])
            if not pd.isna(r.get("step_time_ms", np.nan))
            else None
        )

        rsi = round(ft / gct, 4) if ft and gct else None
        df_ = round(gct / st, 4) if st else None
        cfi = round((ft - gct) / st, 4) if ft is not None and st else None
        freq = round(1000 / st, 4) if st else None

        rows.append(
            {
                "stride_num": int(r["stride_num"]),
                "foot": str(r["foot"]),
                "ic_time": int(r["ic_time"]),
                "gct_ms": gct,
                "flight_ms": ft,
                "step_time_ms": st,
                "rsi": rsi,
                "duty_factor": df_,
                "contact_flight_index": cfi,
                "step_frequency_hz": freq,
            }
        )

    return rows


# ── 2. Stride-time series ─────────────────────────────────────────────────────


def compute_stride_series(
    df: pd.DataFrame,
    approach_end_ms: int | None = None,
) -> list[dict[str, Any]]:
    """
    One row per complete stride (L + R pair with the same stride_num).
    stride_time_ms = Step_Time_L + Step_Time_R

    Used by: Stride Time line chart (🟡 Nice to Have).
    """
    app = _approach_steps(df, approach_end_ms)
    rows: list[dict[str, Any]] = []

    for stride_num, grp in app.groupby("stride_num"):
        left = grp[grp["foot"] == "left"]
        right = grp[grp["foot"] == "right"]

        if left.empty or right.empty:
            continue

        st_l = left.iloc[0].get("step_time_ms")
        st_r = right.iloc[0].get("step_time_ms")

        if pd.isna(st_l) or pd.isna(st_r):
            continue

        rows.append(
            {
                "stride_num": int(stride_num),
                "stride_time_ms": int(st_l) + int(st_r),
            }
        )

    return rows


# ── 3. GCT range buckets ──────────────────────────────────────────────────────

# Default buckets matching the jumps / approach context.
# The frontend can request custom ranges; this default ships with the API.
_DEFAULT_JUMP_BUCKETS: list[tuple[str, int | None, int | None]] = [
    ("< 100 ms", None, 100),
    ("100–120 ms", 100, 120),
    ("120–150 ms", 120, 150),
    ("> 150 ms", 150, None),
]


def compute_gct_range_buckets(
    df: pd.DataFrame,
    approach_end_ms: int | None = None,
    buckets: list[tuple[str, int | None, int | None]] | None = None,
) -> list[dict[str, Any]]:
    """
    Count approach steps whose GCT falls in each range bucket.

    bucket format: (label, lower_bound_inclusive_ms, upper_bound_exclusive_ms)
        None → unbounded on that side.

    Used by: GCT Range pie chart (🟢 MVP).
    """
    if buckets is None:
        buckets = _DEFAULT_JUMP_BUCKETS

    app = _approach_steps(df, approach_end_ms)
    gcts = app["gct_ms"].dropna().astype(int).tolist()
    out = []

    for label, lo, hi in buckets:
        count = sum(
            1 for g in gcts if (lo is None or g >= lo) and (hi is None or g < hi)
        )
        out.append(
            {
                "label": label,
                "count": count,
                "lower_bound_ms": lo,
                "upper_bound_ms": hi,
            }
        )

    return out


# ── 4. Summary KPIs ───────────────────────────────────────────────────────────


def compute_universal_kpis(
    df: pd.DataFrame,
    approach_end_ms: int | None = None,
) -> dict[str, Any]:
    """
    All scalar summary metrics for KPI cards and gauges.

    Metrics (all from StrideTrack Metrics Reference)
    -------------------------------------------------
    Counting
        total_steps, mean_gct_ms, mean_ft_ms, mean_rsi, mean_step_frequency_hz

    Asymmetry  (🟢 MVP)
        gct_asymmetry_pct   |GCT_L − GCT_R| / avg × 100
        ft_asymmetry_pct    |FT_L  − FT_R|  / avg × 100
        delta_gct_lr_ms     GCT_L − GCT_R  (signed, ms)
        delta_ft_lr_ms      FT_L  − FT_R   (signed, ms)

    Drift  (🟢 MVP for jumps – compares first 5 vs last 5 approach steps)
        gct_drift_pct
        ft_drift_pct

    Ratio averages  (🟡 Nice)
        mean_duty_factor
        mean_contact_flight_index
    """
    app = _approach_steps(df, approach_end_ms)

    if app.empty:
        return {}

    left = app[app["foot"] == "left"]
    right = app[app["foot"] == "right"]

    # ── counting ──────────────────────────────────────────────────────────────
    total_steps = int(len(app))
    mean_gct = round(float(app["gct_ms"].mean()), 2)

    ft_vals = app["flight_ms"].dropna()
    mean_ft = round(float(ft_vals.mean()), 2) if not ft_vals.empty else None

    # ── RSI & step frequency ──────────────────────────────────────────────────
    valid = app.dropna(subset=["flight_ms", "step_time_ms"]).copy()
    valid = valid[valid["gct_ms"] > 0]
    valid["rsi"] = valid["flight_ms"] / valid["gct_ms"]
    valid["freq"] = 1000 / valid["step_time_ms"].replace(0, np.nan)

    mean_rsi = round(float(valid["rsi"].mean()), 4) if not valid.empty else None
    mean_freq = round(float(valid["freq"].mean()), 4) if not valid.empty else None

    # ── asymmetry ─────────────────────────────────────────────────────────────
    mean_gct_l = float(left["gct_ms"].mean()) if not left.empty else None
    mean_gct_r = float(right["gct_ms"].mean()) if not right.empty else None
    mean_ft_l = float(left["flight_ms"].dropna().mean()) if not left.empty else None
    mean_ft_r = float(right["flight_ms"].dropna().mean()) if not right.empty else None

    gct_asym = _asym_pct(mean_gct_l, mean_gct_r) if mean_gct_l and mean_gct_r else None
    ft_asym = _asym_pct(mean_ft_l, mean_ft_r) if mean_ft_l and mean_ft_r else None
    delta_gct = round(mean_gct_l - mean_gct_r, 2) if mean_gct_l and mean_gct_r else None
    delta_ft = round(mean_ft_l - mean_ft_r, 2) if mean_ft_l and mean_ft_r else None

    # ── drift: first 5 vs last 5 approach steps ───────────────────────────────
    sorted_app = app.sort_values("ic_time")
    gct_drift = ft_drift = None
    if len(sorted_app) >= 10:
        f5 = sorted_app.iloc[:5]
        l5 = sorted_app.iloc[-5:]
        gct_drift = _drift_pct(float(f5["gct_ms"].mean()), float(l5["gct_ms"].mean()))
        ft_f5 = f5["flight_ms"].dropna()
        ft_l5 = l5["flight_ms"].dropna()
        if not ft_f5.empty and not ft_l5.empty:
            ft_drift = _drift_pct(float(ft_f5.mean()), float(ft_l5.mean()))

    # ── ratio averages ────────────────────────────────────────────────────────
    st_valid = valid[valid["step_time_ms"] > 0].copy()
    st_valid["duty_factor"] = st_valid["gct_ms"] / st_valid["step_time_ms"]
    st_valid["cfi"] = (st_valid["flight_ms"] - st_valid["gct_ms"]) / st_valid[
        "step_time_ms"
    ]
    mean_duty = (
        round(float(st_valid["duty_factor"].mean()), 4) if not st_valid.empty else None
    )
    mean_cfi = round(float(st_valid["cfi"].mean()), 4) if not st_valid.empty else None

    return {
        # counting
        "total_steps": total_steps,
        "mean_gct_ms": mean_gct,
        "mean_ft_ms": mean_ft,
        "mean_rsi": mean_rsi,
        "mean_step_frequency_hz": mean_freq,
        # asymmetry
        "gct_asymmetry_pct": gct_asym,
        "ft_asymmetry_pct": ft_asym,
        "delta_gct_lr_ms": delta_gct,
        "delta_ft_lr_ms": delta_ft,
        # drift
        "gct_drift_pct": gct_drift,
        "ft_drift_pct": ft_drift,
        # ratios
        "mean_duty_factor": mean_duty,
        "mean_contact_flight_index": mean_cfi,
    }
