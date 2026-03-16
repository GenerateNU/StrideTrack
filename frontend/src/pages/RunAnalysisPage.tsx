import { useParams, useNavigate } from "react-router-dom";
import { useGetAllRuns } from "@/hooks/useRuns.hooks";
import { useGetAllAthletes } from "@/hooks/useAthletes.hooks";
import { GroundContactTimeChart } from "@/components/charts/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/FlightTimeChart";
import { StepTimeChart } from "@/components/charts/StepTimeChart";
import { ArrowLeft } from "lucide-react";

function SectionHeader({ title }: { title: string }) {
  return (
    <div className="flex items-center gap-2.5 mb-3">
      <div
        className="h-5 w-1 rounded-full"
        style={{ backgroundColor: "hsl(var(--primary))" }}
      />
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
    </div>
  );
}

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
        className="mb-5 flex items-center gap-1 text-sm text-muted-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to {athlete?.name ?? "Athlete"}
      </button>

      <div className="mb-8">
        <h2 className="text-xl font-bold text-foreground">
          {run ? run.event_type.replace("_", " ") : "Run Analysis"}
        </h2>
        {run && (
          <p className="mt-1 text-sm text-muted-foreground">
            {new Date(run.created_at).toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
            {run.elapsed_ms ? ` · ${(run.elapsed_ms / 1000).toFixed(1)}s` : ""}
          </p>
        )}
      </div>

      {runId ? (
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-5">
            <SectionHeader title="Ground Contact Time — L vs R" />
            <GroundContactTimeChart runId={runId} />
          </div>

          <div className="rounded-2xl border border-border bg-card p-5">
            <SectionHeader title="Flight Time — L vs R" />
            <FlightTimeChart runId={runId} />
          </div>

          <div className="rounded-2xl border border-border bg-card p-5">
            <SectionHeader title="Step Time — GCT + Flight" />
            <StepTimeChart runId={runId} />
          </div>
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-border bg-secondary/30 p-12 text-center">
          <p className="text-sm font-medium text-muted-foreground">
            Run not found.
          </p>
        </div>
      )}
    </div>
  );
}
