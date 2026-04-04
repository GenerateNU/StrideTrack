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

export const TakeoffFtChart = ({ runId }: ChartProps) => {
  const { takeoffFt, takeoffFtIsLoading, takeoffFtError, takeoffFtRefetch } =
    useTakeoffFt(runId);

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
  const dataMin = Math.min(...values);
  const dataMax = Math.max(...values);
  const range = dataMax - dataMin || 1;
  const yDomain: [number, number] = [
    Math.max(0, dataMin - range * 0.2),
    dataMax + range * 0.1,
  ];

  return (
    <ChartCard
      title="Takeoff Flight Time"
      description="Flight time during the hurdle clearance phase at each hurdle."
    >
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={takeoffFt}
          margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
        >
          <CartesianGrid vertical={false} stroke={chartColors.border} />
          <XAxis
            dataKey="hurdle_num"
            label={{
              value: "Hurdle Number",
              position: "insideBottom",
              offset: -30,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
            tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
          />
          <YAxis
            domain={yDomain}
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
            tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
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
