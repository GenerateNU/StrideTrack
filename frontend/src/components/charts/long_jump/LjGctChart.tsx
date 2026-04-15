import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useLjApproachProfile } from "@/hooks/useLongJumpMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface StepRow {
  label: number;
  left: number | null;
  right: number | null;
  phase: string;
  foot: string;
}

export const LjGctChart = ({ runId }: ChartProps) => {
  const {
    approachData,
    approachDataIsLoading,
    approachDataError,
    approachDataRefetch,
  } = useLjApproachProfile(runId);

  if (approachDataIsLoading) return <QueryLoading />;
  if (approachDataError)
    return (
      <QueryError error={approachDataError} refetch={approachDataRefetch} />
    );
  if (!approachData) return null;

  const sorted = [...approachData].sort((a, b) => a.ic_time - b.ic_time);
  const rows: StepRow[] = sorted.map((d, i) => ({
    label: i + 1,
    left: d.foot === "left" ? d.gct_ms : null,
    right: d.foot === "right" ? d.gct_ms : null,
    phase: d.phase,
    foot: d.foot,
  }));

  const finalStepLabel = rows.length >= 3 ? rows[rows.length - 3].label : null;

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={rows}
          margin={{ top: 8, right: 16, left: 16, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={chartColors.border} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: chartColors.mutedForeground }}
            label={{
              value: "Step Number",
              position: "insideBottom",
              offset: -5,
              fontSize: 11,
              fill: chartColors.mutedForeground,
            }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: chartColors.mutedForeground }}
            domain={["auto", "auto"]}
            label={{
              value: "GCT (ms)",
              angle: -90,
              position: "insideLeft",
              offset: -4,
              fontSize: 11,
              fill: chartColors.mutedForeground,
            }}
          />
          <Tooltip
            contentStyle={{
              background: chartColors.card,
              border: `1px solid ${chartColors.border}`,
              borderRadius: 6,
              fontSize: 12,
            }}
            formatter={
              ((value: unknown, name: unknown) => [
                value != null ? `${String(value)} ms` : "N/A",
                name === "left" ? "Left" : "Right",
              ]) as never
            }
          />
          <Legend
            verticalAlign="bottom"
            align="center"
            wrapperStyle={{ paddingTop: 40, fontSize: 11, paddingLeft: 60 }}
            iconType="circle"
            iconSize={8}
            formatter={(value) =>
              value === "left" ? "Left Foot" : "Right Foot"
            }
          />
          {finalStepLabel && (
            <ReferenceLine
              x={finalStepLabel}
              stroke={chartColors.phasePenultimate}
              strokeDasharray="4 2"
              label={{
                value: "Final 3",
                position: "insideTopRight",
                fontSize: 10,
                fill: chartColors.phasePenultimate,
              }}
            />
          )}
          <Line
            type="monotone"
            dataKey="left"
            stroke={chartColors.leftFoot}
            strokeWidth={2}
            dot={{ fill: chartColors.leftFoot }}
            connectNulls
            name="left"
          />
          <Line
            type="monotone"
            dataKey="right"
            stroke={chartColors.rightFoot}
            strokeWidth={2}
            dot={{ fill: chartColors.rightFoot }}
            connectNulls
            name="right"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
