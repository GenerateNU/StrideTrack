import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useGetAllRuns } from "@/hooks/useRuns.hooks";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useEvents } from "@/hooks/useEvents";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";

export default function HistoryPage() {
  const navigate = useNavigate();
  const { runs, runsIsLoading, runsError, runsRefetch } = useGetAllRuns();
  const { athletes } = useGetAllAthletes();
  const events = useEvents();
  const [eventFilter, setEventFilter] = useState<string>("all");

  const athleteMap = useMemo(() => {
    const map = new Map<string, string>();
    athletes.forEach((a) => map.set(a.athlete_id, a.name));
    return map;
  }, [athletes]);

  const filtered = useMemo(() => {
    let result = runs;
    if (eventFilter !== "all") {
      result = result.filter((r) => r.event_type === eventFilter);
    }
    return result.sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  }, [runs, eventFilter]);

  const grouped = useMemo(() => {
    const groups = new Map<string, typeof filtered>();
    filtered.forEach((run) => {
      const dateKey = new Date(run.created_at).toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      });
      if (!groups.has(dateKey)) groups.set(dateKey, []);
      groups.get(dateKey)!.push(run);
    });
    return groups;
  }, [filtered]);

  const filterOptions = [
    { value: "all", label: "All" },
    ...events.map((e) => ({ value: e.value, label: e.label })),
  ];

  if (runsIsLoading) return <QueryLoading />;
  if (runsError) return <QueryError error={runsError} refetch={runsRefetch} />;

  return (
    <div className="space-y-4 py-4">
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {filterOptions.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setEventFilter(opt.value)}
            className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
              eventFilter === opt.value
                ? "text-primary-foreground"
                : "bg-secondary text-secondary-foreground"
            }`}
            style={
              eventFilter === opt.value
                ? { backgroundColor: "hsl(var(--primary))" }
                : undefined
            }
          >
            {opt.label}
          </button>
        ))}
      </div>

      {Array.from(grouped.entries()).map(([dateLabel, dateRuns]) => (
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
                    `/athletes/${run.athlete_id}/runs/${run.run_id}`
                  )
                }
                className="flex w-full items-center justify-between rounded-xl border border-border bg-card px-4 py-3 text-left"
              >
                <div>
                  <div className="text-sm font-semibold text-foreground">
                    {athleteMap.get(run.athlete_id) ?? "Unknown"}
                  </div>
                  <div className="mt-0.5 text-xs text-muted-foreground">
                    <span className="rounded bg-secondary px-1.5 py-0.5 font-medium text-secondary-foreground">
                      {run.event_type.replace("_", " ")}
                    </span>
                  </div>
                </div>
                <div className="text-right text-xs text-muted-foreground">
                  {new Date(run.created_at).toLocaleTimeString("en-US", {
                    hour: "numeric",
                    minute: "2-digit",
                  })}
                </div>
              </button>
            ))}
          </div>
        </div>
      ))}

      {filtered.length === 0 && (
        <p className="py-8 text-center text-sm text-muted-foreground">
          No runs found.
        </p>
      )}
    </div>
  );
}