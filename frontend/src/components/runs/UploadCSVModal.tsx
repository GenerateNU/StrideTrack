import { useState, useRef } from "react";
import { X, UploadCloud } from "lucide-react";
import { AthleteSelector } from "@/components/athletes/AthleteSelector";
import EventSelector from "@/components/events/EventSelector";
import { useUploadCSV } from "@/hooks/useUploadCSV.hooks";
import type { EventTypeEnum } from "@/types/event.types";

interface UploadCSVModalProps {
  open: boolean;
  onClose: () => void;
}

export function UploadCSVModal({ open, onClose }: UploadCSVModalProps) {
  const { uploadCSV, uploadCSVIsLoading, uploadCSVError } = useUploadCSV();
  const [athleteId, setAthleteId] = useState<string | null>(null);
  const [eventType, setEventType] = useState<EventTypeEnum | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const canSubmit = athleteId !== null && eventType !== null && file !== null;

  const resetAndClose = () => {
    setAthleteId(null);
    setEventType(null);
    setFile(null);
    setIsDragging(false);
    setSuccess(false);
    onClose();
  };

  const handleFile = (f: File) => {
    if (f.name.endsWith(".csv")) setFile(f);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) handleFile(dropped);
  };

  const handleSubmit = async () => {
    if (!athleteId || !eventType || !file) return;
    try {
      await uploadCSV({ athleteId, eventType, file });
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        resetAndClose();
      }, 1500);
    } catch {
      // error captured in uploadCSVError
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-foreground/20 backdrop-blur-sm"
        onClick={!success ? resetAndClose : undefined}
      />
      <div className="relative z-10 mx-4 w-full max-w-sm rounded-2xl border border-border bg-card p-6 shadow-xl">
        {success ? (
          <div className="flex flex-col items-center justify-center py-8 gap-3">
            <div
              className="flex h-14 w-14 items-center justify-center rounded-full"
              style={{ backgroundColor: "hsl(var(--primary) / 0.12)" }}
            >
              <svg
                className="h-7 w-7"
                fill="none"
                viewBox="0 0 24 24"
                stroke="hsl(var(--primary))"
                strokeWidth={2.5}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-base font-semibold text-foreground">Upload successful</p>
            <p className="text-sm text-muted-foreground">{file?.name}</p>
          </div>
        ) : (
          <>
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-bold text-foreground">Upload Run</h2>
              <button
                onClick={resetAndClose}
                className="rounded-lg p-1 text-muted-foreground transition-colors hover:text-foreground"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              <AthleteSelector value={athleteId} onChange={setAthleteId} />
              <EventSelector value={eventType} onChange={setEventType} />

              <div>
                <label className="mb-2 block text-sm font-medium text-foreground">
                  CSV File
                </label>
                <div
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setIsDragging(true);
                  }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={handleDrop}
                  className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-6 transition-colors"
                  style={{
                    borderColor: isDragging
                      ? "hsl(var(--primary))"
                      : "hsl(var(--border))",
                    backgroundColor: isDragging
                      ? "hsl(var(--primary) / 0.05)"
                      : "hsl(var(--background))",
                  }}
                >
                  <UploadCloud
                    className="h-7 w-7"
                    style={{ color: "hsl(var(--primary))" }}
                  />
                  {file ? (
                    <p className="text-sm font-medium text-foreground">
                      {file.name}
                    </p>
                  ) : (
                    <>
                      <p className="text-sm font-medium text-foreground">
                        Drop CSV here or{" "}
                        <span style={{ color: "hsl(var(--primary))" }}>
                          browse
                        </span>
                      </p>
                      <p className="text-xs text-muted-foreground">
                        .csv files only
                      </p>
                    </>
                  )}
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) handleFile(f);
                  }}
                />
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={!canSubmit || uploadCSVIsLoading}
              className="mt-6 w-full rounded-xl py-3.5 text-sm font-semibold transition-all disabled:opacity-40"
              style={{
                backgroundColor: "hsl(var(--primary))",
                color: "hsl(var(--primary-foreground))",
              }}
            >
              {uploadCSVIsLoading ? "Uploading..." : "Upload Run"}
            </button>

            {uploadCSVError && (
              <p className="mt-2 text-center text-xs text-destructive">
                Upload failed. Please try again.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
