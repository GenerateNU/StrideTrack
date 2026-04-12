import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useHurdleProjection } from "@/hooks/useHurdleMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface ChartRow {
  hurdle_num: number;
  split_ms: number;
  type: "completed" | "projected";
}

const TITLE = "Projected Splits";
const DESCRIPTION =
  "Completed splits shown solid, projected splits shown hatched. Reference line marks average of completed splits.";

export const ProjectedSplitChart = ({
  runId,
  hurdlesCompleted,
  targetEvent,
}: ChartProps) => {
  const {
    hurdleProjection,
    hurdleProjectionIsLoading,
    hurdleProjectionError,
    hurdleProjectionRefetch,
  } = useHurdleProjection(runId, hurdlesCompleted ?? null, targetEvent ?? null);

  if (hurdleProjectionIsLoading)
    return (
      <ChartCard title={TITLE} description={DESCRIPTION}>
        <QueryLoading />
      </ChartCard>
    );

  if (hurdleProjectionError)
    return (
      <ChartCard title={TITLE} description={DESCRIPTION}>
        <QueryError
          error={hurdleProjectionError as Error}
          refetch={() => void hurdleProjectionRefetch()}
        />
      </ChartCard>
    );

  if (!hurdleProjection) return null;

  const { completed_splits, projected_splits } = hurdleProjection;

  if (completed_splits.length === 0 && projected_splits.length === 0)
    return null;

  const chartData: ChartRow[] = [
    ...completed_splits.map((s) => ({
      hurdle_num: s.hurdle_num,
      split_ms: s.split_ms,
      type: "completed" as const,
    })),
    ...projected_splits.map((s) => ({
      hurdle_num: s.hurdle_num,
      split_ms: s.split_ms,
      type: "projected" as const,
    })),
  ];

  const allValues = chartData.map((d) => d.split_ms);
  const yMin = Math.min(...allValues);
  const yMax = Math.max(...allValues);
  const yPadding = (yMax - yMin) * 0.2 || 1;

  const completedValues = completed_splits.map((s) => s.split_ms);
  const mean =
    completedValues.reduce((a, b) => a + b, 0) / completedValues.length;

  return (
    <ChartCard title={TITLE} description={DESCRIPTION}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <defs>
            <pattern
              id="projected-pattern"
              patternUnits="userSpaceOnUse"
              width="6"
              height="6"
              patternTransform="rotate(45)"
            >
              <rect
                width="6"
                height="6"
                fill="hsl(var(--muted-foreground) / 0.15)"
              />
              <line
                x1="0"
                y1="0"
                x2="0"
                y2="6"
                stroke="hsl(var(--muted-foreground) / 0.4)"
                strokeWidth="2"
              />
            </pattern>
          </defs>
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
            formatter={(value, _name, props) => {
              const label =
                (props.payload as ChartRow).type === "projected"
                  ? "Projected"
                  : "Completed";
              return [`${value} ms`, label];
            }}
          />
          <ReferenceLine
            y={mean}
            stroke={chartColors.primary}
            strokeDasharray="6 3"
            strokeWidth={1.5}
            label={{
              value: "Avg (completed)",
              position: "right",
              fill: chartColors.primary,
              fontSize: 10,
            }}
          />
          <Bar dataKey="split_ms" radius={[6, 6, 0, 0]} name="Split Time">
            {chartData.map((entry, index) => (
              <Cell
                key={index}
                fill={
                  entry.type === "completed"
                    ? chartColors.primary
                    : "url(#projected-pattern)"
                }
                stroke={
                  entry.type === "projected"
                    ? chartColors.mutedForeground
                    : "none"
                }
                strokeWidth={entry.type === "projected" ? 1.5 : 0}
                strokeDasharray={entry.type === "projected" ? "4 3" : "none"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="flex items-center justify-center gap-4 mt-3 sm:gap-6">
        <div className="flex items-center gap-1.5 sm:gap-2">
          <div
            className="w-3 h-2.5 rounded-sm sm:w-4 sm:h-3"
            style={{ backgroundColor: chartColors.primary }}
          />
          <span className="text-[10px] text-muted-foreground sm:text-xs">
            Completed
          </span>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2">
          <div
            className="w-3 h-2.5 rounded-sm border border-dashed sm:w-4 sm:h-3"
            style={{ borderColor: chartColors.mutedForeground }}
          />
          <span className="text-[10px] text-muted-foreground sm:text-xs">
            Projected
          </span>
        </div>
      </div>
    </ChartCard>
  );
};
