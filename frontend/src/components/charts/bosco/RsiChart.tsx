import { useBoscoMetrics } from "@/hooks/useBoscoMetrics";
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

export const RsiChart = ({ runId }: { runId: string }) => {
  const { boscoMetrics } = useBoscoMetrics(runId);

  const data =
    boscoMetrics?.rsi_per_jump.map((rsi, index) => ({
      jump_num: index + 1,
      rsi: parseFloat(rsi.toFixed(3)),
    })) ?? [];

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
            value: "RSI",
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
          formatter={(value) => [`${value}`, "RSI"]}
        />
        <ReferenceLine
          y={1.0}
          stroke={chartColors.mutedForeground}
          strokeDasharray="4 4"
          label={{
            value: "1.0 target",
            fill: chartColors.mutedForeground,
            fontSize: 10,
          }}
        />
        <Line
          type="monotone"
          dataKey="rsi"
          stroke={chartColors.primary}
          strokeWidth={2}
          name="RSI"
          dot={{ fill: chartColors.primary }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
