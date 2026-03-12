import { useParams, useNavigate } from "react-router-dom";
import { useGetAllRuns } from "@/hooks/useRuns.hooks";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { ArrowLeft } from "lucide-react";

export default function RunAnalysisPage() {
  const { athleteId, runId } = useParams<{
    athleteId: string;
    runId: string;
  }>();
  const navigate = useNavigate();
  const { runs } = useGetAllRuns();
  const { athletes } = useGetAllAthletes();

  const run = runs.find((r) => r.run_id === runId);
  const athlete = athletes.find((a) => a.athlete_id === athleteId);

  return (
    <div className="py-4">
      <button
        onClick={() => navigate(`/athletes/${athleteId}`)}
        className="mb-4 flex items-center gap-1 text-sm text-muted-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to {athlete?.name ?? "Athlete"}
      </button>

      {run ? (
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-bold text-foreground">
              {run.event_type.replace("_", " ")}
            </h2>
            <p className="text-xs text-muted-foreground">
              {new Date(run.created_at).toLocaleString()}
              {run.elapsed_ms
                ? ` · ${(run.elapsed_ms / 1000).toFixed(1)}s`
                : ""}
            </p>
          </div>

          <div className="rounded-xl border-2 border-dashed border-border bg-secondary p-8 text-center">
            <p className="text-sm font-medium text-muted-foreground">
              Run analysis visualizations will be migrated here.
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              GCT/FT charts, tempo, distribution, hurdle splits
            </p>
          </div>
        </div>
      ) : (
        <p className="py-12 text-center text-sm text-muted-foreground">
          Run not found.
        </p>
      )}
    </div>
  );
}