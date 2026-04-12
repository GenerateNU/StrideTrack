import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useHurdleSplits } from "@/hooks/useHurdleMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
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

export const HurdleSplitChart = ({
  runId,
  hurdlesCompleted,
  targetEvent,
}: ChartProps) => {
  const {
    hurdleSplits,
    hurdleSplitsIsLoading,
    hurdleSplitsError,
    hurdleSplitsRefetch,
  } = useHurdleSplits(runId, hurdlesCompleted ?? null, targetEvent ?? null);

  if (hurdleSplitsIsLoading)
    return (
      <ChartCard
        title="Hurdle Splits"
        description="Time between consecutive hurdle clearances. Low CV% indicates consistent pacing."
      >
        <QueryLoading />
      </ChartCard>
    );
  if (hurdleSplitsError)
    return (
      <ChartCard
        title="Hurdle Splits"
        description="Time between consecutive hurdle clearances. Low CV% indicates consistent pacing."
      >
        <QueryError
          error={hurdleSplitsError}
          refetch={() => void hurdleSplitsRefetch()}
        />
      </ChartCard>
    );
  if (!hurdleSplits) return null;

  const validSplits = hurdleSplits.filter(
    (s) => s.hurdle_split_ms != null
  ) as Array<{ hurdle_num: number; hurdle_split_ms: number }>;

  if (validSplits.length === 0) return null;

  const splitValues = validSplits.map((s) => s.hurdle_split_ms);
  const mean = splitValues.reduce((a, b) => a + b, 0) / splitValues.length;
  const stdDev = Math.sqrt(
    splitValues.reduce((sum, v) => sum + (v - mean) ** 2, 0) /
      splitValues.length
  );
  const cv = (stdDev / mean) * 100;

  const yMin = Math.min(...splitValues);
  const yMax = Math.max(...splitValues);
  const yPadding = (yMax - yMin) * 0.2 || 1;

  return (
    <ChartCard
      title="Hurdle Splits"
      description="Time between consecutive hurdle clearances. Low CV% indicates consistent pacing."
      headerRight={
        <div className="flex flex-col items-end">
          <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide sm:text-xs">
            CV%
          </span>
          <span className="text-base font-bold text-foreground sm:text-2xl">
            {cv.toFixed(1)}
            <span className="text-[10px] font-medium text-muted-foreground ml-0.5 sm:text-sm sm:ml-1">
              %
            </span>
          </span>
        </div>
      }
    >
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={validSplits}>
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
            strokeDasharray="6 3"
            strokeWidth={1.5}
            label={{
              value: "Mean",
              position: "right",
              fill: chartColors.primary,
              fontSize: 10,
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
    </ChartCard>
  );
};
