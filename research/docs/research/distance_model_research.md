# Sprint Position & Quarter Split Estimation

**Project:** StrideTrack — GenerateNU / NExT Consulting  
**Ticket:** Extend Distance Model Research  
**Status:** Research complete, model trained and validated

---

## What this is

StrideTrack's insole sensors capture when feet hit the ground and for how long — but they have no GPS, no timing gates, and no way to directly measure where a runner is on the track. This research answers the question: **given only a coach's stopwatch time and the sensor's IC timestamps, how accurately can we estimate a runner's position at each stride and produce quarter splits?**

---

## What goes in, what comes out

**Inputs:**

| Source | Data | Required? |
|---|---|---|
| Sensor | IC timestamp per stride (ms) | Always |
| Coach | Race distance (m) | Yes |
| Coach | Finish time (s) | Yes — unlocks real metres |
| Coach | Sex of athlete | Yes — improves accuracy |
| Coach | Intermediate split times | Optional (improves accuracy further) |

**Outputs:**

- Position in metres at each stride's initial ground contact
- Velocity in m/s at each stride
- Quarter split times — how long the runner spent in each 25% of the race

**What the sensor is actually doing:** providing the timestamps at which to evaluate the position model. The GCT and flight time values are used for display metrics (stride length, pacing rhythm) but do not feed into position estimates directly.

---

## The model

Sprint velocity during acceleration follows a mono-exponential function. This has been validated across decades of sprint biomechanics research:

```
v(t) = v_max × (1 − e^(−t / τ))
```

Integrating gives position at any time:

```
distance(t) = v_max × (t + τ × e^(−t/τ) − τ)
```

**v_max** is the runner's top speed. **τ** (tau) is the acceleration time constant — how quickly they reach top speed. Lower τ means faster acceleration.

### How the two parameters are solved

These parameters are not measured. They are solved from the calibration inputs:

```
distance(finish_time) = race_distance        # always available
distance(t_split)     = split_distance       # optional, improves accuracy
```

With only a finish time, there are many valid (v_max, τ) pairs — the system is under-constrained. With one or two intermediate splits, the system is over-determined and the fit is nearly exact.

### Position estimation

Once v_max and τ are known, position at each stride is a direct read from the calibrated integral:

```python
position_m = distance(ic_time_ms / 1000.0)
```

This is not accumulated from stride lengths. It is evaluated directly from the formula, so there is no drift or compounding error over the race.

### Quarter splits

Quarter split times are found by linearly interpolating between adjacent (time, position) pairs to find the exact timestamp when the runner crossed each distance mark.

---

## The trained τ model

The key insight from testing: with only a finish time, the optimizer picks a (v_max, τ) pair that satisfies the total distance but may not match the actual shape of the race. This produces large errors at intermediate splits.

**The fix:** learn the typical τ for a given finish time and sex from historical data. Instead of guessing τ, predict it.

### How training works

1. Collect published sprint data where both 10m splits and finish times are known
2. For each athlete, fit their true τ by minimising split prediction error
3. Fit a linear regression: `τ = slope × finish_time + intercept` separately for men and women
4. At inference: predict τ from finish time and sex, then solve v_max analytically

### Trained model coefficients

```
Male:   τ = 0.218 × finish_time_s − 1.227
Female: τ = 0.569 × finish_time_s − 5.492
```

These are stored in `tau_model.json` and loaded by the production model.

### Why sex matters but height/weight don't

Sex has a meaningful partial correlation with τ (r = +0.326) after controlling for finish time — women's τ genuinely scales differently with performance level. Height and weight show high raw correlations (~0.45 partial r) but are almost entirely explained by the sex variable already. Adding them to the model on 40 athletes made performance worse due to overfitting. The finish time + sex model is the right call.

---

## Training data

| Source | Athletes | Sex | Finish time range | Level |
|---|---|---|---|---|
| 2009 IAAF Berlin WC (Graubner & Nixdorf, 2011) | 5 | M | 9.58–9.93s | Elite |
| 2017 IAAF London WC (Bissas et al., 2018) | 8 | M | 9.92–10.27s | Elite |
| 2017 IAAF London WC (Bissas et al., 2018) | 5 | F | 10.85–11.02s | Elite |
| 2009 IAAF Berlin WC (Graubner & Nixdorf, 2011) | 4 | F | 10.73–10.98s | Elite |
| 2012 HS Invitational (Jakalski / Freelap, 2013) | 2 | M | 11.21–11.63s | High school |
| Synthesised (Morin 2012, Samozino 2016) | 16 | M+F | 11.0–16.0s | Sub-elite → recreational |

**Total: 40 athletes.** The elite data is real measured data. The sub-elite and recreational data points are synthesised from published biomechanics parameters for non-specialist populations and will be replaced with real athlete data as Matteo's users run calibrated races.

---

## Accuracy results

All results use leave-one-out cross-validation (LOO-CV), which is appropriate for a 40-athlete dataset — standard train/test splits are too variable to trust at this scale.

### By model type (quarter split MAE, all 40 athletes)

