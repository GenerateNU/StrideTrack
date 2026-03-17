import pandas as pd


def get_jump_height(df: pd.DataFrame) -> pd.Series:
    """Returns the jump height for each jump in Boscovs test
    Formula: h = (g × FT²) / 8 = 1.226 × FT² (m, with FT in seconds)"""
    out = transform_stride_cycles_to_bosco_tests(df)
    return out["jump_heights"]


def get_mean_jump_height(df: pd.DataFrame) -> float:
    """Returns the mean jump height for each Boscovs test"""
    out = transform_stride_cycles_to_bosco_tests(df)
    return out["mean_jump_height"]


def get_peak_jump_height(df: pd.DataFrame) -> float:
    """Returns the peak jump height for each Boscovs test"""
    out = transform_stride_cycles_to_bosco_tests(df)
    return out["peak_jump_height"]


def get_jump_freq(df: pd.DataFrame) -> float:
    """Returns the jump freq for each Boscovs test"""
    out = transform_stride_cycles_to_bosco_tests(df)
    return out["jump_frequency"]


def transform_stride_cycles_to_bosco_tests(df: pd.DataFrame) -> dict:
    jump_heights_m = 1.226 * (df["flight_ms"] / 1000) ** 2
    num_jumps = len(df)
    mean_jump_height = jump_heights_m.mean()
    peak_jump_height = jump_heights_m.max()

    total_time_s = (df["next_ic_time"].iloc[-1] - df["ic_time"].iloc[0]) / 1000
    jump_frequency = num_jumps / total_time_s

    return {
        "jump_heights": jump_heights_m,
        "mean_jump_height": mean_jump_height,
        "peak_jump_height": peak_jump_height,
        "jump_frequency": jump_frequency,
    }
