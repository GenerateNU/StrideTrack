import { useState } from "react";
import EventSelector from "@/components/events/EventSelector";
import type { EventTypeEnum } from "@/types/event.types";
import type {
  AmountMode,
  EventHistoryFilters,
} from "@/types/eventHistoryFilters.types";

const COUNT_OPTIONS = [5, 10, 20, 50];

interface EventHistoryFilterBarProps {
  athleteId: string;
  onApply: (filters: EventHistoryFilters) => void;
}

export default function EventHistoryFilterBar({
  athleteId,
  onApply,
}: EventHistoryFilterBarProps) {
  const [eventType, setEventType] = useState<EventTypeEnum | null>(null);
  const [amountMode, setAmountMode] = useState<AmountMode>("count");
  const [limit, setLimit] = useState<number>(10);
  const [dateFrom, setDateFrom] = useState<string | null>(null);
  const [dateTo, setDateTo] = useState<string | null>(null);

  const canSubmit = eventType !== null;

  function handleApply() {
    if (!canSubmit) return;
    onApply({
      athleteId,
      eventType,
      amountMode,
      limit,
      dateFrom: amountMode === "dateRange" ? dateFrom : null,
      dateTo: amountMode === "dateRange" ? dateTo : null,
    });
  }

  return (
    <div className="flex flex-wrap items-end gap-3">
      {/* Event Type */}
      <div className="flex-1 min-w-40">
        <EventSelector value={eventType} onChange={setEventType} />
      </div>

      {/* Amount Mode Toggle */}
      <div>
        <p className="block text-sm font-medium text-foreground mb-2">
          Filter By
        </p>
        <div className="flex rounded-xl border border-input overflow-hidden">
          <button
            type="button"
            onClick={() => setAmountMode("count")}
            className={`px-4 py-2.5 text-sm font-medium transition-colors ${
              amountMode === "count"
                ? "bg-primary text-primary-foreground"
                : "bg-card text-muted-foreground hover:bg-secondary"
            }`}
          >
            Last N runs
          </button>
          <button
            type="button"
            onClick={() => setAmountMode("dateRange")}
            className={`px-4 py-2.5 text-sm font-medium transition-colors ${
              amountMode === "dateRange"
                ? "bg-primary text-primary-foreground"
                : "bg-card text-muted-foreground hover:bg-secondary"
            }`}
          >
            Date range
          </button>
        </div>
      </div>

      {/* Count picker or date inputs */}
      {amountMode === "count" ? (
        <div>
          <p className="block text-sm font-medium text-foreground mb-2">
            Number of runs
          </p>
          <div className="flex gap-1">
            {COUNT_OPTIONS.map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => setLimit(n)}
                className={`w-12 rounded-xl border py-2.5 text-sm font-medium transition-colors ${
                  limit === n
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-input bg-card text-muted-foreground hover:bg-secondary"
                }`}
              >
                {n}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex items-end gap-2">
          <div>
            <p className="block text-sm font-medium text-foreground mb-2">
              From
            </p>
            <input
              type="date"
              value={dateFrom ?? ""}
              onChange={(e) => setDateFrom(e.target.value || null)}
              className="appearance-none rounded-xl border border-input bg-card px-4 py-2.5 text-sm font-medium text-foreground focus:outline-none"
            />
          </div>
          <div>
            <p className="block text-sm font-medium text-foreground mb-2">To</p>
            <input
              type="date"
              value={dateTo ?? ""}
              onChange={(e) => setDateTo(e.target.value || null)}
              className="appearance-none rounded-xl border border-input bg-card px-4 py-2.5 text-sm font-medium text-foreground focus:outline-none"
            />
          </div>
        </div>
      )}

      {/* Apply button */}
      <button
        type="button"
        onClick={handleApply}
        disabled={!canSubmit}
        className="rounded-xl bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition-opacity disabled:opacity-50"
      >
        Apply
      </button>
    </div>
  );
}
