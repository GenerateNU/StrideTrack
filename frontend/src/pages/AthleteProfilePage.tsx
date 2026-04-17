import { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useGetAllAthletes, useDeleteAthlete } from "@/hooks/useAthletes.hooks";
import { useGetAllRuns, useDeleteRun } from "@/hooks/useRuns.hooks";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import { DeleteConfirmModal } from "@/components/ui/DeleteConfirmModal";
import { EditAthleteModal } from "@/components/athletes/EditAthleteModal";
import { EditRunModal } from "@/components/runs/EditRunModal";
import type { EventTypeEnum } from "@/types/event.types";
import {
  ArrowLeft,
  Activity,
  Calendar,
  Pencil,
  Trash2,
  Search,
} from "lucide-react";
import EventHistoryFilterBar from "@/components/charts/history/EventHistoryFilterBar";
import { EventHistoryChart } from "@/components/charts/history/EventHistoryChart";
import type { EventHistoryFilters } from "@/types/eventHistoryFilters.types";
import { AverageReactionTimeCard } from "@/components/charts/reaction-time/AverageReactionTimeCard";
import { EVENT_DISPLAY_NAMES } from "@/hooks/useEvents.hooks";

function nameToHue(name: string): number {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash) % 360;
}

function formatEventType(eventType: string): string {
  return (
    EVENT_DISPLAY_NAMES[eventType as EventTypeEnum] ??
    eventType.replace(/_/g, " ")
  );
}

