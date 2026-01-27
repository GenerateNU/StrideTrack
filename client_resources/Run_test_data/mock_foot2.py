import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple

def extrapolate_second_foot(
    foot1_data: pd.DataFrame,
    time_col: str = "Timestamp",
    force_col: str = "Force",
    phase_offset: int = 265,
    asymmetry_ratio: float = 0.99
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extrapolate second foot data and combine with first foot in single DataFrame.
    Added asymmetry and slight variation to simulate real world data. The asymmetry is meant
    for a non dominant foot if there is one.

    Outputs: Two dataframes, one of which has data with unified time column for both feet whereas
    the other has separate time columns for each foot.
    """
    # Offset and asymmetry
    foot2_data = foot1_data.copy()
    foot2_data[time_col] = foot2_data[time_col] + phase_offset
    foot2_data[force_col] = foot2_data[force_col] * asymmetry_ratio
    
    # Variation 
    vary = np.random.normal(0, 0.02 * foot2_data[force_col].std(), len(foot2_data))
    foot2_data[force_col] = foot2_data[force_col] + vary
    
    # Separate foot data version
    separate_df = pd.DataFrame({
        'Time_Foot1': foot1_data[time_col],
        'Force_Foot1': foot1_data[force_col],
        'Time_Foot2': foot2_data[time_col],
        'Force_Foot2': foot2_data[force_col]
    })
    
    # Both feet version
    min_time = max(foot1_data[time_col].min(), foot2_data[time_col].min())
    max_time = min(foot1_data[time_col].max(), foot2_data[time_col].max())
    
    all_times = pd.concat([foot1_data[time_col], foot2_data[time_col]]).sort_values().unique()
    all_times = all_times[(all_times >= min_time) & (all_times <= max_time)]
    
    unified_df = pd.DataFrame({'Time': all_times})
    
    foot1_mapped = foot1_data.set_index(time_col)[force_col]
    foot2_mapped = foot2_data.set_index(time_col)[force_col]
    
    unified_df['Force_Foot1'] = unified_df['Time'].map(foot1_mapped).interpolate(method='linear')
    unified_df['Force_Foot2'] = unified_df['Time'].map(foot2_mapped).interpolate(method='linear')
    
    return unified_df, separate_df

if __name__ == "__main__":
    data_dir = Path(__file__).parent
    sensor_files = ["SensorSprint1.csv", "SensorSprint2.csv", "SensorSprint3.csv"]
    
    for filename in sensor_files:
        print(filename)
        foot1_data = pd.read_csv(data_dir / filename)
        
        unified_data, separate_data = extrapolate_second_foot(foot1_data)
        
        unified_data.to_csv(data_dir / filename.replace(".csv", "_BothFeet_Unified.csv"), index=False)
        separate_data.to_csv(data_dir / filename.replace(".csv", "_BothFeet_Separate.csv"), index=False)
