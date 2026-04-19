// ============================================================
// Page & Typography Setup
// ============================================================
#set page(
  paper: "a4",
  margin: (x: 2.5cm, y: 3cm),
  numbering: "1",
  number-align: center,
)
#set heading(numbering: "1.")
#set text(size: 10pt)
#set par(justify: true, leading: 0.7em)

#show link: set text(fill: blue, weight: 700)
#show link: underline

#show raw.where(block: true): it => block(
  fill: luma(242),
  inset: (x: 1em, y: 0.8em),
  radius: 4pt,
  width: 100%,
  it,
)

#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(0.5em, weak: true)
  it
  v(0.3em, weak: true)
}

#set table(
  stroke: (_, y) => if y == 0 { (bottom: 0.7pt + black) } else { (bottom: 0.3pt + luma(190)) },
  fill: (_, y) => if y == 0 { luma(225) } else if calc.odd(y) { luma(248) } else { white },
  inset: (x: 0.7em, y: 0.5em),
)
#show table.cell.where(y: 0): strong

// ============================================================
// Title Page
// ============================================================
#align(center + horizon)[
  #text(size: 30pt, weight: "bold")[StrideTrack]
  #v(0.3em)
  #text(size: 18pt)[Technical Documentation]
  #v(0.8em)
  #line(length: 55%, stroke: 0.7pt)
  #v(0.8em)
  #text(size: 11pt)[
    *Technical Leads:* Samuel Baldwin and Ben Marler\
    *Date:* April 2026
  ]
  #v(1.2em)
  #block(width: 75%)[
    #set text(size: 10pt, style: "italic")
    A biomechanical analytics dashboard for track and field coaches that replaces
    manual video analysis with real-time sensor-based feedback. Shoe-mounted sensors
    capture ground contact and flight data, which is processed into actionable coaching
    metrics including hurdle analysis, reaction time, jump height, sprint fatigue,
    and asymmetry detection.
  ]
]

#pagebreak()

// ============================================================
// Table of Contents
// ============================================================
#outline(title: "Contents", depth: 3, indent: 1.5em)

#pagebreak()

// ============================================================
// 1. Summary
// ============================================================
= Summary

== What StrideTrack Does

StrideTrack addresses the problem of time-intensive, subjective video analysis in track and
field coaching. Coaches upload sensor data captured from shoe-mounted force sensors and
immediately receive structured performance metrics. The system:

- Accepts raw force sensor CSV data from shoe-mounted sensors (left and right foot)
- Transforms raw force data into stride cycles with ground contact time (GCT) and flight time (FT)
- Detects hurdle clearances from flight-time gaps in the sensor signal
- Computes per-hurdle splits, takeoff/landing GCT, and flight time
- Projects full race times from partial hurdle runs
- Measures reaction time at race start and classifies it into green/yellow/red zones
- Computes Bosco jump test metrics including jump height, RSI, and fatigue index
- Scores athlete splits against population benchmarks with coaching notes
- Tracks GCT and FT drift across a sprint to quantify fatigue accumulation
- Detects left/right asymmetry in ground contact and flight time
- Maintains a historical record of all events per athlete with time-series filtering

== Tech Stack Overview

*Backend:*
- Python 3.13 + FastAPI (REST API)
- Supabase (PostgreSQL + Auth)
- Pandas + NumPy (sensor data processing)
- OpenTelemetry + Jaeger (observability)
- uv (package manager), Ruff (linter/formatter)

*Frontend:*
- React 19 + Vite + TypeScript
- TanStack Query v5 (server state)
- TailwindCSS v3 + shadcn/ui (styling)
- Zod (runtime validation)
- Axios (HTTP client)
- Bun (package manager)

*Infrastructure:*
- Docker & Docker Compose
- Supabase CLI (local development)
- Make (task automation)

== Implemented Features

*Authentication & User Management:*
- Supabase email and Google OAuth login
- JWT-based authentication with automatic token refresh
- Coach role enforcement via middleware dependency
- Auto-provisioning of profile and coach record on first login

*Athlete Management:*
- Full CRUD for athletes (name, height, weight)
- Athletes scoped to authenticated coach; no cross-coach access

*Run Management:*
- Create, update, and delete training runs
- Event type metadata (sprint, hurdles, jump, Bosco test)
- Partial hurdle run support with target event for projection

*Sensor Data Ingestion:*
- CSV upload via multipart form
- Dropout fill for sensor noise (< 20 ms gaps)
- Automatic stride cycle extraction and DB insertion
- Returns run ID and row count on success

*Hurdle Analytics:*
- Per-hurdle metrics table (split, steps between, GCT, FT)
- Takeoff and landing GCT time series
- Takeoff flight time per hurdle
- GCT increase hurdle-to-hurdle
- Full race time projection from partial runs
- Hurdle timeline chart data

*Sprint Analytics:*
- GCT/FT drift (fatigue indicator)
- Step frequency time series

*Universal Metrics:*
- Left/right foot GCT and FT overlay
- Stacked bar chart (GCT + FT per stride)
- Asymmetry percentage (GCT and FT)
- GCT range bucketing (configurable min/max)

*Reaction Time:*
- Per-run reaction time with zone classification
- Average reaction time across all runs for an athlete

*Bosco Jump Test:*
- Jump height per jump ($h = 1.226 times "FT"^2$)
- Mean and peak jump height, jump frequency
- RSI per jump, fatigue index

*Split Score:*
- Segment-by-segment time comparison to population benchmarks
- Supports 400m hurdles (11 segments) and 400m sprint (4 segments)
- Coaching notes with delta in seconds and percentage

*Event History:*
- Time-series query by event type, date range, and athlete
- Used for long-term performance trend visualization

*Observability:*
- OpenTelemetry traces on all backend requests
- Jaeger UI for trace visualization and trace-log correlation

