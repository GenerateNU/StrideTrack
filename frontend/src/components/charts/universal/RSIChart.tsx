import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
import { ChartCard } from "@/components/charts/shared/ChartCard";
import { MeanRSIKPI } from "@/components/charts/universal/MeanRSIKPI";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";

export const RSIChart = ({ runId }: ChartProps) => {
  const {
    runMetrics,
    runMetricsIsLoading,
    runMetricsError,
    runMetricsRefetch,
  } = useRunMetrics(runId);

  if (runMetricsIsLoading) return <QueryLoading />;
  if (runMetricsError)
    return <QueryError error={runMetricsError} refetch={runMetricsRefetch} />;
  if (!runMetrics) return null;

  const rsiData = runMetrics.map((m) => ({
    label: m.stride_num,
    rsi: m.gct_ms > 0 ? parseFloat((m.flight_ms / m.gct_ms).toFixed(3)) : 0,
  }));

  const meanRSI =
    runMetrics.length > 0
      ? runMetrics.reduce(
          (s, m) => s + (m.gct_ms > 0 ? m.flight_ms / m.gct_ms : 0),
          0
        ) / runMetrics.length
      : null;

  return (
    <ChartCard
      title="Reactive Strength Index (RSI)"
      description="Flight time divided by ground contact time per stride. Elite sprinters target RSI > 1.0 at max velocity."
      headerRight={meanRSI != null ? <MeanRSIKPI mean={meanRSI} /> : undefined}
    >
      <div className="overflow-x-auto">
        <div style={{ minWidth: Math.max(rsiData.length * 20, 0) }}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={rsiData}
              margin={{ top: 16, right: 24, left: 0, bottom: 24 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke={chartColors.border}
              />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 11, fill: chartColors.mutedForeground }}
                label={{
                  value: "Stride Number",
                  position: "insideBottom",
                  offset: -10,
                  style: {
                    fill: chartColors.mutedForeground,
                    fontSize: 11,
                    textAnchor: "middle",
                  },
                }}
              />
              <YAxis
                tick={{ fontSize: 11, fill: chartColors.mutedForeground }}
                label={{
                  value: "RSI",
                  angle: -90,
                  position: "insideLeft",
                  offset: 10,
                  style: {
                    fill: chartColors.mutedForeground,
                    fontSize: 11,
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
                formatter={(value) => [value, "RSI"]}
                labelFormatter={(label) => `Stride ${label}`}
              />
              <ReferenceLine
                y={1.0}
                stroke={chartColors.primary}
                strokeDasharray="6 3"
                strokeWidth={1.5}
                label={{
                  value: "Elite (1.0)",
                  position: "insideBottomRight",
                  style: { fill: chartColors.primary, fontSize: 10 },
                }}
              />
              <Line
                type="monotone"
                dataKey="rsi"
                stroke={chartColors.foreground}
                strokeWidth={2}
                name="RSI"
                dot={{ fill: chartColors.foreground, r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </ChartCard>
  );
};
