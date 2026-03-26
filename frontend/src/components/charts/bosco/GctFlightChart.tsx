import { useBoscoMetrics } from "@/hooks/useBoscoMetrics";
import { chartColors } from "@/lib/chartColors";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { BoscoMetricsResponse } from "@/types/bosco.types";

function buildChartData(metrics: BoscoMetricsResponse) {
  return metrics.flight_per_jump.map((flight, index) => ({
    jump_num: index + 1,
    flight_ms: flight,
    jump_height_cm: parseFloat((metrics.jump_heights[index] * 100).toFixed(1)),
  }));
}

export const GctFlightChart = ({ runId }: { runId: string }) => {
  const { boscoMetrics } = useBoscoMetrics(runId);

  const data = boscoMetrics ? buildChartData(boscoMetrics) : [];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
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
            value: "Time (ms)",
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
        <Legend
          verticalAlign="bottom"
          align="center"
          wrapperStyle={{ paddingTop: 40, fontSize: 11, paddingLeft: 60 }}
          iconType="circle"
          iconSize={8}
        />
        <Line
          type="monotone"
          dataKey="flight_ms"
          stroke={chartColors.primary}
          strokeWidth={2}
          name="Flight Time"
          dot={{ fill: chartColors.primary }}
        />
        <Line
          type="monotone"
          dataKey="jump_height_cm"
          stroke={chartColors.foreground}
          strokeWidth={2}
          name="Jump Height (cm)"
          dot={{ fill: chartColors.foreground }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
