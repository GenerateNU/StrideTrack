import numpy as np
import pandas as pd

# Counting Metrics


def calculate_total_steps(df: pd.DataFrame) -> int:
    """
    Calculate total number of steps (ground contacts) in the run.

    Args:
        df: Transformed stride DataFrame
    Returns:
        Total count of steps (each row is one step)

    Example:
        >>> df = pd.DataFrame({'stride_num': [1, 1, 2, 2], 'foot': ['left', 'right', 'left', 'right']})
        >>> calculate_total_steps(df)
        4
    """
    return len(df)


def calculate_mean_gct(df: pd.DataFrame) -> float:
    """
    Calculate mean ground contact time across all steps.

    Formula: Σ(GCT) / n

    Args:
        df: Transformed stride DataFrame

    Returns:
        Mean GCT in milliseconds

    Example:
        >>> df = pd.DataFrame({'gct_ms': [200, 210, 205, 215]})
        >>> calculate_mean_gct(df)
        207.5
    """
    if df.empty:
        return 0.0
    return float(df["gct_ms"].mean())


def calculate_mean_flight_time(df: pd.DataFrame) -> float:
    """
    Calculate mean flight time across all steps.

    Formula: Σ(FT) / n

    Args:
        df: Transformed stride DataFrame

    Returns:
        Mean flight time in milliseconds

    Example:
        >>> df = pd.DataFrame({'flight_ms': [100, 110, 105, 115]})
        >>> calculate_mean_flight_time(df)
        107.5
    """
    if df.empty:
        return 0.0
    return float(df["flight_ms"].mean())


# Ratio Metrics


def calculate_rsi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Reactive Strength Index (RSI) for each step.

    Formula: RSI = FT / GCT

    RSI indicates leg spring stiffness and reactive ability. Higher RSI means
    more "bounce". Elite sprinters typically have RSI > 1.0 at max velocity.

    Args:
        df: Transformed stride DataFrame

    Returns:
        DataFrame with columns: stride_num, foot, ic_time, rsi

    Example:
        >>> df = pd.DataFrame({
        ...     'stride_num': [1, 1],
        ...     'foot': ['left', 'right'],
        ...     'ic_time': [0, 100],
        ...     'gct_ms': [200, 210],
        ...     'flight_ms': [300, 315]
        ... })
        >>> result = calculate_rsi(df)
        >>> result['rsi'].tolist()
        [1.5, 1.5]
    """
    if df.empty:
        return pd.DataFrame(columns=["stride_num", "foot", "ic_time", "rsi"])

    result = df[["stride_num", "foot", "ic_time"]].copy()
    result["rsi"] = df["flight_ms"] / df["gct_ms"]

    return result


def calculate_mean_rsi(df: pd.DataFrame) -> float:
    """
    Calculate mean RSI across all steps.

    Args:
        df: Transformed stride DataFrame

    Returns:
        Mean RSI value

    Example:
        >>> df = pd.DataFrame({'gct_ms': [200, 200], 'flight_ms': [300, 400]})
        >>> calculate_mean_rsi(df)
        1.75
    """
    if df.empty:
        return 0.0

    rsi_values = df["flight_ms"] / df["gct_ms"]
    return float(rsi_values.mean())


def calculate_duty_factor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Duty Factor for each step.

    Formula: Duty Factor = GCT / Step_Time

    Duty factor represents the proportion of step time spent on the ground.
    < 0.5 = flight-dominant (running)
    > 0.5 = ground-dominant (walking/fatigue)

    Args:
        df: Transformed stride DataFrame

    Returns:
        DataFrame with columns: stride_num, foot, ic_time, duty_factor

    Example:
        >>> df = pd.DataFrame({
        ...     'stride_num': [1, 1],
        ...     'foot': ['left', 'right'],
        ...     'ic_time': [0, 100],
        ...     'gct_ms': [200, 300],
        ...     'step_time_ms': [500, 600]
        ... })
        >>> result = calculate_duty_factor(df)
        >>> result['duty_factor'].tolist()
        [0.4, 0.5]
    """
    if df.empty:
        return pd.DataFrame(columns=["stride_num", "foot", "ic_time", "duty_factor"])

    result = df[["stride_num", "foot", "ic_time"]].copy()
    result["duty_factor"] = df["gct_ms"] / df["step_time_ms"]

    return result


