import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";
import { ChevronDown } from "lucide-react";

interface Athlete {
  athlete_id: string;
  coach_id: string;
  name: string;
  height_in: number | null;
  weight_lbs: number | null;
  created_at: string;
}

interface AthleteSelectorProps {
  value: string | null;
  onChange: (athleteId: string | null) => void;
  label?: string;
}

export function AthleteSelector({
  value,
  onChange,
  label = "Athlete",
}: AthleteSelectorProps) {
  const { athletes, athletesIsLoading, athletesError, athletesRefetch } =
    useGetAllAthletes();

  if (athletesIsLoading) return <QueryLoading />;
  if (athletesError)
    return <QueryError error={athletesError} refetch={athletesRefetch} />;

  return (
    <div>
      <label className="block text-sm font-medium text-foreground mb-2">
        {label}
      </label>
      <div className="relative">
        <select
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value || null)}
          className="w-full appearance-none rounded-xl border border-border bg-card px-4 py-3.5 pr-10 text-sm font-medium text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
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
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      </div>
    </div>
  );
}
