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
import { chartColors } from "@/lib/chartColors";
import type { HurdleSplit } from "@/types/hurdleMetrics.types";

interface HurdleSplitBarChartProps {
  splits: HurdleSplit[];
  meanSplitMs: number;
}

export const HurdleSplitBarChart = ({
  splits,
  meanSplitMs,
}: HurdleSplitBarChartProps) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={splits}
        margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
      >
        <CartesianGrid vertical={false} stroke={chartColors.border} />
        <XAxis
          dataKey="hurdle_number"
          label={{
            value: "Hurdle Number",
            position: "insideBottom",
            offset: -30,
          }}
          tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
        />
        <YAxis
          label={{
            value: "Split Time (ms)",
            angle: -90,
            position: "insideLeft",
          }}
          tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
        />
        <Tooltip formatter={(value: number) => [`${value} ms`]} />
        <ReferenceLine
          y={meanSplitMs}
          stroke={chartColors.primary}
          strokeDasharray="4 4"
          label="Mean"
        />
        <Bar
          dataKey="split_time_ms"
          fill={chartColors.primary}
          radius={[6, 6, 0, 0]}
          name="Split Time"
        />
      </BarChart>
    </ResponsiveContainer>
  );
};
