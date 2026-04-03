import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import {
  useTjStepSeries,
  useTripleJumpMetrics,
} from "@/hooks/useTripleJumpMetrics.hooks";
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
  gct_left: number | null;
  gct_right: number | null;
  ft_left: number | null;
  ft_right: number | null;
  foot: string;
}

export const TjPhaseTimelineChart = ({ runId }: { runId: string }) => {
  const {
    stepSeriesData,
    stepSeriesLoading,
    stepSeriesError,
    refetchStepSeriesData,
  } = useTjStepSeries(runId);
  const { tjMetrics, tjMetricsLoading, tjMetricsError, refetchTjMetrics } =
    useTripleJumpMetrics(runId);

  if (stepSeriesLoading || tjMetricsLoading) return <QueryLoading />;
  if (stepSeriesError)
    return (
      <QueryError
        error={stepSeriesError as Error}
        refetch={() => void refetchStepSeriesData()}
      />
    );
  if (tjMetricsError)
    return (
      <QueryError
        error={tjMetricsError as Error}
        refetch={() => void refetchTjMetrics()}
      />
    );
  if (!stepSeriesData || !tjMetrics) return null;

  const sorted = [...stepSeriesData].sort((a, b) => a.ic_time - b.ic_time);
  const rows: StepRow[] = sorted.map((d, i) => ({
    label: i + 1,
    gct_left: d.foot === "left" ? d.gct_ms : null,
    gct_right: d.foot === "right" ? d.gct_ms : null,
    ft_left: d.foot === "left" ? (d.flight_ms ?? null) : null,
    ft_right: d.foot === "right" ? (d.flight_ms ?? null) : null,
    foot: d.foot,
  }));

  const phaseLines = [
    { label: rows[rows.length - 3]?.label, name: "Hop", color: "#3b82f6" },
    { label: rows[rows.length - 2]?.label, name: "Step", color: "#8b5cf6" },
    { label: rows[rows.length - 1]?.label, name: "Jump", color: "#10b981" },
  ];

  const sharedChart = (
    dataKeys: { left: string; right: string },
    leftLabel: string,
    rightLabel: string,
    yAxisLabel: string
  ) => (
    <ResponsiveContainer width="100%" height={250}>
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
            value: yAxisLabel,
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
              name === dataKeys.left ? leftLabel : rightLabel,
            ]) as never
          }
        />
        <Legend
          verticalAlign="bottom"
          align="center"
          wrapperStyle={{ paddingTop: 40, fontSize: 11, paddingLeft: 60 }}
          iconType="circle"
          iconSize={8}
          formatter={(v) => (v === dataKeys.left ? "Left Foot" : "Right Foot")}
        />
        {phaseLines.map(({ label, name, color }) =>
          label ? (
            <ReferenceLine
              key={name}
              x={label}
              stroke={color}
              strokeDasharray="4 2"
              label={{
                value: name,
                position: "insideTopRight",
                fontSize: 9,
                fill: color,
              }}
            />
          ) : null
        )}
        <Line
          type="monotone"
          dataKey={dataKeys.left}
          stroke={LEFT_COLOR}
          strokeWidth={2}
          dot={{ r: 3, fill: LEFT_COLOR }}
          connectNulls
          name={dataKeys.left}
        />
        <Line
          type="monotone"
          dataKey={dataKeys.right}
          stroke={RIGHT_COLOR}
          strokeWidth={2}
          dot={{ r: 3, fill: RIGHT_COLOR }}
          connectNulls
          name={dataKeys.right}
        />
      </LineChart>
    </ResponsiveContainer>
  );

  return (
    <div className="w-full space-y-6">
      <div>
        <h4 className="text-sm font-semibold text-foreground mb-2">
          Ground Contact Time — Approach with Phase Labels
        </h4>
        {sharedChart(
          { left: "gct_left", right: "gct_right" },
          "Left GCT",
          "Right GCT",
          "GCT (ms)"
        )}
      </div>
      <div>
        <h4 className="text-sm font-semibold text-foreground mb-2">
          Flight Time — Approach with Phase Labels
        </h4>
        {sharedChart(
          { left: "ft_left", right: "ft_right" },
          "Left FT",
          "Right FT",
          "Flight Time (ms)"
        )}
      </div>
    </div>
  );
};
