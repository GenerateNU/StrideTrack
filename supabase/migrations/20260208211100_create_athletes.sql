CREATE TABLE athletes (
    athlete_id UUID PRIMARY KEY,
    coach_id UUID REFERENCES coaches(coach_id),
    name VARCHAR(50),
    height NUMERIC,
    weight NUMERIC,
    created_at TIMESTAMPTZ
);