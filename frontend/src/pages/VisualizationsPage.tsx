import { GroundContactTimeChart } from "@/components/charts/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/FlightTimeChart";
import { StepTimeChart } from "@/components/charts/StepTimeChart";
import { SprintDriftKPIs } from "@/components/charts/sprint/DriftKPI";
import { StepFrequencyChart } from "@/components/charts/sprint/StepFrequencyChart";

const HARDCODED_RUN_ID = "d0271452-4bec-4759-84ef-c62beaafdbf0";

export default function VisualizationsPage() {
  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-foreground">
          Performance Metrics
        </h1>

        <div className="space-y-8">
          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              Ground Contact Time (GCT) - Left vs Right Foot
            </h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <GroundContactTimeChart runId={HARDCODED_RUN_ID} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              Flight Time (FT) - Left vs Right Foot
            </h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <FlightTimeChart runId={HARDCODED_RUN_ID} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              Step Time - Ground Contact + Flight (Stacked)
            </h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <StepTimeChart runId={HARDCODED_RUN_ID} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              Step Frequency - (Hz)
            </h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <StepFrequencyChart runId={HARDCODED_RUN_ID} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              Sprint Drift
            </h2>
            <SprintDriftKPIs runId={HARDCODED_RUN_ID} />
          </div>
        </div>
      </div>
    </div>
  );
}
