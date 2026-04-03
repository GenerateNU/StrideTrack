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

const LEFT_COLOR = "#3b82f6";
const RIGHT_COLOR = "#f97316";

interface ChartRow {
  label: string;
  left: number | null;
  right: number | null;
  phase: string;
}

interface CustomDotProps {
  cx?: number;
  cy?: number;
  payload?: ChartRow;
}

const CustomDot = (props: CustomDotProps) => {
  const { cx, cy, payload } = props;
  if (cx === undefined || cy === undefined || !payload) return null;
  const isFinal =
    payload.phase === "antepenultimate" ||
    payload.phase === "penultimate" ||
    payload.phase === "takeoff";
  return (
    <circle
      cx={cx}
      cy={cy}
      r={isFinal ? 6 : 3}
      fill={isFinal ? "#ef4444" : "var(--primary)"}
      stroke={isFinal ? "#fff" : "transparent"}
      strokeWidth={isFinal ? 2 : 0}
      opacity={isFinal ? 1 : 0.7}
    />
  );
};

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

  const strideNums = [...new Set(approachData.map((d) => d.stride_num))].sort(
    (a, b) => a - b
  );
  const rows: ChartRow[] = strideNums.map((stride) => {
    const leftStep = approachData.find(
      (d) => d.stride_num === stride && d.foot === "left"
    );
    const rightStep = approachData.find(
      (d) => d.stride_num === stride && d.foot === "right"
    );
    return {
      label: `S${stride}`,
      left: leftStep?.gct_ms ?? null,
      right: rightStep?.gct_ms ?? null,
      phase: leftStep?.phase ?? rightStep?.phase ?? "approach",
    };
  });

  const allGcts = rows
    .flatMap((r) => [r.left, r.right])
    .filter((v): v is number => v !== null);
  const meanGct = allGcts.length
    ? Math.round(allGcts.reduce((a, b) => a + b, 0) / allGcts.length)
    : null;
  const finalStepLabel = rows.at(-3)?.label;

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={rows}
          margin={{ top: 8, right: 16, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
          />
          <YAxis
            unit="ms"
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
            domain={["auto", "auto"]}
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
            formatter={(value) => (value === "left" ? "Left" : "Right")}
            wrapperStyle={{ fontSize: 12 }}
          />
          {meanGct !== null && (
            <ReferenceLine
              y={meanGct}
              stroke="var(--muted-foreground)"
              strokeDasharray="4 2"
              label={{
                value: `Mean ${meanGct}ms`,
                position: "insideTopRight",
                fontSize: 10,
                fill: "var(--muted-foreground)",
              }}
            />
          )}
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
            dot={<CustomDot />}
            connectNulls
            name="left"
          />
          <Line
            type="monotone"
            dataKey="right"
            stroke={RIGHT_COLOR}
            strokeWidth={2}
            dot={<CustomDot />}
            connectNulls
            name="right"
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-muted-foreground mt-2 text-center">
        Final 3 steps highlighted — GCT should decrease sharply into takeoff
      </p>
    </div>
  );
};
