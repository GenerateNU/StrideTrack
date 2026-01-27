import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple

def extrapolate_second_foot(
    foot1_data: pd.DataFrame,
    time_col: str = "Timestamp",
    force_col: str = "Force",
    sample_shift: int = 26,
    asymmetry_ratio: float = 0.99,
    adc_min: float = 0.0,
    adc_max: float = 4095.0
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extrapolate second foot data and combine with first foot in single DataFrame.
    Added asymmetry and slight variation to simulate real world data. The asymmetry is meant
    for a non dominant foot if there is one. Returns unifed DataFrame of mocked two foot sensors.
    """
    unified_df = pd.DataFrame({'Time': foot1_data[time_col].values})
    unified_df['Force_Foot1'] = foot1_data[force_col].astype(int).values

    f2 = np.roll(unified_df['Force_Foot1'].values, sample_shift) * asymmetry_ratio

    # Variation 
    vary = np.random.normal(0, 0.02 * np.std(f2), len(f2))
    f2 = np.clip(f2 + vary, adc_min, adc_max)
    f2 = np.rint(f2).astype(int)

    unified_df['Force_Foot2'] = f2
    
    # Separate foot data version
    separate_df = pd.DataFrame({
        'Time_Foot1': unified_df['Time'],
        'Force_Foot1': unified_df['Force_Foot1'],
        'Time_Foot2': unified_df['Time'],
        'Force_Foot2': unified_df['Force_Foot2']
    })
    
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