def calculate_contact_flight_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Contact-Flight Index for each step.

    Formula: CFI = (FT − GCT) / Step_Time

    Represents the balance between flight and contact time.
    Positive = flight-dominant
    Negative = contact-dominant

    Args:
        df: Transformed stride DataFrame

    Returns:
        DataFrame with columns: stride_num, foot, ic_time, contact_flight_index

    Example:
        >>> df = pd.DataFrame({
        ...     'stride_num': [1, 1],
        ...     'foot': ['left', 'right'],
        ...     'ic_time': [0, 100],
        ...     'gct_ms': [200, 300],
        ...     'flight_ms': [300, 200],
        ...     'step_time_ms': [500, 500]
        ... })
        >>> result = calculate_contact_flight_index(df)
        >>> result['contact_flight_index'].tolist()
        [0.2, -0.2]
    """
    if df.empty:
        return pd.DataFrame(
            columns=["stride_num", "foot", "ic_time", "contact_flight_index"]
        )

    result = df[["stride_num", "foot", "ic_time"]].copy()
    result["contact_flight_index"] = (df["flight_ms"] - df["gct_ms"]) / df[
        "step_time_ms"
    ]

    return result


# Aysmmetry metircs


def _get_paired_strides(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function to pair left and right steps within the same stride.

    Returns a DataFrame with one row per stride containing both feet's metrics.
    """
    if df.empty:
        return pd.DataFrame()

    # Separate left and right foot data
    left_df = df[df["foot"] == "left"].set_index("stride_num")
    right_df = df[df["foot"] == "right"].set_index("stride_num")

    # Merge on stride_num to get paired data
    paired = left_df.join(right_df, lsuffix="_left", rsuffix="_right", how="inner")

    return paired.reset_index()


