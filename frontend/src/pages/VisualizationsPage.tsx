import { FatigueIndexKPI } from "@/components/charts/bosco/FatigueIndexKPI";
import { GctFlightChart } from "@/components/charts/bosco/GctFlightChart";
import { JumpHeightChart } from "@/components/charts/bosco/JumpHeightChart";
import { RsiChart } from "@/components/charts/bosco/RsiChart";
import { EventHistoryChart } from "@/components/charts/history/EventHistoryChart";
import EventHistoryFilterBar from "@/components/charts/history/EventHistoryFilterBar";
import { GctIncreaseChart } from "@/components/charts/hurdles/GctIncreaseChart";
import { HurdleSplitChart } from "@/components/charts/hurdles/HurdleSplitChart";
import { HurdleTimelineChart } from "@/components/charts/hurdles/HurdleTimelineChart";
import { LandingGctChart } from "@/components/charts/hurdles/LandingGctChart";
import { ProjectedFinishKPI } from "@/components/charts/hurdles/ProjectedFinishChart";
import { ProjectedSplitChart } from "@/components/charts/hurdles/ProjectedSplitChart";
import { SplitScoreChart } from "@/components/charts/hurdles/SplitScoreChart";
import { StepsBetweenHurdlesChart } from "@/components/charts/hurdles/StepsBetweenHurdlesChart";
import { TakeoffFtChart } from "@/components/charts/hurdles/TakeoffFtChart";
import { TakeoffGctChart } from "@/components/charts/hurdles/TakeoffGctChart";
import { GraphInfoCard } from "@/components/charts/shared/GraphInfoCard";
import { ApproachProfileChart } from "@/components/charts/long_jump/ApproachProfileChart";
import { JumpFlightTimeCard } from "@/components/charts/long_jump/JumpFlightTimeCard";
import { LastStepGctCard } from "@/components/charts/long_jump/LastStepGctCard";
import { LjFlightTimeChart } from "@/components/charts/long_jump/LjFlightTimeChart";
import { LjGctChart } from "@/components/charts/long_jump/LjGctChart";
import { SprintDriftKPIs } from "@/components/charts/sprint/DriftKPI";
import { StepFrequencyChart } from "@/components/charts/sprint/StepFrequencyChart";
import { ContactTimeEfficiencyCard } from "@/components/charts/triple_jump/ContactTimeEfficiencyCard";
import { PhaseRatioChart } from "@/components/charts/triple_jump/PhaseRatioChart";
import { TjPhaseTimelineChart } from "@/components/charts/triple_jump/TjPhaseTimelineChart";
import { FlightTimeChart } from "@/components/charts/universal/FlightTimeChart";
import { FTAsymmetryKPI } from "@/components/charts/universal/FTAsymmetryKPI";
import { GCTAsymmetryKPI } from "@/components/charts/universal/GCTAsymmetryKPI";
import { GCTRangePieChart } from "@/components/charts/universal/GCTRangePieChart";
import { GroundContactTimeChart } from "@/components/charts/universal/GroundContactChart";
import { RSIChart } from "@/components/charts/universal/RSIChart";
import { StepTimeChart } from "@/components/charts/universal/StepTimeChart";
import { TotalStepsKPI } from "@/components/charts/universal/TotalStepsKPI";
import type { EventHistoryFilters } from "@/types/eventHistoryFilters.types";
import { useState } from "react";

