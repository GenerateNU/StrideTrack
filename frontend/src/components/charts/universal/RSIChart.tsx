import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";
import { chartColors } from "@/lib/chartColors";
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

export const RSIChart = ({ runId }: { runId: string }) => {
  const { metrics, metricsIsLoading, metricsError, metricsRefetch } =
    useRunMetrics(runId);

  if (metricsIsLoading) return <QueryLoading />;
  if (metricsError)
    return <QueryError error={metricsError} refetch={metricsRefetch} />;
  if (!metrics) return null;

  const rsiData = metrics.map((m) => ({
    label: m.stride_num,
    rsi: m.gct_ms > 0 ? parseFloat((m.flight_ms / m.gct_ms).toFixed(3)) : 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={rsiData} margin={{ top: 16, right: 24, left: 0, bottom: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={chartColors.border} />
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
  );
};
