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

const PHASE_COLORS: Record<string, string> = {
  approach: "#000000",
  antepenultimate: "#facc15",
  penultimate: "#ef4444",
  takeoff: "#22c55e",
};

const PHASE_LABELS: Record<string, string> = {
  approach: "Approach",
  antepenultimate: "Antepenultimate",
  penultimate: "Penultimate",
  takeoff: "Takeoff",
};

interface StepRow {
  label: number;
  left: number | null;
  right: number | null;
  phase: string;
  foot: string;
}

interface CustomDotProps {
  cx?: number;
  cy?: number;
  payload?: StepRow;
}

const CustomDot = (props: CustomDotProps) => {
  const { cx, cy, payload } = props;
  if (cx === undefined || cy === undefined || !payload) return null;
  const color = PHASE_COLORS[payload.phase] ?? "#000000";
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
              style: { fill: "var(--muted-foreground)", fontSize: 10 },
            }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
            domain={["auto", "auto"]}
            label={{
              value: "GCT (ms)",
              angle: -90,
              position: "insideLeft",
              offset: 0,
              style: {
                fill: "var(--muted-foreground)",
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
          />
          <Tooltip
            contentStyle={{
              background: "var(--card)",
              border: "1px solid var(--border)",
              borderRadius: 6,
              fontSize: 12,
            }}
            formatter={((value: unknown, name: unknown) => [
              value != null ? `${String(value)} ms` : "N/A",
              name === "left" ? "Left" : "Right",
            ]) as never}
          />
          <Legend
            verticalAlign="bottom"
            align="center"
            wrapperStyle={{ paddingTop: 40, fontSize: 11, paddingLeft: 60 }}
            iconType="circle"
            iconSize={8}
            formatter={(v) => (v === "left" ? "Left Foot" : "Right Foot")}
          />
          {finalStepLabel && (
            <ReferenceLine
              x={finalStepLabel}
              stroke="#f59e0b"
              strokeDasharray="4 2"
              label={{
                value: "Final 3 Steps",
                position: "insideTopRight",
                fontSize: 10,
                fill: "#f59e0b",
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
    </div>
  );
};
