import numpy as np
import pandas as pd


def _median_dt_ms(time: np.ndarray) -> float:
    """
    Return the median time difference between consecutive timestamps.
    """
    dt = np.diff(time.astype(np.int64))
    dt = dt[dt > 0]

    return float(np.median(dt)) if dt.size else 1.0


def _fill_short_zero_dropouts_in_contact(
    contact: np.ndarray, max_hole_len_samples: int
) -> np.ndarray:
    """
    Fill brief False gaps inside the contact signal (bounded by True) so short sensor dropouts don't split one stance
    into multiple stances.
    """
    if max_hole_len_samples <= 0 or contact.size == 0:
        return contact

    x = contact.copy()
    n = len(x)
    i = 0

    while i < n:
        if x[i]:
            i += 1
            continue

        j = i
        while j < n and not x[j]:
            j += 1

        run_len = j - i
        if run_len <= max_hole_len_samples and i > 0 and j < n and x[i - 1] and x[j]:
            x[i:j] = True

        i = j

    return x


def _extract_stance_intervals(
    time: np.ndarray, force: np.ndarray, threshold: int
) -> pd.DataFrame:
    """
    Identify each continuous ground-contact segment where force stays above the threshold, and return its start (IC)
    and end (TO) indices and timestamps.
    """
    n = len(time)
    if n == 0:
        return pd.DataFrame(columns=["ic_idx", "to_idx", "ic_time_raw", "to_time_raw"])

    contact = force > threshold
    changes = np.flatnonzero(contact[1:] != contact[:-1]) + 1
    boundaries = np.r_[0, changes, n]

    rows: list[dict] = []
    for s, e in zip(boundaries[:-1], boundaries[1:], strict=False):
        if not contact[s]:
            continue

        ic_idx = int(s)
        to_idx = int(e)
        ic_time_raw = int(time[ic_idx])
        to_time_raw = int(time[to_idx] if to_idx < n else time[-1])

        if to_time_raw > ic_time_raw:
            rows.append(
                {
                    "ic_idx": ic_idx,
                    "to_idx": to_idx,
                    "ic_time_raw": ic_time_raw,
                    "to_time_raw": to_time_raw,
                }
            )

    return pd.DataFrame(rows)


def _build_stride_rows(
    stance_df: pd.DataFrame, foot_label: str, t0_raw: int
) -> pd.DataFrame:
    """
    Turn one foot's stance intervals into complete stride-cycle rows by pairing each initial contact with its toe-off
    and the next initial contact of the same foot, then computing ground contact time and flight time in milliseconds
    relative to the file start.
    """
    if stance_df.empty:
        return pd.DataFrame(
            columns=[
                "foot",
                "ic_time",
                "to_time",
                "next_ic_time",
                "gct_ms",
                "flight_ms",
                "step_time_ms",
            ]
        )

    stance_df = stance_df.sort_values("ic_time_raw").reset_index(drop=True)
    next_ic_raw = stance_df["ic_time_raw"].shift(-1)

    out = pd.DataFrame(
        {
            "foot": foot_label.lower(),
            "ic_time": (stance_df["ic_time_raw"] - t0_raw).astype("int64"),
            "to_time": (stance_df["to_time_raw"] - t0_raw).astype("int64"),
            "next_ic_time": (next_ic_raw - t0_raw).astype("float64"),
        }
    )

    out = out.dropna(subset=["next_ic_time"]).copy()

    out["next_ic_time"] = out["next_ic_time"].astype("int64")
    out["gct_ms"] = (out["to_time"] - out["ic_time"]).astype("int64")
    out["flight_ms"] = (out["next_ic_time"] - out["to_time"]).astype("int64")
    out["step_time_ms"] = (out["gct_ms"] + out["flight_ms"]).astype("int64")

    return out


def _assign_stride_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign a stride number to each row by sorting by initial contact time and grouping events until both left and
    right feet have seen an initial contact, then incrementing the stride number.
    """

    if df.empty:
        return df

    df = df.sort_values(["ic_time", "foot"]).reset_index(drop=True).copy()

    stride_nums: list[int] = []
    stride = 1
    seen: set = set()

    for _, row in df.iterrows():
        stride_nums.append(stride)
        seen.add(row["foot"])
        if "left" in seen and "right" in seen:
            stride += 1
            seen = set()

    df.insert(0, "stride_num", stride_nums)
    return df


# Main transformation


def transform_feet_to_stride_cycles(
    df: pd.DataFrame,
    time_col: str = "Time",
    foot1_col: str = "Force_Foot1",
    foot2_col: str = "Force_Foot2",
    foot1_label: str = "left",
    foot2_label: str = "right",
    force_threshold: int = 0,
    dropout_fill_ms: int = 20,
) -> pd.DataFrame:
    """
    Final output columns:
      stride_num, foot, ic_time, to_time, next_ic_time, gct_ms, flight_ms, step_time_ms
    """
    for col in (time_col, foot1_col, foot2_col):
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in uploaded CSV")

    time = df[time_col].to_numpy(dtype=np.int64)
    f1 = df[foot1_col].to_numpy(dtype=np.int64)
    f2 = df[foot2_col].to_numpy(dtype=np.int64)

    if time.size == 0:
        return pd.DataFrame(
            columns=[
                "stride_num",
                "foot",
                "ic_time",
                "to_time",
                "next_ic_time",
                "gct_ms",
                "flight_ms",
                "step_time_ms",
            ]
        )

    # Convert dropout_fill_ms to samples using median dt
    med_dt = _median_dt_ms(time)
    max_hole_len_samples = int(round(dropout_fill_ms / med_dt))

    # Per-foot contact with dropout fix
    contact1 = f1 > force_threshold
    contact2 = f2 > force_threshold
    contact1 = _fill_short_zero_dropouts_in_contact(contact1, max_hole_len_samples)
    contact2 = _fill_short_zero_dropouts_in_contact(contact2, max_hole_len_samples)

    # Use the cleaned contact signals to build stance intervals:
    stance1 = _extract_stance_intervals(time, contact1.astype(np.int8), threshold=0)
    stance2 = _extract_stance_intervals(time, contact2.astype(np.int8), threshold=0)

    t0_raw = int(time[0])

    # Build per-foot stride-cycle rows
    foot1_rows = _build_stride_rows(stance1, foot1_label, t0_raw)
    foot2_rows = _build_stride_rows(stance2, foot2_label, t0_raw)

    out = pd.concat([foot1_rows, foot2_rows], ignore_index=True)

    # Assign stride numbers
    out = _assign_stride_numbers(out)

    # Final column order
    out = (
        out[
            [
                "stride_num",
                "foot",
                "ic_time",
                "to_time",
                "next_ic_time",
                "gct_ms",
                "flight_ms",
                "step_time_ms",
            ]
        ]
        .sort_values(["stride_num", "foot", "ic_time"])
        .reset_index(drop=True)
    )

    return out
