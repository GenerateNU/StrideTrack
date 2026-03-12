import { useParams, useNavigate } from "react-router-dom";
import { useGetAllRuns } from "@/hooks/useRuns.hooks";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { GroundContactTimeChart } from "@/components/charts/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/FlightTimeChart";
import { StepTimeChart } from "@/components/charts/StepTimeChart";
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
    <div className="py-6">
      <button
        onClick={() => navigate(`/athletes/${athleteId}`)}
        className="mb-5 flex items-center gap-1 text-sm text-muted-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to {athlete?.name ?? "Athlete"}
      </button>

      {/* Run header */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-foreground">
          {run
            ? run.event_type.replace("_", " ")
            : "Run Analysis"}
        </h2>
        {run && (
          <p className="mt-1 text-xs text-muted-foreground">
            {new Date(run.created_at).toLocaleString()}
            {run.elapsed_ms
              ? ` · ${(run.elapsed_ms / 1000).toFixed(1)}s`
              : ""}
          </p>
        )}
      </div>

      {/* Charts */}
      {runId ? (
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-4">
            <h3 className="mb-3 text-sm font-semibold text-foreground">
              Ground Contact Time — L vs R
            </h3>
            <GroundContactTimeChart runId={runId} />
          </div>

          <div className="rounded-2xl border border-border bg-card p-4">
            <h3 className="mb-3 text-sm font-semibold text-foreground">
              Flight Time — L vs R
            </h3>
            <FlightTimeChart runId={runId} />
          </div>

          <div className="rounded-2xl border border-border bg-card p-4">
            <h3 className="mb-3 text-sm font-semibold text-foreground">
              Step Time — GCT + Flight (Stacked)
            </h3>
            <StepTimeChart runId={runId} />
          </div>
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-border bg-secondary/30 p-8 text-center">
          <p className="text-sm text-muted-foreground">Run not found.</p>
        </div>
      )}
    </div>
  );
}