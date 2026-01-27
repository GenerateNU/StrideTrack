import pandas as pd
import numpy as np
from pathlib import Path

def extrapolate_second_foot(
    foot1_data: pd.DataFrame,
    time_col: str = "Time",
    force_col: str = "Force",
    phase_offset_ms: int = 180,
    asymmetry_ratio: float = 0.95
) -> pd.DataFrame:
    """Extrapolate second foot data and combine with first foot in single DataFrame."""
    
    if len(foot1_data) < 2:
        raise ValueError("Insufficient data points")
    
    # Create second offseting time and creating assymmetry in force (assuming there is a non dominant foot)
    foot2_data = foot1_data.copy()
    foot2_data[time_col] = foot2_data[time_col] + phase_offset_ms
    foot2_data[force_col] = foot2_data[force_col] * asymmetry_ratio
    
    # Adding variation
    vary = np.random.normal(0, 0.02 * foot2_data[force_col].std(), len(foot2_data))
    foot2_data[force_col] = foot2_data[force_col] + vary

    combined = pd.DataFrame({
        'Time_Foot1': foot1_data[time_col],
        'Force_Foot1': foot1_data[force_col],
        'Time_Foot2': foot2_data[time_col],
        'Force_Foot2': foot2_data[force_col]
    })
    
    return combined




if __name__ == "__main__":
    data_dir = Path(__file__).parent
    sensor_files = ["SensorSprint1.csv", "SensorSprint2.csv", "SensorSprint3.csv"]
    
    for filename in sensor_files:
        print(filename)
        
        foot1_data = pd.read_csv(data_dir / filename)
        combined_data = extrapolate_second_foot(foot1_data)
        
        output_filename = filename.replace(".csv", "_BothFeet.csv")
        combined_data.to_csv(data_dir / output_filename, index=False)
        
        print(output_filename)