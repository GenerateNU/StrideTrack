CREATE TABLE IF NOT EXISTS training_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    athlete_name TEXT NOT NULL,
    distance_meters INTEGER NOT NULL CHECK (distance_meters > 0),
    duration_seconds NUMERIC(10, 2) NOT NULL CHECK (duration_seconds > 0),
    avg_ground_contact_time_ms NUMERIC(10, 2) CHECK (avg_ground_contact_time_ms > 0),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_training_runs_created_at ON training_runs(created_at DESC);
CREATE INDEX idx_training_runs_athlete_name ON training_runs(athlete_name);

ALTER TABLE training_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations on training_runs"
    ON training_runs
    FOR ALL
    USING (true)
    WITH CHECK (true);