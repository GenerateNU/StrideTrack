CREATE TABLE coaches (
    coach_id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE athletes (
    athlete_id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    coach_id UUID REFERENCES coaches(coach_id),
    name VARCHAR(100) NOT NULL,
    height_in NUMERIC,
    weight_lbs NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TYPE event_type_enum AS ENUM (
    'sprint_60m',
    'sprint_100m',
    'sprint_200m',
    'sprint_400m',
    'hurdles_60m',
    'hurdles_110m',
    'hurdles_100m',
    'hurdles_400m',
    'long_jump',
    'triple_jump',
    'high_jump',
    'bosco_test'
);

CREATE TABLE RUN (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    athlete_id UUID NOT NULL,
    event_type event_type_enum NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    name VARCHAR(100),
    CONSTRAINT fk_run_athlete
        FOREIGN KEY (athlete_id)
        REFERENCES athletes(athlete_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE RUN_METRICS (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    run_id UUID NOT NULL,
    stride_num INTEGER NOT NULL,
    foot VARCHAR(10) NOT NULL CHECK (foot IN ('left', 'right')),
    ic_time INTEGER NOT NULL CHECK (ic_time >= 0),
    to_time INTEGER NOT NULL CHECK (to_time >= 0),
    next_ic_time INTEGER NOT NULL CHECK (next_ic_time >= 0),
    gct_ms INTEGER NOT NULL CHECK (gct_ms >= 0),
    flight_ms INTEGER NOT NULL CHECK (flight_ms >= 0),
    step_time_ms INTEGER NOT NULL CHECK (step_time_ms >= 0),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT fk_run_metrics_run
        FOREIGN KEY (run_id)
        REFERENCES RUN(run_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_run_metrics_run_id ON RUN_METRICS(run_id);
CREATE INDEX idx_run_metrics_stride_num ON RUN_METRICS(stride_num);
CREATE INDEX idx_run_metrics_foot ON RUN_METRICS(foot);
