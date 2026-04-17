"""
Generate realistic 400m hurdles mock sensor data.

Fixed from original:
  1. True strictly-alternating foot contacts — left and right feet NEVER
     overlap on the ground, matching real sprint/hurdle biomechanics.
  2. Realistic hurdle placement — last hurdle at ~51.5 s for a 58 s race,
     so H10->Fin is ~11 % of total time (not 21 %).
  3. Gradual per-segment fatigue modelled in hurdle spacing.
"""

import csv
import math
import random

random.seed(42)

SAMPLE_RATE_HZ = 100
MS_PER_SAMPLE = 10

# Stride parameters (ms)
NORMAL_GCT_MS = (120, 160)      # ground contact time
STEP_FLIGHT_MS = (50, 90)       # gap from one foot lifting to OTHER foot landing
HURDLE_FLIGHT_MS = (320, 420)   # lead-leg clearance gap
FORCE_PEAK = (2000, 3500)

RACE_DURATION_MS = 58000
NUM_HURDLES = 10

# H10 at ~51.5s leaves ~6.5s (11.2%) for H10->Fin — no spike
HURDLE_TIMES_MS = [
    5600,   # H1
    10180,  # H2
    14860,  # H3
    19640,  # H4
    24570,  # H5
    29650,  # H6
    34880,  # H7
    40260,  # H8
    45790,  # H9
    51470,  # H10
]


def generate_alternating_contacts():
    """
    Strictly alternating (foot, ic_ms, to_ms) tuples.
    After each lift-off there is a flight gap before the OTHER foot lands.
    Guaranteed: no two entries overlap in time.
    """
    contacts = []
    t = 0
    foot = "left"
    hurdle_queue = list(HURDLE_TIMES_MS)

    while t < RACE_DURATION_MS:
        gct = random.randint(*NORMAL_GCT_MS)
        to_time = t + gct
        contacts.append((foot, t, to_time))

        if hurdle_queue and to_time >= hurdle_queue[0] - 300:
            flight_gap = random.randint(*HURDLE_FLIGHT_MS)
            hurdle_queue.pop(0)
        else:
            flight_gap = random.randint(*STEP_FLIGHT_MS)

        t = to_time + flight_gap
        foot = "right" if foot == "left" else "left"

    return contacts


def force_curve(t_ms, start_ms, end_ms):
    duration = end_ms - start_ms
    if duration <= 0:
        return 0
    mid = (start_ms + end_ms) / 2
    sigma = duration / 4
    peak = random.randint(*FORCE_PEAK)
    val = peak * math.exp(-((t_ms - mid) ** 2) / (2 * sigma ** 2))
    return max(0, int(val))


def build_force_arrays(contacts, duration_ms):
    n = duration_ms // MS_PER_SAMPLE + 1
    left_f = [0] * n
    right_f = [0] * n
    for foot, start, end in contacts:
        arr = left_f if foot == "left" else right_f
        s_idx = start // MS_PER_SAMPLE
        e_idx = end // MS_PER_SAMPLE
        for i in range(s_idx, min(e_idx + 1, n)):
            t = i * MS_PER_SAMPLE
            arr[i] = force_curve(t, start, end)
    return left_f, right_f


def validate_no_overlap(contacts):
    for i in range(len(contacts) - 1):
        f1, s1, e1 = contacts[i]
        f2, s2, e2 = contacts[i + 1]
        if s2 < e1:
            raise ValueError(f"Overlap: {f1}[{s1}-{e1}] -> {f2}[{s2}-{e2}]")
    print("OK No simultaneous ground contact")


def print_splits():
    checkpoints = [0] + HURDLE_TIMES_MS + [RACE_DURATION_MS]
    labels = ["Start"] + [f"H{i}" for i in range(1, 11)] + ["Fin"]
    print("\nSplit distribution:")
    for i in range(len(checkpoints) - 1):
        seg = checkpoints[i + 1] - checkpoints[i]
        pct = seg / RACE_DURATION_MS * 100
        print(f"  {labels[i]:7s}->{labels[i+1]:<4s}: {seg:5d}ms  {pct:5.1f}%")


def main():
    print("Generating fixed 400m hurdles data...")
    contacts = generate_alternating_contacts()
    validate_no_overlap(contacts)
    left_f, right_f = build_force_arrays(contacts, RACE_DURATION_MS)
    n = min(len(left_f), len(right_f))

    with open("hurdle_400m.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Force_Foot1", "Force_Foot2"])
        for i in range(n):
            writer.writerow([i * MS_PER_SAMPLE, left_f[i], right_f[i]])

    lc = sum(1 for foot, _, _ in contacts if foot == "left")
    rc = sum(1 for foot, _, _ in contacts if foot == "right")
    print(f"Written {n} rows ({n * MS_PER_SAMPLE / 1000:.1f}s) to hurdle_400m.csv")
    print(f"Left contacts: {lc}, Right contacts: {rc}")
    print_splits()


if __name__ == "__main__":
    main()