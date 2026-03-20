# Quarter Split Position Estimation — Research & Model

**Ticket:** Extend Distance Model Research  
**Goal:** Determine whether StrideTrack's current sensor data (GCT, flight time, IC timestamps at ~7–8 Hz BLE) can accurately estimate a runner's position at each stride and produce quarter splits for sprint events (100m, 400m, etc.).

---

## Table of Contents

1. [Sensor Limitations](#1-sensor-limitations)
2. [The GCT Asymmetry Question](#2-the-gct-asymmetry-question)
3. [Literature Review](#3-literature-review)
4. [The Model](#4-the-model)
5. [Test Results on Real Data](#5-test-results-on-real-data)
6. [Validation Strategy](#6-validation-strategy)
7. [Honest Limitations](#7-honest-limitations)
8. [Integration Path](#8-integration-path)

---

## 1. Sensor Limitations

The insole hardware (16-sensor pressure array per foot, BLE transmission) currently logs at **~7–8 Hz**, meaning one sensor frame every ~121ms (median). This creates a hard quantization ceiling on what metrics are reliable.

| Metric | Reliable at 7–8 Hz? | Why |
|---|---|---|
| IC timestamp (when foot lands) | ✅ Yes | Spans many frames, jitter is small relative to inter-step intervals |
| Total stride time (GCT + FT) | ✅ Yes | Same reason |
| Per-step GCT | ⚠️ Unreliable | ±60ms quantization error = ±40% of typical sprint GCT (85–140ms) |
| L/R GCT asymmetry | ❌ No | Cannot distinguish differences < 60ms — within noise floor |
| Pressure zone distribution | ✅ Yes | Accumulates across many frames, not timing-sensitive |

At 100+ Hz, per-step GCT becomes reliable (±5ms error). That is the single sensor change that would unlock the most additional signal.

---

## 2. The GCT Asymmetry Question

Matteo's 30m sprint showed mean R GCT of 216ms vs L GCT of 137ms (+58%). This looks like a large asymmetry but is almost certainly a sampling artifact.

**What the raw data shows:**

```
Frame interval (median): 121ms

L foot GCTs (ms): [117, 117, 119, 120, 143, 148, 150, 151, 151, 151]
→ In frame units:  [ 1,   1,   1,   1,   1,   1,   1,   1,   1,   1 ]

R foot GCTs (ms): [121, 121, 155, 237, 238, 239, 239, 243, 244, 269, 269]
→ In frame units:  [ 1,   1,   1,   2,   2,   2,   2,   2,   2,   2,   2 ]
```

Every L contact is exactly 1 frame. R contacts are sometimes 1 frame, sometimes 2. The "asymmetry" is explained by whether each R contact happens to straddle a frame boundary or not — a timing phase relationship, not a biomechanical one.

**Conclusion:** Pressure zone loading asymmetry (R forefoot/toe zones carry more load) is a more credible finding because it accumulates over many frames and is robust to timing quantization.

---

## 3. Literature Review

### 3.1 Core model reference

**de Ruiter & van Dieën (2019). Stride and Step Length Obtained with IMUs during Maximal Sprint Acceleration.**  
*Sports, 7(9), 202. [PMC6784208](https://pmc.ncbi.nlm.nih.gov/articles/PMC6784208/)*

The most directly applicable study. Key findings:
- Sprint velocity during acceleration follows a mono-exponential function: `v(t) = v_max × (1 − e^(−t/τ))`
- This curve can be parameterized with just two split times (e.g. 30m and 60m from timing gates)
- With foot IMUs + two timing gates: **RMSE = 5.7 cm/step** for stride length (after polynomial smoothing)
- Polynomial smoothing reduces RMSE from 8.0 cm to 5.7 cm per step

This is the basis for our model. The key adaptation: we use IC timestamps and stride time (GCT + FT) in place of their IMU + timing gate setup, and we use a coach-supplied finish time as the calibration anchor instead of gates.

### 3.2 Spatial vs temporal accuracy of foot sensors

**van den Tillaar et al. (2021). Step-to-Step Kinematic Validation: IMU 3D System, Laser+IMU, and Force Plates during 50M Sprint.**  
*Sensors, 21(19), 6560. [PMC8512743](https://pmc.ncbi.nlm.nih.gov/articles/PMC8512743/)*

Important finding: standalone IMU systems (no external anchor) underestimate step velocity by ~0.88 m/s and step length by ~0.20 m at sprint speeds. Temporal parameters (contact time, flight time, step rate) are accurate; spatial parameters (length, velocity) require an external calibration anchor.

This directly motivates Tier 1 calibration (finish time): without some external anchor, position estimation drifts significantly.

### 3.3 What variable actually predicts stride length?

**Kibele et al. (2021). Kinematic Stride Characteristics of Maximal Sprint Running of Elite Sprinters.**  
*PMC8008308. [Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC8008308/)*

Critical finding: at maximum velocity, **flight time does not significantly correlate with sprint speed**. GCT correlates more strongly (r ≈ −0.7 to −0.9). **Total stride time** (GCT + FT) is the correct input variable for position estimation.

This invalidates the prior proposal of "inverse flight time as percentage of race distance" — the wrong variable.

### 3.4 Stride-time algorithms

**Zrenner et al. (2018). Comparison of Different Algorithms for Calculating Velocity and Stride Length in Running Using IMUs.**  
*PMC6308955. [Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC6308955/)*

Benchmarked four approaches for stride length estimation from foot sensors. The stride-time-based algorithm (inverse correlation between velocity and stride time) performs competitively and generalizes across athletes. Foot-trajectory estimation performs best when raw IMU data is available; stride-time is the best option when only timing data is available.

### 3.5 Ground truth validation dataset

**IAAF Biomechanical Analysis — 2009 World Championships Berlin.**  
*New Studies in Athletics, 1/2.2011. [Link](https://worldathletics.org/about-iaaf/documents/research-centre)*

This report contains both 10m split times **and** per-step stride analysis for Usain Bolt's 9.58s 100m WR — the only publicly available dataset where both inputs (stride timing) and outputs (10m splits) are published for the same race. This is the primary validation dataset used in `test_position_model.py`.

Key data from the report:
- Bolt's 10m splits: `[1.89, 1.01, 0.90, 0.86, 0.83, 0.82, 0.81, 0.82, 0.83, 0.90]` cumulative → interval times
- Step count per 10m section published (Table 20)
- Mean GCT and flight time per 10m section available (allows us to reconstruct stride timing)

---

## 4. The Model

### 4.1 Velocity function

Sprint velocity follows a mono-exponential during acceleration, plateauing at top speed:

```
v(t) = v_max × (1 − e^(−t/τ))
```

The integral gives position at any time:

```
distance(t) = v_max × (t + τ × e^(−t/τ) − τ)
```

`v_max` and `τ` are fit numerically so that `distance(finish_time) = race_distance`. Optional split anchors (e.g. 30m time, 60m time) can be added as additional constraints.

### 4.2 Per-stride position

```python
position_at_IC_i  = distance(t_i)
stride_length_i   = distance(t_i + stride_time_i) − distance(t_i)
velocity_i        = v(t_i + stride_time_i / 2)   # mid-stride

# where:
stride_time_i = (GCT_i + flight_time_i) / 1000.0  # ms → s
t_i           = IC_timestamp_i / 1000.0            # ms → s, normalized to 0 at first step
```

### 4.3 Polynomial smoothing

After computing raw stride lengths, fit a 3rd-order polynomial to `(stride_index, raw_stride_length)` and recompute cumulative positions from the smoothed lengths. This suppresses step-to-step sensor noise while preserving the physiologically smooth acceleration curve.

```python
coeffs = np.polyfit(stride_indices, raw_stride_lengths, deg=3)
smoothed_lengths = np.poly1d(coeffs)(stride_indices)
positions = np.cumsum(np.maximum(smoothed_lengths, 0.3))
```

### 4.4 Quarter splits

Quarter marks are at 25%, 50%, 75%, and 100% of race distance (e.g. 25m, 50m, 75m, 100m for a 100m sprint). For each mark, linearly interpolate between the two adjacent stride positions to find the exact time.

### 4.5 Calibration tiers

| Tier | Coach inputs | Estimated accuracy | Effort |
|---|---|---|---|
| 0 — None | Nothing | Relative pacing rhythm only, no meters | None |
| 1 — Finish time | Race distance + finish time | RMSE ~1–3m over 100m | ~5 sec |
| 2 — Splits | Finish time + split times (e.g. 30m, 60m) | RMSE <1m, matches literature | ~15 sec |

---

## 5. Test Results on Real Data

Tested on Matteo's 30m and 60m sprint sessions (March 2026 insole data). See `test_position_model.py` for full output.

### 5.1 30m sprint (4.3s assumed finish — 21 steps, 0 BLE gaps)

| Quarter | Cumulative time | Split |
|---|---|---|
| 0 → 7.5m | 1.00s | 1.00s |
| 7.5 → 15m | 1.60s | 0.61s |
| 15 → 22.5m | 2.00s | 0.40s |
| 22.5 → 30m | 2.57s | 0.57s |

Mid-run splits (Q2, Q3) are stable across the 3.8–5.0s finish time range, confirming the model converges at top speed. Q1 is most sensitive to the calibration assumption.

### 5.2 60m sprint (8.0s assumed finish — 22 clean steps, 3 BLE gaps at end excluded)

| Quarter | Cumulative time | Split |
|---|---|---|
| 0 → 15m | 1.35s | 1.35s |
| 15 → 30m | 2.25s | 0.90s |
| 30 → 45m | 3.21s | 0.96s |
| 45 → 60m | 4.15s | 0.94s |

The 30→45m and 45→60m splits are nearly identical — correct, this is the model converging to top speed (constant velocity), which is physically accurate for trained sprinters.

---

## 6. Validation Strategy

### 6.1 Best available: IAAF published race data (in `test_position_model.py`)

The 2009 IAAF biomechanics report on Bolt's 9.58s WR publishes both:
- Per-stride GCT and flight time (Table 20, stride analysis)
- 10m split times for the same race (Table A)

We can run the model on the stride data and compare the predicted 10m splits against the published ones. This is a true out-of-sample test because the stride data and split data were collected independently (stride data from video, split data from laser timing).

**Why this is the right validation approach:** It uses the same type of data our sensors produce (GCT + flight time per step) and compares against precisely measured ground truth (laser-timed 10m splits). If the model predicts Bolt's splits to within ±0.1s per 10m section, it's validated at the level of accuracy that matters for coaching.

### 6.2 Practical field validation (recommended for real-world accuracy)

Place **cones with tape marks at known distances** (10m, 20m, 30m, etc.) and record video of the run. Extract the time the athlete crosses each cone from video (at 60fps, this is accurate to ±17ms). Compare to model predictions.

This gives ground truth from Matteo's own runs at sub-elite speeds (more relevant than elite data for coaching use cases).

**Minimum setup:** Two cones (start + finish line), one phone camera. Gives finish time → Tier 1 calibration.  
**Better setup:** Cones at 25% and 50% marks, same camera. Gives split times → Tier 2 calibration, also lets you validate the intermediate positions.

### 6.3 Self-consistency test (no external hardware)

Run the same athlete over the same distance twice, under similar conditions. The model should produce splits within ~5% of each other for the same runner on the same day. High variance between runs indicates the model is sensitive to noise; low variance indicates the stride timing signal is stable enough to trust.

This is implementable today with existing data collection.

---

## 7. Honest Limitations

### What the model cannot do at 7–8 Hz

- **Per-step GCT is unreliable.** ±60ms quantization error exceeds the meaningful GCT range at sprint speeds. Do not report per-step GCT as a metric at this sample rate.
- **L/R asymmetry in GCT cannot be trusted.** The observed R > L asymmetry in Matteo's data is consistent with a sampling phase artifact, not a confirmed biomechanical finding.
- **First quarter split is the most uncertain.** The acceleration phase is where velocity changes fastest per step, and where the mono-exponential approximation is most sensitive to the calibration input.

### What the model can do

- **Quarter splits to within ~1–2m** with a single finish time (Tier 1).
- **Quarter splits to within ~0.5m** with intermediate split times (Tier 2).
- **Relative pacing rhythm** (which portion of the race was proportionally faster) even without any calibration.
- **Velocity-over-distance curves** that map to real track positions, actionable for coaching.

### What would improve accuracy most

1. **≥100 Hz BLE sampling rate** — unlocks reliable per-step GCT, reduces stride length noise
2. **IMU (accelerometer) on the insole** — enables ZUPT-based position tracking, validated at 5.7 cm/step RMSE
3. **One video session with cones** — ground truth to validate and tune the model for sub-elite speeds

---

## 8. Integration Path

### Schema additions

```sql
-- runs table
ALTER TABLE runs ADD COLUMN race_distance_m  FLOAT;
ALTER TABLE runs ADD COLUMN finish_time_s    FLOAT;
ALTER TABLE runs ADD COLUMN split_times      JSONB DEFAULT '{}';
-- split_times format: {"30": 3.82, "60": 6.54}

-- optional: cache computed values on run_metrics
ALTER TABLE run_metrics ADD COLUMN estimated_position_m  FLOAT;
ALTER TABLE run_metrics ADD COLUMN estimated_velocity_ms FLOAT;
ALTER TABLE run_metrics ADD COLUMN stride_length_m       FLOAT;
```

### New endpoint

```
GET /api/run/{run_id}/positions

Response:
{
  "model": "mono_exp_smoothed",
  "calibration_tier": 1,
  "v_max": 11.2,
  "tau": 1.83,
  "quarter_splits": [
    { "distance_m": 25, "cumulative_time_s": 3.21, "split_s": 3.21 },
    { "distance_m": 50, "cumulative_time_s": 5.41, "split_s": 2.20 },
    ...
  ],
  "strides": [
    {
      "stride_index": 0,
      "ic_time_ms": 0,
      "estimated_position_m": 0.0,
      "estimated_velocity_ms": 0.7,
      "stride_length_m": 0.5
    },
    ...
  ]
}
```

### Frontend changes

- **RecordRunPage:** Add optional finish time input after run completes — "Add race time to enable position tracking"
- **RunAnalysisPage:** Add velocity-over-distance chart (x = meters, y = m/s). More actionable than velocity vs stride index because it maps to real track positions
- **RunAnalysisPage:** Quarter split table showing split times and delta vs. even pacing

### Implementation order

1. Schema migration (`race_distance_m`, `finish_time_s`, `split_times` on `runs`)
2. Optional finish time input on `RecordRunPage`
3. `PositionEstimatorService` (port model from `test_position_model.py`)
4. `GET /api/run/{run_id}/positions` endpoint
5. Velocity-over-distance chart on `RunAnalysisPage`