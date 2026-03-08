import { useState, useRef, useCallback } from "react";
import { AthleteSelector } from "@/components/athletes/AthleteSelector";
import EventSelector from "@/components/events/EventSelector";
import { useCreateRun } from "@/hooks/useCreateRun.hooks";
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

  // POST hook for creating a run
  const { mutate: createRun, isPending } = useCreateRun();

  // Both selections required to proceed
  const canProceed = athleteId !== null && eventType !== null;

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
    return (
      <div className="min-h-screen bg-background px-6 py-10">
        <div className="max-w-md mx-auto">
          <h1 className="text-2xl font-bold text-foreground mb-1">New Run</h1>
          <p className="text-sm text-muted-foreground mb-10">
            Select an athlete and event to begin recording
          </p>

          <div className="space-y-6">
            <AthleteSelector value={athleteId} onChange={setAthleteId} />

            <div>
              <label className="block text-sm font-medium mb-2">Event</label>
              <EventSelector value={eventType} onChange={setEventType} />
            </div>

            <button
              onClick={() => setScreen("recording")}
              disabled={!canProceed}
              className={`w-full py-3.5 rounded-xl font-semibold text-lg transition-all ${
                canProceed
                  ? "cursor-pointer opacity-100"
                  : "cursor-not-allowed opacity-40"
              }`}
              style={{
                backgroundColor: canProceed
                  ? "hsl(var(--primary))"
                  : "hsl(var(--primary))",
                color: "hsl(var(--primary-foreground))",
              }}
            >
              Continue
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Recording Screen ──
  return (
    <div className="min-h-screen bg-background flex flex-col items-center px-6 pt-16">
      {/* Header info — athlete name and event would go here */}
      <h1 className="text-2xl font-bold text-foreground mb-1">New Run</h1>
      <p className="text-sm text-muted-foreground mb-12">Recording Session</p>

      {/* Timer circle — matches artifact style with subtle border */}
      <div
        className="w-56 h-56 rounded-full flex flex-col items-center justify-center transition-all"
        style={{
          border: `4px solid ${
            isRunning
              ? "hsl(var(--destructive))"
              : "hsl(var(--border))"
          }`,
          boxShadow: isRunning
            ? "0 0 24px hsl(var(--destructive) / 0.15)"
            : "0 4px 20px hsl(var(--foreground) / 0.06)",
        }}
      >
        <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          {isRunning ? "Recording" : isStopped ? "Stopped" : "Ready"}
        </span>
        <span
          className="text-5xl font-bold text-foreground mt-1"
          style={{ fontVariantNumeric: "tabular-nums" }}
        >
          {formatTime(elapsedMs)}
        </span>
      </div>

      {/* Status pill — similar to "Waiting for Sensor" in the artifact */}
      <div
        className="mt-6 inline-flex items-center gap-2 px-4 py-1.5 rounded-full"
        style={{
          backgroundColor: isRunning
            ? "hsl(142 71% 45% / 0.1)"
            : "hsl(var(--muted))",
        }}
      >
        <div
          className="w-2 h-2 rounded-full"
          style={{
            backgroundColor: isRunning
              ? "hsl(142, 71%, 45%)"
              : "hsl(var(--muted-foreground))",
          }}
        />
        <span
          className="text-xs font-medium"
          style={{
            color: isRunning
              ? "hsl(142, 71%, 35%)"
              : "hsl(var(--muted-foreground))",
          }}
        >
          {isRunning ? "Connected" : "Waiting for Sensor"}
        </span>
      </div>

      {/* Start/Stop button — large and prominent like the artifact */}
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
            className="px-10 py-4 rounded-2xl font-semibold text-lg cursor-pointer transition-colors"
            style={{
              border: "1px solid hsl(var(--border))",
              color: "hsl(var(--foreground))",
              backgroundColor: "transparent",
            }}
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
          Change Selection
        </button>
      )}
    </div>
  );
}