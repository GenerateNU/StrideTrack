import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import {
  useTjStepSeries,
  useTripleJumpMetrics,
} from "@/hooks/useTripleJumpMetrics.hooks";
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
  gct_left: number | null;
  gct_right: number | null;
  ft_left: number | null;
  ft_right: number | null;
  foot: string;
}

export const TjPhaseTimelineChart = ({ runId }: ChartProps) => {
  const {
    tjStepSeries,
    tjStepSeriesIsLoading,
    tjStepSeriesError,
    tjStepSeriesRefetch,
  } = useTjStepSeries(runId);
  const {
    tjMetrics,
    tjMetricsIsLoading,
    tjMetricsError,
    tjMetricsRefetch,
  } = useTripleJumpMetrics(runId);

  if (tjStepSeriesIsLoading || tjMetricsIsLoading) return <QueryLoading />;
  if (tjStepSeriesError)
    return <QueryError error={tjStepSeriesError} refetch={tjStepSeriesRefetch} />;
  if (tjMetricsError)
    return <QueryError error={tjMetricsError} refetch={tjMetricsRefetch} />;
  if (!tjStepSeries || !tjMetrics) return null;

  const sorted = [...tjStepSeries].sort((a, b) => a.ic_time - b.ic_time);
  const rows: StepRow[] = sorted.map((d, i) => ({
    label: i + 1,
    gct_left: d.foot === "left" ? d.gct_ms : null,
    gct_right: d.foot === "right" ? d.gct_ms : null,
    ft_left: d.foot === "left" ? (d.flight_ms ?? null) : null,
    ft_right: d.foot === "right" ? (d.flight_ms ?? null) : null,
    foot: d.foot,
  }));

  const phaseLines = [
    { label: rows[rows.length - 3]?.label, name: "Hop", color: chartColors.phaseHop },
    { label: rows[rows.length - 2]?.label, name: "Step", color: chartColors.phaseStep },
    { label: rows[rows.length - 1]?.label, name: "Jump", color: chartColors.phaseJump },
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
            value: yAxisLabel,
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
          stroke={chartColors.leftFoot}
          strokeWidth={2}
          dot={{ r: 3, fill: chartColors.leftFoot }}
          connectNulls
          name={dataKeys.left}
        />
        <Line
          type="monotone"
          dataKey={dataKeys.right}
          stroke={chartColors.rightFoot}
          strokeWidth={2}
          dot={{ r: 3, fill: chartColors.rightFoot }}
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
