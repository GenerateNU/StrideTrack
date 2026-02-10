import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict


def extract_flight_intervals_runs(
    time: np.ndarray,
    force: np.ndarray,
    foot_label: str,
    drop_incomplete: bool = False
) -> List[Dict]:
    n = len(time)
    if n == 0:
        return []

    contact = force != 0
    flight = ~contact  # True where the foot is in the air

    # Find indices where flight state changes
    changes = np.flatnonzero(flight[1:] != flight[:-1]) + 1
    boundaries = np.r_[0, changes, n]

    events: List[Dict] = []

    for start_idx, end_idx in zip(boundaries[:-1], boundaries[1:]):
        if not flight[start_idx]:
            continue

        # Drop incomplete run at the beginning if wanted
        if drop_incomplete and start_idx == 0:
            continue

        start_t = time[start_idx]

        # Determine end time for the flight run
        if end_idx >= n:
            if drop_incomplete:
                continue
            end_t = time[-1]
        else:
            end_t = time[end_idx]

        if end_t <= start_t:
            continue

        events.append({
            "start_time": int(start_t),
            "end_time": int(end_t),
            "total_time": int(end_t - start_t),
            "foot": foot_label
        })

    return events


def merge_back_to_back_same_foot(events_df: pd.DataFrame) -> pd.DataFrame:
    if events_df.empty:
        return events_df

    df = events_df.sort_values(["start_time", "end_time"]).reset_index(drop=True).copy()

    merged_rows: List[Dict] = []
    cur = df.iloc[0].to_dict()

    for i in range(1, len(df)):
        nxt = df.iloc[i].to_dict()

        if nxt["foot"] == cur["foot"]:
            # Extend the current interval
            cur["end_time"] = int(max(cur["end_time"], nxt["end_time"]))
            cur["start_time"] = int(min(cur["start_time"], nxt["start_time"]))
            cur["total_time"] = int(cur["end_time"] - cur["start_time"])
        else:
            merged_rows.append(cur)
            cur = nxt

    merged_rows.append(cur)

    return pd.DataFrame(merged_rows, columns=["start_time", "end_time", "total_time", "foot"])


def extract_flight_times_from_unified_csv(
    input_csv: Path,
    time_col: str = "Time",
    foot1_col: str = "Force_Foot1",
    foot2_col: str = "Force_Foot2",
    drop_incomplete: bool = False,
    foot1_label: str = "Left",
    foot2_label: str = "Right",
    enable_merge_same_foot: bool = True
) -> pd.DataFrame:
    df = pd.read_csv(input_csv)

    for col in (time_col, foot1_col, foot2_col):
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in {input_csv.name}")

    time = df[time_col].to_numpy()
    f1 = df[foot1_col].to_numpy()
    f2 = df[foot2_col].to_numpy()

    events: List[Dict] = []
    events += extract_flight_intervals_runs(time, f1, foot1_label, drop_incomplete)
    events += extract_flight_intervals_runs(time, f2, foot2_label, drop_incomplete)

    out = pd.DataFrame(events, columns=["start_time", "end_time", "total_time", "foot"])
    out = out.sort_values(["start_time", "foot"]).reset_index(drop=True)

    if enable_merge_same_foot and not out.empty:
        out = merge_back_to_back_same_foot(out)
        out = out.sort_values(["start_time", "foot"]).reset_index(drop=True)

    return out


def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    input_dir = PROJECT_ROOT / "R&D" / "Tests" / "Two_finger" / "Raw_data"
    output_dir = PROJECT_ROOT / "R&D" / "Tests" / "Two_finger" / "Flight_times"
    output_dir.mkdir(parents=True, exist_ok=True)

    unified_files = sorted(input_dir.glob("*_BothFeet.csv"))

    drop_incomplete = False

    foot1_label = "Left"
    foot2_label = "Right"

    enable_merge_same_foot = True

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Reading from:  {input_dir}")
    print(f"Writing to:    {output_dir}")

    if not unified_files:
        print(f"No *_BothFeet.csv files found in: {input_dir}")
        return

    for input_file in unified_files:
        output_file = output_dir / input_file.name.replace("_BothFeet.csv", "_FlightTimes.csv")

        flight_df = extract_flight_times_from_unified_csv(
            input_file,
            drop_incomplete=drop_incomplete,
            foot1_label=foot1_label,
            foot2_label=foot2_label,
            enable_merge_same_foot=enable_merge_same_foot
        )

        flight_df.to_csv(output_file, index=False)
        print(f"Wrote: {output_file}")


if __name__ == "__main__":
    main()