== Quick Start Guide

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd StrideTrack

# 2. Check dependencies and generate .env files
make init

# 3. Start all services (Supabase + backend + frontend)
make up

# 4. Apply database migrations
make db-reset

# Access points:
# Frontend:        http://localhost:5173
# Backend API:     http://localhost:8000
# Swagger docs:    http://localhost:8000/docs
# Supabase Studio: http://localhost:54323
# Jaeger traces:   http://localhost:16686
```

// ============================================================
// 2. Architecture Overview
// ============================================================
= Architecture Overview

== System Architecture

StrideTrack follows a 3-tier layered architecture:

*Presentation Layer (Frontend):*
- React 19 SPA with TanStack Query for server state
- Communicates with the backend exclusively via REST API
- Supabase client handles auth session and token refresh

*Application Layer (Backend):*
- FastAPI with route → service → repository pattern
- Routes: request validation and delegation only
- Services: business logic and error handling
- Repositories: Supabase database operations only

*Data Layer:*
- Supabase-hosted PostgreSQL
- Row-level security policies enforce coach/athlete data isolation
- Supabase Auth manages user identity and JWT issuance

*Observability:*
- OpenTelemetry SDK instruments all backend requests
- Traces exported to Jaeger for distributed tracing

```
┌──────────────────────────────────────┐
│           React Frontend              │
│  (TanStack Query + Zod + Axios)      │
└──────────────┬───────────────────────┘
               │  REST API (JWT Bearer)
┌──────────────▼───────────────────────┐
│          FastAPI Backend              │
│  Routes → Services → Repositories    │
└──────────────┬───────────────────────┘
               │  Supabase Python Client
┌──────────────▼───────────────────────┐
│   Supabase (PostgreSQL + Auth + RLS)  │
└──────────────┬───────────────────────┘
               │  OTLP gRPC
┌──────────────▼───────────────────────┐
│         Jaeger (Tracing UI)           │
└──────────────────────────────────────┘
```

== Data Flow

The system processes sensor data through the following pipeline:

+ *Upload* --- Coach uploads CSV from shoe sensors via the Record Run page.
+ *Transform* --- Backend applies dropout fill, extracts stance intervals, and builds stride cycle rows.
+ *Store* --- Stride cycles inserted into `run_metrics`; run record created in `run`.
+ *Analyze* --- Frontend queries metric endpoints; backend services compute analytics on-demand from `run_metrics`.
+ *Visualize* --- Frontend renders charts and tables using TanStack Query-cached responses.

== Technology Choices

*FastAPI:* A modern Python web framework that automatically generates interactive API
documentation (Swagger UI), making it easy to explore and test every endpoint in a browser.
It also supports high-performance async request handling and has a built-in dependency
injection system for cleanly separating authentication, business logic, and data access.

*Supabase:* An all-in-one backend platform that provides the database, user authentication,
and data security rules out of the box. Instead of building and maintaining separate systems
for user login, database hosting, and access control, Supabase bundles all of these into a
single managed service backed by PostgreSQL with row-level security policies.

*Pandas + NumPy:* Libraries purpose-built for processing large volumes of tabular data
efficiently. They handle the raw sensor CSV files --- filling in signal dropouts, extracting
stride cycles, and computing metrics --- using optimized batch operations rather than slow
row-by-row processing. This is critical for quickly transforming thousands of sensor readings
into usable stride data.

*TanStack Query:* Manages how the frontend fetches and caches data from the backend. It
automatically handles loading indicators, error states, and background data refreshing so
that the UI always shows up-to-date information without requiring manual refresh logic or
complex state management code.

*Zod:* Validates the shape of data coming back from the backend before the frontend uses it.
If the backend sends an unexpected response structure, Zod catches the mismatch immediately
at the boundary rather than letting bad data silently break charts or tables deeper in the UI.

*shadcn/ui:* A library of pre-built, accessible UI components (buttons, dropdowns, modals,
etc.) that can be freely customized with our styling system. It provides a consistent look
and feel across the application without imposing rigid design constraints, giving us
full control over appearance while saving development time on common UI patterns.

*OpenTelemetry + Jaeger:* A monitoring setup that tracks every request through the system
from start to finish. When something goes wrong, developers can trace the exact path a
request took --- from the frontend, through the backend, into the database --- to pinpoint
where the issue occurred. This uses open standards, so we are not locked into any specific
vendor's monitoring tools.

== Key Design Decisions

=== Compute-on-Read vs. Pre-computed Analytics

All analytics (hurdle metrics, Bosco metrics, split scores, etc.) are computed at query time
from raw `run_metrics` rows rather than stored in derived tables. This means:

- The schema stays simple --- one source of truth (`run_metrics`)
- Algorithms can be updated without a migration or backfill
- Trade-off: repeated queries re-compute the same data; acceptable for current dataset sizes

For high-traffic production use, a caching layer (Redis) or materialized views would be the
next step.

=== On-Demand Stride Cycle Extraction

The CSV transformation runs synchronously at upload time and inserts all stride cycles in a
single batch before returning the run ID to the frontend. This keeps the API response useful
(returns row count, surfaces errors immediately) and avoids background-job complexity.
For very long sessions (> 50,000 strides) this may need to move to an async task queue.

=== Row-Level Security for Multi-Tenancy

Supabase RLS policies enforce data isolation at the database level using helper functions
(`coach_id()`, `athlete_ids()`, `run_ids()`). Even if the application layer has a bug,
coaches cannot access another coach's athletes or runs.

// ============================================================
// 3. Authentication
// ============================================================
= Authentication

== Supabase JWT Flow

+ *Frontend login* --- User authenticates via Supabase email/password or Google OAuth. Supabase issues a signed JWT and stores the session in `localStorage`.
+ *Request header* --- Axios interceptor reads the active Supabase session and attaches `Authorization: Bearer <token>` to every API request automatically.
+ *Backend verification* --- The `get_current_user` FastAPI dependency fetches the Supabase JWKS from `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` and verifies the signature. Supported algorithms: ES256, HS256. Required audience: `authenticated`.
+ *Profile resolution* --- The backend looks up the user's profile by `auth_user_id`. If no profile exists (first login), one is created automatically with role `coach` and a corresponding `coaches` table entry.
+ *Token refresh* --- Supabase client SDK handles silent token refresh in the browser. The backend does not participate in refresh --- each request carries a fresh JWT.

== Coach Role Verification

Endpoints that require coach access declare the `get_current_coach` dependency:

```python
@router.get("/athletes")
async def get_athletes(
    coach: Coach = Depends(get_current_coach),
    service: AthleteService = Depends(get_athlete_service),
) -> list[AthleteResponse]:
    ...
