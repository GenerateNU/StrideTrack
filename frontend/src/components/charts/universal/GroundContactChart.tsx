import { LROverlayLineChart } from "@/components/charts/shared/LROverlayLineChart";
import type { ChartProps } from "@/types/chart.types";
import { ChartCard } from "@/components/charts/shared/ChartCard";
import { useLROverlayData } from "@/hooks/useRunMetrics.hooks";
import { MeanGCTKPI } from "@/components/charts/universal/MeanGCTKPI";

export const GroundContactTimeChart = ({ runId }: ChartProps) => {
  const { lrOverlay } = useLROverlayData(runId, "gct_ms");

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
      title="Ground Contact Time — L vs R"
      description="Lower is better at max velocity. Compares left and right foot ground contact times per stride."
      headerRight={mean != null ? <MeanGCTKPI mean={mean} /> : undefined}
    >
      <LROverlayLineChart runId={runId} metric="gct_ms" showMeanReferenceLine />
    </ChartCard>
  );
};
