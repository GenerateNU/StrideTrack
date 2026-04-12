import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useGetRunMeta } from "@/hooks/useRuns.hooks";
import { getChartsForEventType } from "@/lib/runAnalysisVisualizations";
import { ArrowLeft } from "lucide-react";

const TARGET_EVENT_OPTIONS = ["60m hurdles", "100m hurdles", "110m hurdles", "400m hurdles"];

export default function RunAnalysisPage() {
  const { athleteId, runId } = useParams<{
    athleteId: string;
    runId: string;
  }>();
  const navigate = useNavigate();

  const { runMeta } = useGetRunMeta(runId);
  const isHurdlesPartial = runMeta?.event_type === "hurdles_partial";

  const [hurdleParams, setHurdleParams] = useState<{
    targetEvent: string | null;
    hurdlesCompleted: number | null;
    hasSubmitted: boolean;
  }>({ targetEvent: null, hurdlesCompleted: null, hasSubmitted: false });

  useEffect(() => {
    if (runMeta) {
      queueMicrotask(() => {
        const te = runMeta.target_event ?? null;
        const hc = runMeta.hurdles_completed ?? null;
        setHurdleParams({ targetEvent: te, hurdlesCompleted: hc, hasSubmitted: !!(te && hc) });
      });
    }
  }, [runMeta]);

  const canSubmit = hurdleParams.targetEvent !== null && hurdleParams.hurdlesCompleted !== null;

  const handleSubmit = () => {
    setHurdleParams((prev) => ({ ...prev, hasSubmitted: true }));
  };

  const charts = runMeta?.event_type
    ? getChartsForEventType(runMeta.event_type)
    : [];

  const showCharts = !isHurdlesPartial || hurdleParams.hasSubmitted;

  return (
    <div className="flex h-full flex-col pt-4">
      <div className="mb-6">
        <button
          onClick={() => navigate(`/athletes/${athleteId}`)}
          className="mb-4 flex items-center gap-1 text-sm text-muted-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Athlete
        </button>
        <h2 className="text-xl font-bold text-foreground">Event Analysis</h2>
        {runMeta && (
          <p className="text-sm text-muted-foreground mt-1">
            {runMeta.event_type
              .replace(/_/g, " ")
              .replace(/\b\w/g, (c) => c.toUpperCase())}{" "}
            · {new Date(runMeta.created_at).toLocaleDateString()}
            {` · ${(runMeta.elapsed_ms / 1000).toFixed(2)}s`}
          </p>
        )}
      </div>

      {isHurdlesPartial && (
        <div className="mb-6 flex items-end gap-4 rounded-lg border border-border p-4">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-foreground">Target Event</label>
            <select
              value={hurdleParams.targetEvent ?? ""}
              onChange={(e) =>
                setHurdleParams((prev) => ({
                  ...prev,
                  targetEvent: e.target.value || null,
                  hasSubmitted: false,
                }))
              }
              className="rounded-md border border-border bg-background px-3 py-2 text-sm"
            >
              <option value="">Select event...</option>
              {TARGET_EVENT_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-foreground">Hurdles Completed</label>
            <input
              type="number"
              min={1}
              max={10}
              value={hurdleParams.hurdlesCompleted ?? ""}
              onChange={(e) =>
                setHurdleParams((prev) => ({
                  ...prev,
                  hurdlesCompleted: e.target.value ? Number(e.target.value) : null,
                  hasSubmitted: false,
                }))
              }
              className="rounded-md border border-border bg-background px-3 py-2 text-sm w-24"
            />
          </div>
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
          >
            Apply
          </button>
        </div>
      )}

      {runId && showCharts ? (
        <div className="flex flex-1 flex-col gap-6">
          {charts.map((ChartComponent, i) => (
            <ChartComponent key={i} runId={runId} />
          ))}
        </div>
      ) : runId && !showCharts ? (
        <div className="rounded-2xl border border-dashed border-border p-12 text-center">
          <p className="text-sm font-medium text-muted-foreground">
            Select a target event and hurdles completed, then click Apply to view charts.
          </p>
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-border p-12 text-center">
          <p className="text-sm font-medium text-muted-foreground">
            Event not found.
          </p>
        </div>
      )}
    </div>
  );
}
