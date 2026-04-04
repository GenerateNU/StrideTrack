import { useParams, useNavigate } from "react-router-dom";
import { useGetRunMeta } from "@/hooks/useRuns.hooks";
import { getChartsForEventType } from "@/lib/runAnalysisVisualizations";
import { ArrowLeft } from "lucide-react";

export default function RunAnalysisPage() {
  const { athleteId, runId } = useParams<{
    athleteId: string;
    runId: string;
  }>();
  const navigate = useNavigate();

  const { runMeta } = useGetRunMeta(runId);
  const charts = runMeta?.event_type
     ? getChartsForEventType(runMeta.event_type)
     : [];

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

      {runId ? (
        <div className="flex flex-1 flex-col gap-6">
          {charts.map((ChartComponent, i) => (
            <ChartComponent key={i} runId={runId} />
          ))}
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
