# Time Prediction Model Planning

## Data Analysis - Athlete First Website

### Available Data from athletefirst.org

Race Performance Data (100h, 400h):
- Touchdown times at each hurdle (H1-H10 for 110h, H1-H10 for 400h)
- Split times between sections (H1-H4, H4-H7, H7-H10)
- Interval times between consecutive hurdles
- Stride patterns (number of steps between hurdles)
- Velocity at each hurdle
- Race metadata: athlete info, competition, wind conditions, reaction time

Data Structure Example (from 110h PDF):

Athlete: Zhoya, Sasha (FRA)
Event: Men's 110m Hurdles
Hurdle Times: H1=2.32s, H2=3.36s, H3=4.32s ... H10=11.16s
Official Time: 12.72s
Intervals: 1.04s, 0.96s, 0.96s, 0.96s, 0.96s, 1.00s, 1.00s, 0.96s, 1.00s
Velocity: 5.91, 8.79, 9.52, 9.52, 9.52, 9.52, 9.14, 9.14, 9.52, 9.14 m/s


Key Insights/Data Gaps
- Comprehensive elite-level race data (world records, Olympic performances)
- Shows relationship between splits and final times
- Demonstrates pacing patterns and fatigue curves
- Can be used as benchmark/validation data
- athletefirst.org only has competition results


Data Schema:
Race Record:
├─ athlete_name: str
├─ country: str
├─ birth_year: int
├─ event: str (110h, 100h, 400h)
├─ competition: str
├─ date: date
├─ hurdle_times: [H1, H2, ..., H10]
├─ intervals: [interval between each hurdle]
├─ velocities: [velocity at each hurdle]
├─ splits: {H1-H4, H4-H7, H7-H10}
├─ official_time: float
├─ wind: float
├─ reaction_time: float
└─ lane: int



## Model Input/Output Design

### Approach A: Using Available Data (Race-to-Race Prediction)

Since athletefirst.org only has race data, we can build a model that predicts race times based on **previous race performance**.

Input Features (from previous races):
1. Recent Race Times:
   - Last race official time
   - Best time this season
   - Personal record (PR)
   
2. Split Performance:
   - H1-H4 split time
   - H4-H7 split time
   - H7-H10 split time
   - First hurdle time (H1)
   
3. Performance Metrics:
   - Average velocity across race
   - Hurdle interval consistency (std deviation of intervals)
   - Deceleration in final section (H7-H10 velocity drop)
   
4. Race Context:
   - Wind conditions
   - Days since last race
   - Competition level (local, national, international)

Output:
- Predicted race time for next competition
- Confidence interval [lower_bound, upper_bound]
- Predicted splits (H1-H4, H4-H7, H7-H10)


### Approach B

**What Would Be Better**:

To truly predict race times from **practice performance** (the original ticket goal), we would need:

**Additional Practice Metrics to Collect**:
1. **Short Sprint Times**:
2. **Hurdle Drill Times**:
3. **Partial Race Simulations**:




## Implementation Plan

### Phase 1: Data Collection

Tasks:
- Scrape athletefirst.org PDFs (110h, 100h, 400h, 60h)
- Parse tables into structured CSV format
- Clean data: remove outliers, handle missing values
- EDA: analyze splits, velocities, pacing patterns

### Phase 2: Feature Engineering

Tasks:
- Derived features: velocity metrics, deceleration rate, split consistency
- Temporal features: season progression, recent form, days between races
- Performance benchmarks: distance from PR, percentile rankings

### Phase 3: Model Development

1. Linear Regression (baseline): last race time → next race time
2. Multiple Regression: add splits, velocities
4. Event-specific models for 60h, 100h/110h, 400h


### Phase 4: Deployment

**Infrastructure**: AWS Lambda + API Gateway (serverless, cost effective)

