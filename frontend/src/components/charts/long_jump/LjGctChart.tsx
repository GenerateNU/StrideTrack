import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useLjApproachProfile } from "@/hooks/useLongJumpMetrics.hooks";
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

const LEFT_COLOR = "#f97316";
const RIGHT_COLOR = "#000000";

interface StepRow {
  label: number;
  left: number | null;
  right: number | null;
  phase: string;
  foot: string;
}

export const LjGctChart = ({ runId }: { runId: string }) => {
  const { approachData, approachLoading, approachError, refetchApproachData } =
    useLjApproachProfile(runId);

  if (approachLoading) return <QueryLoading />;
  if (approachError)
    return (
      <QueryError
        error={approachError as Error}
        refetch={() => void refetchApproachData()}
      />
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
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
            label={{
              value: "Step Number",
              position: "insideBottom",
              offset: -5,
              fontSize: 11,
              fill: "var(--muted-foreground)",
            }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
            domain={["auto", "auto"]}
            label={{
              value: "GCT (ms)",
              angle: -90,
              position: "insideLeft",
              offset: -4,
              fontSize: 11,
              fill: "var(--muted-foreground)",
            }}
          />
          <Tooltip
            contentStyle={{
              background: "var(--card)",
              border: "1px solid var(--border)",
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
              stroke="#ef4444"
              strokeDasharray="4 2"
              label={{
                value: "Final 3",
                position: "insideTopRight",
                fontSize: 10,
                fill: "#ef4444",
              }}
            />
          )}
          <Line
            type="monotone"
            dataKey="left"
            stroke={LEFT_COLOR}
            strokeWidth={2}
            dot={{ fill: LEFT_COLOR }}
            connectNulls
            name="left"
          />
          <Line
            type="monotone"
            dataKey="right"
            stroke={RIGHT_COLOR}
            strokeWidth={2}
            dot={{ fill: RIGHT_COLOR }}
            connectNulls
            name="right"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
