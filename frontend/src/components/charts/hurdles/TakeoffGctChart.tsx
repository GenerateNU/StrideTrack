import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useTakeoffGct } from "@/hooks/useHurdleMetrics.hooks";
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

export const TakeoffGctChart = ({
  runId,
  hurdlesCompleted,
  targetEvent,
}: ChartProps) => {
  const {
    takeoffGct,
    takeoffGctIsLoading,
    takeoffGctError,
    takeoffGctRefetch,
  } = useTakeoffGct(runId, hurdlesCompleted ?? null, targetEvent ?? null);

  if (takeoffGctIsLoading)
    return (
      <ChartCard
        title="Takeoff GCT"
        description="Ground contact time on the takeoff step before each hurdle clearance."
      >
        <QueryLoading />
      </ChartCard>
    );
  if (takeoffGctError)
    return (
      <ChartCard
        title="Takeoff GCT"
        description="Ground contact time on the takeoff step before each hurdle clearance."
      >
        <QueryError
          error={takeoffGctError}
          refetch={() => void takeoffGctRefetch()}
        />
      </ChartCard>
    );
  if (!takeoffGct) return null;

  const values = takeoffGct
    .map((d) => d.takeoff_gct_ms)
    .filter((v): v is number => v != null);

  const yMin = Math.min(...values);
  const yMax = Math.max(...values);
  const yPadding = (yMax - yMin) * 0.2 || 1;

  return (
    <ChartCard
      title="Takeoff GCT"
      description="Ground contact time on the takeoff step before each hurdle clearance."
    >
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={takeoffGct}>
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
              value: "Ground Contact Time (ms)",
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
            formatter={(value) => [value != null ? `${value} ms` : "N/A"]}
          />
          <Bar
            dataKey="takeoff_gct_ms"
            fill={chartColors.primary}
            radius={[6, 6, 0, 0]}
            name="Takeoff GCT"
          />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};
