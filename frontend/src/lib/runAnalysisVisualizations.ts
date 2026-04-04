import type { ComponentType } from "react";
import type { ChartProps } from "@/types/chart.types";
import { EventCategory } from "@/types/event.types";
import type { EventTypeEnum } from "@/types/event.types";

// Universal charts
import { GroundContactTimeChart } from "@/components/charts/universal/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/universal/FlightTimeChart";

// Hurdle charts
import { GctIncreaseChart } from "@/components/charts/hurdles/GctIncreaseChart";
import { HurdleSplitChart } from "@/components/charts/hurdles/HurdleSplitChart";
import { LandingGctChart } from "@/components/charts/hurdles/LandingGctChart";
import { StepsBetweenHurdlesChart } from "@/components/charts/hurdles/StepsBetweenHurdlesChart";
import { TakeoffFtChart } from "@/components/charts/hurdles/TakeoffFtChart";
import { TakeoffGctChart } from "@/components/charts/hurdles/TakeoffGctChart";
import { ProjectedFinishKPI } from "@/components/charts/hurdles/ProjectedFinishChart";
import { ProjectedSplitChart } from "@/components/charts/hurdles/ProjectedSplitChart";
import { SplitScoreChart } from "@/components/charts/hurdles/SplitScoreChart";

// Sprint charts
import { SprintDriftKPIs } from "@/components/charts/sprint/DriftKPI";
import { StepFrequencyChart } from "@/components/charts/sprint/StepFrequencyChart";

// Bosco charts
import { FatigueIndexKPI } from "@/components/charts/bosco/FatigueIndexKPI";
import { GctFlightChart } from "@/components/charts/bosco/GctFlightChart";
import { JumpHeightChart } from "@/components/charts/bosco/JumpHeightChart";
import { RsiChart } from "@/components/charts/bosco/RsiChart";
import { HurdleTimelineChart } from "@/components/charts/hurdles/HurdleTimelineChart";
import { FTAsymmetryKPI } from "@/components/charts/universal/FTAsymmetryKPI";
import { GCTAsymmetryKPI } from "@/components/charts/universal/GCTAsymmetryKPI";
import { GCTRangePieChart } from "@/components/charts/universal/GCTRangePieChart";
import { RSIChart } from "@/components/charts/universal/RSIChart";
import { StepTimeChart } from "@/components/charts/universal/StepTimeChart";
import { TotalStepsKPI } from "@/components/charts/universal/TotalStepsKPI";

export type VisualizationConfig = ComponentType<ChartProps>;

const DEFAULT_CHARTS: VisualizationConfig[] = [
  GroundContactTimeChart,
  FlightTimeChart,
  FTAsymmetryKPI,
  GCTAsymmetryKPI,
  GCTRangePieChart,
  RSIChart,
  StepTimeChart,
  TotalStepsKPI,
];

const visualizationsByEventType: Record<string, VisualizationConfig[]> = {
  sprint: [
    ...DEFAULT_CHARTS,
    SprintDriftKPIs,
    StepFrequencyChart,
    SplitScoreChart,
  ],
  hurdles: [
    ...DEFAULT_CHARTS,
    GctIncreaseChart,
    HurdleSplitChart,
    LandingGctChart,
    StepsBetweenHurdlesChart,
    TakeoffFtChart,
    TakeoffGctChart,
    SplitScoreChart,
    HurdleTimelineChart,
  ],
  hurdles_partial: [
    ...DEFAULT_CHARTS,
    GctIncreaseChart,
    HurdleSplitChart,
    LandingGctChart,
    StepsBetweenHurdlesChart,
    TakeoffFtChart,
    TakeoffGctChart,
    SplitScoreChart,
    ProjectedFinishKPI,
    ProjectedSplitChart,
    HurdleTimelineChart,
  ],
  bosco: [GctFlightChart, JumpHeightChart, RsiChart, FatigueIndexKPI],
};

export function getEventCategory(
  eventType: EventTypeEnum
): EventCategory | null {
  if (eventType.startsWith(EventCategory.HURDLES)) return EventCategory.HURDLES;
  if (eventType.startsWith(EventCategory.SPRINT)) return EventCategory.SPRINT;
  if (eventType.startsWith(EventCategory.BOSCO)) return EventCategory.BOSCO;
  return null;
}

export function getChartsForEventType(
  eventType: EventTypeEnum
): VisualizationConfig[] {
  if (eventType in visualizationsByEventType) {
    return visualizationsByEventType[eventType];
  }
  const category = getEventCategory(eventType);
  if (!category) return DEFAULT_CHARTS;
  return visualizationsByEventType[category] ?? DEFAULT_CHARTS;
}
