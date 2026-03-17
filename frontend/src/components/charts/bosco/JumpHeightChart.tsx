import { useBoscoMetrics } from "@/hooks/useBoscoMetrics";
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

export const JumpHeightChart = ({ runId }: { runId: string }) => {
  const { boscoMetrics } = useBoscoMetrics(runId);

  const data =
    boscoMetrics?.jump_heights.map((height, index) => ({
      jump_num: index + 1,
      height: parseFloat(height.toFixed(3)),
    })) ?? [];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
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
          y={boscoMetrics?.mean_jump_height}
          stroke={chartColors.mutedForeground}
          strokeDasharray="4 4"
          label={{
            value: "Mean",
            fill: chartColors.mutedForeground,
            fontSize: 10,
          }}
        />
        <Bar dataKey="height" fill={chartColors.primary} radius={[4, 4, 0, 0]} name="Jump Height" />
      </BarChart>
    </ResponsiveContainer>
  );
};