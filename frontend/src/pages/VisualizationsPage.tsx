import { GroundContactTimeChart } from "@/components/charts/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/FlightTimeChart";
import { StepTimeChart } from "@/components/charts/StepTimeChart";
import { JumpHeightChart } from "@/components/charts/bosco/JumpHeightChart";
import { RsiChart } from "@/components/charts/bosco/RsiChart";
import { GctFlightChart } from "@/components/charts/bosco/GctFlightChart";
import { FatigueIndexKPI } from "@/components/charts/bosco/FatigueIndexKPI";

const HARDCODED_RUN_ID = "d0271452-4bec-4759-84ef-c62beaafdbf0";
const HARDCODED_BOSCO_RUN_ID = "b1a2c3d4-5678-9abc-def0-111111111111";

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
        </div>

        <h2 className="text-2xl font-bold mb-6 text-foreground">Bosco Test</h2>
        <div className="space-y-8">
          <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-bold mb-3 text-primary">
              Jump Height
            </h3>
            <JumpHeightChart runId={HARDCODED_BOSCO_RUN_ID} />
          </div>

          <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-bold mb-3 text-primary">
              Reactive Strength Index (RSI)
            </h3>
            <RsiChart runId={HARDCODED_BOSCO_RUN_ID} />
          </div>

          <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-bold mb-3 text-primary">
              Flight Time & Jump Height
            </h3>
            <GctFlightChart runId={HARDCODED_BOSCO_RUN_ID} />
          </div>

          <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-bold mb-3 text-primary">
              Fatigue Index
            </h3>
            <FatigueIndexKPI runId={HARDCODED_BOSCO_RUN_ID} />
          </div>
        </div>


      </div>
    </div>
  );
}
