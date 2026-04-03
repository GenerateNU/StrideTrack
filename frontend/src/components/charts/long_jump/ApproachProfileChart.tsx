import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useLjApproachProfile } from "@/hooks/useLongJumpMetrics.hooks";
import {
  CartesianGrid,
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

const PHASE_COLORS: Record<string, string> = {
  approach: "hsl(var(--primary))",
  antepenultimate: "#f59e0b",
  penultimate: "#f97316",
  takeoff: "#ef4444",
};

const PHASE_LABELS: Record<string, string> = {
  approach: "Approach",
  antepenultimate: "Antepenultimate",
  penultimate: "Penultimate",
  takeoff: "Takeoff",
};

interface ChartRow {
  index: number;
  label: string;
  left: number | null;
  right: number | null;
  phase: string;
}

interface CustomDotProps {
  cx?: number;
  cy?: number;
  payload?: ChartRow;
  dataKey?: string;
}

const CustomDot = (props: CustomDotProps) => {
  const { cx, cy, payload } = props;
  if (cx === undefined || cy === undefined || !payload) return null;
  const color = PHASE_COLORS[payload.phase] ?? "hsl(var(--primary))";
  const isHighlighted = payload.phase !== "approach";
  return (
    <circle
      cx={cx}
      cy={cy}
      r={isHighlighted ? 6 : 3}
      fill={color}
      stroke={isHighlighted ? "#fff" : color}
      strokeWidth={isHighlighted ? 2 : 0}
    />
  );
};

export const ApproachProfileChart = ({ runId }: { runId: string }) => {
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
      index: stride,
      label: `S${stride}`,
      left: leftStep?.gct_ms ?? null,
      right: rightStep?.gct_ms ?? null,
      phase: leftStep?.phase ?? rightStep?.phase ?? "approach",
    };
  });

  const finalStrideIndex = strideNums[strideNums.length - 3] ?? 0;

  return (
    <div className="w-full">
      <div className="flex flex-wrap gap-4 mb-4 text-sm">
        {Object.entries(PHASE_LABELS).map(([key, label]) => (
          <div key={key} className="flex items-center gap-1.5">
            <span
              className="inline-block w-3 h-3 rounded-full"
              style={{ backgroundColor: PHASE_COLORS[key] }}
            />
            <span className="text-muted-foreground">{label}</span>
          </div>
        ))}
      </div>
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
          <ReferenceLine
            x={`S${finalStrideIndex}`}
            stroke="#f59e0b"
            strokeDasharray="4 2"
            label={{
              value: "Final 3 Steps",
              position: "insideTopRight",
              fontSize: 10,
              fill: "#f59e0b",
            }}
          />
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
        GCT decreasing into takeoff — final 3 steps highlighted
      </p>
    </div>
  );
};