```

`get_current_coach` calls `get_current_user`, then checks `profile.role == "coach"`. If the
role is not `coach`, it raises `NotACoachException`, which maps to HTTP 403.

== Development Token Bypass

In `ENVIRONMENT=development`, sending `Authorization: Bearer dev-token` skips JWT
verification entirely and returns a hardcoded dev user:

```
UUID: 00000000-0000-0000-0000-000000000099
```

This allows frontend and backend development without a live Supabase Auth session.

// ============================================================
// 4. Sensor Data Pipeline
// ============================================================
= Sensor Data Pipeline <sensor-data-pipeline>

== CSV Ingestion

The `POST /api/csv/upload-run` endpoint accepts a multipart form with:

#table(
  columns: (auto, auto, 1fr),
  [Field], [Type], [Description],
  [`file`], [`UploadFile`], [Raw sensor CSV (Time, Force_Foot1, Force_Foot2)],
  [`athlete_id`], [`UUID`], [Target athlete],
  [`event_type`], [`event_type_enum`], [Event classification],
  [`name`], [`string`], [Optional run name],
  [`target_event`], [`event_type_enum`], [Required for `hurdles_partial` runs],
)

*Response:*
```json
{
  "run_id": "uuid",
  "rows_inserted": 1240
}
```

== Stride Cycle Transformation

*Input:* Raw CSV with columns `Time` (ms), `Force_Foot1`, `Force_Foot2`

*Step 1 --- Dropout Fill:*
Brief gaps (< 20 ms) in the force signal where force drops to zero are filled. These gaps
represent sensor noise or electrical dropout, not true toe-offs. Without this step, a single
stance interval may be split into multiple false contacts.

*Step 2 --- Stance Interval Extraction:*
Regions where force exceeds a threshold are identified as ground-contact (stance) intervals.
The start of each interval is the *Initial Contact (IC)* and the end is the *Toe-Off (TO)*.

*Step 3 --- Stride Row Construction:*
For each stance interval, pair it with the next IC of the same foot to compute stride timing.
The key timestamps used in each formula are:

- *`ic_time`* --- the moment (in ms) the foot first touches the ground (Initial Contact)
- *`to_time`* --- the moment (in ms) the foot lifts off the ground (Toe-Off)
- *`next_ic_time`* --- the moment (in ms) the same foot touches the ground again on the next stride

From these three timestamps, the following metrics are derived:

#table(
  columns: (auto, 1fr),
  [Column], [Formula & Meaning],
  [`gct_ms`], [*Ground Contact Time* = `to_time − ic_time`. How long the foot stays on the ground during a single stance.],
  [`flight_ms`], [*Flight Time* = `next_ic_time − to_time`. How long the foot is airborne between toe-off and the next ground contact.],
  [`step_time_ms`], [*Step Time* = `gct_ms + flight_ms`. Total duration of one complete stride cycle (ground + air).],
)

*Step 4 --- Stride Numbering:*
Left and right strides are numbered sequentially based on their IC order in time.

== Edge Cases & Signal Noise

#table(
  columns: (1fr, 1fr),
  [Scenario], [Handling],
  [Short signal gap (< 20 ms)], [Filled as stance (dropout fill)],
  [Missing final IC for a stance], [Last stride row excluded (no valid `next_ic_time`)],
  [Empty or malformed CSV], [`CSVService` raises `ValueError`; maps to HTTP 422],
  [Zero-force entire file], [No strides extracted; `rows_inserted = 0` returned],
)

// ============================================================
// 5. Analytics Engine
// ============================================================
= Analytics Engine

All analytics are computed on-demand by backend services reading from `run_metrics`.

== Hurdle Detection & Metrics

*File:* `backend/app/utils/hurdle_metrics.py`

*Detection Algorithm:*

+ Merge overlapping ground-contact intervals from both feet across all strides.
+ Find gaps between merged contact intervals --- these represent airborne phases.
+ Filter gaps by configurable min/max duration thresholds to isolate hurdle clearances (distinguishing from normal inter-stride flight time).
+ Each qualifying gap is one hurdle clearance.

*Per-Hurdle Metrics Extracted:*

#table(
  columns: (auto, 1fr),
  [Metric], [Description],
  [`split_ms`], [Time from previous hurdle landing IC to this hurdle takeoff IC],
  [`steps_between`], [Number of ICs in the inter-hurdle interval],
  [`takeoff_gct_ms`], [GCT of the last ground contact before the gap (takeoff foot)],
  [`landing_gct_ms`], [GCT of the first ground contact after the gap (landing foot)],
  [`takeoff_ft_ms`], [Flight time of the takeoff foot immediately before clearance],
  [`clearance_ft_ms`], [Duration of the hurdle gap (airborne time)],
)

*Expected Hurdle Counts by Event:*

#table(
  columns: (auto, auto),
  [Event], [Expected Hurdles],
  [`hurdles_60m`], [5],
  [`hurdles_100m`], [10],
  [`hurdles_110m`], [10],
  [`hurdles_400m`], [10],
)

== Race Projection <race-projection>

*File:* `backend/app/utils/hurdle_projection.py`

For `hurdles_partial` runs, a full race time is projected using a phase-ratio model:

+ The race is split into phases: *acceleration* (H1--H3), *peak speed* (H4--H6), and *fatigue* (H7--H10), each with phase-specific ratio multipliers.
+ The completed split times are averaged and scaled by the phase ratios and remaining hurdle count.
+ A sprint scalar accounts for the final sprint from the last hurdle to the finish line.

*Example: 110m hurdles (10 hurdles, 9.14 m inter-hurdle, 13.02 m final segment)*

#table(
  columns: (auto, auto, auto),
  [Phase], [Hurdles], [Ratio],
  [Acceleration], [H1--H3], [1.02, 1.00, 0.98],
  [Peak], [H4--H6], [0.98],
  [Fatigue], [H7--H10], [1.00 → 1.03],
)

== Reaction Time

*File:* `backend/app/services/reaction_time_service.py`

*Definition:* Reaction time = `to_time` of the first stride --- when the foot first leaves
the ground after the start signal. This is the earliest measurable response in the sensor data.

*Zone Classification:*

#table(
  columns: (auto, auto, auto),
  [Zone], [Range], [Label],
  [Green], [< 200 ms], [Excellent],
  [Yellow], [200--300 ms], [Average],
  [Red], [> 300 ms], [Slow],
)

== Bosco Jump Test

*File:* `backend/app/utils/bosco_transformations.py`

The Bosco test uses continuous jumping to measure reactive strength and fatigue.

*Jump Height Formula:*
$ h = 1.226 times "FT"^2 $
where $h$ is in meters and FT is flight time in seconds.

*Computed Metrics:*

#table(
  columns: (1fr, 1fr),
  [Metric], [Formula / Description],
  [Jump height (per jump)], [$1.226 times "FT"^2$],
  [Mean jump height], [Mean of all per-jump heights],
  [Peak jump height], [Max of all per-jump heights],
  [Jump frequency], [Total jumps / total time (s)],
  [RSI (per jump)], [$"FT" \/ "GCT"$],
  [Fatigue index], [$("GCT"_"last" - "GCT"_"first") \/ "GCT"_"first" times 100%$],
)

== Split Score Analysis

*Files:* `backend/app/utils/split_score.py`, `backend/app/services/split_score_service.py`

*Supported Events:*

#table(
  columns: (auto, 1fr),
  [Event], [Segments],
  [400m hurdles], [11 (start → H1, H1--H2, ..., H10 → finish)],
  [400m sprint], [4 equal quarters (0--25%, 25--50%, 50--75%, 75--100%)],
)

*Computation:*
+ Segment the run by hurdle splits or time quarters.
+ Express each segment as a percentage of total time.
+ Compare to population mean percentage for that segment.
+ Compute delta in seconds and percentage.
+ Generate coaching note: _"Segment 3: 0.5s slower than average (8% slower)"_

== Sprint Fatigue Tracking

*File:* `backend/app/services/sprint_metric_service.py`

*GCT/FT Drift:* Tracks how ground contact time and flight time evolve across the run.
Early strides are compared to late strides to quantify fatigue accumulation. A rising GCT
trend indicates the athlete is spending more time on the ground as they tire.

*Step Frequency:* Steps per second over time. Declining frequency in later strides is an
indicator of neuromuscular fatigue.

// ============================================================
// 6. Frontend Architecture
// ============================================================
= Frontend Architecture

== Application Structure

```
frontend/src/
├── pages/          # Top-level route components
├── components/     # Reusable UI (feature-organized + ui/ primitives)
├── hooks/          # TanStack Query hooks (*.hooks.ts)
├── context/        # React Context providers (auth, theme)
├── lib/            # Utilities, Axios client, Supabase client, config
```

All server state lives in TanStack Query hooks. Components consume hooks and render
data --- they do not own fetch logic. Mutations (create, update, delete) are also wrapped
in hooks so components stay declarative.

== State Management Pattern

- *Server state:* TanStack Query (`useQuery`, `useMutation`)
- *Auth state:* React Context wrapping the Supabase session
- *UI state:* `useState`/`useReducer` local to components

*Example hook --- fetching all training runs:*

The `useGetAllRuns` hook below is a typical pattern used throughout the frontend. It fetches
all training runs from the backend, validates the response with Zod to catch any unexpected
data shapes, and returns the results along with loading and error states. Any component that
needs the run list simply calls this hook --- it never writes its own fetch logic. TanStack
Query automatically caches the response under the `"runs"` key, so navigating between pages
does not trigger redundant network requests.

```typescript
// frontend/src/hooks/useRuns.hooks.ts
export function useGetAllRuns() {
  const query = useQuery({
    queryKey: ["runs"],
    queryFn: async () => {
      const response = await api.get<Run[]>("/runs");
      return validateResponse(response.data, z.array(runResponseSchema));
    },
  });

  return {
    runs: query.data ?? [],
    runsIsLoading: query.isLoading,
    runsError: query.error,
    runsRefetch: query.refetch,
  };
}
```

== Page Overview

#table(
  columns: (auto, auto, 1fr),
  [Page], [Route], [Purpose],
  [`LoginPage`], [`/login`], [Supabase email/Google OAuth login],
  [`HomePage`], [`/`], [Dashboard: athlete list, recent runs, quick access],
  [`AthleteProfilePage`], [`/athletes/:id`], [Per-athlete stats, run history, biometrics],
  [`RecordRunPage`], [`/record`], [CSV upload interface; sensor data ingestion],
  [`RunAnalysisPage`], [`/runs/:id`], [Deep-dive analysis for a single run (all metrics)],
  [`VisualizationsPage`], [`/visualizations`], [Multi-metric dashboard with chart selection],
  [`HistoryPage`], [`/history`], [Time-series history by event type with date filtering],
)

== Visualizations

The frontend renders 27 chart components across 6 event categories, all built with Recharts
and fed by dedicated TanStack Query hooks. The tables below map each visualization to
what it shows for the coach.

=== Core Metrics

These charts are available for all run types regardless of event.

#table(
  columns: (auto, 1fr),
  [Chart], [What It Shows],
  [Ground Contact (L/R)], [Left vs. right foot GCT overlay across strides],
  [Flight Time (L/R)], [Left vs. right foot flight time overlay across strides],
  [L/R Overlay], [Reusable left/right comparison for any stride metric],
  [Step Time], [Total stride duration (GCT + FT) per stride],
  [RSI (per stride)], [Reactive Strength Index (flight / GCT) across strides],
  [GCT Range Pie], [Pie chart bucketing strides by GCT range with adjustable thresholds],
  [GCT Asymmetry KPI], [Single-value display of left/right GCT imbalance percentage],
  [FT Asymmetry KPI], [Single-value display of left/right flight time imbalance percentage],
)

=== Sprint

#table(
  columns: (auto, 1fr),
  [Chart], [What It Shows],
  [GCT/FT Drift], [How ground contact and flight time evolve across the run (fatigue tracking)],
  [Step Frequency], [Steps per second as a time series; declining frequency indicates fatigue],
)

=== Hurdles

#table(
  columns: (auto, 1fr),
  [Chart], [What It Shows],
  [Hurdle Splits], [Bar chart of time between consecutive hurdles with CV% consistency overlay],
  [Steps Between Hurdles], [Ground contact count between each hurdle pair (e.g., 3-step vs. 4-step)],
  [Takeoff GCT], [Ground contact time on the takeoff foot before each clearance],
  [Landing GCT], [Ground contact time on the landing foot after each clearance],
  [Takeoff Flight Time], [Airborne duration during each hurdle clearance],
  [GCT Increase], [GCT change first-to-last hurdle, color-coded (green/yellow/red) by fatigue severity],
  [Hurdle Timeline], [Time-series of left/right foot contact phases with hurdle clearance markers],
  [Split Score], [Per-segment comparison of athlete splits against population benchmarks],
)

=== Partial Hurdles

#table(
  columns: (auto, 1fr),
  [Chart], [What It Shows],
  [Projected Finish], [Estimated full race time from a partial hurdle run],
  [Projected Splits], [Completed vs. projected split times with mean reference line],
)

=== Bosco Jump Test

#table(
  columns: (auto, 1fr),
  [Chart], [What It Shows],
  [Jump Height], [Bar chart of estimated jump height per repetition],
  [RSI (per jump)], [Reactive Strength Index per jump with 1.0 target line],
  [GCT vs. Flight], [Ground contact and flight time side-by-side per jump],
)

=== Long Jump

#table(
  columns: (auto, 1fr),
  [Chart], [What It Shows],
  [Approach Profile], [GCT progression across approach steps with phase coloring],
  [Flight Time], [Per-foot flight time across the approach run],
  [GCT], [Ground contact time per step in the approach],
)

=== Triple Jump

#table(
  columns: (auto, 1fr),
  [Chart], [What It Shows],
  [Phase Ratio], [Stacked bar showing Hop:Step:Jump flight time distribution],
  [Phase Timeline], [Dual timeline of GCT and flight time per step with phase labels],
)

=== Event History

#table(
  columns: (auto, 1fr),
  [Chart], [What It Shows],
  [Event History], [Line chart of total run time progression across sessions for trend tracking],
)

// ============================================================
// 7. Database Schema
// ============================================================
= Database Schema <database-schema>

== Schema Diagram

The diagram below shows the full database schema as seen in Supabase Studio, including all
tables, columns, types, and foreign key relationships.

#layout(size => {
  let h = measure(image("schema.png", width: size.width)).height
  box(clip: true, width: size.width, height: h * 0.65)[
    #place(bottom)[
      #image("schema.png", width: size.width)
    ]
  ]
})

== Tables

=== `profiles`

Bridge between Supabase Auth and application data.

#table(
  columns: (auto, auto, 1fr),
  [Column], [Type], [Notes],
  [`id`], [`UUID`], [PK],
  [`auth_user_id`], [`UUID`], [FK → Supabase auth.users],
  [`email`], [`text`], [],
  [`name`], [`text`], [],
  [`role`], [`role_enum`], [`coach` or `athlete`],
  [`created_at`], [`timestamptz`], [],
)

=== `coaches`

One row per coach user.

#table(
  columns: (auto, auto, 1fr),
  [Column], [Type], [Notes],
  [`id`], [`UUID`], [PK],
  [`profile_id`], [`UUID`], [FK → profiles(id)],
  [`created_at`], [`timestamptz`], [],
)

=== `athletes`

Athletes owned by a coach.

#table(
  columns: (auto, auto, 1fr),
  [Column], [Type], [Notes],
  [`id`], [`UUID`], [PK],
  [`coach_id`], [`UUID`], [FK → coaches(id)],
  [`name`], [`text`], [],
  [`height_in`], [`numeric`], [Height in inches],
  [`weight_lbs`], [`numeric`], [Weight in pounds],
  [`created_at`], [`timestamptz`], [],
)

=== `run`

A single training session.

#table(
  columns: (auto, auto, 1fr),
  [Column], [Type], [Notes],
  [`id`], [`UUID`], [PK],
  [`athlete_id`], [`UUID`], [FK → athletes(id) ON DELETE CASCADE],
  [`event_type`], [`event_type_enum`], [Event classification],
  [`name`], [`text`], [Optional display name],
  [`elapsed_ms`], [`integer`], [Total run duration (ms), NOT NULL],
  [`target_event`], [`event_type_enum`], [For `hurdles_partial` projection target],
  [`created_at`], [`timestamptz`], [],
)

=== `run_metrics`

One row per stride cycle. Core data table.

#table(
  columns: (auto, auto, 1fr),
  [Column], [Type], [Notes],
  [`id`], [`UUID`], [PK],
  [`run_id`], [`UUID`], [FK → run(id) ON DELETE CASCADE],
  [`stride_num`], [`integer`], [Stride index],
  [`foot`], [`text`], [`left` or `right`],
  [`ic_time`], [`numeric`], [Initial contact (ms from run start)],
  [`to_time`], [`numeric`], [Toe-off (ms from run start)],
  [`next_ic_time`], [`numeric`], [Next IC of same foot (ms from run start)],
  [`gct_ms`], [`numeric`], [Ground contact time (to_time − ic_time)],
  [`flight_ms`], [`numeric`], [Flight time (next_ic_time − to_time)],
  [`step_time_ms`], [`numeric`], [Stride duration (gct_ms + flight_ms)],
  [`created_at`], [`timestamptz`], [],
)

Indexes on: `run_id`, `stride_num`, `foot`.

== Enums

=== `event_type_enum`

#table(
  columns: (auto, 1fr),
  [Category], [Values],
  [*Sprints*], [`sprint_60m`, `sprint_100m`, `sprint_200m`, `sprint_400m`],
  [*Hurdles*], [`hurdles_60m`, `hurdles_100m`, `hurdles_110m`, `hurdles_400m`, `hurdles_partial`],
  [*Jumps*], [`long_jump`, `triple_jump`, `high_jump`],
  [*Other*], [`bosco_test`],
)

The `hurdles_partial` value is used when a coach records a subset of hurdles during practice.
It requires a `target_event` field to specify which full hurdle event is being trained
(e.g., `hurdles_110m`), so the system can project a complete race time.

=== `role_enum`

#table(
  columns: (auto, 1fr),
  [Value], [Description],
  [`coach`], [Can manage athletes, upload sensor data, and view all analytics],
  [`athlete`], [Reserved for future use --- athletes viewing their own data],
)

== Row-Level Security

RLS is enabled on `profiles`, `athletes`, `run`, and `run_metrics`. All policies use
helper functions evaluated against the active JWT:

#table(
  columns: (auto, 1fr),
  [Function], [Returns],
  [`profile_id()`], [Profile UUID of the calling user],
  [`coach_id()`], [Coach UUID of the calling user],
  [`athlete_ids()`], [Array of athlete UUIDs belonging to the coach],
  [`run_ids()`], [Array of run UUIDs for all of the coach's athletes],
)

Policy examples:
- `profiles`: `auth_user_id = auth.uid()`
- `athletes`: `coach_id = coach_id()`
- `run`: `id = ANY(run_ids())`
- `run_metrics`: `run_id = ANY(run_ids())`

// ============================================================
// 8. API Reference
// ============================================================
= API Reference

All endpoints require `Authorization: Bearer <token>` unless noted. Base URL: `/api`.

== Authentication Endpoints

=== `GET /auth/me`

Returns the current user's profile.

```json
{ "id": "uuid", "email": "coach@example.com", "name": "Jane Smith", "role": "coach" }
```

=== `GET /auth/me/coach`

Returns the current user's coach record. Requires coach role.

== Athlete Endpoints

=== `GET /athletes`
Returns all athletes for the authenticated coach.

=== `GET /athletes/{athlete_id}`
Returns a single athlete.

=== `POST /athletes`
Creates a new athlete.
```json
{ "name": "John Doe", "height_in": 72, "weight_lbs": 165 }
```

=== `PATCH /athletes/{athlete_id}`
Updates an athlete. All fields optional.

=== `DELETE /athletes/{athlete_id}`
Deletes an athlete and all associated runs/metrics (CASCADE).

== Run Endpoints

=== `GET /runs`
Returns all runs across all of the coach's athletes.

=== `GET /runs/athlete/{athlete_id}`
Returns all runs for a specific athlete.

=== `GET /runs/{run_id}/metadata`
Returns run metadata (event_type, name, elapsed_ms, target_event).

=== `POST /runs`
Creates a run record manually (without sensor data). Primarily used for testing.

=== `PATCH /runs/{run_id}`
Updates run name, event type, or target event.

=== `DELETE /runs/{run_id}`
Deletes a run and all associated metrics (CASCADE).

== Universal Metric Endpoints

=== `GET /runs/{run_id}/metrics`
Returns all raw stride cycle rows for the run.

=== `GET /runs/{run_id}/metrics/lr-overlay`
Left/right foot GCT or FT overlay. Query param: `metric` (`gct_ms` or `flight_ms`).

=== `GET /runs/{run_id}/metrics/stacked-bar`
Stacked bar data: GCT and FT per stride, both feet.

=== `GET /runs/{run_id}/metrics/asymmetry`
GCT and FT asymmetry percentage between left and right foot.

=== `GET /runs/{run_id}/metrics/gct-range`
Counts strides within a GCT window. Query params: `min_ms`, `max_ms`.

== Sprint Metric Endpoints

=== `GET /runs/{run_id}/metrics/sprint/drift`
GCT and FT drift (fatigue tracking) --- early vs. late stride comparison.

=== `GET /runs/{run_id}/metrics/sprint/step-frequency`
Step frequency (steps/sec) as a time series across the run.

== Hurdle Metric Endpoints

=== `GET /runs/{run_id}/metrics/hurdles`
Per-hurdle metrics table: split, steps between, takeoff/landing GCT, flight time.

=== `GET /runs/{run_id}/metrics/hurdles/splits`
Hurdle split bar chart data.

=== `GET /runs/{run_id}/metrics/hurdles/steps-between`
Step count between each consecutive hurdle.

=== `GET /runs/{run_id}/metrics/hurdles/takeoff-gct`
Takeoff GCT per hurdle.

=== `GET /runs/{run_id}/metrics/hurdles/landing-gct`
Landing GCT per hurdle.

=== `GET /runs/{run_id}/metrics/hurdles/takeoff-ft`
Takeoff flight time per hurdle.

=== `GET /runs/{run_id}/metrics/hurdles/gct-increase`
GCT increase hurdle-to-hurdle (fatigue indicator).

=== `GET /runs/{run_id}/metrics/hurdles/projection`
Projects full race time from a partial hurdle run. Requires `target_event` set on the run.

=== `GET /runs/{run_id}/metrics/hurdles/timeline`
Time-series data for hurdle clearances, used to render the hurdle timeline chart.

== Reaction Time Endpoints

=== `GET /runs/{run_id}/metrics/reaction-time`
Reaction time for a specific run with zone classification.
```json
{ "reaction_time_ms": 187, "zone": "green" }
```

=== `GET /runs/athletes/{athlete_id}/metrics/reaction-time/average`
Average reaction time across all valid runs for an athlete.

== Bosco Test Endpoints

=== `GET /runs/{run_id}/metrics/bosco`
Computed Bosco metrics: per-jump heights, mean/peak, frequency, RSI, fatigue index.

=== `GET /runs/athlete/{athlete_id}/bosco`
All Bosco test runs for an athlete (for trend visualization).

== Split Score Endpoints

=== `GET /runs/{run_id}/metrics/split-score`
Split score with per-segment comparison to population benchmarks and coaching notes.

```json
{
  "segments": [
    {
      "label": "Segment 1",
      "athlete_pct": 9.2,
      "mean_pct": 8.8,
      "delta_s": 0.3,
      "delta_pct": 3.4,
      "note": "0.3s slower than average (3% slower)"
    }
  ]
}
```

== CSV Upload Endpoint

=== `POST /csv/upload-run`

Uploads sensor CSV and creates a new run with stride cycle metrics. Request format:
`multipart/form-data`. See @sensor-data-pipeline for the full field specification and
response format.

Error responses: `400` invalid CSV, `422` missing/invalid fields, `404` athlete not found.

== Event History Endpoints

=== `GET /event-history/metrics`

Returns historical run data for an athlete filtered by event type, with optional date range
and result limit. Query parameters: `athlete_id` (required), `event_type` (required),
`limit` (optional, default 10), `date_from` (optional), `date_to` (optional).

See @database-schema for the underlying table and column definitions.

== Health Endpoint

=== `GET /api/health`

```json
{ "status": "ok", "database": "connected" }
```

// ============================================================
// 9. Development Guide
// ============================================================
= Development Guide

== Prerequisites

#table(
  columns: (auto, auto, 1fr),
  [Tool], [Version], [Purpose],
  [Docker Desktop], [Latest], [Service containerization],
  [Supabase CLI], [Latest], [Local Supabase instance],
  [Bun], [Latest], [Frontend package manager],
  [uv], [Latest], [Backend package manager],
  [Make], [Any], [Task runner],
)

== Local Setup

```bash
git clone <repo-url> && cd StrideTrack
make init          # Check deps, generate .env files
supabase start     # Start Supabase (creates Docker network)
make up            # Start backend + frontend containers
make db-reset      # Apply all migrations
```

== Environment Variables

*Backend* (`backend/.env`):

#table(
  columns: (1.3fr, 1.5fr, 1fr),
  [Variable], [Example], [Description],
  [`ENVIRONMENT`], [`development`], [Controls dev-token bypass],
  [`SUPABASE_URL`], [`http://supabase_kong_...:8000`], [Internal Supabase URL],
  [`SUPABASE_SERVICE_ROLE_KEY`], [`eyJ...`], [Supabase admin key],
  [`SUPABASE_JWT_SECRET`], [`super-secret-...`], [For local JWT verification],
  [`OTEL_ENDPOINT`], [`http://jaeger:4317`], [OpenTelemetry gRPC target],
  [`OTEL_PYTHON_LOG_CORRELATION`], [`true`], [Inject trace IDs into logs],
)