| Model | MAE | Max error | Within 0.20s |
|---|---|---|---|
| Baseline — τ = 1.5 constant | 0.304s | 0.924s | 15/40 |
| Finish time only | 0.201s | 0.617s | 19/40 |
| Finish time + sex ✓ | **0.189s** | **0.619s** | **24/40** |
| Finish time + sex + height + weight | 0.191s | 0.615s | 24/40 |

### What the error means in metres

At the 50m mark, runners are near top speed. Time error × velocity = distance error.

| Athlete | MAE (time) | → Distance error |
|---|---|---|
| Elite man (~9.7s) | ~0.12s | ~1.4m |
| Sub-elite man (~11s) | ~0.14s | ~1.4m |
| Collegiate man (~12–13s) | ~0.20s | ~1.8m |
| Recreational man (~14s) | ~0.18s | ~1.5m |
| Elite woman (~11s) | ~0.17s | ~1.7m |
| Collegiate woman (~13s) | ~0.23s | ~2.0m |
| Recreational woman (~15s) | ~0.42s | ~3.3m |

**In plain terms:** for most athletes, the model estimates which quarter of the race they were in to within about 1.5–2 metres. For coaches using this to understand pacing patterns — whether an athlete went out too fast, where they faded — this is actionable. It is not precise enough to place cones or make metre-level calls.

### External validation — Bolt's 9.58s WR (Tier 2)

Using the 2009 IAAF Berlin biomechanics report (stride data + 10m laser splits from the same race), the model predicts all nine 10m cumulative splits with RMSE = 11.6ms and max error 19.7ms. This is the strongest validation result because it uses independently measured ground truth, not synthesised data.

---

## Known limitations

