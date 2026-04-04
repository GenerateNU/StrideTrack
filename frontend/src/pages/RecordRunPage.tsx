import { useState, useRef, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { AthleteSelector } from "@/components/athletes/AthleteSelector";
import EventSelector from "@/components/events/EventSelector";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useEvents } from "@/hooks/useEvents.hooks";
import { useBle } from "@/hooks/useBle.hooks";
import api from "@/lib/api";
import type { EventTypeEnum } from "@/types/event.types";

export default function RecordRunPage() {
  const queryClient = useQueryClient();

  // Which screen we're on — setup or recording
  const [screen, setScreen] = useState<"setup" | "recording">("setup");

  // Setup selections
  const [athleteId, setAthleteId] = useState<string | null>(null);
  const [eventType, setEventType] = useState<EventTypeEnum | null>(null);

  // Timer state
  const [elapsedMs, setElapsedMs] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [isStopped, setIsStopped] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Refs persist across re-renders without causing re-renders
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number>(0);
  const stopTimeRef = useRef<number>(0);

  // Data hooks — used for display names on recording screen
  const { athletes } = useGetAllAthletes();
  const events = useEvents();
  // BLE hook
  const {
    bleIsAvailable,
    bleIsConnected,
    bleIsScanning,
    bleConnect,
    bleDisconnect,
    bleDataBuffer,
    bleClearBuffer,
  } = useBle();

  // Both selections required to proceed
  const canProceed = athleteId !== null && eventType !== null;

  // Get display names for the recording screen header
  const selectedAthlete = athletes.find((a) => a.athlete_id === athleteId);
  const selectedEvent = events.find((e) => e.value === eventType);

  // Start the timer — connects BLE first, then captures real start time
  const startTimer = useCallback(async () => {
    setIsConnecting(true);
    try {
      await bleConnect();
    } catch (error) {
      console.error("BLE connection failed:", error);
      setIsConnecting(false);
      return;
    }
    setIsConnecting(false);

    startTimeRef.current = Date.now();
    setIsRunning(true);
    setIsStopped(false);
    setElapsedMs(0);
    intervalRef.current = setInterval(() => {
      setElapsedMs(Date.now() - startTimeRef.current);
    }, 10);
  }, [bleConnect]);

  // Stop the timer — clears interval, takes final measurement, disconnects BLE
  const stopTimer = useCallback(async () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    stopTimeRef.current = Date.now();
    setElapsedMs(stopTimeRef.current - startTimeRef.current);
    setIsRunning(false);
    setIsStopped(true);
    await bleDisconnect();
  }, [bleDisconnect]);

  // Save the run to the database, then reset
  const handleSave = async () => {
    if (!athleteId || !eventType) return;

    setIsSaving(true);
    try {
      // Buffer only contains rows received between connect and disconnect
      const rows = bleDataBuffer();

      const csvLines = ["Time,Force_Foot1,Force_Foot2"];
      for (const row of rows) {
        csvLines.push(`${row.time},${row.force_foot1},${row.force_foot2}`);
      }
      const csvString = csvLines.join("\n");

      const blob = new Blob([csvString], { type: "text/csv" });
      const file = new File([blob], "run_data.csv", { type: "text/csv" });

      const formData = new FormData();
      formData.append("athlete_id", athleteId);
      formData.append("event_type", eventType);
      formData.append("elapsed_ms", String(elapsedMs));
      formData.append("file", file);

      await api.post("/csv/upload-run", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      await queryClient.invalidateQueries({ queryKey: ["runs"] });
      bleClearBuffer();
      resetAll();
    } catch (error) {
      console.error("Failed to save run:", error);
    } finally {
      setIsSaving(false);
    }
  };

  // Reset everything back to setup screen — used by both Delete and Save
  const resetAll = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setElapsedMs(0);
    setIsRunning(false);
    setIsStopped(false);
    setIsConnecting(false);
    setScreen("setup");
  };

  // Delete handler — also disconnects and clears buffer
  const handleDelete = async () => {
    await bleDisconnect();
    bleClearBuffer();
    resetAll();
  };

  // Format milliseconds as M:SS.cc (centisecond precision)
  const formatTime = (ms: number) => {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const centiseconds = Math.floor((ms % 1000) / 10);
    return `${minutes}:${seconds.toString().padStart(2, "0")}.${centiseconds.toString().padStart(2, "0")}`;
  };

  // ── BLE Unavailable Screen ──
  if (!bleIsAvailable) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] px-6 text-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-muted-foreground mb-6"
        >
          <path d="m7 7 10 10-5 5V2l5 5L7 17" />
          <line x1="2" y1="2" x2="22" y2="22" />
        </svg>
        <h1 className="text-xl font-bold text-foreground mb-2">
          Bluetooth Required
        </h1>
        <p className="text-sm text-muted-foreground max-w-xs">
          StrideTrack requires Bluetooth to connect to force plate sensors.
          Please enable Bluetooth in your device settings or use a
          Bluetooth-compatible device.
        </p>
      </div>
    );
  }

  // ── Setup Screen ──
  if (screen === "setup") {
    return (
      <div className="py-10">
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
  const saving = isSaving;

  return (
    <div className="flex flex-col items-center pt-10">
      {/* Header */}
      <h1 className="text-2xl font-bold text-foreground">New Run</h1>
      <p className="text-sm text-muted-foreground mt-1 mb-10">
        {selectedAthlete?.name} · {selectedEvent?.label}
      </p>

      {/* BLE status indicator during recording */}
      {isRunning && (
        <div
          className="flex items-center gap-2 mb-4 px-4 py-1.5 rounded-full text-xs font-medium"
          style={{
            backgroundColor: bleIsConnected
              ? "hsl(var(--primary) / 0.1)"
              : "hsl(var(--destructive) / 0.1)",
            color: bleIsConnected
              ? "hsl(var(--primary))"
              : "hsl(var(--destructive))",
          }}
        >
          <span
            className="w-2 h-2 rounded-full"
            style={{
              backgroundColor: bleIsConnected
                ? "hsl(var(--primary))"
                : "hsl(var(--destructive))",
            }}
          />
          {bleIsConnected ? "Connected" : "Sensor Disconnected — buffering..."}
        </div>
      )}

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
          {isConnecting
            ? "Connecting..."
            : isRunning
              ? "Recording"
              : isStopped
                ? "Stopped"
                : "Ready"}
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
          disabled={isConnecting || bleIsScanning}
          className="mt-10 w-56 py-4 rounded-2xl font-semibold text-xl cursor-pointer transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            backgroundColor: isRunning
              ? "hsl(var(--destructive))"
              : "hsl(var(--primary))",
            color: "hsl(var(--primary-foreground))",
          }}
        >
          {isConnecting || bleIsScanning
            ? "Connecting..."
            : isRunning
              ? "Stop"
              : "Start"}
        </button>
      )}

      {/* Save/Delete buttons — shown after stopping */}
      {isStopped && (
        <div className="mt-10 flex gap-4">
          <button
            onClick={handleDelete}
            disabled={saving}
            className="px-10 py-4 rounded-2xl font-semibold text-lg cursor-pointer transition-colors border border-border text-foreground bg-card disabled:opacity-50"
          >
            Delete
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-10 py-4 rounded-2xl font-semibold text-lg cursor-pointer transition-colors disabled:opacity-50"
            style={{
              backgroundColor: "hsl(var(--primary))",
              color: "hsl(var(--primary-foreground))",
            }}
          >
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      )}

      {/* Change selection link — only before starting */}
      {!isRunning && !isStopped && !isConnecting && (
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
