import { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useGetAllRuns } from "@/hooks/useRuns.hooks";
import { ArrowLeft, Activity, Calendar } from "lucide-react";

function nameToHue(name: string): number {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash) % 360;
}

export default function AthleteProfilePage() {
  const { athleteId } = useParams<{ athleteId: string }>();
  const navigate = useNavigate();
  const { athletes } = useGetAllAthletes();
  const { runs } = useGetAllRuns();
  const [tab, setTab] = useState<"summary" | "runs">("summary");

  const athlete = athletes.find((a) => a.athlete_id === athleteId);
  const athleteRuns = useMemo(
    () =>
      runs
        .filter((r) => r.athlete_id === athleteId)
        .sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        ),
    [runs, athleteId]
  );

  const groupedRuns = useMemo(() => {
    const groups = new Map<string, typeof athleteRuns>();
    athleteRuns.forEach((run) => {
      const dateKey = new Date(run.created_at).toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      });
      if (!groups.has(dateKey)) groups.set(dateKey, []);
      groups.get(dateKey)!.push(run);
    });
    return groups;
  }, [athleteRuns]);

  const latestRun = athleteRuns[0] ?? null;

  if (!athlete) {
    return (
      <div className="py-12 text-center text-sm text-muted-foreground">
        Athlete not found.
      </div>
    );
  }

  const hue = nameToHue(athlete.name);

  return (
    <div className="py-4">
      <button
        onClick={() => navigate("/")}
        className="mb-5 flex items-center gap-1 text-sm text-muted-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      {/* Profile header */}
      <div className="mb-6 flex items-center gap-4">
        <div
          className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full text-lg font-bold text-white"
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
          <h2 className="text-xl font-bold text-foreground">{athlete.name}</h2>
          <p className="text-xs text-muted-foreground">
            {[
              athlete.height_in ? `${athlete.height_in}"` : null,
              athlete.weight_lbs ? `${athlete.weight_lbs} lbs` : null,
              `${athleteRuns.length} run${athleteRuns.length !== 1 ? "s" : ""}`,
            ]
              .filter(Boolean)
              .join(" · ")}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-5 flex gap-1 rounded-xl bg-secondary p-1">
        {(["summary", "runs"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 rounded-lg py-2.5 text-xs font-semibold transition-colors ${
              tab === t
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground"
            }`}
          >
            {t === "summary" ? "Summary" : "Runs"}
          </button>
        ))}
      </div>

      {tab === "summary" && (
        <div className="space-y-4">
          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-2xl border border-border bg-card p-4 shadow-sm shadow-foreground/[0.02]">
              <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-secondary">
                <Activity className="h-4 w-4 text-foreground" />
              </div>
              <div className="text-2xl font-bold text-foreground">
                {athleteRuns.length}
              </div>
              <div className="text-xs text-muted-foreground">Total Runs</div>
            </div>
            <div className="rounded-2xl border border-border bg-card p-4 shadow-sm shadow-foreground/[0.02]">
              <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-secondary">
                <Calendar className="h-4 w-4 text-foreground" />
              </div>
              <div className="text-2xl font-bold text-foreground">
                {new Set(athleteRuns.map((r) => r.event_type)).size}
              </div>
              <div className="text-xs text-muted-foreground">Event Types</div>
            </div>
          </div>

          {/* Latest run */}
          <div className="rounded-2xl border border-border bg-card p-4 shadow-sm shadow-foreground/[0.02]">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Latest Run
            </p>
            {latestRun ? (
              <button
                onClick={() =>
                  navigate(`/athletes/${athleteId}/runs/${latestRun.run_id}`)
                }
                className="w-full text-left"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-foreground">
                    {latestRun.event_type.replace("_", " ")}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(latestRun.created_at).toLocaleDateString()}
                  </span>
                </div>
                {latestRun.elapsed_ms && (
                  <p className="mt-1 text-xs text-muted-foreground">
                    Duration: {(latestRun.elapsed_ms / 1000).toFixed(1)}s
                  </p>
                )}
                <p
                  className="mt-2 text-xs font-medium"
                  style={{ color: "hsl(var(--primary))" }}
                >
                  View analysis →
                </p>
              </button>
            ) : (
              <p className="text-sm text-muted-foreground">
                No runs recorded yet.
              </p>
            )}
          </div>
        </div>
      )}

      {tab === "runs" && (
        <div className="space-y-4">
          {Array.from(groupedRuns.entries()).map(([dateLabel, dateRuns]) => (
            <div key={dateLabel}>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {dateLabel}
              </p>
              <div className="space-y-2">
                {dateRuns.map((run) => (
                  <button
                    key={run.run_id}
                    onClick={() =>
                      navigate(`/athletes/${athleteId}/runs/${run.run_id}`)
                    }
                    className="flex w-full items-center justify-between rounded-2xl border border-border bg-card px-4 py-3 text-left shadow-sm shadow-foreground/[0.02]"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-secondary">
                        <Activity className="h-4 w-4 text-foreground" />
                      </div>
                      <div>
                        <span className="text-sm font-medium text-foreground">
                          {run.event_type.replace("_", " ")}
                        </span>
                        {run.elapsed_ms && (
                          <p className="text-[10px] text-muted-foreground">
                            {(run.elapsed_ms / 1000).toFixed(1)}s
                          </p>
                        )}
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(run.created_at).toLocaleTimeString("en-US", {
                        hour: "numeric",
                        minute: "2-digit",
                      })}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ))}
          {athleteRuns.length === 0 && (
            <div className="rounded-2xl border border-dashed border-border p-12 text-center">
              <p className="text-sm font-medium text-muted-foreground">
                No runs yet.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
