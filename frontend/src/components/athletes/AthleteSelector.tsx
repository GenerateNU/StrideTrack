import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";

interface Athlete {
  athlete_id: string;
  coach_id: string;
  name: string;
  height_in: number | null;
  weight_lbs: number | null;
  created_at: string;
}

export function AthleteSelector() {
  const { athletes, athletesIsLoading, athletesError, athletesRefetch } =
    useGetAllAthletes();

  if (athletesIsLoading) return <QueryLoading />;
  if (athletesError)
    return <QueryError error={athletesError} refetch={athletesRefetch} />;

  return (
    <div className="max-w-md">
      <label
        htmlFor="athlete-select"
        className="block text-sm font-medium mb-2"
      >
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
        {athletes.map((athlete: Athlete) => (
          <option key={athlete.athlete_id} value={athlete.athlete_id}>
            {athlete.name}
          </option>
        ))}
      </select>
    </div>
  );
}
