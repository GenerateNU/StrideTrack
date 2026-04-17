import { ChartCard } from "@/components/charts/shared/ChartCard";
import { LROverlayLineChart } from "@/components/charts/shared/LROverlayLineChart";
import { MeanFTKPI } from "@/components/charts/universal/MeanFTKPI";
import { useLROverlayData } from "@/hooks/useRunMetrics.hooks";
import type { ChartProps } from "@/types/chart.types";

export const FlightTimeChart = ({ runId }: ChartProps) => {
  const { lrOverlay } = useLROverlayData(runId, "flight_ms");

  const mean =
    lrOverlay && lrOverlay.length > 0
      ? (() => {
          const vals: number[] = [];
          for (const d of lrOverlay) {
            if (d.left != null) vals.push(d.left);
            if (d.right != null) vals.push(d.right);
          }
          return vals.length > 0
            ? vals.reduce((s, v) => s + v, 0) / vals.length
            : null;
        })()
      : null;

  return (
    <ChartCard
      title="Flight Time — L vs R"
      description="Context-dependent (sprinting vs jumping). Compares left and right foot flight times per stride."
      headerRight={mean != null ? <MeanFTKPI mean={mean} /> : undefined}
    >
      <LROverlayLineChart runId={runId} metric="flight_ms" />
    </ChartCard>
  );
};
