import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import {
  useLjStepSeries,
  useLongJumpMetrics,
} from "@/hooks/useLongJumpMetrics.hooks";
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

const TITLE = "Flight Time (FT) — Left vs Right Foot";
const DESCRIPTION =
  "Per-foot flight time across the approach with emphasis on the takeoff step. A sharp spike in flight time at the final step confirms a powerful, well-timed board contact. Left/right comparison helps detect any asymmetry in propulsive output.";

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
      <circle
        cx={cx}
        cy={cy}
        r={8}
        fill={chartColors.phaseTakeoff}
        stroke="#fff"
        strokeWidth={2}
      />
    );
  return (
    <circle
      cx={cx}
      cy={cy}
      r={3}
      fill={
        payload.foot === "left" ? chartColors.leftFoot : chartColors.rightFoot
      }
      opacity={0.6}
    />
  );
};

export const LjFlightTimeChart = ({ runId }: ChartProps) => {
  const {
    ljStepSeries,
    ljStepSeriesIsLoading,
    ljStepSeriesError,
    ljStepSeriesRefetch,
  } = useLjStepSeries(runId);
  const { ljMetrics, ljMetricsIsLoading } = useLongJumpMetrics(runId);

  if (ljStepSeriesIsLoading || ljMetricsIsLoading)
    return (
      <ChartCard title={TITLE} description={DESCRIPTION}>
        <QueryLoading />
      </ChartCard>
    );
  if (ljStepSeriesError)
    return (
      <ChartCard title={TITLE} description={DESCRIPTION}>
        <QueryError
          error={ljStepSeriesError}
          refetch={() => void ljStepSeriesRefetch()}
        />
      </ChartCard>
    );
  if (!ljStepSeries) return null;

  const sorted = [...ljStepSeries].sort((a, b) => a.ic_time - b.ic_time);
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
    <ChartCard title={TITLE} description={DESCRIPTION}>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={rows}
          margin={{ top: 8, right: 80, left: 16, bottom: 0 }}
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
              value: "Flight Time (ms)",
              angle: -90,
              position: "insideLeft",
              offset: -4,
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
            formatter={(v) => (v === "left" ? "Left Foot" : "Right Foot")}
          />
          {takeoffRow && (
            <ReferenceLine
              x={takeoffRow.label}
              stroke={chartColors.phaseTakeoff}
              strokeDasharray="4 2"
              label={{
                value: jumpFtMs ? `Takeoff → ${jumpFtMs}ms` : "Takeoff",
                position: "insideTopLeft",
                dx: -90,
                fontSize: 10,
                fill: chartColors.phaseTakeoff,
              }}
            />
          )}
          <Line
            type="monotone"
            dataKey="left"
            stroke={chartColors.leftFoot}
            strokeWidth={2}
            dot={<CustomDot />}
            connectNulls
            name="left"
          />
          <Line
            type="monotone"
            dataKey="right"
            stroke={chartColors.rightFoot}
            strokeWidth={2}
            dot={<CustomDot />}
            connectNulls
            name="right"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};
