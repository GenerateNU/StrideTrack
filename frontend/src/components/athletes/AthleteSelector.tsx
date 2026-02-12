import { useAthletes } from "@/hooks/useAthletes.hooks";

export function AthleteSelector() {
  const { data: athletes, isLoading, error } = useAthletes();

  if (isLoading) return <div>Loading athletes...</div>;
  if (error) return <div>Error loading athletes: {error.message}</div>;

  return (
    <div className="max-w-md">
      <label htmlFor="athlete-select" className="block text-sm font-medium mb-2">
        Choose an athlete:
      </label>
      <select
        id="athlete-select"
        className="w-full p-2 border rounded-md bg-background"
        defaultValue=""
      >
        <option value="" disabled>
          Select an athlete
        </option>
        {athletes?.map((athlete) => (
          <option key={athlete.athlete_id} value={athlete.athlete_id}>
            {athlete.name}
          </option>
        ))}
      </select>
    </div>
  );
}