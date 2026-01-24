-- Create training_runs table
CREATE TABLE IF NOT EXISTS coaches (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    coach_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
CREATE TABLE IF NOT EXISTS athletes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    athlete_name TEXT NOT NULL UNIQUE,
    coach_id UUID NOT NULL REFERENCES coaches(id) ON DELETE CASCADE, 
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS training_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    athlete_id UUID NOT NULL REFERENCES athletes(id) ON DELETE CASCADE, 
    athlete_name TEXT NOT NULL,
    distance_meters INTEGER NOT NULL CHECK (distance_meters > 0),
    duration_seconds NUMERIC(10, 2) NOT NULL CHECK (duration_seconds > 0),
    avg_ground_contact_time_ms NUMERIC(10, 2) CHECK (avg_ground_contact_time_ms > 0),
    run_date DATE, -- don't need this if coach is not manually entering data (automatically comes from shoe)
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);


-- Create index for common queries
CREATE INDEX idx_training_runs_athlete_id ON training_runs(athlete_id);
CREATE INDEX idx_training_runs_run_date ON training_runs(run_date);
CREATE INDEX idx_training_runs_created_at ON training_runs(created_at DESC);
CREATE INDEX idx_training_runs_athlete_name ON training_runs(athlete_name);

-- Enable Row Level Security
ALTER TABLE training_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE athletes ENABLE ROW LEVEL SECURITY;
ALTER TABLE coaches ENABLE ROW LEVEL SECURITY;

-- Function to automatically create coach profile on signup
CREATE OR REPLACE FUNCTION public.new_coach()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.coaches (id, coach_name)
  VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'full_name',
                            NEW.raw_user_meta_data->>'name', 
                            NEW.email));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger after a new user is created in auth.users
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.new_coach();

-- Create policies for users (only coaches for now)
CREATE POLICY "Coaches can view own profile"
ON coaches FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Coaches can update own profile"
ON coaches FOR UPDATE
USING (auth.uid() = id);

CREATE POLICY "Coaches can create own profile"
ON coaches FOR INSERT
WITH CHECK (auth.uid() = id);

CREATE POLICY "Coaches can view their athletes"
ON athletes FOR SELECT
USING (coach_id = auth.uid());

CREATE POLICY "Coaches can create their athletes"
ON athletes FOR INSERT
WITH CHECK (coach_id = auth.uid());

CREATE POLICY "Coaches can update their athletes"
ON athletes FOR UPDATE
USING (coach_id = auth.uid());

CREATE POLICY "Coaches can delete their athletes"
ON athletes FOR DELETE
USING (coach_id = auth.uid());

CREATE POLICY "Coaches can create runs for their athletes"
ON training_runs FOR INSERT
WITH CHECK (
    athlete_id IN (
        SELECT id FROM athletes WHERE coach_id = auth.uid()
    )
);

CREATE POLICY "Coaches can update their athletes runs"
ON training_runs FOR UPDATE
USING (
    athlete_id IN (
        SELECT id FROM athletes WHERE coach_id = auth.uid()
    )
);

CREATE POLICY "Coaches can delete their athletes runs"
ON training_runs FOR DELETE
USING (
    athlete_id IN (
        SELECT id FROM athletes WHERE coach_id = auth.uid()
    )
);