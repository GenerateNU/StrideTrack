import pandas as pd
import numpy as np
from pathlib import Path


def dilate_binary(x: np.ndarray, k: int) -> np.ndarray:
    if k <= 0:
        return x
    
    x_int = x.astype(int)
    kernel = np.ones(2 * k + 1, dtype=int)
    
    return (np.convolve(x_int, kernel, mode="same") > 0)


def make_two_feet_for_timing(
    foot1_data: pd.DataFrame,
    time_col: str = "Timestamp",
    force_col: str = "Force",
    contact_threshold: int = 4075,
    overlap_extension: int = 0,
    adc_max: int = 4095
) -> pd.DataFrame:
    # Clean readings where force is 0
    cleaned = foot1_data.loc[foot1_data[force_col] != 0, [time_col, force_col]].copy()
    cleaned[force_col] = cleaned[force_col].astype(int)

    # Build unified dataframe
    unified_df = pd.DataFrame({
        "Time": cleaned[time_col].values,
        "Force_Foot1": cleaned[force_col].values
    })

    #  Determine Foot1 contact
    foot1_on_ground = unified_df["Force_Foot1"].values >= contact_threshold

    # Foot2 is complement
    foot2_on_ground = ~foot1_on_ground

    # Extend Foot2 contact blocks to create overlap
    foot2_on_ground = dilate_binary(foot2_on_ground, overlap_extension)

    # Convert Foot2 contact boolean into force
    unified_df["Force_Foot2"] = np.where(foot2_on_ground, adc_max, 0).astype(int)

    return unified_df


if __name__ == "__main__":
    from pathlib import Path
    import pandas as pd

    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    input_dir = PROJECT_ROOT / "client_resources" / "Run_test_data"
    output_dir = PROJECT_ROOT / "R&D" / "Tests" / "Two_foot" / "Raw_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    sensor_files = ["SensorSprint1.csv", "SensorSprint2.csv", "SensorSprint3.csv"]

    contact_threshold = 4075
    overlap_extension = 3

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Reading from:  {input_dir}")
    print(f"Writing to:    {output_dir}")

    for filename in sensor_files:
        input_path = input_dir / filename

        if not input_path.exists():
            print(f"Skipping (not found): {input_path}")
            continue

        print(f"Processing: {input_path.name}")
        foot1_data = pd.read_csv(input_path)

        unified_data = make_two_feet_for_timing(
            foot1_data,
            contact_threshold=contact_threshold,
            overlap_extension=overlap_extension
        )

        output_path = output_dir / filename.replace(".csv", "_BothFeet.csv")
        unified_data.to_csv(output_path, index=False)

        print(f"Wrote: {output_path}")
