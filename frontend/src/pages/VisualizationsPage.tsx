import { FlightTimeChart } from "@/components/charts/FlightTimeChart";
import { GroundContactTimeChart } from "@/components/charts/GroundContactChart";
import { GctIncreaseChart } from "@/components/charts/hurdles/GctIncreaseChart";
import { HurdleSplitChart } from "@/components/charts/hurdles/HurdleSplitChart";
import { LandingGctChart } from "@/components/charts/hurdles/LandingGctChart";
import { StepsBetweenHurdlesChart } from "@/components/charts/hurdles/StepsBetweenHurdlesChart";
import { TakeoffFtChart } from "@/components/charts/hurdles/TakeoffFtChart";
import { TakeoffGctChart } from "@/components/charts/hurdles/TakeoffGctChart";
import { StepTimeChart } from "@/components/charts/StepTimeChart";
import { SprintDriftKPIs } from "@/components/charts/sprint/DriftKPI";
import { StepFrequencyChart } from "@/components/charts/sprint/StepFrequencyChart";

const HARDCODED_RUN_ID = "d0271452-4bec-4759-84ef-c62beaafdbf0";
const HARDCODED_HURDLE_RUN_ID = "11111111-1111-1111-1111-111111111111";

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

          {/* Hurdle Metrics */}
          <h1 className="text-3xl font-bold mb-8 text-foreground">
            Hurdle Metrics
          </h1>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              Hurdle Splits
            </h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <HurdleSplitChart runId={HARDCODED_HURDLE_RUN_ID} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">Takeoff GCT</h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <TakeoffGctChart runId={HARDCODED_HURDLE_RUN_ID} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">Landing GCT</h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <LandingGctChart runId={HARDCODED_HURDLE_RUN_ID} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              Takeoff Flight Time
            </h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <TakeoffFtChart runId={HARDCODED_HURDLE_RUN_ID} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              Steps Between Hurdles
            </h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <StepsBetweenHurdlesChart runId={HARDCODED_HURDLE_RUN_ID} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              GCT Increase Hurdle-to-Hurdle
            </h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <GctIncreaseChart runId={HARDCODED_HURDLE_RUN_ID} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}