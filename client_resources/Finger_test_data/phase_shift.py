import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple


def find_contact_blocks(force: np.ndarray) -> List[Tuple[int, int]]:
    """
    Find contiguous non-zero contact blocks.
    Returns list of (start_idx, end_idx) where end_idx is exclusive.
    """
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
    """
    Add integer noise in [-noise_max, +noise_max] to non-zero samples only.
    """
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
    seed: int = 12345
) -> pd.DataFrame:
    """
    Create two-foot mock data from finger trials.

    Foot2 generation rules:
      1) Detect Foot1 contact blocks (contiguous Force > 0).
      2) For each block [start, end):
           place a copy into Foot2 starting at (end + buffer_samples)
           i.e. shift = (end - start) + buffer_samples
      3) If that placed Foot2 block would overlap the next Foot1 contact,
           truncate Foot2 so it ends at (next_start - buffer_samples).

    Noise:
      - Adds slight noise to any non-zero samples (both feet), clipped to [0, adc_max].
    """
    rng = np.random.default_rng(seed)

    # Load/clean
    df = foot1_data[[time_col, force_col]].copy()
    df[force_col] = pd.to_numeric(df[force_col], errors="coerce").fillna(0).astype(int)
    df[force_col] = np.clip(df[force_col], 0, adc_max)

    time = df[time_col].to_numpy()
    f1_raw = df[force_col].to_numpy()

    # Noise on Foot1 (non-zero only)
    f1 = add_noise_nonzero(f1_raw, noise_max, adc_max, rng)

    blocks = find_contact_blocks(f1)
    f2 = np.zeros_like(f1)

    if not blocks:
        return pd.DataFrame({
            "Time": time,
            "Force_Foot1": f1,
            "Force_Foot2": f2
        })

    n = len(f1)

    for i, (start, end) in enumerate(blocks):
        duration = end - start
        if duration <= 0:
            continue

        # Shift so Foot2 starts after Foot1 ends + buffer
        shift = duration + buffer_samples
        new_start = start + shift           # equals end + buffer_samples
        new_end = end + shift               # equals end + duration + buffer_samples

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

        f2[new_start:new_end] = np.maximum(
            f2[new_start:new_end],
            f1[start:src_end]
        )

    # Noise on Foot2 (non-zero only)
    f2 = add_noise_nonzero(f2, noise_max, adc_max, rng)

    return pd.DataFrame({
        "Time": time,
        "Force_Foot1": f1,
        "Force_Foot2": f2
    })


def main():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    input_dir = PROJECT_ROOT / "client_resources" / "Finger_test_data"
    output_dir = PROJECT_ROOT / "client_resources" / "Finger_test_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Tunables
    buffer_samples = 3
    noise_max = 12
    adc_max = 4095
    seed = 12345

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Reading from:  {input_dir}")
    print(f"Writing to:    {output_dir}")
    print(f"buffer_samples={buffer_samples}, noise_max={noise_max}, adc_max={adc_max}, seed={seed}")

    csvs = sorted(input_dir.glob("*.csv"))
    if not csvs:
        print(f"No CSV files found in: {input_dir}")
        return

    for input_path in csvs:
        print(f"Processing: {input_path.name}")
        df = pd.read_csv(input_path)

        unified = make_two_feet_phase_shifted_adaptive(
            df,
            time_col="Timestamp",
            force_col="Force",
            buffer_samples=buffer_samples,
            noise_max=noise_max,
            adc_max=adc_max,
            seed=seed
        )

        out_path = output_dir / f"{input_path.stem}_BothFeet.csv"
        unified.to_csv(out_path, index=False)
        print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
