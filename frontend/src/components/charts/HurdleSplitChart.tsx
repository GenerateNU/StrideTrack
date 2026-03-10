import { useHurdleSplits } from "@/hooks/useHurdleMetrics";
import { chartColors } from "@/lib/chartColors";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const HurdleSplitChart = ({ runId }: { runId: string }) => {
  const { splitData, splitLoading } = useHurdleSplits(runId);

  if (splitLoading || !splitData) {
    return null;
  }

  // Filter out the last hurdle (null split) for display and stats
  const validSplits = splitData.filter(
    (s) => s.hurdle_split_ms != null
  ) as Array<{ hurdle_num: number; hurdle_split_ms: number }>;

  if (validSplits.length === 0) {
    return null;
  }

  // Compute summary stats from the flat list
  const splitValues = validSplits.map((s) => s.hurdle_split_ms);
  const mean = splitValues.reduce((a, b) => a + b, 0) / splitValues.length;
  const stdDev = Math.sqrt(
    splitValues.reduce((sum, v) => sum + (v - mean) ** 2, 0) /
      splitValues.length
  );
  const cv = (stdDev / mean) * 100;

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={validSplits}
          margin={{ top: 20, right: 60, left: 20, bottom: 40 }}
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
            domain={["auto", "auto"]}
            label={{
              value: "Split Time (ms)",
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
            formatter={(value) => [value != null ? `${value} ms` : "N/A"]}
          />
          <ReferenceLine
            y={mean}
            stroke={chartColors.primary}
            strokeDasharray="4 4"
            label={{
              value: "Mean",
              position: "right",
              fill: chartColors.primary,
              fontSize: 11,
            }}
          />
          <Bar
            dataKey="hurdle_split_ms"
            fill={chartColors.primary}
            radius={[6, 6, 0, 0]}
            name="Split Time"
          />
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 bg-card border border-border rounded-lg p-4 text-center">
        <p className="text-sm text-muted-foreground">Consistency (CV%)</p>
        <p className="text-2xl font-bold text-foreground">{cv.toFixed(1)}%</p>
      </div>
    </div>
  );
};
