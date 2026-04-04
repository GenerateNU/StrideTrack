import { useState } from "react";
import { X } from "lucide-react";
import { useUpdateRun } from "@/hooks/useRuns.hooks";
import EventSelector from "@/components/events/EventSelector";
import type { EventTypeEnum } from "@/types/event.types";

interface Run {
  run_id: string;
  event_type: EventTypeEnum;
  name?: string | null;
  target_event?: string | null;
}

interface EditRunModalProps {
  open: boolean;
  onClose: () => void;
  run: Run;
}

export function EditRunModal({ open, onClose, run }: EditRunModalProps) {
  const { updateRun, updateRunIsLoading, updateRunError } = useUpdateRun();
  const [eventType, setEventType] = useState<EventTypeEnum>(run.event_type);
  const [name, setName] = useState(run.name ?? "");
  const [targetEvent, setTargetEvent] = useState(run.target_event ?? "");

  const handleSubmit = async () => {
    try {
      await updateRun({
        runId: run.run_id,
        payload: {
          event_type: eventType,
          name: name.trim() || null,
          ...(eventType === "hurdles_partial" && { target_event: targetEvent || null }),
          ...(eventType !== "hurdles_partial" && { target_event: null }),
        },
      });
      onClose();
    } catch {
      // error captured in updateRunError
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-foreground/20 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative z-10 mx-4 w-full max-w-sm rounded-2xl border border-border bg-card p-6 shadow-xl">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-lg font-bold text-foreground">Edit Run</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-muted-foreground transition-colors hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4">
          <EventSelector
            value={eventType}
            onChange={(v) => {
              if (v) {
                setEventType(v);
                if (v !== "hurdles_partial") setTargetEvent("");
              }
            }}
          />

          {eventType === "hurdles_partial" && (
            <div>
              <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-foreground">
              </label>
              <select
                value={targetEvent}
                onChange={(e) => setTargetEvent(e.target.value)}
                className="w-full appearance-none rounded-xl border border-input bg-background px-4 py-2.5 text-sm text-foreground focus:outline-none"
              >
                <option value="">Select target event</option>
                <option value="hurdles_60m">60m Hurdles</option>
                <option value="hurdles_100m">100m Hurdles</option>
                <option value="hurdles_110m">110m Hurdles</option>
                <option value="hurdles_400m">400m Hurdles</option>
              </select>
            </div>
          )}

          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-foreground">
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Morning sprint session"
              className="w-full rounded-xl border border-input bg-background px-4 py-2.5 text-sm placeholder:text-muted-foreground focus:outline-none"
            />
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!eventType || (eventType === "hurdles_partial" && !targetEvent) || updateRunIsLoading}
          className="mt-6 w-full rounded-xl py-3.5 text-sm font-semibold transition-all disabled:opacity-40"
          style={{
            backgroundColor: "hsl(var(--primary))",
            color: "hsl(var(--primary-foreground))",
          }}
        >
          {updateRunIsLoading ? "Saving..." : "Save Changes"}
        </button>

        {updateRunError && (
          <p className="mt-2 text-center text-xs text-destructive">
            Failed to update run. Please try again.
          </p>
        )}
      </div>
    </div>
  );
}
