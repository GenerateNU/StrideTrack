import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useTakeoffFt } from "@/hooks/useHurdleMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const TakeoffFtChart = ({
  runId,
  hurdlesCompleted,
  targetEvent,
}: ChartProps) => {
  const { takeoffFt, takeoffFtIsLoading, takeoffFtError, takeoffFtRefetch } =
    useTakeoffFt(runId, hurdlesCompleted ?? null, targetEvent ?? null);

  if (takeoffFtIsLoading)
    return (
      <ChartCard
        title="Takeoff Flight Time"
        description="Flight time during the hurdle clearance phase at each hurdle."
      >
        <QueryLoading />
      </ChartCard>
    );
  if (takeoffFtError)
    return (
      <ChartCard
        title="Takeoff Flight Time"
        description="Flight time during the hurdle clearance phase at each hurdle."
      >
        <QueryError
          error={takeoffFtError}
          refetch={() => void takeoffFtRefetch()}
        />
      </ChartCard>
    );
  if (!takeoffFt) return null;

  const values = takeoffFt.map((d) => d.takeoff_ft_ms);

  const yMin = Math.min(...values);
  const yMax = Math.max(...values);
  const yPadding = (yMax - yMin) * 0.2 || 1;

  return (
    <ChartCard
      title="Takeoff Flight Time"
      description="Flight time during the hurdle clearance phase at each hurdle."
    >
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={takeoffFt}>
          <CartesianGrid strokeDasharray="3 3" stroke={chartColors.border} />
          <XAxis
            dataKey="hurdle_num"
            label={{
              value: "Hurdle Number",
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
            domain={[
              Math.max(0, Math.floor((yMin - yPadding) / 10) * 10),
              Math.ceil((yMax + yPadding) / 10) * 10,
            ]}
            label={{
              value: "Flight Time (ms)",
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
            formatter={(value) => [`${value} ms`]}
          />
          <Bar
            dataKey="takeoff_ft_ms"
            fill={chartColors.primary}
            radius={[6, 6, 0, 0]}
            name="Takeoff FT"
          />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};
