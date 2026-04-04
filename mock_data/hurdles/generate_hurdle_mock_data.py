"""
Generate realistic 400m hurdles mock sensor data.

Realistic parameters:
- Sample rate: 100Hz (10ms per sample)
- Race duration: ~58 seconds
- Normal stride GCT: 120-160ms, flight: 90-130ms
- Hurdle clearance flight: 350-480ms
- 10 hurdles evenly spaced across the race
- Left/right foot alternate, offset by half a stride cycle
"""

import csv
import random

random.seed(42)

SAMPLE_RATE_HZ = 100
MS_PER_SAMPLE = 10

# Stride parameters (in ms)
NORMAL_GCT_MS = (120, 160)  # ground contact time range
NORMAL_FLIGHT_MS = (90, 130)  # normal flight time range
HURDLE_FLIGHT_MS = (350, 480)  # hurdle clearance flight time range
FORCE_PEAK = (2000, 4000)  # peak force during ground contact

# Race structure
RACE_DURATION_MS = 58000
NUM_HURDLES = 10

# Hurdle positions — spaced roughly evenly, first at ~3.5s, last at ~50s
HURDLE_TIMES_MS = [3500, 8200, 12900, 17600, 22300, 27000, 31700, 36400, 41100, 45800]

print("Script starting...")


def in_hurdle_clearance(t_ms: int) -> bool:
    for ht in HURDLE_TIMES_MS:
        if ht - 50 <= t_ms <= ht + 500:
            return True
    return False


def generate_foot_contacts(offset_ms: int = 0) -> list[tuple[int, int]]:
    """
    Generate (start_ms, end_ms) ground contact intervals for one foot.
    offset_ms staggers left vs right foot.
    """
    contacts = []
    t = offset_ms

    while t < RACE_DURATION_MS:
        # Check if we're approaching a hurdle clearance
        near_hurdle = any(abs(t - ht) < 300 for ht in HURDLE_TIMES_MS)

        gct = random.randint(*NORMAL_GCT_MS)
        if near_hurdle:
            flight = random.randint(*HURDLE_FLIGHT_MS)
        else:
            flight = random.randint(*NORMAL_FLIGHT_MS)

        contact_start = t
        contact_end = t + gct
        contacts.append((contact_start, contact_end))

        t = contact_end + flight

    return contacts


def force_curve(t_ms: int, start_ms: int, end_ms: int) -> int:
    """Bell-curve shaped force during ground contact."""
    duration = end_ms - start_ms
    if duration <= 0:
        return 0
    mid = (start_ms + end_ms) / 2
    sigma = duration / 4
    peak = random.randint(*FORCE_PEAK)
    import math

    val = peak * math.exp(-((t_ms - mid) ** 2) / (2 * sigma**2))
    return max(0, int(val))


def build_force_array(contacts: list[tuple[int, int]], duration_ms: int) -> list[int]:
    """Build force array at 10ms resolution."""
    n_samples = duration_ms // MS_PER_SAMPLE + 1
    forces = [0] * n_samples

    for start, end in contacts:
        s_idx = start // MS_PER_SAMPLE
        e_idx = end // MS_PER_SAMPLE
        for i in range(s_idx, min(e_idx + 1, n_samples)):
            t = i * MS_PER_SAMPLE
            forces[i] = force_curve(t, start, end)

    return forces


def main():
    left_contacts = generate_foot_contacts(offset_ms=0)
    right_contacts = generate_foot_contacts(offset_ms=200)  # offset by ~half stride

    left_forces = build_force_array(left_contacts, RACE_DURATION_MS)
    right_forces = build_force_array(right_contacts, RACE_DURATION_MS)

    n = min(len(left_forces), len(right_forces))

    with open("hurdle_400m_mock.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Force_Foot1", "Force_Foot2"])
        for i in range(n):
            writer.writerow([i * MS_PER_SAMPLE, left_forces[i], right_forces[i]])

    print(f"Generated {n} rows (~{n * MS_PER_SAMPLE / 1000:.1f}s of data)")
    print(f"Left foot contacts: {len(left_contacts)}")
    print(f"Right foot contacts: {len(right_contacts)}")


if __name__ == "__main__":
    main()
