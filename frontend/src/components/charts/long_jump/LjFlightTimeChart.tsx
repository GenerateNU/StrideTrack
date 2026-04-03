import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import {
  useLjStepSeries,
  useLongJumpMetrics,
} from "@/hooks/useLongJumpMetrics.hooks";
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

interface CustomDotProps {
  cx?: number;
  cy?: number;
  payload?: StepRow;
}

const CustomDot = (props: CustomDotProps) => {
  const { cx, cy, payload } = props;
  if (cx === undefined || cy === undefined || !payload) return null;
  const isTakeoff = payload.phase === "takeoff";
  if (isTakeoff)
    return (
      <circle cx={cx} cy={cy} r={8} fill="#22c55e" stroke="#fff" strokeWidth={2} />
    );
  return (
    <circle
      cx={cx}
      cy={cy}
      r={3}
      fill={payload.foot === "left" ? LEFT_COLOR : RIGHT_COLOR}
      opacity={0.6}
    />
  );
};

export const LjFlightTimeChart = ({ runId }: { runId: string }) => {
  const { stepSeriesData, stepSeriesLoading, stepSeriesError, refetchStepSeriesData } =
    useLjStepSeries(runId);
  const { ljMetrics, ljMetricsLoading } = useLongJumpMetrics(runId);

  if (stepSeriesLoading || ljMetricsLoading) return <QueryLoading />;
  if (stepSeriesError)
    return (
      <QueryError
        error={stepSeriesError as Error}
        refetch={() => void refetchStepSeriesData()}
      />
    );
  if (!stepSeriesData) return null;

  const sorted = [...stepSeriesData].sort((a, b) => a.ic_time - b.ic_time);
  const rows: StepRow[] = sorted.map((d, i) => ({
    label: i + 1,
    left: d.foot === "left" ? (d.flight_ms ?? null) : null,
    right: d.foot === "right" ? (d.flight_ms ?? null) : null,
    phase: "approach",
    foot: d.foot,
  }));

  const jumpFtMs = ljMetrics?.jump_ft_ms;
  const takeoffRow = rows[rows.length - 1];

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={rows}
          margin={{ top: 8, right: 80, left: 16, bottom: 0 }}
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
              value: "Flight Time (ms)",
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
          {takeoffRow && (
            <ReferenceLine
              x={takeoffRow.label}
              stroke="#22c55e"
              strokeDasharray="4 2"
              label={{
                value: jumpFtMs ? `Takeoff → ${jumpFtMs}ms` : "Takeoff",
                position: "insideTopLeft",
                dx: -90,
                fontSize: 10,
                fill: "#22c55e",
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