*Frontend* (`frontend/.env`):

#table(
  columns: (1.3fr, 1.5fr, 1fr),
  [Variable], [Example], [Description],
  [`VITE_ENVIRONMENT`], [`development`], [Enables dev-token bypass],
  [`VITE_SUPABASE_URL`], [`http://localhost:54321`], [Browser-accessible Supabase URL],
  [`VITE_SUPABASE_PUBLISHABLE_KEY`], [`eyJ...`], [Supabase anon key],
  [`VITE_API_URL`], [`http://localhost:8000/api`], [Backend base URL],
)

== Docker Services & Ports

#table(
  columns: (auto, auto, 1fr),
  [Service], [Port(s)], [Description],
  [`backend`], [8000], [FastAPI; Swagger at `/docs`],
  [`frontend`], [5173], [Vite dev server with hot reload],
  [`jaeger`], [16686 (UI), 4317 (gRPC)], [Distributed tracing],
  [`supabase`], [54321 (API), 54323 (Studio)], [Managed by Supabase CLI],
)

== Common Commands

```bash
make up              # Start all services
make down            # Stop all services
make build           # Rebuild Docker images
make unit-test       # Backend unit tests (no Supabase needed)
make int-test        # Integration tests (requires make up)
make check-format    # Lint and format check
make format          # Auto-fix formatting issues
make db-reset        # Reset and re-apply all migrations
make logs SERVICE=backend   # Tail logs for a service
```

