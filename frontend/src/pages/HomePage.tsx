import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useGetAllRuns } from "@/hooks/useRuns.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";
import { Search, ChevronDown, ChevronUp } from "lucide-react";

export default function HomePage() {
  const navigate = useNavigate();
  const { athletes, athletesIsLoading, athletesError, athletesRefetch } =
    useGetAllAthletes();
  const { runs } = useGetAllRuns();
  const [search, setSearch] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (athletesIsLoading) return <QueryLoading />;
  if (athletesError)
    return <QueryError error={athletesError} refetch={athletesRefetch} />;

  const filtered = athletes.filter((a) =>
    a.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4 py-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search athletes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-xl border border-input bg-card py-2.5 pl-10 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none"
        />
      </div>

      <p className="text-xs text-muted-foreground">
        {filtered.length} athlete{filtered.length !== 1 ? "s" : ""}
      </p>

      <div className="space-y-2">
        {filtered.map((athlete) => {
          const athleteRuns = runs
            .filter((r) => r.athlete_id === athlete.athlete_id)
            .sort(
              (a, b) =>
                new Date(b.created_at).getTime() -
                new Date(a.created_at).getTime()
            )
            .slice(0, 3);
          const isExpanded = expandedId === athlete.athlete_id;

          return (
            <div
              key={athlete.athlete_id}
              className="rounded-xl border border-border bg-card"
            >
              <div className="flex items-center justify-between p-3">
                <button
                  onClick={() =>
                    navigate(`/athletes/${athlete.athlete_id}`)
                  }
                  className="flex items-center gap-3 text-left"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary text-sm font-bold text-foreground">
                    {athlete.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .toUpperCase()}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-foreground">
                      {athlete.name}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {athlete.height_in ? `${athlete.height_in}" · ` : ""}
                      {athlete.weight_lbs ? `${athlete.weight_lbs} lbs` : ""}
                    </div>
                  </div>
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      navigate(`/athletes/${athlete.athlete_id}`)
                    }
                    className="rounded-lg bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground"
                  >
                    Profile
                  </button>
                  {athleteRuns.length > 0 && (
                    <button
                      onClick={() =>
                        setExpandedId(
                          isExpanded ? null : athlete.athlete_id
                        )
                      }
                      className="rounded-lg p-1.5 text-muted-foreground"
                    >
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </button>
                  )}
                </div>
              </div>

              {isExpanded && athleteRuns.length > 0 && (
                <div className="border-t border-border px-3 pb-3 pt-2">
                  <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                    Recent Runs
                  </p>
                  <div className="space-y-1.5">
                    {athleteRuns.map((run) => (
                      <button
                        key={run.run_id}
                        onClick={() =>
                          navigate(
                            `/athletes/${athlete.athlete_id}/runs/${run.run_id}`
                          )
                        }
                        className="flex w-full items-center justify-between rounded-lg bg-secondary px-3 py-2 text-left"
                      >
                        <span className="text-xs font-medium text-secondary-foreground">
                          {run.event_type.replace("_", " ")}
                        </span>
                        <span className="text-[10px] text-muted-foreground">
                          {formatTimeAgo(run.created_at)}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatTimeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}