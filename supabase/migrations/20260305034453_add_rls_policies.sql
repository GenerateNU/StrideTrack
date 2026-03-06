-- helper functions
CREATE OR REPLACE FUNCTION auth.profile_id()
RETURNS uuid AS $$
  SELECT profile_id FROM profiles
  WHERE auth_user_id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION auth.coach_id()
RETURNS uuid AS $$
  SELECT coach_id FROM coaches
  WHERE profile_id = auth.profile_id()
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION auth.athlete_ids()
RETURNS SETOF uuid AS $$
  SELECT athlete_id FROM athletes
  WHERE coach_id = auth.coach_id()
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION auth.run_ids()
RETURNS SETOF uuid AS $$
  SELECT run_id FROM RUN
  WHERE athlete_id IN (SELECT auth.athlete_ids())
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- enable RLS
ALTER TABLE coaches ENABLE ROW LEVEL SECURITY;
ALTER TABLE athletes ENABLE ROW LEVEL SECURITY;
ALTER TABLE RUN ENABLE ROW LEVEL SECURITY;
ALTER TABLE RUN_METRICS ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- policies 
CREATE POLICY "profile_access" ON profiles
FOR ALL USING (profile_id = auth.profile_id());

CREATE POLICY "coach_access" ON coaches
FOR ALL USING (profile_id = auth.profile_id());

CREATE POLICY "athlete_access" ON athletes
FOR ALL USING (coach_id = auth.coach_id())
WITH CHECK (coach_id = auth.coach_id());

CREATE POLICY "run_access" ON RUN
FOR ALL USING (athlete_id IN (SELECT auth.athlete_ids()))
WITH CHECK (athlete_id IN (SELECT auth.athlete_ids()));

CREATE POLICY "run_metrics_access" ON RUN_METRICS
FOR ALL USING (run_id IN (SELECT auth.run_ids()))
WITH CHECK (run_id IN (SELECT auth.run_ids()));