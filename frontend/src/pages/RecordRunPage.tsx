import { useState, useRef, useCallback } from "react";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useEvents } from "@/hooks/useEvents";
import { useCreateRun } from "@/hooks/useCreateRun.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { ChevronDown } from "lucide-react";

import type { EventTypeEnum } from "@/types/event.types";

export default function RecordingPage() {
  // Which screen we're on — setup or recording
  const [screen, setScreen] = useState<"setup" | "recording">("setup");

  // Setup selections
  const [athleteId, setAthleteId] = useState<string | null>(null);
  const [eventType, setEventType] = useState<EventTypeEnum | null>(null);

  // Timer state
  const [elapsedMs, setElapsedMs] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [isStopped, setIsStopped] = useState(false);

  // Refs persist across re-renders without causing re-renders
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number>(0);

  // Data hooks
  const { athletes, athletesIsLoading } = useGetAllAthletes();
  const events = useEvents();
  const { mutate: createRun, isPending } = useCreateRun();

  // Both selections required to proceed
  const canProceed = athleteId !== null && eventType !== null;

  // Get display names for the recording screen header
  const selectedAthlete = athletes.find((a) => a.athlete_id === athleteId);
  const selectedEvent = events.find((e) => e.value === eventType);

  // Start the timer — captures real start time, updates every 10ms
  const startTimer = useCallback(() => {
    startTimeRef.current = Date.now();
    setIsRunning(true);
    setIsStopped(false);
    setElapsedMs(0);
    intervalRef.current = setInterval(() => {
      setElapsedMs(Date.now() - startTimeRef.current);
    }, 10);
  }, []);

  // Stop the timer — clears interval, takes final measurement
  const stopTimer = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setElapsedMs(Date.now() - startTimeRef.current);
    setIsRunning(false);
    setIsStopped(true);
  }, []);

  // Save the run to the database, then reset
  const handleSave = () => {
    if (!athleteId || !eventType) return;
    createRun(
      { athlete_id: athleteId, event_type: eventType, elapsed_ms: elapsedMs },
      { onSuccess: () => resetAll() }
    );
  };

  // Reset everything back to setup screen — used by both Delete and Save
  const resetAll = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setElapsedMs(0);
    setIsRunning(false);
    setIsStopped(false);
    setScreen("setup");
  };

  // Format milliseconds as M:SS.cc (centisecond precision)
  const formatTime = (ms: number) => {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const centiseconds = Math.floor((ms % 1000) / 10);
    return `${minutes}:${seconds.toString().padStart(2, "0")}.${centiseconds.toString().padStart(2, "0")}`;
  };

  // ── Setup Screen ──
  if (screen === "setup") {
    if (athletesIsLoading) return <QueryLoading />;

    return (
      <div className="min-h-screen bg-background px-6 py-10">
        <div className="max-w-md mx-auto">
          <h1 className="text-2xl font-bold text-foreground">New Run</h1>
          <p className="text-sm text-muted-foreground mt-1 mb-10">
            Select an athlete and event to begin recording
          </p>

          {/* Athlete selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-foreground mb-2">
              Athlete
            </label>
            <div className="relative">
              <select
                value={athleteId ?? ""}
                onChange={(e) => setAthleteId(e.target.value || null)}
                className="w-full appearance-none rounded-xl border border-border bg-card px-4 py-3.5 pr-10 text-sm font-medium text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
              >
                <option value="" disabled>
                  Select an athlete
                </option>
                {athletes.map((athlete) => (
                  <option key={athlete.athlete_id} value={athlete.athlete_id}>
                    {athlete.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            </div>
          </div>

          {/* Event selector */}
          <div className="mb-10">
            <label className="block text-sm font-medium text-foreground mb-2">
              Event
            </label>
            <div className="relative">
              <select
                value={eventType ?? ""}
                onChange={(e) =>
                  setEventType((e.target.value as EventTypeEnum) || null)
                }
                className="w-full appearance-none rounded-xl border border-border bg-card px-4 py-3.5 pr-10 text-sm font-medium text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
              >
                <option value="" disabled>
                  Select an event
                </option>
                {events.map((event) => (
                  <option key={event.value} value={event.value}>
                    {event.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            </div>
          </div>

          {/* Continue button */}
          <button
            onClick={() => setScreen("recording")}
            disabled={!canProceed}
            className={`w-full py-3.5 rounded-xl font-semibold text-base transition-all ${
              canProceed
                ? "cursor-pointer opacity-100"
                : "cursor-not-allowed opacity-40"
            }`}
            style={{
              backgroundColor: "hsl(var(--primary))",
              color: "hsl(var(--primary-foreground))",
            }}
          >
            Continue
          </button>
        </div>
      </div>
    );
  }

  // ── Recording Screen ──
  return (
    <div className="min-h-screen bg-background flex flex-col items-center px-6 pt-14">
      {/* Header */}
      <h1 className="text-2xl font-bold text-foreground">New Run</h1>
      <p className="text-sm text-muted-foreground mt-1 mb-10">
        {selectedAthlete?.name} · {selectedEvent?.label}
      </p>

      {/* Timer circle */}
      <div
        className="w-56 h-56 rounded-full flex flex-col items-center justify-center bg-card"
        style={{
          border: `4px solid ${
            isRunning
              ? "hsl(var(--destructive))"
              : isStopped
                ? "hsl(var(--primary))"
                : "hsl(var(--border))"
          }`,
          boxShadow: "0 2px 16px hsl(var(--foreground) / 0.04)",
        }}
      >
        <span className="text-[11px] font-semibold uppercase tracking-[0.15em] text-muted-foreground">
          {isRunning ? "Recording" : isStopped ? "Stopped" : "Ready"}
        </span>
        <span
          className="text-5xl font-bold text-foreground mt-1"
          style={{ fontVariantNumeric: "tabular-nums" }}
        >
          {formatTime(elapsedMs)}
        </span>
      </div>

      {/* Start/Stop button — hidden after stopping */}
      {!isStopped && (
        <button
          onClick={isRunning ? stopTimer : startTimer}
          className="mt-10 w-56 py-4 rounded-2xl font-semibold text-xl cursor-pointer transition-all"
          style={{
            backgroundColor: isRunning
              ? "hsl(var(--destructive))"
              : "hsl(var(--primary))",
            color: "hsl(var(--primary-foreground))",
          }}
        >
          {isRunning ? "Stop" : "Start"}
        </button>
      )}

      {/* Save/Delete buttons — shown after stopping */}
      {isStopped && (
        <div className="mt-10 flex gap-4">
          <button
            onClick={resetAll}
            className="px-10 py-4 rounded-2xl font-semibold text-lg cursor-pointer transition-colors border border-border text-foreground bg-card"
          >
            Delete
          </button>
          <button
            onClick={handleSave}
            disabled={isPending}
            className="px-10 py-4 rounded-2xl font-semibold text-lg cursor-pointer transition-colors disabled:opacity-50"
            style={{
              backgroundColor: "hsl(var(--primary))",
              color: "hsl(var(--primary-foreground))",
            }}
          >
            {isPending ? "Saving..." : "Save"}
          </button>
        </div>
      )}

      {/* Change selection link — only before starting */}
      {!isRunning && !isStopped && (
        <button
          onClick={() => setScreen("setup")}
          className="mt-5 text-sm font-medium cursor-pointer"
          style={{ color: "hsl(var(--primary))" }}
        >
          Change Event
        </button>
      )}
    </div>
  );
}