**The model cannot handle deceleration.** The mono-exponential only rises to a plateau. Runners who significantly slow in the final 20m (common in women's 100m and recreational athletes) will have their Q4 split underestimated. Tori Bowie's final 20m error reached 0.41s for this reason.

**At 7–8 Hz BLE, per-step GCT is not reliable.** The quantisation error is ±60ms — larger than the meaningful sprint GCT range of 85–140ms. The model uses IC timestamps (reliable) and total stride time (useful for display), not per-step GCT as a position predictor.

**The recreational data is synthesised.** The 11.5–16s range uses constructed split profiles based on published population parameters. Every real athlete race that gets added to training will improve accuracy in that range.

---

## Accuracy tiers

| Tier | Coach provides | Accuracy | Notes |
|---|---|---|---|
| 0 — None | Nothing | Relative rhythm only | No real metres |
| 1 — Finish time | Race distance + time | ~1.5–2m distance error | Default |
| 2 — Splits | Finish + 1–2 split times | ~0.1–0.5m distance error | Dramatically better |

---

## Application integration

### Overview

The model needs three things from the app: a database schema change, a backend service and endpoint, and two small frontend additions. None of this touches the existing run recording flow.

### Database

Add three columns to the `runs` table and one optional column to `athletes`:

```sql
-- runs table
ALTER TABLE runs ADD COLUMN race_distance_m  FLOAT;
ALTER TABLE runs ADD COLUMN finish_time_s    FLOAT;
ALTER TABLE runs ADD COLUMN split_times      JSONB DEFAULT '{}';
-- split_times format: {"30": 3.82, "60": 6.54}
-- keys are distance in metres as strings, values are seconds from motion start

-- athletes table (already has sex if stored — verify)
-- sex is used by the model; if not already stored, add:
ALTER TABLE athletes ADD COLUMN sex CHAR(1); -- 'M' or 'F'
```

`race_distance_m` and `finish_time_s` are nullable. The model degrades gracefully when they are absent — it returns relative pacing rhythm without real metre values.

### Backend service

Create `services/position_estimator.py`. The logic maps directly from `sprint_position_model.py` in the research folder:

```python
from sprint_position_model import run_model, load_tau_model

_tau_model = load_tau_model()  # load once at startup

class PositionEstimatorService:
    def estimate(self, run: Run, metrics: list[RunMetric]) -> ModelResult | None:
        if not run.finish_time_s or not run.race_distance_m:
            return None  # no calibration — skip

        ic_timestamps = [m.ic_time_ms for m in sorted(metrics, key=lambda m: m.ic_time_ms)]
        sex = run.athlete.sex or "M"  # fallback if not stored

        return run_model(
            finish_time_s=run.finish_time_s,
            race_distance_m=run.race_distance_m,
            sex=sex,
            ic_timestamps_ms=ic_timestamps,
            tau_model=_tau_model,
            split_times=run.split_times or None,
        )
```

### New endpoint

```
GET /api/run/{run_id}/positions
```

Returns per-stride positions and quarter splits. Computes on demand — no caching needed at this stage.

```python
# routes/run.py
@router.get("/run/{run_id}/positions")
async def get_positions(run_id: str, coach=Depends(get_current_coach)):
    run     = await run_repo.get(run_id, coach_id=coach.id)
    metrics = await metrics_repo.get_by_run(run_id)
    result  = position_service.estimate(run, metrics)

    if result is None:
        raise HTTPException(404, "No calibration data for this run")

    return {
        "v_max":              result.v_max,
        "tau":                result.tau,
        "calibration_tier":   result.calibration_tier,
        "quarter_splits": [
            {
                "distance_m":        s.distance_m,
                "cumulative_time_s": s.cumulative_time_s,
                "split_s":           s.split_s,
            }
            for s in result.quarter_splits
        ],
        "strides": [
            {
                "stride_index":    s.stride_index,
                "ic_time_ms":      s.ic_time_ms,
                "position_m":      s.position_m,
                "velocity_ms":     s.velocity_ms,
                "stride_length_m": s.stride_length_m,
            }
            for s in result.strides
        ],
    }
```

### Frontend — RecordRunPage

After a run completes, show an optional input:

```tsx
// After the existing "Stop" button flow, before navigating away
<div className="mt-4 space-y-2">
  <p className="text-sm text-muted-foreground">
    Add race time to enable split tracking
  </p>
  <div className="flex gap-2">
    <Input
      placeholder="Finish time (e.g. 11.43)"
      value={finishTime}
      onChange={e => setFinishTime(e.target.value)}
    />
    <Select value={raceDistance} onValueChange={setRaceDistance}>
      <SelectItem value="60">60m</SelectItem>
      <SelectItem value="100">100m</SelectItem>
      <SelectItem value="200">200m</SelectItem>
      <SelectItem value="400">400m</SelectItem>
    </Select>
  </div>
</div>
```

This is fully optional. If the coach skips it the run saves normally without split data.

### Frontend — RunAnalysisPage

Add a quarter splits section that calls `GET /api/run/{run_id}/positions`:

```tsx
const { data: positions } = useQuery({
  queryKey: ["positions", runId],
  queryFn: () => api.get(`/run/${runId}/positions`).then(r => r.data),
  enabled: !!runId,
});

// Render quarter splits table
{positions?.quarter_splits.map((split, i) => (
  <div key={i} className="flex justify-between py-2 border-b border-border">
    <span className="text-muted-foreground">
      {i === 0 ? "0" : positions.quarter_splits[i-1].distance_m}m
      → {split.distance_m}m
    </span>
    <span className="font-medium">{split.split_s.toFixed(2)}s</span>
  </div>
))}

// Velocity over distance chart using positions.strides
// x-axis = position_m, y-axis = velocity_ms
// More actionable than velocity vs stride index — maps to real track positions
```

### Implementation order

1. Migration — add `race_distance_m`, `finish_time_s`, `split_times` to `runs`
2. Copy `sprint_position_model.py` and `tau_model.json` into the backend services directory
3. `PositionEstimatorService` wrapping the model
4. `GET /api/run/{run_id}/positions` endpoint
5. Optional finish time input on `RecordRunPage`
6. Quarter splits table + velocity-over-distance chart on `RunAnalysisPage`

Steps 1–4 can be done and tested independently of the frontend changes. The endpoint returns a 404 for uncalibrated runs which the frontend handles gracefully.

---

## Files in this package

| File | Purpose |
|---|---|
| `SPRINT_POSITION_RESEARCH.md` | This document |
| `sprint_position_model.py` | Production model — import this into the backend |
| `tau_model.json` | Trained τ coefficients — ship alongside the model |
| `train_tau_model.py` | Training pipeline — run to retrain with new data |

---

## References

- de Ruiter & van Dieën (2019). Stride and Step Length Obtained with IMUs during Maximal Sprint Acceleration. *Sports* 7(9), 202. [PMC6784208](https://pmc.ncbi.nlm.nih.gov/articles/PMC6784208/)
- Graubner & Nixdorf (2011). Biomechanical Analysis of the Sprint and Hurdles Events at the 2009 IAAF World Championships. *New Studies in Athletics* 1/2.2011. [worldathletics.org](https://worldathletics.org/about-iaaf/documents/research-centre)
- Bissas et al. (2018). Biomechanical Reports for the IAAF World Championships London 2017: 100m Men's and Women's. Leeds Beckett University / World Athletics. [worldathletics.org](https://worldathletics.org/about-iaaf/documents/research-centre)
- Haugen et al. (2019). Profiling elite male 100m sprint performance: The role of maximum velocity and relative acceleration. *Journal of Sport and Health Science*. [PMC8847979](https://pmc.ncbi.nlm.nih.gov/articles/PMC8847979/)
- Morin et al. (2012). Mechanical determinants of 100m sprint running performance. *European Journal of Applied Physiology*. [PubMed 22422028](https://pubmed.ncbi.nlm.nih.gov/22422028/)
- van den Tillaar et al. (2021). Step-to-Step Kinematic Validation: IMU 3D vs Force Plates during 50M Sprint. *Sensors* 21(19). [PMC8512743](https://pmc.ncbi.nlm.nih.gov/articles/PMC8512743/)
- Kibele et al. (2021). Kinematic Stride Characteristics of Maximal Sprint Running. [PMC8008308](https://pmc.ncbi.nlm.nih.gov/articles/PMC8008308/)