import numpy as np
import pandas as pd


def _drift_window(total: int) -> int:
    return max(3, min(10, round(total * 0.1)))


def calculate_drift(data: list[dict]) -> dict:
    """
    Calculate GCT and FT drift % comparing max-velocity phase to terminal phase.

    Max-velocity baseline is approximated by:
      - GCT: mean of N shortest ground contact times
      - FT: mean of N longest flight times
    Terminal window: last N strides.
    N = round(total_strides * 0.1), clamped between 3 and 10.

    Positive GCT drift = fatigue (more time on ground).
    Negative FT drift = power loss (less time in air).
    """
    n = _drift_window(len(data))

    gct_vals = np.array([row["gct_ms"] for row in data])
    ft_vals = np.array([row["flight_ms"] for row in data])

    gct_baseline = np.mean(np.sort(gct_vals)[:n])
    gct_terminal = np.mean(gct_vals[-n:])

    ft_baseline = np.mean(np.sort(ft_vals)[::-1][:n])
    ft_terminal = np.mean(ft_vals[-n:])

    gct_drift = (
        float((gct_terminal - gct_baseline) / gct_baseline * 100)
        if gct_baseline
        else 0.0
    )
    ft_drift = (
        float((ft_terminal - ft_baseline) / ft_baseline * 100) if ft_baseline else 0.0
    )

    return {
        "gct_drift_pct": round(gct_drift, 2),
        "ft_drift_pct": round(ft_drift, 2),
    }


def calculate_step_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Step Frequency for each step.

    Formula: step_frequency_hz = 1000 / step_time_ms

    Steps per second. Elite sprinters: 4.5–5.0 Hz at max velocity.
    Typical buildup: ~3.5 Hz at start → ~4.8 Hz at max velocity.

    Args:
        df: Transformed stride DataFrame

    Returns:
        DataFrame with columns: stride_num, foot, ic_time, step_frequency_hz
    """
    if df.empty:
        return pd.DataFrame(
            columns=["stride_num", "foot", "ic_time", "step_frequency_hz"]
        )

    result = df[["stride_num", "foot", "ic_time"]].copy()
    result["step_frequency_hz"] = 1000 / df["step_time_ms"]

    return result


def calculate_mean_step_frequency(df: pd.DataFrame) -> float:
    """
    Calculate mean Step Frequency across all steps.

    Returns:
        Mean step frequency in Hz
    """
    if df.empty:
        return 0.0
    return float((1000 / df["step_time_ms"]).mean())


def calculate_sprint_metrics(df: pd.DataFrame) -> dict:
    return {
        "summary_metrics": {
            "mean_step_frequency_hz": calculate_mean_step_frequency(df),
        },
        "time_series_metrics": {
            "step_frequency": calculate_step_frequency(df),
        },
    }


def main() -> None:
    from pathlib import Path

    csv_path = Path(
        "../R&D/Tests/Two_foot/Transformed_Data/SensorSprint3_TransformedData.csv"
    )

    if not csv_path.exists():
        print(f"CSV not found at: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    print("Step Frequency (first 10 rows):")
    print(calculate_step_frequency(df).head(10))
    print()
    print("Mean Step Frequency:", calculate_mean_step_frequency(df), "Hz")


if __name__ == "__main__":
    main()
