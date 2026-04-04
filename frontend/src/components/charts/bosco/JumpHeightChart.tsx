import type { ChartProps } from "@/types/chart.types";
import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import { useBoscoMetrics } from "@/hooks/useBoscoMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";

export const JumpHeightChart = ({ runId }: ChartProps) => {
  const {
    boscoMetrics,
    boscoMetricsIsLoading,
    boscoMetricsError,
    boscoMetricsRefetch,
  } = useBoscoMetrics(runId);

  if (boscoMetricsIsLoading) return <QueryLoading />;
  if (boscoMetricsError)
    return (
      <QueryError
        error={boscoMetricsError}
        refetch={() => void boscoMetricsRefetch()}
      />
    );
  if (!boscoMetrics) return null;

  const chartData =
    boscoMetrics.jump_heights.map((height, index) => ({
      jump_num: index + 1,
      height: parseFloat(height.toFixed(3)),
    })) ?? [];

  return (
    <ChartCard
      title="Jump Height"
      description="Estimated jump height per repetition. Derived from flight time using ballistic equations."
    >
      <div className="overflow-x-auto">
        <div style={{ minWidth: Math.max(chartData.length * 30, 0) }}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke={chartColors.border} />
          <XAxis
            dataKey="jump_num"
            label={{
              value: "Jump Number",
              position: "insideBottom",
              offset: -5,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
          />
          <YAxis
            label={{
              value: "Height (m)",
              angle: -90,
              position: "insideLeft",
              offset: 0,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: "none",
              boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
              fontSize: 13,
              backgroundColor: chartColors.card,
              color: chartColors.foreground,
            }}
            formatter={(value) => [`${value} m`, "Jump Height"]}
          />
          <ReferenceLine
            y={boscoMetrics.mean_jump_height}
            stroke={chartColors.mutedForeground}
            strokeDasharray="4 4"
            label={{
              value: "Mean",
              fill: chartColors.mutedForeground,
              fontSize: 10,
            }}
          />
          <Bar
            dataKey="height"
            fill={chartColors.primary}
            radius={[4, 4, 0, 0]}
            name="Jump Height"
          />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </ChartCard>
  );
};
