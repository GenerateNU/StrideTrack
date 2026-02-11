import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple


def find_contact_blocks(force: np.ndarray) -> List[Tuple[int, int]]:
    contact = force > 0
    if len(force) == 0:
        return []

    changes = np.flatnonzero(contact[1:] != contact[:-1]) + 1
    bounds = np.r_[0, changes, len(force)]

    blocks: List[Tuple[int, int]] = []
    for s, e in zip(bounds[:-1], bounds[1:]):
        if contact[s]:
            blocks.append((s, e))
    return blocks


def add_noise_nonzero(x: np.ndarray, noise_max: int, adc_max: int, rng) -> np.ndarray:
    x = x.astype(int)
    x = np.clip(x, 0, adc_max)

    if noise_max <= 0:
        return x.astype(int)

    mask = x != 0
    noise = rng.integers(-noise_max, noise_max + 1, size=x.shape)

    out = x.copy()
    out[mask] += noise[mask]
    return np.clip(out, 0, adc_max).astype(int)


def make_two_feet_phase_shifted_adaptive(
    foot1_data: pd.DataFrame,
    time_col: str = "Timestamp",
    force_col: str = "Force",
    buffer_samples: int = 3,
    noise_max: int = 12,
    adc_max: int = 4095,
) -> pd.DataFrame:
    rng = np.random.default_rng()

    # Load
    df = foot1_data[[time_col, force_col]].copy()

    time = df[time_col].to_numpy()
    f1_raw = df[force_col].to_numpy()

    # Noise on Foot1 non-zero values
    f1 = add_noise_nonzero(f1_raw, noise_max, adc_max, rng)

    blocks = find_contact_blocks(f1)
    f2 = np.zeros_like(f1)

    if not blocks:
        return pd.DataFrame({"Time": time, "Force_Foot1": f1, "Force_Foot2": f2})

    n = len(f1)

    for i, (start, end) in enumerate(blocks):
        duration = end - start
        if duration <= 0:
            continue

        # Shift so Foot2 starts after Foot1 ends + buffer
        shift = duration + buffer_samples
        new_start = start + shift  # equals end + buffer_samples
        new_end = end + shift  # equals end + duration + buffer_samples

        if new_start >= n:
            continue

        # Truncate so Foot2 ends buffer_samples before the next Foot1 contact starts
        if i < len(blocks) - 1:
            next_start, _ = blocks[i + 1]
            cutoff = max(0, next_start - buffer_samples)
            new_end = min(new_end, cutoff)

        # Boundaries
        new_end = min(new_end, n)

        if new_end <= new_start:
            continue

        span = new_end - new_start
        src_end = start + span

        f2[new_start:new_end] = np.maximum(f2[new_start:new_end], f1[start:src_end])

    # Noise on Foot2 non-zero values
    f2 = add_noise_nonzero(f2, noise_max, adc_max, rng)

    return pd.DataFrame({"Time": time, "Force_Foot1": f1, "Force_Foot2": f2})


def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    input_dir = PROJECT_ROOT / "client_resources" / "Finger_test_data"
    output_dir = PROJECT_ROOT / "R&D" / "Tests" / "Two_finger" / "Raw_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    buffer_samples = 3
    noise_max = 12
    adc_max = 4095

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Reading from:  {input_dir}")
    print(f"Writing to:    {output_dir}")

    csvs = sorted(input_dir.glob("*.csv"))
    if not csvs:
        print(f"No CSV files found in: {input_dir}")
        return

    for input_path in csvs:
        print(f"Processing: {input_path.name}")
        df = pd.read_csv(input_path)

        unified = make_two_feet_phase_shifted_adaptive(
            df, buffer_samples=buffer_samples, noise_max=noise_max, adc_max=adc_max
        )

        out_path = output_dir / f"{input_path.stem}_BothFeet.csv"
        unified.to_csv(out_path, index=False)
        print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
