import { ChartCard } from "@/components/charts/shared/ChartCard";
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

const TITLE = "Ground Contact Time (GCT) — Left vs Right Foot";
const DESCRIPTION =
  "Per-foot GCT across every approach step, with the final 3 steps highlighted. GCT should decrease sharply into takeoff. Allows coaches to identify foot asymmetry in the critical final steps and assess how quickly the athlete transitions from approach to board contact.";

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

  if (approachDataIsLoading)
    return (
      <ChartCard title={TITLE} description={DESCRIPTION}>
        <QueryLoading />
      </ChartCard>
    );
  if (approachDataError)
    return (
      <ChartCard title={TITLE} description={DESCRIPTION}>
        <QueryError
          error={approachDataError}
          refetch={() => void approachDataRefetch()}
        />
      </ChartCard>
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
    <ChartCard title={TITLE} description={DESCRIPTION}>
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
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: chartColors.mutedForeground }}
            domain={["auto", "auto"]}
            label={{
              value: "GCT (ms)",
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
    </ChartCard>
  );
};
