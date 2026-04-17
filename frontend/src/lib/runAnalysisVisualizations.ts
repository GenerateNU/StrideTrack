import type { ChartProps } from "@/types/chart.types";
import type { EventTypeEnum } from "@/types/event.types";
import { EventCategory } from "@/types/event.types";
import type { ComponentType } from "react";

// Universal charts
import { FlightTimeChart } from "@/components/charts/universal/FlightTimeChart";
import { FTAsymmetryKPI } from "@/components/charts/universal/FTAsymmetryKPI";
import { GCTAsymmetryKPI } from "@/components/charts/universal/GCTAsymmetryKPI";
import { GCTRangePieChart } from "@/components/charts/universal/GCTRangePieChart";
import { GroundContactTimeChart } from "@/components/charts/universal/GroundContactChart";
import { RSIChart } from "@/components/charts/universal/RSIChart";
import { StepTimeChart } from "@/components/charts/universal/StepTimeChart";
import { TotalStepsKPI } from "@/components/charts/universal/TotalStepsKPI";

// Hurdle charts
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

// Sprint charts
import { SprintDriftKPIs } from "@/components/charts/sprint/DriftKPI";
import { StepFrequencyChart } from "@/components/charts/sprint/StepFrequencyChart";

// Bosco charts
import { FatigueIndexKPI } from "@/components/charts/bosco/FatigueIndexKPI";
import { GctFlightChart } from "@/components/charts/bosco/GctFlightChart";
import { JumpHeightChart } from "@/components/charts/bosco/JumpHeightChart";
import { RsiChart } from "@/components/charts/bosco/RsiChart";
import { ReactionTimeCard } from "@/components/charts/reaction-time/ReactionTimeCard";

// Long jump charts
import { ApproachProfileChart } from "@/components/charts/long_jump/ApproachProfileChart";
import { JumpFlightTimeCard } from "@/components/charts/long_jump/JumpFlightTimeCard";
import { LastStepGctCard } from "@/components/charts/long_jump/LastStepGctCard";
import { LjFlightTimeChart } from "@/components/charts/long_jump/LjFlightTimeChart";
import { LjGctChart } from "@/components/charts/long_jump/LjGctChart";

// Triple jump charts
import { ContactTimeEfficiencyCard } from "@/components/charts/triple_jump/ContactTimeEfficiencyCard";
import { PhaseRatioChart } from "@/components/charts/triple_jump/PhaseRatioChart";
import { TjPhaseTimelineChart } from "@/components/charts/triple_jump/TjPhaseTimelineChart";

export type VisualizationConfig = ComponentType<ChartProps>;

export type ChartSection = {
  label: string;
  charts: VisualizationConfig[];
  defaultExpanded?: boolean;
};

// Reusable universal sections

const CORE_TEMPORAL: ChartSection = {
  label: "Core Temporal",
  charts: [GroundContactTimeChart, FlightTimeChart, StepTimeChart],
  defaultExpanded: false,
};

const ASYMMETRY: ChartSection = {
  label: "Asymmetry & Balance",
  charts: [GCTAsymmetryKPI, FTAsymmetryKPI],
};

const PERFORMANCE: ChartSection = {
  label: "Performance",
  charts: [RSIChart, GCTRangePieChart, TotalStepsKPI, ReactionTimeCard],
};

const HURDLE_SPECIFIC: ChartSection = {
  label: "Hurdle-Specific",
  charts: [
    HurdleSplitChart,
    StepsBetweenHurdlesChart,
    TakeoffGctChart,
    LandingGctChart,
    TakeoffFtChart,
    GctIncreaseChart,
    HurdleTimelineChart,
  ],
};

// Event-type sections

const sectionsByEventType: Record<string, ChartSection[]> = {
  sprint: [
    {
      label: "Sprint-Specific",
      charts: [SprintDriftKPIs, StepFrequencyChart, SplitScoreChart],
      defaultExpanded: true,
    },
    CORE_TEMPORAL,
    ASYMMETRY,
    PERFORMANCE,
  ],
  hurdles: [
    {
      label: "Hurdle-Specific",
      charts: [
        HurdleSplitChart,
        StepsBetweenHurdlesChart,
        TakeoffGctChart,
        LandingGctChart,
        TakeoffFtChart,
        GctIncreaseChart,
        SplitScoreChart,
        HurdleTimelineChart,
      ],
      defaultExpanded: true,
    },
    CORE_TEMPORAL,
    ASYMMETRY,
    PERFORMANCE,
  ],
  hurdles_60m: [
    { ...HURDLE_SPECIFIC, defaultExpanded: true },
    CORE_TEMPORAL,
    ASYMMETRY,
    PERFORMANCE,
  ],
  hurdles_partial: [
    {
      label: "Projected Performance",
      charts: [ProjectedFinishKPI, ProjectedSplitChart],
      defaultExpanded: true,
    },
    HURDLE_SPECIFIC,
    CORE_TEMPORAL,
    ASYMMETRY,
    PERFORMANCE,
  ],
  long_jump: [
    {
      label: "Long Jump",
      charts: [
        LastStepGctCard,
        JumpFlightTimeCard,
        ApproachProfileChart,
        LjGctChart,
        LjFlightTimeChart,
      ],
      defaultExpanded: true,
    },
    ASYMMETRY,
  ],
  triple_jump: [
    {
      label: "Triple Jump",
      charts: [
        ContactTimeEfficiencyCard,
        PhaseRatioChart,
        TjPhaseTimelineChart,
      ],
      defaultExpanded: true,
    },
    ASYMMETRY,
  ],
  bosco: [
    {
      label: "Jump Height",
      charts: [JumpHeightChart],
      defaultExpanded: true,
    },
    {
      label: "Rhythm & Power",
      charts: [GctFlightChart, RsiChart],
    },
    {
      label: "Fatigue",
      charts: [FatigueIndexKPI],
    },
  ],
};

// Lookup helpers

export function getEventCategory(
  eventType: EventTypeEnum
): EventCategory | null {
  if (eventType.startsWith(EventCategory.HURDLES)) return EventCategory.HURDLES;
  if (eventType.startsWith(EventCategory.SPRINT)) return EventCategory.SPRINT;
  if (eventType.startsWith(EventCategory.BOSCO)) return EventCategory.BOSCO;
  return null;
}

const DEFAULT_SECTIONS: ChartSection[] = [
  CORE_TEMPORAL,
  ASYMMETRY,
  PERFORMANCE,
];

export function getSectionsForEventType(
  eventType: EventTypeEnum
): ChartSection[] {
  if (eventType in sectionsByEventType) {
    return sectionsByEventType[eventType];
  }
  const category = getEventCategory(eventType);
  if (!category) return DEFAULT_SECTIONS;
  return sectionsByEventType[category] ?? DEFAULT_SECTIONS;
}
