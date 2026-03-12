import { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useGetAllRuns } from "@/hooks/useRuns.hooks";
import { ArrowLeft } from "lucide-react";

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
            new Date(b.created_at).getTime() -
            new Date(a.created_at).getTime()
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

  return (
    <div className="py-4">
      <button
        onClick={() => navigate("/")}
        className="mb-4 flex items-center gap-1 text-sm text-muted-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-secondary text-base font-bold text-foreground">
          {athlete.name
            .split(" ")
            .map((n) => n[0])
            .join("")
            .toUpperCase()}
        </div>
        <div>
          <h2 className="text-lg font-bold text-foreground">{athlete.name}</h2>
          <p className="text-xs text-muted-foreground">
            {athlete.height_in ? `${athlete.height_in}" · ` : ""}
            {athlete.weight_lbs ? `${athlete.weight_lbs} lbs` : ""}
            {` · ${athleteRuns.length} run${athleteRuns.length !== 1 ? "s" : ""}`}
          </p>
        </div>
      </div>

      <div className="mb-4 flex gap-1 rounded-lg bg-secondary p-1">
        {(["summary", "runs"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 rounded-md py-2 text-xs font-semibold transition-colors ${
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
          <div className="rounded-xl border border-border bg-card p-4">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Latest Run
            </p>
            {latestRun ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">
                    {latestRun.event_type.replace("_", " ")}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(latestRun.created_at).toLocaleDateString()}
                  </span>
                </div>
                {latestRun.elapsed_ms && (
                  <p className="text-xs text-muted-foreground">
                    Duration: {(latestRun.elapsed_ms / 1000).toFixed(1)}s
                  </p>
                )}
                <p className="text-xs italic text-muted-foreground">
                  Detailed metrics will appear after visualization integration.
                </p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No runs recorded yet.
              </p>
            )}
          </div>

          <div className="rounded-xl border border-border bg-card p-4">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Activity
            </p>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-secondary p-3">
                <div className="text-lg font-bold text-foreground">
                  {athleteRuns.length}
                </div>
                <div className="text-[10px] font-medium text-muted-foreground">
                  Total Runs
                </div>
              </div>
              <div className="rounded-lg bg-secondary p-3">
                <div className="text-lg font-bold text-foreground">
                  {new Set(athleteRuns.map((r) => r.event_type)).size}
                </div>
                <div className="text-[10px] font-medium text-muted-foreground">
                  Event Types
                </div>
              </div>
            </div>
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
              <div className="space-y-1.5">
                {dateRuns.map((run) => (
                  <button
                    key={run.run_id}
                    onClick={() =>
                      navigate(
                        `/athletes/${athleteId}/runs/${run.run_id}`
                      )
                    }
                    className="flex w-full items-center justify-between rounded-xl border border-border bg-card px-4 py-3 text-left"
                  >
                    <span className="rounded bg-secondary px-1.5 py-0.5 text-xs font-medium text-secondary-foreground">
                      {run.event_type.replace("_", " ")}
                    </span>
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
            <p className="py-8 text-center text-sm text-muted-foreground">
              No runs yet.
            </p>
          )}
        </div>
      )}
    </div>
  );
}