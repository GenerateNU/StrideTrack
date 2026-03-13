import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useGetAllRuns } from "@/hooks/useRuns.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";
import { Search, ChevronDown, ChevronUp } from "lucide-react";

// Generate a consistent hue from a string for avatar variety
function nameToHue(name: string): number {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash) % 360;
}

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
    <div className="space-y-6 py-6">
      <div>
        <h2 className="text-2xl font-bold text-foreground">Your Athletes</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          {athletes.length} athlete{athletes.length !== 1 ? "s" : ""} ·{" "}
          {runs.length} run{runs.length !== 1 ? "s" : ""} recorded
        </p>
      </div>

      <div className="relative">
        <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search athletes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-2xl border border-input bg-card py-3 pl-10 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none"
        />
      </div>

      <div className="space-y-3">
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
          const hue = nameToHue(athlete.name);

          return (
            <div
              key={athlete.athlete_id}
              className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm shadow-foreground/[0.02]"
            >
              <div className="flex items-center justify-between p-4">
                <button
                  onClick={() => navigate(`/athletes/${athlete.athlete_id}`)}
                  className="flex items-center gap-3.5 text-left"
                >
                  <div
                    className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
                    style={{
                      background: `linear-gradient(135deg, hsl(${hue} 45% 42%), hsl(${hue + 30} 40% 55%))`,
                    }}
                  >
                    {athlete.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")
                      .toUpperCase()}
                  </div>
                  <div>
                    <div className="text-[15px] font-semibold text-foreground">
                      {athlete.name}
                    </div>
                    <div className="mt-0.5 text-xs text-muted-foreground">
                      {[
                        athlete.height_in ? `${athlete.height_in}"` : null,
                        athlete.weight_lbs ? `${athlete.weight_lbs} lbs` : null,
                        `${runs.filter((r) => r.athlete_id === athlete.athlete_id).length} runs`,
                      ]
                        .filter(Boolean)
                        .join(" · ")}
                    </div>
                  </div>
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => navigate(`/athletes/${athlete.athlete_id}`)}
                    className="rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-colors"
                    style={{
                      backgroundColor: "hsl(var(--primary))",
                      color: "hsl(var(--primary-foreground))",
                    }}
                  >
                    Profile
                  </button>
                  {athleteRuns.length > 0 && (
                    <button
                      onClick={() =>
                        setExpandedId(isExpanded ? null : athlete.athlete_id)
                      }
                      className="rounded-xl p-2 text-muted-foreground transition-colors hover:bg-secondary"
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
                <div className="border-t border-border bg-secondary/20 px-4 pb-3 pt-3">
                  <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
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
                        className="flex w-full items-center justify-between rounded-xl border border-border bg-card px-3.5 py-2.5 text-left"
                      >
                        <span className="text-xs font-medium text-foreground">
                          {run.event_type.replace("_", " ")}
                        </span>
                        <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                          {run.elapsed_ms && (
                            <span className="font-medium">
                              {(run.elapsed_ms / 1000).toFixed(1)}s
                            </span>
                          )}
                          <span>{formatTimeAgo(run.created_at)}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="rounded-2xl border border-dashed border-border p-12 text-center">
            <p className="text-sm font-medium text-muted-foreground">
              {search ? "No athletes match your search." : "No athletes yet."}
            </p>
            <p className="mt-1.5 text-xs text-muted-foreground">
              {search
                ? "Try a different search term."
                : "Add your first athlete from the menu above."}
            </p>
          </div>
        )}
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
