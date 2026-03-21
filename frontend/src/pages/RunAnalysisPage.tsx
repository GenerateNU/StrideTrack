import { useParams, useNavigate } from "react-router-dom";
import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";
import { GroundContactTimeChart } from "@/components/charts/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/FlightTimeChart";
import { StepDataTable } from "@/components/charts/StepDataTable";
import { ArrowLeft } from "lucide-react";

function SectionHeader({ title }: { title: string }) {
  return (
    <div className="mb-3 flex items-center gap-2.5">
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
  const { metrics, metricsIsLoading } = useRunMetrics(runId ?? null);

  // ADD HERE: Replace with dedicated GET /api/run/:runId and GET /api/athletes/:athleteId
  // endpoints once they exist. Currently we only have the runId from the URL.

  return (
    <div className="pt-4">
      <button
        onClick={() => navigate(`/athletes/${athleteId}`)}
        className="mb-5 flex items-center gap-1 text-sm text-muted-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Athlete
      </button>

      <div className="mb-8">
        <h2 className="text-xl font-bold text-foreground">Run Analysis</h2>
        {/* ADD HERE: Display run event_type, date, elapsed_ms once GET /api/run/:runId exists */}
      </div>

      {runId ? (
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-5 shadow-sm shadow-foreground/[0.02]">
            <SectionHeader title="Ground Contact Time — L vs R" />
            <GroundContactTimeChart runId={runId} />
          </div>

          <div className="rounded-2xl border border-border bg-card p-5 shadow-sm shadow-foreground/[0.02]">
            <SectionHeader title="Flight Time — L vs R" />
            <FlightTimeChart runId={runId} />
          </div>

          <StepDataTable metrics={metrics ?? []} isLoading={metricsIsLoading} />
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-border p-12 text-center">
          <p className="text-sm font-medium text-muted-foreground">
            Run not found.
          </p>
        </div>
      )}
    </div>
  );
}