== Adding a New Endpoint

Follow the *route → service → repository* pattern:

+ *Repository* (`backend/app/repositories/`) --- Query Supabase; return raw data; no business logic.
+ *Service* (`backend/app/services/`) --- Accept the repository via constructor injection; apply business logic; raise domain exceptions.
+ *Route* (`backend/app/routes/`) --- Validate with Pydantic; delegate to the service; return a Pydantic response model.
+ *Register* the router in `backend/app/api.py` via `app.include_router(...)`.
+ *Unit test* (`backend/tests/unit/`) --- Add `test_{feature}.py` mocking the repository. Services must have unit test coverage.
+ *Frontend hook* (`frontend/src/hooks/`) --- Add a `use*.hooks.ts` file using TanStack Query's `useQuery` or `useMutation`.

// ============================================================
// 10. Deployment
// ============================================================
= Deployment

== Current Deployment

StrideTrack is currently run locally via Docker Compose. There is no production deployment
configured. The backend and frontend containers run in development mode with hot reload.

== Production Considerations

*Database:*
- Use a hosted Supabase project (supabase.com) rather than the local CLI instance
- Update `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` to hosted project values
- Run migrations via `supabase db push` against the hosted project

*Backend:*
- Set `ENVIRONMENT=production` to disable the dev-token bypass
- Configure `OTEL_ENDPOINT` to point to a production tracing backend
- Consider Gunicorn + Uvicorn workers behind an Nginx reverse proxy