const HARDCODED_RUN_ID = "8fef5e24-b871-4fd7-afd4-190a1f96e42f";
const HARDCODED_BOSCO_RUN_ID = "b1a2c3d4-5678-9abc-def0-111111111111";
const HARDCODED_HURDLE_RUN_ID = "11111111-1111-1111-1111-111111111111";
const HARDCODED_PARTIAL_RUN_ID = "22222222-2222-2222-2222-222222222222";
const HARDCODED_LJ_RUN_ID = "aaaaaaaa-0001-4000-8000-000000000001";
const HARDCODED_TJ_RUN_ID = "bbbbbbbb-0001-4000-8000-000000000001";

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
          <h2 className="text-2xl font-bold text-foreground">Hurdle Metrics</h2>
          <HurdleTimelineChart runId={HARDCODED_HURDLE_RUN_ID} />
          <HurdleSplitChart runId={HARDCODED_HURDLE_RUN_ID} />
          <TakeoffGctChart runId={HARDCODED_HURDLE_RUN_ID} />
          <LandingGctChart runId={HARDCODED_HURDLE_RUN_ID} />
          <TakeoffFtChart runId={HARDCODED_HURDLE_RUN_ID} />
          <StepsBetweenHurdlesChart runId={HARDCODED_HURDLE_RUN_ID} />
          <GctIncreaseChart runId={HARDCODED_HURDLE_RUN_ID} />
          <SplitScoreChart runId={HARDCODED_HURDLE_RUN_ID} />
          <ProjectedFinishKPI runId={HARDCODED_PARTIAL_RUN_ID} />
          <ProjectedSplitChart runId={HARDCODED_PARTIAL_RUN_ID} />

          {/* Long Jump Metrics */}
          <h2 className="text-2xl font-bold text-foreground">
            Long Jump Metrics
          </h2>
          <div className="flex gap-4 flex-wrap">
            <LastStepGctCard runId={HARDCODED_LJ_RUN_ID} />
            <JumpFlightTimeCard runId={HARDCODED_LJ_RUN_ID} />
          </div>
          <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
            <GraphInfoCard description="Line chart of GCT across all approach steps, with the final 3 steps shaded. An effective approach shows progressively decreasing GCT into takeoff, reflecting acceleration and increasing reactivity as the athlete attacks the board. Dot colors indicate phase: yellow = antepenultimate, red = penultimate, green = takeoff." />
            <h3 className="text-xl font-bold mb-3 text-primary">
              Approach Profile
            </h3>
            <ApproachProfileChart runId={HARDCODED_LJ_RUN_ID} />
          </div>
          <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
            <GraphInfoCard description="Per-foot GCT across every approach step, with the final 3 steps highlighted. GCT should decrease sharply into takeoff. Allows coaches to identify foot asymmetry in the critical final steps and assess how quickly the athlete transitions from approach to board contact." />
            <h3 className="text-xl font-bold mb-3 text-primary">
              Ground Contact Time (GCT) — Left vs Right Foot
            </h3>
            <LjGctChart runId={HARDCODED_LJ_RUN_ID} />
          </div>
          <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
            <GraphInfoCard description="Per-foot flight time across the approach with emphasis on the takeoff step. A sharp spike in flight time at the final step confirms a powerful, well-timed board contact. Left/right comparison helps detect any asymmetry in propulsive output." />
            <h3 className="text-xl font-bold mb-3 text-primary">
              Flight Time (FT) — Left vs Right Foot
            </h3>
            <LjFlightTimeChart runId={HARDCODED_LJ_RUN_ID} />
          </div>

          {/* Triple Jump Metrics */}
          <h2 className="text-2xl font-bold text-foreground">
            Triple Jump Metrics
          </h2>
          <div className="flex gap-4 flex-wrap">
            <ContactTimeEfficiencyCard runId={HARDCODED_TJ_RUN_ID} />
          </div>
          <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
            <GraphInfoCard description="Stacked bar showing how total flight time is distributed across the three phases. The ideal ratio is approximately 35:30:35 (Hop:Step:Jump). A dominant hop phase often means energy is wasted early; a weak jump phase suggests technical breakdown in the final takeoff." />
            <h3 className="text-xl font-bold mb-3 text-primary">
              Phase Ratio — Hop : Step : Jump
            </h3>
            <PhaseRatioChart runId={HARDCODED_TJ_RUN_ID} />
          </div>
          <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
            <GraphInfoCard description="Dual timeline showing GCT and flight time per step across the full approach and all three jump phases, annotated with phase labels (Hop, Step, Jump). Helps coaches see how contact and flight mechanics evolve from the approach into each phase and whether the athlete maintains consistent rhythm across all three." />
            <h3 className="text-xl font-bold mb-3 text-primary">
              GCT & Flight Time Timeline — Phase Labels
            </h3>
            <TjPhaseTimelineChart runId={HARDCODED_TJ_RUN_ID} />
          </div>

          {/* Event History */}
          <EventHistoryFilterBar
            athleteId={HARDCODED_ATHLETE_ID}
            onApply={(filters) => setEventHistoryFilters(filters)}
          />
          {eventHistoryFilters && (
            <EventHistoryChart filters={eventHistoryFilters} enabled={true} />
          )}

          {/* Bosco Metrics */}
          <h2 className="text-2xl font-bold text-foreground">Bosco Test</h2>
          <JumpHeightChart runId={HARDCODED_BOSCO_RUN_ID} />
          <RsiChart runId={HARDCODED_BOSCO_RUN_ID} />
          <GctFlightChart runId={HARDCODED_BOSCO_RUN_ID} />
          <FatigueIndexKPI runId={HARDCODED_BOSCO_RUN_ID} />
        </div>
      </div>
    </div>
  );
}
