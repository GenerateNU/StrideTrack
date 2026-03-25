import { useState, useRef, useCallback } from "react";
import { useForm, Controller } from "react-hook-form";
import { AthleteSelector } from "@/components/athletes/AthleteSelector";
import EventSelector from "@/components/events/EventSelector";
import { useCreateRun } from "@/hooks/useCreateRun.hooks";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { useEvents } from "@/hooks/useEvents";
import { UploadCSVModal } from "@/components/runs/UploadCSVModal";
import type { EventTypeEnum } from "@/types/event.types";

interface SetupFormValues {
  athleteId: string;
  eventType: EventTypeEnum;
}

export default function RecordingPage() {
  const [screen, setScreen] = useState<"setup" | "recording">("setup");
  const [elapsedMs, setElapsedMs] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [isStopped, setIsStopped] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number>(0);

  const { athletes } = useGetAllAthletes();
  const events = useEvents();
  const { createRun, createRunIsLoading } = useCreateRun();

  const {
    control,
    handleSubmit,
    getValues,
    formState: { isValid },
  } = useForm<SetupFormValues>({
    mode: "onChange",
    defaultValues: { athleteId: "", eventType: "" as EventTypeEnum },
  });

  const { athleteId, eventType } = getValues();

  const selectedAthlete = athletes.find((a) => a.athlete_id === athleteId);
  const selectedEvent = events.find((e) => e.value === eventType);

  const startTimer = useCallback(() => {
    startTimeRef.current = Date.now();
    setIsRunning(true);
    setIsStopped(false);
    setElapsedMs(0);
    intervalRef.current = setInterval(() => {
      setElapsedMs(Date.now() - startTimeRef.current);
    }, 10);
  }, []);

  const stopTimer = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setElapsedMs(Date.now() - startTimeRef.current);
    setIsRunning(false);
    setIsStopped(true);
  }, []);

  const handleSave = async () => {
    if (!athleteId || !eventType) return;
    try {
      await createRun({
        athlete_id: athleteId,
        event_type: eventType,
        elapsed_ms: elapsedMs,
      });
      resetAll();
    } catch (error) {
      console.error("Failed to save run:", error);
    }
  };

  const resetAll = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setElapsedMs(0);
    setIsRunning(false);
    setIsStopped(false);
    setScreen("setup");
  };

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
      <>
        <div className="py-10">
          <div className="max-w-md mx-auto">
            <h1 className="text-2xl font-bold text-foreground">New Run</h1>
            <p className="text-sm text-muted-foreground mt-1 mb-10">
              Select an athlete and event to begin recording
            </p>

            <form
              onSubmit={handleSubmit(() => setScreen("recording"))}
              className="space-y-6"
            >
              <Controller
                name="athleteId"
                control={control}
                rules={{ required: true }}
                render={({ field }) => (
                  <AthleteSelector
                    value={field.value || null}
                    onChange={(val) => field.onChange(val ?? "")}
                  />
                )}
              />

              <Controller
                name="eventType"
                control={control}
                rules={{ required: true }}
                render={({ field }) => (
                  <EventSelector
                    value={(field.value as EventTypeEnum) || null}
                    onChange={(val) => field.onChange(val ?? "")}
                  />
                )}
              />

              <button
                type="submit"
                disabled={!isValid}
                className={`w-full py-3.5 rounded-xl font-semibold text-base transition-all ${
                  isValid
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

              <button
                type="button"
                onClick={() => setUploadModalOpen(true)}
                className="w-full py-3.5 rounded-xl font-semibold text-base border border-border text-foreground bg-card transition-colors hover:bg-secondary"
              >
                Upload Run
              </button>
            </form>
          </div>
        </div>

        <UploadCSVModal
          open={uploadModalOpen}
          onClose={() => setUploadModalOpen(false)}
        />
      </>
    );
  }

  // ── Recording Screen ──
  return (
    <div className="flex flex-col items-center pt-10">
      <h1 className="text-2xl font-bold text-foreground">New Run</h1>
      <p className="text-sm text-muted-foreground mt-1 mb-10">
        {selectedAthlete?.name} · {selectedEvent?.label}
      </p>

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
