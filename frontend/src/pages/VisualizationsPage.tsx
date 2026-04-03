import { FlightTimeChart } from "@/components/charts/FlightTimeChart";
import { GroundContactTimeChart } from "@/components/charts/GroundContactChart";
import { GctIncreaseChart } from "@/components/charts/hurdles/GctIncreaseChart";
import { HurdleSplitChart } from "@/components/charts/hurdles/HurdleSplitChart";
import { LandingGctChart } from "@/components/charts/hurdles/LandingGctChart";
import { StepsBetweenHurdlesChart } from "@/components/charts/hurdles/StepsBetweenHurdlesChart";
import { TakeoffFtChart } from "@/components/charts/hurdles/TakeoffFtChart";
import { TakeoffGctChart } from "@/components/charts/hurdles/TakeoffGctChart";
import { StepTimeChart } from "@/components/charts/StepTimeChart";
import { JumpHeightChart } from "@/components/charts/bosco/JumpHeightChart";
import { RsiChart } from "@/components/charts/bosco/RsiChart";
import { GctFlightChart } from "@/components/charts/bosco/GctFlightChart";
import { FatigueIndexKPI } from "@/components/charts/bosco/FatigueIndexKPI";
import { SprintDriftKPIs } from "@/components/charts/sprint/DriftKPI";
import { StepFrequencyChart } from "@/components/charts/sprint/StepFrequencyChart";
import { HurdleTimelineChart } from "@/components/charts/hurdles/HurdleTimelineChart";
import { useState } from "react";
import EventHistoryFilterBar from "@/components/charts/EventHistoryFilterBar";
import { EventHistoryChart } from "@/components/charts/EventHistoryChart";
import type { EventHistoryFilters } from "@/types/eventHistoryFilters.types";
import { TotalStepsKPI } from "@/components/charts/universal/TotalStepsKPI";
import { RSIChart } from "@/components/charts/universal/RSIChart";
import { GCTAsymmetryKPI } from "@/components/charts/universal/GCTAsymmetryKPI";
import { FTAsymmetryKPI } from "@/components/charts/universal/FTAsymmetryKPI";
import { MeanGCTKPI } from "@/components/charts/universal/MeanGCTKPI";
import { MeanFTKPI } from "@/components/charts/universal/MeanFTKPI";
import { MeanRSIKPI } from "@/components/charts/universal/MeanRSIKPI";
import { GCTRangePieChart } from "@/components/charts/universal/GCTRangePieChart";
import { GraphInfoCard } from "@/components/charts/GraphInfoCard";
import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";

const HARDCODED_RUN_ID = "d0271452-4bec-4759-84ef-c62beaafdbf0";
const HARDCODED_BOSCO_RUN_ID = "b1a2c3d4-5678-9abc-def0-111111111111";
const HARDCODED_HURDLE_RUN_ID = "11111111-1111-1111-1111-111111111111";

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

function UniversalMetrics() {
  const { metrics } = useRunMetrics(HARDCODED_RUN_ID);

  const meanGCT =
    metrics && metrics.length > 0
      ? metrics.reduce((s, m) => s + m.gct_ms, 0) / metrics.length
      : null;

  const meanFT =
    metrics && metrics.length > 0
      ? metrics.reduce((s, m) => s + m.flight_ms, 0) / metrics.length
      : null;

  const meanRSI =
    metrics && metrics.length > 0
      ? metrics.reduce(
          (s, m) => s + (m.gct_ms > 0 ? m.flight_ms / m.gct_ms : 0),
          0
        ) / metrics.length
      : null;

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-foreground">Universal Metrics</h1>

      {/* Item 1 — Total Steps */}
      <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
        <GraphInfoCard description="Basic volume metric." />
        <TotalStepsKPI runId={HARDCODED_RUN_ID} />
      </div>

      {/* Item 2 — Mean GCT */}
      <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
        <GraphInfoCard description="Lower is better at max velocity." />
        <div className="flex items-start justify-between mb-3">
          <SectionHeader title="Ground Contact Time — L vs R" />
          {meanGCT != null && <MeanGCTKPI mean={meanGCT} />}
        </div>
        <GroundContactTimeChart runId={HARDCODED_RUN_ID} />
      </div>

      {/* Item 3 — Mean FT */}
      <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
        <GraphInfoCard description="Context-dependent (sprinting vs jumping)." />
        <div className="flex items-start justify-between mb-3">
          <SectionHeader title="Flight Time — L vs R" />
          {meanFT != null && <MeanFTKPI mean={meanFT} />}
        </div>
        <FlightTimeChart runId={HARDCODED_RUN_ID} />
      </div>

      {/* Item 4 — RSI */}
      <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
        <GraphInfoCard description="Elite sprinters RSI > 1.0 at max velocity." />
        <div className="flex items-start justify-between mb-3">
          <SectionHeader title="Reactive Strength Index (RSI)" />
          {meanRSI != null && <MeanRSIKPI mean={meanRSI} />}
        </div>
        <RSIChart runId={HARDCODED_RUN_ID} />
      </div>

      {/* Items 5 & 6 — Asymmetry */}
      <div className="grid grid-cols-2 gap-3">
        <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
          <GraphInfoCard description=">10% may indicate injury risk. Target <5%." />
          <GCTAsymmetryKPI runId={HARDCODED_RUN_ID} />
        </div>
        <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
          <GraphInfoCard description="Push-off power imbalance between legs." />
          <FTAsymmetryKPI runId={HARDCODED_RUN_ID} />
        </div>
      </div>

      {/* Item 8 — GCT Range */}
      <div className="relative bg-card border border-border rounded-lg p-6 shadow-sm">
        <GraphInfoCard description="Bucketing done client-side from existing per-step gct_ms data." />
        <SectionHeader title="Steps in GCT Range" />
        <GCTRangePieChart runId={HARDCODED_RUN_ID} />
      </div>
    </div>
  );
}

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
          <UniversalMetrics />

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
        <h2 className="text-2xl font-bold mb-6 text-foreground">Bosco Test</h2>
        <div className="space-y-8">
          <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
            <h3 className="text-xl font-bold mb-3 text-primary">Jump Height</h3>
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
