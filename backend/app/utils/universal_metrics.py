from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _safe_div(num: float, denom: float) -> float | None:
    if denom == 0 or np.isnan(num) or np.isnan(denom):
        return None
    return float(num / denom)


def _asym_pct(a: float, b: float) -> float | None:
    denom = (a + b) / 2
    return None if denom == 0 else round(abs(a - b) / denom * 100, 2)


def _drift_pct(first: float, last: float) -> float | None:
    return None if first == 0 else round((last - first) / first * 100, 2)


def _approach_steps(df: pd.DataFrame, approach_end_ms: int | None) -> pd.DataFrame:
    if approach_end_ms is None:
        return df.copy()
    return df[df["ic_time"] < approach_end_ms].copy()


def compute_step_series(
    df: pd.DataFrame,
    approach_end_ms: int | None = None,
) -> list[dict[str, Any]]:
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


def compute_stride_series(
    df: pd.DataFrame,
    approach_end_ms: int | None = None,
) -> list[dict[str, Any]]:
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


def compute_universal_kpis(
    df: pd.DataFrame,
    approach_end_ms: int | None = None,
) -> dict[str, Any]:
    app = _approach_steps(df, approach_end_ms)

    if app.empty:
        return {}

    left = app[app["foot"] == "left"]
    right = app[app["foot"] == "right"]

    total_steps = int(len(app))
    mean_gct = round(float(app["gct_ms"].mean()), 2)

    ft_vals = app["flight_ms"].dropna()
    mean_ft = round(float(ft_vals.mean()), 2) if not ft_vals.empty else None

    valid = app.dropna(subset=["flight_ms", "step_time_ms"]).copy()
    valid = valid[valid["gct_ms"] > 0]
    valid["rsi"] = valid["flight_ms"] / valid["gct_ms"]
    valid["freq"] = 1000 / valid["step_time_ms"].replace(0, np.nan)

    mean_rsi = round(float(valid["rsi"].mean()), 4) if not valid.empty else None
    mean_freq = round(float(valid["freq"].mean()), 4) if not valid.empty else None

    mean_gct_l = float(left["gct_ms"].mean()) if not left.empty else None
    mean_gct_r = float(right["gct_ms"].mean()) if not right.empty else None
    mean_ft_l = float(left["flight_ms"].dropna().mean()) if not left.empty else None
    mean_ft_r = float(right["flight_ms"].dropna().mean()) if not right.empty else None

    gct_asym = _asym_pct(mean_gct_l, mean_gct_r) if mean_gct_l and mean_gct_r else None
    ft_asym = _asym_pct(mean_ft_l, mean_ft_r) if mean_ft_l and mean_ft_r else None
    delta_gct = round(mean_gct_l - mean_gct_r, 2) if mean_gct_l and mean_gct_r else None
    delta_ft = round(mean_ft_l - mean_ft_r, 2) if mean_ft_l and mean_ft_r else None

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
        "total_steps": total_steps,
        "mean_gct_ms": mean_gct,
        "mean_ft_ms": mean_ft,
        "mean_rsi": mean_rsi,
        "mean_step_frequency_hz": mean_freq,
        "gct_asymmetry_pct": gct_asym,
        "ft_asymmetry_pct": ft_asym,
        "delta_gct_lr_ms": delta_gct,
        "delta_ft_lr_ms": delta_ft,
        "gct_drift_pct": gct_drift,
        "ft_drift_pct": ft_drift,
        "mean_duty_factor": mean_duty,
        "mean_contact_flight_index": mean_cfi,
    }
