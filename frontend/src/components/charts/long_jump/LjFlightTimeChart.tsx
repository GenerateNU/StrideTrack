import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import {
  useLjApproachProfile,
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
  const isTakeoff = payload.phase === "takeoff";
  const isPenultimate = payload.phase === "penultimate";
  if (isTakeoff)
    return <circle cx={cx} cy={cy} r={8} fill="#ef4444" stroke="#fff" strokeWidth={2} />;
  if (isPenultimate)
    return <circle cx={cx} cy={cy} r={5} fill="#f97316" stroke="#fff" strokeWidth={1.5} />;
  return <circle cx={cx} cy={cy} r={3} fill="var(--primary)" opacity={0.6} />;
};

export const LjFlightTimeChart = ({ runId }: { runId: string }) => {
  const { approachData, approachLoading, approachError, refetchApproachData } =
    useLjApproachProfile(runId);
  const { ljMetrics, ljMetricsLoading } = useLongJumpMetrics(runId);

  if (approachLoading || ljMetricsLoading) return <QueryLoading />;
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

  const takeoffLabel = rows.find((r) => r.phase === "takeoff")?.label;
  const jumpFtMs = ljMetrics?.jump_ft_ms;

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={rows} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="label" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} />
          <YAxis unit="ms" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} domain={["auto", "auto"]} />
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
          <Legend formatter={(v) => (v === "left" ? "Left" : "Right")} wrapperStyle={{ fontSize: 12 }} />
          {takeoffLabel && (
            <ReferenceLine
              x={takeoffLabel}
              stroke="#ef4444"
              strokeDasharray="4 2"
              label={{
                value: jumpFtMs ? `Takeoff → ${jumpFtMs}ms jump` : "Takeoff",
                position: "insideTopRight",
                fontSize: 10,
                fill: "#ef4444",
              }}
            />
          )}
          <Line type="monotone" dataKey="left" stroke={LEFT_COLOR} strokeWidth={2} dot={<CustomDot />} connectNulls name="left" />
          <Line type="monotone" dataKey="right" stroke={RIGHT_COLOR} strokeWidth={2} dot={<CustomDot />} connectNulls name="right" />
        </LineChart>
      </ResponsiveContainer>
      <div className="flex items-center gap-5 mt-3 justify-center text-xs text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 rounded-full bg-red-500" />
          Takeoff step
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-3 h-3 rounded-full bg-orange-500" />
          Penultimate step
        </div>
        {jumpFtMs && (
          <div className="flex items-center gap-1.5">
            <span className="font-medium text-foreground">Jump flight: {jumpFtMs} ms</span>
          </div>
        )}
      </div>
    </div>
  );
};