export default function AthleteProfilePage() {
  const { athleteId } = useParams<{ athleteId: string }>();
  const navigate = useNavigate();
  const { athletes, athletesIsLoading, athletesError, athletesRefetch } =
    useGetAllAthletes();
  const { runs, runsIsLoading, runsError, runsRefetch } = useGetAllRuns();
  const { deleteAthlete, deleteAthleteIsLoading } = useDeleteAthlete();
  const { deleteRun, deleteRunIsLoading } = useDeleteRun();

  const [tab, setTab] = useState<"summary" | "runs" | "trends">("summary");
  const [eventHistoryFilters, setEventHistoryFilters] =
    useState<EventHistoryFilters | null>(null);
  const [editAthleteOpen, setEditAthleteOpen] = useState(false);
  const [deleteAthleteOpen, setDeleteAthleteOpen] = useState(false);
  const [deleteRunId, setDeleteRunId] = useState<string | null>(null);
  const [editRun, setEditRun] = useState<(typeof athleteRuns)[0] | null>(null);
  const [search, setSearch] = useState("");
  const [eventFilter, setEventFilter] = useState<string>("all");

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

  const filteredRuns = useMemo(() => {
    return athleteRuns.filter((r) => {
      const matchesSearch =
        search.trim() === "" ||
        (r.name ?? "").toLowerCase().includes(search.toLowerCase()) ||
        formatEventType(r.event_type)
          .toLowerCase()
          .includes(search.toLowerCase());
      const matchesEvent =
        eventFilter === "all" || r.event_type === eventFilter;
      return matchesSearch && matchesEvent;
    });
  }, [athleteRuns, search, eventFilter]);

  const eventTypes = useMemo(
    () => Array.from(new Set(athleteRuns.map((r) => r.event_type))),
    [athleteRuns]
  );

  const groupedRuns = useMemo(() => {
    const groups = new Map<string, typeof filteredRuns>();
    filteredRuns.forEach((run) => {
      const dateKey = new Date(run.created_at).toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      });
      if (!groups.has(dateKey)) groups.set(dateKey, []);
      groups.get(dateKey)!.push(run);
    });
    return groups;
  }, [filteredRuns]);

  const latestRun = athleteRuns[0] ?? null;

  if (athletesIsLoading || runsIsLoading) return <QueryLoading />;
  if (athletesError)
    return <QueryError error={athletesError} refetch={athletesRefetch} />;
  if (runsError) return <QueryError error={runsError} refetch={runsRefetch} />;

  if (!athlete) {
    return (
      <div className="py-12 text-center text-sm text-muted-foreground">
        Athlete not found.
      </div>
    );
  }

  const hue = nameToHue(athlete.name);

  const handleDeleteAthlete = async () => {
    await deleteAthlete(athlete.athlete_id);
    navigate("/");
  };

  const handleDeleteRun = async () => {
    if (!deleteRunId) return;
    await deleteRun(deleteRunId);
    setDeleteRunId(null);
  };

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
        <div className="flex-1">
          <h2 className="text-xl font-bold text-foreground">{athlete.name}</h2>
          <p className="text-xs text-muted-foreground">
            {[
              athlete.height_in ? `${athlete.height_in}"` : null,
              athlete.weight_lbs ? `${athlete.weight_lbs} lbs` : null,
              `${athleteRuns.length} recording${athleteRuns.length !== 1 ? "s" : ""}`,
            ]
              .filter(Boolean)
              .join(" · ")}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setEditAthleteOpen(true)}
            className="rounded-lg p-2 text-muted-foreground transition-colors hover:text-foreground hover:bg-secondary"
          >
            <Pencil className="h-4 w-4" />
          </button>
          <button
            onClick={() => setDeleteAthleteOpen(true)}
            className="rounded-lg p-2 text-muted-foreground transition-colors hover:text-destructive hover:bg-secondary"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-5 flex gap-1 rounded-xl bg-secondary p-1">
        {(["summary", "runs", "trends"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 rounded-lg py-2.5 text-xs font-semibold transition-colors ${
              tab === t
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground"
            }`}
          >
            {t === "summary" ? "Summary" : t === "runs" ? "Runs" : "Trends"}
          </button>
        ))}
      </div>

      {tab === "summary" && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="rounded-2xl border border-border bg-card p-4 shadow-sm shadow-foreground/[0.02]">
              <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-secondary">
                <Activity className="h-4 w-4 text-foreground" />
              </div>
              <div className="text-2xl font-bold text-foreground">
                {athleteRuns.length}
              </div>
              <div className="text-xs text-muted-foreground">
                Total Recordings
              </div>
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
            <div className="col-span-2 sm:col-span-1">
              <AverageReactionTimeCard athleteId={athleteId!} />
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-4 shadow-sm shadow-foreground/[0.02]">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Latest Recording
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
                    {formatEventType(latestRun.event_type)}
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
                No events recorded yet.
              </p>
            )}
          </div>
        </div>
      )}

      {tab === "runs" && (
        <div className="space-y-4">
          {/* Search bar */}
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search runs..."
              className="w-full rounded-xl border border-input bg-card py-2.5 pl-9 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
            />
          </div>

          {/* Event type filter — dropdown on mobile, pills on desktop */}
          {eventTypes.length > 1 && (
            <>
              {/* Mobile dropdown */}
              <div className="sm:hidden relative">
                <select
                  value={eventFilter}
                  onChange={(e) => setEventFilter(e.target.value)}
                  className="w-full appearance-none rounded-xl border border-input bg-card py-2.5 pl-4 pr-10 text-sm font-medium text-foreground focus:outline-none"
                >
                  <option value="all">All Events</option>
                  {eventTypes.map((et) => (
                    <option key={et} value={et}>
                      {formatEventType(et)}
                    </option>
                  ))}
                </select>
                <svg
                  className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>

              {/* Desktop pills */}
              <div className="hidden sm:flex gap-2 flex-wrap">
                <button
                  onClick={() => setEventFilter("all")}
                  className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                    eventFilter === "all"
                      ? "bg-foreground text-background"
                      : "bg-secondary text-muted-foreground hover:text-foreground"
                  }`}
                >
                  All
                </button>
                {eventTypes.map((et) => (
                  <button
                    key={et}
                    onClick={() => setEventFilter(et)}
                    className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                      eventFilter === et
                        ? "bg-foreground text-background"
                        : "bg-secondary text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {formatEventType(et)}
                  </button>
                ))}
              </div>
            </>
          )}

          {Array.from(groupedRuns.entries()).map(([dateLabel, dateRuns]) => (
            <div key={dateLabel}>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {dateLabel}
              </p>
              <div className="space-y-2">
                {dateRuns.map((run) => (
                  <div
                    key={run.run_id}
                    className="flex w-full items-center justify-between rounded-2xl border border-border bg-card px-4 py-3 shadow-sm shadow-foreground/[0.02]"
                  >
                    <button
                      onClick={() =>
                        navigate(`/athletes/${athleteId}/runs/${run.run_id}`)
                      }
                      className="flex flex-1 items-center gap-3 text-left"
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-secondary">
                        <Activity className="h-4 w-4 text-foreground" />
                      </div>
                      <div>
                        <span className="text-sm font-medium text-foreground">
                          {run.name ?? formatEventType(run.event_type)}
                        </span>
                        <p className="text-[10px] text-muted-foreground">
                          {run.event_type === "hurdles_partial" &&
                          run.target_event
                            ? `Partial Hurdles (${formatEventType(run.target_event)})`
                            : formatEventType(run.event_type)}
                          {run.elapsed_ms
                            ? ` · ${(run.elapsed_ms / 1000).toFixed(1)}s`
                            : ""}
                        </p>
                      </div>
                    </button>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">
                        {new Date(run.created_at).toLocaleTimeString("en-US", {
                          hour: "numeric",
                          minute: "2-digit",
                        })}
                      </span>
                      <button
                        onClick={() => setEditRun(run)}
                        className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:text-foreground hover:bg-secondary"
                      >
                        <Pencil className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => setDeleteRunId(run.run_id)}
                        className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:text-destructive hover:bg-secondary"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {filteredRuns.length === 0 && (
            <div className="rounded-2xl border border-dashed border-border p-12 text-center">
              <p className="text-sm font-medium text-muted-foreground">
                {athleteRuns.length === 0
                  ? "No events recorded yet."
                  : "No runs match your search."}
              </p>
            </div>
          )}
        </div>
      )}

      {tab === "trends" && (
        <div className="space-y-4">
          <EventHistoryFilterBar
            athleteId={athleteId!}
            onApply={(filters) => setEventHistoryFilters(filters)}
          />
          {eventHistoryFilters && (
            <EventHistoryChart filters={eventHistoryFilters} enabled={true} />
          )}
        </div>
      )}

      {/* Modals */}
      <EditAthleteModal
        open={editAthleteOpen}
        onClose={() => setEditAthleteOpen(false)}
        athlete={athlete}
      />

      {editRun && (
        <EditRunModal
          open={!!editRun}
          onClose={() => setEditRun(null)}
          run={{ ...editRun, event_type: editRun.event_type as EventTypeEnum }}
        />
      )}

      <DeleteConfirmModal
        open={deleteAthleteOpen}
        onClose={() => setDeleteAthleteOpen(false)}
        onConfirm={handleDeleteAthlete}
        isLoading={deleteAthleteIsLoading}
        title="Delete Athlete"
        description={`Are you sure you want to delete ${athlete.name}? This will permanently remove the athlete and all their runs.`}
      />

      <DeleteConfirmModal
        open={!!deleteRunId}
        onClose={() => setDeleteRunId(null)}
        onConfirm={handleDeleteRun}
        isLoading={deleteRunIsLoading}
        title="Delete Run"
        description="Are you sure you want to delete this run? This action cannot be undone."
      />
    </div>
  );
}
