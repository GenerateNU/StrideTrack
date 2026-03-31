import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useHurdleProjection } from "@/hooks/useHurdleMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
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

export const ProjectedSplitChart = ({ runId }: { runId: string }) => {
  const {
    projectionData,
    projectionLoading,
    projectionError,
    refetchProjectionData,
  } = useHurdleProjection(runId);

  if (projectionLoading) {
    return <QueryLoading />;
  }

  if (projectionError) {
    return (
      <QueryError
        error={projectionError as Error}
        refetch={() => void refetchProjectionData()}
      />
    );
  }

  if (!projectionData) {
    return null;
  }

  const { completed_splits, projected_splits } = projectionData;

  if (completed_splits.length === 0 && projected_splits.length === 0) {
    return null;
  }

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

  const completedValues = completed_splits.map((s) => s.split_ms);
  const mean =
    completedValues.reduce((a, b) => a + b, 0) / completedValues.length;

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 60, left: 20, bottom: 40 }}
        >
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
            strokeDasharray="4 4"
            label={{
              value: "Avg (completed)",
              position: "right",
              fill: chartColors.primary,
              fontSize: 11,
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

      <div className="flex items-center justify-center gap-6 mt-3">
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-3 rounded-sm"
            style={{ backgroundColor: chartColors.primary }}
          />
          <span className="text-xs text-muted-foreground">Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-3 rounded-sm border border-dashed"
            style={{ borderColor: chartColors.mutedForeground }}
          />
          <span className="text-xs text-muted-foreground">Projected</span>
        </div>
      </div>
    </div>
  );
};
