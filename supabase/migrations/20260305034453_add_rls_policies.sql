-- helper functions
CREATE OR REPLACE FUNCTION public.profile_id()
RETURNS uuid AS $$
  SELECT profile_id FROM public.profiles
  WHERE auth_user_id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER STABLE SET search_path = '';

CREATE OR REPLACE FUNCTION public.coach_id()
RETURNS uuid AS $$
  SELECT coach_id FROM public.coaches
  WHERE profile_id = public.profile_id()
$$ LANGUAGE sql SECURITY DEFINER STABLE SET search_path = '';

CREATE OR REPLACE FUNCTION public.athlete_ids()
RETURNS SETOF uuid AS $$
  SELECT athlete_id FROM public.athletes
  WHERE coach_id = public.coach_id()
$$ LANGUAGE sql SECURITY DEFINER STABLE SET search_path = '';

CREATE OR REPLACE FUNCTION public.run_ids()
RETURNS SETOF uuid AS $$
  SELECT run_id FROM public.RUN
  WHERE athlete_id IN (SELECT public.athlete_ids())
$$ LANGUAGE sql SECURITY DEFINER STABLE SET search_path = '';

-- enable RLS
ALTER TABLE coaches ENABLE ROW LEVEL SECURITY;
ALTER TABLE athletes ENABLE ROW LEVEL SECURITY;
ALTER TABLE RUN ENABLE ROW LEVEL SECURITY;
ALTER TABLE RUN_METRICS ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- policies 
DROP POLICY "Allow all operations on training_runs" ON training_runs;
CREATE POLICY "training_runs_authenticated" ON training_runs
FOR ALL USING ((SELECT auth.uid()) IS NOT NULL);

CREATE POLICY "profile_access" ON profiles
FOR ALL USING (profile_id = (SELECT public.profile_id()));

CREATE POLICY "coach_access" ON coaches
FOR ALL USING (profile_id = (SELECT public.profile_id()));

CREATE POLICY "athlete_access" ON athletes
FOR ALL USING (coach_id = (SELECT public.coach_id()))
WITH CHECK (coach_id = (SELECT public.coach_id()));

CREATE POLICY "run_access" ON RUN
FOR ALL USING (athlete_id IN (SELECT public.athlete_ids()))
WITH CHECK (athlete_id IN (SELECT public.athlete_ids()));

CREATE POLICY "run_metrics_access" ON RUN_METRICS
FOR ALL USING (run_id IN (SELECT public.run_ids()))
WITH CHECK (run_id IN (SELECT public.run_ids()));