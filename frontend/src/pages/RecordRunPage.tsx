import { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { AthleteSelector } from "@/components/athletes/AthleteSelector";
import EventSelector from "@/components/events/EventSelector";
import { useCreateRun } from "@/hooks/useCreateRun.hooks";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useEvents } from "@/hooks/useEvents";
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

  // Data hooks — used for display names on recording screen
  const { athletes } = useGetAllAthletes();
  const events = useEvents();
  const { createRun, createRunIsLoading } = useCreateRun();

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
  const navigate = useNavigate();
  const handleSave = async () => {
    if (!athleteId || !eventType) return;
    try {
      const result = await createRun({
        athlete_id: athleteId,
        event_type: eventType,
        elapsed_ms: elapsedMs,
      });
      navigate(`/athletes/${athleteId}/runs/${result.run_id}`);
    } catch (error) {
      console.error("Failed to save run:", error);
    }
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
          <h1 className="text-2xl font-bold text-foreground">New Run</h1>
          <p className="text-sm text-muted-foreground mt-1 mb-10">
            Select an athlete and event to begin recording
          </p>

          <div className="space-y-6">
            <AthleteSelector value={athleteId} onChange={setAthleteId} />
            <EventSelector value={eventType} onChange={setEventType} />

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
            disabled={createRunIsLoading}
            className="px-10 py-4 rounded-2xl font-semibold text-lg cursor-pointer transition-colors disabled:opacity-50"
            style={{
              backgroundColor: "hsl(var(--primary))",
              color: "hsl(var(--primary-foreground))",
            }}
          >
            {createRunIsLoading ? "Saving..." : "Save"}
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
