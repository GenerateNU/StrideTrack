-- Seed data for training_runs
INSERT INTO training_runs (athlete_name, distance_meters, duration_seconds, avg_ground_contact_time_ms, created_at) VALUES
    ('Sarah Johnson', 100, 12.45, 95.3, NOW() - INTERVAL '2 days'),
    ('Marcus Chen', 200, 24.89, 102.7, NOW() - INTERVAL '1 day'),
    ('Elena Rodriguez', 400, 58.32, 98.5, NOW() - INTERVAL '12 hours'),
    ('James Wright', 100, 11.92, 89.4, NOW() - INTERVAL '6 hours'),
    ('Aisha Patel', 200, 26.14, 105.2, NOW() - INTERVAL '3 hours');


-- Insert seed coach
INSERT INTO coaches (coach_id, name)
VALUES ('00000000-0000-0000-0000-000000000001', 'Coach Sam Baldwin');

-- Insert seed athlete
INSERT INTO athletes (athlete_id, coach_id, name, height_in, weight_lbs)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'Ben Marler',
    76,
    165
);