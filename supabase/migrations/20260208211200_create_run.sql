CREATE TYPE event_type_enum AS ENUM (
    '60m',
    '100m',
    '200m',
    '400m',
    '60m_hurdles_men',
    '60m_hurdles_women',
    '110m_hurdles_men',
    '100m_hurdles_women',
    '400m_hurdles_men',
    '400m_hurdles_women',
    '800m',
    '1500m',
    '3000m',
    '5000m',
    '10000m',
    '4x100m',
    '4x400m',
    'other'
);

CREATE TABLE RUN (
    run_id BIGSERIAL PRIMARY KEY,
    athlete_id UUID,
    event_type event_type_enum NOT NULL,
    created_at TIMESTAMPTZ,
    name VARCHAR(50),
    CONSTRAINT fk_run_athlete
        FOREIGN KEY (athlete_id)
        REFERENCES athletes(athlete_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);