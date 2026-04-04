import { GctIncreaseChart } from "@/components/charts/hurdles/GctIncreaseChart";
import { HurdleSplitChart } from "@/components/charts/hurdles/HurdleSplitChart";
import { LandingGctChart } from "@/components/charts/hurdles/LandingGctChart";
import { ProjectedFinishKPI } from "@/components/charts/hurdles/ProjectedFinishChart";
import { ProjectedSplitChart } from "@/components/charts/hurdles/ProjectedSplitChart";
import { StepsBetweenHurdlesChart } from "@/components/charts/hurdles/StepsBetweenHurdlesChart";
import { TakeoffFtChart } from "@/components/charts/hurdles/TakeoffFtChart";
import { TakeoffGctChart } from "@/components/charts/hurdles/TakeoffGctChart";
import { StepTimeChart } from "@/components/charts/universal/StepTimeChart";
import { JumpHeightChart } from "@/components/charts/bosco/JumpHeightChart";
import { RsiChart } from "@/components/charts/bosco/RsiChart";
import { GctFlightChart } from "@/components/charts/bosco/GctFlightChart";
import { FatigueIndexKPI } from "@/components/charts/bosco/FatigueIndexKPI";
import { SprintDriftKPIs } from "@/components/charts/sprint/DriftKPI";
import { StepFrequencyChart } from "@/components/charts/sprint/StepFrequencyChart";
import { SplitScoreChart } from "@/components/charts/hurdles/SplitScoreChart";
import { ReactionTimeCard } from "@/components/charts/reaction-time/ReactionTimeCard";
import { HurdleTimelineChart } from "@/components/charts/hurdles/HurdleTimelineChart";
import { useState } from "react";
import EventHistoryFilterBar from "@/components/charts/history/EventHistoryFilterBar";
import { EventHistoryChart } from "@/components/charts/history/EventHistoryChart";
import type { EventHistoryFilters } from "@/types/eventHistoryFilters.types";
import { TotalStepsKPI } from "@/components/charts/universal/TotalStepsKPI";
import { RSIChart } from "@/components/charts/universal/RSIChart";
import { GCTAsymmetryKPI } from "@/components/charts/universal/GCTAsymmetryKPI";
import { FTAsymmetryKPI } from "@/components/charts/universal/FTAsymmetryKPI";
import { GCTRangePieChart } from "@/components/charts/universal/GCTRangePieChart";
import { GroundContactTimeChart } from "@/components/charts/universal/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/universal/FlightTimeChart";
import { GraphInfoCard } from "@/components/charts/shared/GraphInfoCard";

const HARDCODED_RUN_ID = "d0271452-4bec-4759-84ef-c62beaafdbf0";
const HARDCODED_BOSCO_RUN_ID = "b1a2c3d4-5678-9abc-def0-111111111111";
const HARDCODED_HURDLE_RUN_ID = "11111111-1111-1111-1111-111111111111";
const HARDCODED_PARTIAL_RUN_ID = "22222222-2222-2222-2222-222222222222";
const HARDCODED_RT_RUN_ID = "cccccccc-0001-4000-8000-000000000001";

export default function VisualizationsPage() {
  const HARDCODED_ATHLETE_ID = "00000000-0000-0000-0000-000000000003";
  const [eventHistoryFilters, setEventHistoryFilters] =
    useState<EventHistoryFilters | null>(null);

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-foreground">
          Performance Metrics
        </h1>

        <div className="space-y-8">
          {/* Universal Metrics */}
          <h2 className="text-2xl font-bold text-foreground">
            Universal Metrics
          </h2>
          <TotalStepsKPI runId={HARDCODED_RUN_ID} />
          <GroundContactTimeChart runId={HARDCODED_RUN_ID} />
          <FlightTimeChart runId={HARDCODED_RUN_ID} />
          <RSIChart runId={HARDCODED_RUN_ID} />

          <div className="grid grid-cols-2 gap-3">
            <GCTAsymmetryKPI runId={HARDCODED_RUN_ID} />
            <FTAsymmetryKPI runId={HARDCODED_RUN_ID} />
          </div>

          <GCTRangePieChart runId={HARDCODED_RUN_ID} />
          <StepTimeChart runId={HARDCODED_RUN_ID} />
          <StepFrequencyChart runId={HARDCODED_RUN_ID} />
          <SprintDriftKPIs runId={HARDCODED_RUN_ID} />

          {/* Hurdle Metrics */}
          <h1 className="text-3xl font-bold mb-8 text-foreground">
            Hurdle Metrics
          </h1>
          <div>
            <h2 className="text-xl font-bold mb-3 text-primary">
              Hurdle Timeline
            </h2>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <HurdleTimelineChart runId={HARDCODED_HURDLE_RUN_ID} />
            </div>
          </div>

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
        <div>
          <h2 className="text-xl font-bold mb-3 text-primary">
            Split Score Analysis
          </h2>
          <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
            <GraphInfoCard description="Compares split distribution to population average. Shaded band = normal range (±1 std dev). Red/green dots = segments outside expected range." />
            <SplitScoreChart runId={HARDCODED_HURDLE_RUN_ID} />
          </div>
        </div>

        <div>
          <h2 className="text-xl font-bold mb-3 text-primary">
            Event Time History
          </h2>
          <div className="bg-card border border-border rounded-lg p-6 shadow-sm space-y-4">
            <EventHistoryFilterBar
              athleteId={HARDCODED_ATHLETE_ID}
              onApply={(filters) => setEventHistoryFilters(filters)}
            />
            {eventHistoryFilters && (
              <EventHistoryChart filters={eventHistoryFilters} enabled={true} />
            )}
          </div>
        </div>

        {/* Bosco Metrics */}
        <h2 className="text-2xl font-bold text-foreground">Bosco Test</h2>
        <JumpHeightChart runId={HARDCODED_BOSCO_RUN_ID} />
        <RsiChart runId={HARDCODED_BOSCO_RUN_ID} />
        <GctFlightChart runId={HARDCODED_BOSCO_RUN_ID} />
        <FatigueIndexKPI runId={HARDCODED_BOSCO_RUN_ID} />

        {/* Reaction Time */}
        <h2 className="text-2xl font-bold text-foreground">
          Reaction Time Test
        </h2>
        <ReactionTimeCard runId={HARDCODED_RT_RUN_ID} />
      </div>
    </div>
  );
}
