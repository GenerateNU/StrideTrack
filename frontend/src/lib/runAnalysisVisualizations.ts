import type { ComponentType } from "react";
import type { ChartProps } from "@/types/chart.types";

// Universal charts
import { GroundContactTimeChart } from "@/components/charts/universal/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/universal/FlightTimeChart";
import { ReactionTimeCard } from "@/components/charts/reaction-time/ReactionTimeCard";

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

export type VisualizationConfig = ComponentType<ChartProps>;

const DEFAULT_CHARTS: VisualizationConfig[] = [
  GroundContactTimeChart,
  FlightTimeChart,
  ReactionTimeCard,
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
    ProjectedFinishKPI,
    ProjectedSplitChart,
  ],
  bosco: [
    ...DEFAULT_CHARTS,
    GctFlightChart,
    JumpHeightChart,
    RsiChart,
    FatigueIndexKPI,
  ],
};

export function getChartsForEventType(
  eventType: string
): VisualizationConfig[] {
  const category = eventType.startsWith("hurdles")
    ? "hurdles"
    : eventType.startsWith("sprint")
      ? "sprint"
      : eventType.startsWith("bosco")
        ? "bosco"
        : eventType;
  return visualizationsByEventType[category] ?? DEFAULT_CHARTS;
}
