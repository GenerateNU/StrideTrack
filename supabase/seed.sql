-- Seed data for training_runs (example table)
INSERT INTO training_runs (athlete_name, distance_meters, duration_seconds, avg_ground_contact_time_ms, created_at) VALUES
    ('Sarah Johnson', 100, 12.45, 95.3, NOW() - INTERVAL '2 days'),
    ('Marcus Chen', 200, 24.89, 102.7, NOW() - INTERVAL '1 day'),
    ('Elena Rodriguez', 400, 58.32, 98.5, NOW() - INTERVAL '12 hours'),
    ('James Wright', 100, 11.92, 89.4, NOW() - INTERVAL '6 hours'),
    ('Aisha Patel', 200, 26.14, 105.2, NOW() - INTERVAL '3 hours');


-- Dev auth user (required for FK constraint)
INSERT INTO auth.users (id, email, created_at, updated_at, instance_id, aud, role)
VALUES (
    '00000000-0000-0000-0000-000000000099',
    'dev@stridetrack.dev',
    NOW(),
    NOW(),
    '00000000-0000-0000-0000-000000000000',
    'authenticated',
    'authenticated'
);

-- Dev user profile
INSERT INTO profiles (profile_id, auth_user_id, email, name, role)
VALUES (
    '00000000-0000-0000-0000-000000000010',
    '00000000-0000-0000-0000-000000000099',
    'dev@stridetrack.dev',
    'Coach Sam Baldwin',
    'coach'
);

-- Seed coach linked to dev profile
INSERT INTO coaches (coach_id, profile_id)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000010'
);

-- Seed athletes
INSERT INTO athletes (athlete_id, coach_id, name, height_in, weight_lbs)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'Ben Marler',
    76,
    185
);

INSERT INTO athletes (athlete_id, coach_id, name, height_in, weight_lbs)
VALUES (
    '00000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    'Michael Maaseide',
    70,
    160
);

-- Insert RUN records
INSERT INTO run (run_id, athlete_id, event_type, name) VALUES
    ('d0271452-4bec-4759-84ef-c62beaafdbf0', '00000000-0000-0000-0000-000000000002', 'sprint_100m', 'Ben Sprint 1'),
    ('86fb3baf-264d-4047-ad17-d97be11eaec3', '00000000-0000-0000-0000-000000000003', 'sprint_100m', 'Michael Sprint 1'),
    ('acf9da17-bf30-4eb2-8494-3d641de4301b', '00000000-0000-0000-0000-000000000003', 'sprint_100m', 'Michael Sprint 2');

-- Insert RUN_METRICS (5 sample records)
INSERT INTO run_metrics (run_id, stride_num, foot, ic_time, to_time, next_ic_time, gct_ms, flight_ms, step_time_ms) VALUES
    ('d0271452-4bec-4759-84ef-c62beaafdbf0', 1, 'right', 0, 1290, 1440, 1290, 150, 1440),
    ('d0271452-4bec-4759-84ef-c62beaafdbf0', 1, 'left', 1320, 1410, 1850, 90, 440, 530),
    ('86fb3baf-264d-4047-ad17-d97be11eaec3', 1, 'right', 0, 2300, 2370, 2300, 70, 2370),
    ('86fb3baf-264d-4047-ad17-d97be11eaec3', 1, 'left', 2330, 2340, 2560, 10, 220, 230),
    ('acf9da17-bf30-4eb2-8494-3d641de4301b', 1, 'right', 0, 1969, 2699, 1969, 730, 2699);