def calculate_gct_asymmetry_percent(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate GCT asymmetry percentage for each stride.

    Formula: |GCT_L − GCT_R| / ((GCT_L + GCT_R) / 2) × 100

    Percentage difference in GCT between feet. Values > 10% may indicate
    injury risk or compensation. Target: < 5%.

    Args:
        df: Transformed stride DataFrame

    Returns:
        DataFrame with columns: stride_num, ic_time, gct_asymmetry_percent, gct_left, gct_right

    Example:
        >>> df = pd.DataFrame({
        ...     'stride_num': [1, 1, 2, 2],
        ...     'foot': ['left', 'right', 'left', 'right'],
        ...     'ic_time': [0, 100, 500, 600],
        ...     'gct_ms': [200, 220, 200, 180]
        ... })
        >>> result = calculate_gct_asymmetry_percent(df)
        >>> round(result.iloc[0]['gct_asymmetry_percent'], 2)
        9.52
    """
    paired = _get_paired_strides(df)

    if paired.empty:
        return pd.DataFrame(
            columns=[
                "stride_num",
                "ic_time",
                "gct_asymmetry_percent",
                "gct_left",
                "gct_right",
            ]
        )

    gct_left = paired["gct_ms_left"]
    gct_right = paired["gct_ms_right"]

    avg_gct = (gct_left + gct_right) / 2
    asymmetry = (np.abs(gct_left - gct_right) / avg_gct) * 100

    result = pd.DataFrame(
        {
            "stride_num": paired["stride_num"],
            "ic_time": paired["ic_time_left"],  # Use left foot IC as reference
            "gct_asymmetry_percent": asymmetry,
            "gct_left": gct_left,
            "gct_right": gct_right,
        }
    )

    return result


def calculate_ft_asymmetry_percent(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Flight Time asymmetry percentage for each stride.

    Formula: |FT_L − FT_R| / ((FT_L + FT_R) / 2) × 100

    Push-off power difference between legs. Often correlates with GCT asymmetry.

    Args:
        df: Transformed stride DataFrame

    Returns:
        DataFrame with columns: stride_num, ic_time, ft_asymmetry_percent, ft_left, ft_right

    Example:
        >>> df = pd.DataFrame({
        ...     'stride_num': [1, 1, 2, 2],
        ...     'foot': ['left', 'right', 'left', 'right'],
        ...     'ic_time': [0, 100, 500, 600],
        ...     'flight_ms': [100, 120, 100, 90]
        ... })
        >>> result = calculate_ft_asymmetry_percent(df)
        >>> round(result.iloc[0]['ft_asymmetry_percent'], 2)
        18.18
    """
    paired = _get_paired_strides(df)

    if paired.empty:
        return pd.DataFrame(
            columns=[
                "stride_num",
                "ic_time",
                "ft_asymmetry_percent",
                "ft_left",
                "ft_right",
            ]
        )

    ft_left = paired["flight_ms_left"]
    ft_right = paired["flight_ms_right"]

    avg_ft = (ft_left + ft_right) / 2
    asymmetry = (np.abs(ft_left - ft_right) / avg_ft) * 100

    result = pd.DataFrame(
        {
            "stride_num": paired["stride_num"],
            "ic_time": paired["ic_time_left"],
            "ft_asymmetry_percent": asymmetry,
            "ft_left": ft_left,
            "ft_right": ft_right,
        }
    )

    return result


def calculate_gct_difference_lr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate raw GCT difference (Left - Right) for each stride.

    Formula: ΔGCT L-R = GCT_L − GCT_R

    Shows direction of imbalance:
    - Positive = left foot longer contact
    - Negative = right foot longer contact

    Args:
        df: Transformed stride DataFrame

    Returns:
        DataFrame with columns: stride_num, ic_time, gct_diff_lr_ms, gct_left, gct_right

    Example:
        >>> df = pd.DataFrame({
        ...     'stride_num': [1, 1, 2, 2],
        ...     'foot': ['left', 'right', 'left', 'right'],
        ...     'ic_time': [0, 100, 500, 600],
        ...     'gct_ms': [200, 220, 200, 180]
        ... })
        >>> result = calculate_gct_difference_lr(df)
        >>> result['gct_diff_lr_ms'].tolist()
        [-20, 20]
    """
    paired = _get_paired_strides(df)

    if paired.empty:
        return pd.DataFrame(
            columns=["stride_num", "ic_time", "gct_diff_lr_ms", "gct_left", "gct_right"]
        )

    result = pd.DataFrame(
        {
            "stride_num": paired["stride_num"],
            "ic_time": paired["ic_time_left"],
            "gct_diff_lr_ms": paired["gct_ms_left"] - paired["gct_ms_right"],
            "gct_left": paired["gct_ms_left"],
            "gct_right": paired["gct_ms_right"],
        }
    )

    return result


def calculate_ft_difference_lr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate raw Flight Time difference (Left - Right) for each stride.

    Formula: ΔFT L-R = FT_L − FT_R

    Shows direction and magnitude of push-off asymmetry:
    - Positive = left foot longer flight
    - Negative = right foot longer flight

    Args:
        df: Transformed stride DataFrame

    Returns:
        DataFrame with columns: stride_num, ic_time, ft_diff_lr_ms, ft_left, ft_right

    Example:
        >>> df = pd.DataFrame({
        ...     'stride_num': [1, 1, 2, 2],
        ...     'foot': ['left', 'right', 'left', 'right'],
        ...     'ic_time': [0, 100, 500, 600],
        ...     'flight_ms': [100, 120, 100, 90]
        ... })
        >>> result = calculate_ft_difference_lr(df)
        >>> result['ft_diff_lr_ms'].tolist()
        [-20, 10]
    """
    paired = _get_paired_strides(df)

    if paired.empty:
        return pd.DataFrame(
            columns=["stride_num", "ic_time", "ft_diff_lr_ms", "ft_left", "ft_right"]
        )

    result = pd.DataFrame(
        {
            "stride_num": paired["stride_num"],
            "ic_time": paired["ic_time_left"],
            "ft_diff_lr_ms": paired["flight_ms_left"] - paired["flight_ms_right"],
            "ft_left": paired["flight_ms_left"],
            "ft_right": paired["flight_ms_right"],
        }
    )

    return result


def calculate_mean_gct_asymmetry(df: pd.DataFrame) -> float:
    """
    Calculate mean GCT asymmetry percentage across all strides.

    Args:
        df: Transformed stride DataFrame

    Returns:
        Mean GCT asymmetry percentage
    """
    asymmetry_df = calculate_gct_asymmetry_percent(df)
    if asymmetry_df.empty:
        return 0.0
    return float(asymmetry_df["gct_asymmetry_percent"].mean())


def calculate_mean_ft_asymmetry(df: pd.DataFrame) -> float:
    """
    Calculate mean Flight Time asymmetry percentage across all strides.

    Args:
        df: Transformed stride DataFrame

    Returns:
        Mean FT asymmetry percentage
    """
    asymmetry_df = calculate_ft_asymmetry_percent(df)
    if asymmetry_df.empty:
        return 0.0
    return float(asymmetry_df["ft_asymmetry_percent"].mean())


def calculate_all_metrics(df: pd.DataFrame) -> dict:
    """
    Calculate all metrics at once and return as a dictionary.

    Args:
        df: Transformed stride DataFrame

    Returns:
        Dictionary containing:
            - summary_metrics: dict of single-value metrics
            - time_series_metrics: dict of DataFrames with per-stride metrics

    Example:
        >>> df = pd.DataFrame({
        ...     'stride_num': [1, 1],
        ...     'foot': ['left', 'right'],
        ...     'ic_time': [0, 100],
        ...     'to_time': [200, 300],
        ...     'next_ic_time': [500, 600],
        ...     'gct_ms': [200, 200],
        ...     'flight_ms': [300, 300],
        ...     'step_time_ms': [500, 500]
        ... })
        >>> metrics = calculate_all_metrics(df)
        >>> metrics['summary_metrics']['total_steps']
        2
    """
    summary_metrics = {
        "total_steps": calculate_total_steps(df),
        "mean_gct_ms": calculate_mean_gct(df),
        "mean_flight_time_ms": calculate_mean_flight_time(df),
        "mean_rsi": calculate_mean_rsi(df),
        "mean_gct_asymmetry_percent": calculate_mean_gct_asymmetry(df),
        "mean_ft_asymmetry_percent": calculate_mean_ft_asymmetry(df),
    }

    time_series_metrics = {
        "rsi": calculate_rsi(df),
        "duty_factor": calculate_duty_factor(df),
        "contact_flight_index": calculate_contact_flight_index(df),
        "gct_asymmetry_percent": calculate_gct_asymmetry_percent(df),
        "ft_asymmetry_percent": calculate_ft_asymmetry_percent(df),
        "gct_difference_lr": calculate_gct_difference_lr(df),
        "ft_difference_lr": calculate_ft_difference_lr(df),
    }

    return {
        "summary_metrics": summary_metrics,
        "time_series_metrics": time_series_metrics,
    }


def main() -> None:
    """
    Test function using real transformed data from R&D/Tests.
    Uses: R&D/Tests/Two_foot/Transformed_Data/SensorSprint3_TransformedData.csv
    """
    from pathlib import Path

    # Path to the transformed CSV file
    csv_path = Path(
        "../R&D/Tests/Two_foot/Transformed_Data/SensorSprint3_TransformedData.csv"
    )

    if not csv_path.exists():
        print(f"❌ CSV file not found at: {csv_path}")
        print("Make sure you're running from the backend directory")
        return

    # Load transformed data
    df = pd.read_csv(csv_path)

    print("Loaded Data from SensorSprint3_TransformedData.csv")
    print(f"Total rows: {len(df)}")
    print()
    print("Sample Data (first 10 rows):")
    print(df.head(10))
    print()

    # Test all counting metrics
    print("=" * 60)
    print("COUNTING METRICS")
    print("=" * 60)
    print("calculate_total_steps():", calculate_total_steps(df))
    print("calculate_mean_gct():", calculate_mean_gct(df))
    print("calculate_mean_flight_time():", calculate_mean_flight_time(df))
    print()

    # Test ratio metrics
    print("=" * 60)
    print("RATIO METRICS")
    print("=" * 60)
    print("calculate_mean_rsi():", calculate_mean_rsi(df))
    print()
    print("calculate_rsi():")
    print(calculate_rsi(df).head(10))
    print()

    print("calculate_duty_factor():")
    print(calculate_duty_factor(df).head(10))
    print()

    print("calculate_contact_flight_index():")
    print(calculate_contact_flight_index(df).head(10))
    print()

    # Test asymmetry metrics
    print("=" * 60)
    print("ASYMMETRY METRICS")
    print("=" * 60)
    print("calculate_mean_gct_asymmetry():", calculate_mean_gct_asymmetry(df))
    print("calculate_mean_ft_asymmetry():", calculate_mean_ft_asymmetry(df))
    print()


if __name__ == "__main__":
    main()