*Frontend:*
- Run `bun run build` to produce a static build in `frontend/dist/`
- Serve via Vercel, Cloudflare Pages, or Nginx
- Update `VITE_API_URL` and Supabase vars to production values

*Scaling Considerations:*
- Add Redis caching keyed on `run_id` for read-only analytics endpoints
- Move CSV ingestion to a background task queue (Celery, ARQ) for very large runs

// ============================================================
// 11. Known Issues & Future Work
// ============================================================
= Known Issues & Future Work

== Current Limitations

- *No pagination:* All `GET /runs` and `GET /athletes` responses return the full list. Large datasets (50+ athletes, 500+ runs) will become slow.
- *Synchronous CSV processing:* Large uploads block the response until all strides are inserted. No progress indicator available to the user.
- *Static split score benchmarks:* Benchmark percentages are hardcoded constants, not derived from a live population dataset.
- *No integration test coverage* for analytics endpoints (hurdle, Bosco, split score).

== Potential Improvements

- Pagination and filtering query params on all list endpoints
- Redis caching for analytics endpoints (keyed on `run_id`)
- Async CSV ingestion with a task queue and progress polling
- Live population benchmarks for split score (aggregate opt-in athlete data)
- BLE real-time sensor streaming --- hook stub exists in `useBle.hooks.ts`
- Athlete role support (athletes view their own data; coaches manage their roster)
- Notification system for new run uploads or coaching notes

