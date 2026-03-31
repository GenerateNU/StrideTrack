import type { ComponentType } from "react";

// Shared charts
import { GroundContactTimeChart } from "@/components/charts/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/FlightTimeChart";

// Hurdle charts
import { GctIncreaseChart } from "@/components/charts/hurdles/GctIncreaseChart";
import { HurdleSplitChart } from "@/components/charts/hurdles/HurdleSplitChart";
import { LandingGctChart } from "@/components/charts/hurdles/LandingGctChart";
import { StepsBetweenHurdlesChart } from "@/components/charts/hurdles/StepsBetweenHurdlesChart";
import { TakeoffFtChart } from "@/components/charts/hurdles/TakeoffFtChart";
import { TakeoffGctChart } from "@/components/charts/hurdles/TakeoffGctChart";

// Sprint charts
import { SprintDriftKPIs } from "@/components/charts/sprint/DriftKPI";
import { FTDriftCard } from "@/components/charts/sprint/FTDriftCard";
import { GCTDriftCard } from "@/components/charts/sprint/GCTDriftCard";
import { StepFrequencyChart } from "@/components/charts/sprint/StepFrequencyChart";

// Bosco charts
import { FatigueIndexKPI } from "@/components/charts/bosco/FatigueIndexKPI";
import { GctFlightChart } from "@/components/charts/bosco/GctFlightChart";
import { JumpHeightChart } from "@/components/charts/bosco/JumpHeightChart";
import { RsiChart } from "@/components/charts/bosco/RsiChart";

export type VisualizationConfig = {
  title: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  component: ComponentType<any>;
};

const DEFAULT_CHARTS: VisualizationConfig[] = [
  { title: "Ground Contact Time — L vs R", component: GroundContactTimeChart },
  { title: "Flight Time — L vs R", component: FlightTimeChart },
];

const visualizationsByEventType: Record<string, VisualizationConfig[]> = {
  sprint: [
    ...DEFAULT_CHARTS,
    { title: "Drift KPI", component: SprintDriftKPIs },
    { title: "FT Drift", component: FTDriftCard },
    { title: "GCT Drift", component: GCTDriftCard },
    { title: "Step Frequency", component: StepFrequencyChart },
  ],
  hurdles: [
    ...DEFAULT_CHARTS,
    { title: "GCT Increase", component: GctIncreaseChart },
    { title: "Hurdle Splits", component: HurdleSplitChart },
    { title: "Landing GCT", component: LandingGctChart },
    { title: "Steps Between Hurdles", component: StepsBetweenHurdlesChart },
    { title: "Takeoff Flight Time", component: TakeoffFtChart },
    { title: "Takeoff GCT", component: TakeoffGctChart },
  ],
  bosco: [
    ...DEFAULT_CHARTS,
    { title: "GCT Flight", component: GctFlightChart },
    { title: "Jump Height", component: JumpHeightChart },
    { title: "RSI", component: RsiChart },
    { title: "Fatigue Index", component: FatigueIndexKPI },
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
