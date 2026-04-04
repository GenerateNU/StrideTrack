import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useGetAllRuns } from "@/hooks/useRuns.hooks";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useEvents } from "@/hooks/useEvents.hooks";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import { ChevronDown } from "lucide-react";

type DateRange = "all" | "today" | "week" | "month";

function getDateRangeStart(range: DateRange): Date | null {
  if (range === "all") return null;
  const now = new Date();
  if (range === "today") {
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
  }
  if (range === "week") {
    const d = new Date(now);
    d.setDate(d.getDate() - 7);
    return d;
  }
  const d = new Date(now);
  d.setDate(d.getDate() - 30);
  return d;
}

export default function HistoryPage() {
  const navigate = useNavigate();
  const { runs, runsIsLoading, runsError, runsRefetch } = useGetAllRuns();
  const {
    athletes,
    athletesIsLoading: athletesLoading,
    athletesError,
    athletesRefetch,
  } = useGetAllAthletes();
  const events = useEvents();
  const [eventFilter, setEventFilter] = useState<string>("all");
  const [dateRange, setDateRange] = useState<DateRange>("all");

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
    const rangeStart = getDateRangeStart(dateRange);
    if (rangeStart) {
      result = result.filter(
        (r) => new Date(r.created_at).getTime() >= rangeStart.getTime()
      );
    }
    return result.sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  }, [runs, eventFilter, dateRange]);

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

  const dateFilterOptions: { value: DateRange; label: string }[] = [
    { value: "all", label: "All Time" },
    { value: "today", label: "Today" },
    { value: "week", label: "This Week" },
    { value: "month", label: "This Month" },
  ];

  if (runsIsLoading || athletesLoading) return <QueryLoading />;
  if (athletesError)
    return <QueryError error={athletesError} refetch={athletesRefetch} />;
  if (runsError) return <QueryError error={runsError} refetch={runsRefetch} />;

  return (
    <div className="space-y-4 py-4">
      {/* Filters row */}
      <div className="flex items-center gap-3">
        {/* Event type dropdown */}
        <div className="relative flex-1">
          <select
            value={eventFilter}
            onChange={(e) => setEventFilter(e.target.value)}
            className="w-full appearance-none rounded-xl border border-input bg-card py-2.5 pl-4 pr-10 text-sm font-medium text-foreground focus:outline-none"
          >
            <option value="all">All Events</option>
            {events.map((e) => (
              <option key={e.value} value={e.value}>
                {e.label}
              </option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        </div>

        {/* Date range dropdown */}
        <div className="relative flex-1">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as DateRange)}
            className="w-full appearance-none rounded-xl border border-input bg-card py-2.5 pl-4 pr-10 text-sm font-medium text-foreground focus:outline-none"
          >
            {dateFilterOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        </div>
      </div>

      {/* Active filter indicator */}
      {(eventFilter !== "all" || dateRange !== "all") && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">
            {filtered.length} result{filtered.length !== 1 ? "s" : ""}
          </span>
          <button
            onClick={() => {
              setEventFilter("all");
              setDateRange("all");
            }}
            className="text-xs font-medium"
            style={{ color: "hsl(var(--primary))" }}
          >
            Clear filters
          </button>
        </div>
      )}

      {/* Grouped runs */}
      {Array.from(grouped.entries()).map(([dateLabel, dateRuns]) => (
        <div key={dateLabel}>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            {dateLabel}
          </p>
          <div className="space-y-2">
            {dateRuns.map((run) => (
              <button
                key={run.run_id}
                onClick={() =>
                  navigate(`/athletes/${run.athlete_id}/runs/${run.run_id}`)
                }
                className="flex w-full items-center justify-between rounded-2xl border border-border bg-card px-4 py-3 text-left shadow-sm shadow-foreground/[0.02]"
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
                <div className="text-right">
                  <div className="text-xs text-muted-foreground">
                    {new Date(run.created_at).toLocaleTimeString("en-US", {
                      hour: "numeric",
                      minute: "2-digit",
                    })}
                  </div>
                  {run.elapsed_ms && (
                    <div className="text-[10px] text-muted-foreground">
                      {(run.elapsed_ms / 1000).toFixed(1)}s
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      ))}

      {filtered.length === 0 && (
        <div className="py-12 text-center">
          <p className="text-sm text-muted-foreground">No runs found.</p>
          {(eventFilter !== "all" || dateRange !== "all") && (
            <button
              onClick={() => {
                setEventFilter("all");
                setDateRange("all");
              }}
              className="mt-2 text-xs font-medium"
              style={{ color: "hsl(var(--primary))" }}
            >
              Clear filters
            </button>
          )}
        </div>
      )}
    </div>
  );
}