== Tech Debt

- `ExampleRepository` and `ExamplePage` are template scaffolding that can be removed
- Hurdle detection thresholds are hardcoded constants --- should be configurable per event type
- The `dev-token` bypass relies on a magic string; should be an environment flag

// ============================================================
// 12. Appendix
// ============================================================
= Appendix

== Glossary of Terms

#table(
  columns: (auto, 1fr),
  [Term], [Definition],
  [GCT], [Ground Contact Time. Duration in ms from IC to TO. Lower GCT indicates more explosive force production.],
  [FT], [Flight Time. Duration in ms from TO to next IC of the same foot.],
  [IC], [Initial Contact. The moment the foot first contacts the ground (force exceeds threshold).],
  [TO], [Toe-Off. The moment the foot leaves the ground (force drops below threshold).],
  [Stride Cycle], [One complete IC → TO → next IC sequence for a single foot.],
  [Dropout Fill], [Technique to fill brief (< 20 ms) sensor gaps to avoid false toe-off detection.],
  [RSI], [Reactive Strength Index. FT / GCT. Measures explosive power ratio; used in Bosco test.],
  [Fatigue Index], [% increase in GCT from first to last Bosco jump. Higher values indicate neuromuscular fatigue.],
  [Asymmetry], [% difference in GCT or FT between left and right foot. Values > 10% may indicate injury risk.],
  [Split], [Elapsed time between two consecutive hurdles or race segments.],
  [Hurdle Projection], [Estimation of full race time from a partial hurdle run using phase-ratio multipliers.],
  [Split Score], [Segment-by-segment comparison of athlete splits against population mean percentages.],
  [Bosco Test], [A continuous jump test protocol to assess reactive strength and fatigue characteristics.],
  [RLS], [Row-Level Security. PostgreSQL feature restricting row access per user; isolates coach/athlete data.],
  [JWT], [JSON Web Token. Signed token issued by Supabase Auth used to authenticate API requests.],
  [TanStack Query], [React library for server state management with automatic caching and background refetching.],
  [shadcn/ui], [Accessible React component primitives built on Radix UI and styled with TailwindCSS.],
)

== External Documentation Links

#table(
  columns: (auto, 1fr),
  [Resource], [URL],
  [FastAPI], [#link("https://fastapi.tiangolo.com")],
  [Supabase Docs], [#link("https://supabase.com/docs")],
  [Supabase Python Client], [#link("https://supabase.com/docs/reference/python")],
  [TanStack Query], [#link("https://tanstack.com/query/latest")],
  [Pydantic], [#link("https://docs.pydantic.dev")],
  [Ruff Linter], [#link("https://docs.astral.sh/ruff")],
  [Zod], [#link("https://zod.dev")],
  [shadcn/ui], [#link("https://ui.shadcn.com")],
  [OpenTelemetry Python], [#link("https://opentelemetry.io/docs/languages/python")],
  [Jaeger], [#link("https://www.jaegertracing.io/docs")],
  [TailwindCSS], [#link("https://tailwindcss.com/docs")],
)
