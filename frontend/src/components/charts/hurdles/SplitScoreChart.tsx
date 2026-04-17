import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useSplitScore } from "@/hooks/useSplitScore.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
import axios from "axios";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface ChartDataPoint {
  label: string;
  athlete: number;
  ideal: number;
  stdBand025: [number, number];
  stdBand050: [number, number];
  stdBand100: [number, number];
  std: number;
  diff_s: number;
  diff_pct: number;
}

function getDeviationColor(athletePct: number, idealPct: number, std: number) {
  const deviation = athletePct - idealPct;
  if (Math.abs(deviation) <= std) return chartColors.primary;
  return deviation > 0 ? "#ef4444" : "#22c55e";
}

function CustomTooltip(props: {
  active?: boolean;
  payload?: Array<{ payload: ChartDataPoint }>;
}) {
  const { active, payload } = props;
  if (!active || !payload?.length) return null;

  const data = payload[0]?.payload as ChartDataPoint | undefined;
  if (!data) return null;

  const { athlete, ideal, std, diff_s, label } = data;
  const deviation = athlete - ideal;
  const isOnPace = Math.abs(deviation) <= std;
  const color = getDeviationColor(athlete, ideal, std);

  let text: string;
  if (isOnPace) {
    text = "on pace";
  } else {
    const sign = diff_s > 0 ? "+" : "";
    const direction = diff_s > 0 ? "slower" : "faster";
    text = `${sign}${diff_s.toFixed(2)}s ${direction}`;
  }

  return (
    <div
      style={{
        borderRadius: 12,
        border: "none",
        boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
        fontSize: 13,
        backgroundColor: chartColors.card,
        color: chartColors.foreground,
        padding: "8px 12px",
      }}
    >
      <p style={{ margin: 0, marginBottom: 4, fontWeight: 600 }}>{label}</p>
      <p style={{ margin: 0, color }}>{text}</p>
    </div>
  );
}

export const SplitScoreChart = ({
  runId,
  hurdlesCompleted,
  targetEvent,
}: ChartProps) => {
  const {
    splitScore,
    splitScoreIsLoading,
    splitScoreError,
    splitScoreRefetch,
  } = useSplitScore(runId, hurdlesCompleted ?? null, targetEvent ?? null);

  if (splitScoreIsLoading)
    return (
      <ChartCard
        title="Split Score Analysis"
        description="Compares split distribution to population average. Shaded band = normal range (±1 std dev). Red/green dots = segments outside expected range."
      >
        <QueryLoading />
      </ChartCard>
    );
  if (splitScoreError) {
    const isUnsupported =
      axios.isAxiosError(splitScoreError) &&
      splitScoreError.response?.status === 422;
    if (isUnsupported) {
      return (
        <ChartCard
          title="Split Score Analysis"
          description="Compares split distribution to population average. Shaded band = normal range (±1 std dev). Red/green dots = segments outside expected range."
        >
          <p className="text-sm text-muted-foreground py-6 text-center">
            Split score analysis is only available for 400m events.
          </p>
        </ChartCard>
      );
    }
    return (
      <ChartCard
        title="Split Score Analysis"
        description="Compares split distribution to population average. Shaded band = normal range (±1 std dev). Red/green dots = segments outside expected range."
      >
        <QueryError
          error={new Error(String(splitScoreError))}
          refetch={() => void splitScoreRefetch()}
        />
      </ChartCard>
    );
  }
  if (!splitScore) return null;

  const { segments, population_mean_pcts, population_std_pcts } = splitScore;

  const allPcts = [
    ...segments.map((s) => s.pct_of_total),
    ...population_mean_pcts,
    ...population_mean_pcts.map((m, i) => m + population_std_pcts[i]),
    ...population_mean_pcts.map((m, i) => m - population_std_pcts[i]),
  ];
  const pctMin = Math.min(...allPcts);
  const pctMax = Math.max(...allPcts);
  const pctRange = pctMax - pctMin || 1;
  const yDomain: [number, number] = [
    Math.max(0, pctMin - pctRange * 0.2),
    pctMax + pctRange * 0.1,
  ];

  const chartData: ChartDataPoint[] = segments.map((seg, i) => {
    const mean = population_mean_pcts[i];
    const std = population_std_pcts[i];
    return {
      label: seg.label,
      athlete: parseFloat(seg.pct_of_total.toFixed(2)),
      ideal: parseFloat(mean.toFixed(2)),
      stdBand025: [
        parseFloat((mean - std * 0.25).toFixed(2)),
        parseFloat((mean + std * 0.25).toFixed(2)),
      ],
      stdBand050: [
        parseFloat((mean - std * 0.5).toFixed(2)),
        parseFloat((mean + std * 0.5).toFixed(2)),
      ],
      stdBand100: [
        parseFloat((mean - std).toFixed(2)),
        parseFloat((mean + std).toFixed(2)),
      ],
      std,
      diff_s: seg.diff_s,
      diff_pct: seg.diff_pct,
    };
  });

  return (
    <ChartCard
      title="Split Score Analysis"
      description="Compares split distribution to population average. Shaded band = normal range (±1 std dev). Red/green dots = segments outside expected range."
    >
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 60, left: 20, bottom: 40 }}
        >
          <CartesianGrid vertical={false} stroke={chartColors.border} />
          <XAxis
            dataKey="label"
            label={{
              value: "Segment",
              position: "insideBottom",
              offset: -30,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
            tick={{ fill: chartColors.mutedForeground, fontSize: 9 }}
          />
          <YAxis
            label={{
              value: "% of Total Time",
              angle: -90,
              position: "insideLeft",
              offset: 0,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
            tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
            domain={yDomain}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="line"
            wrapperStyle={{ fontSize: 11 }}
          />

          {/* +/-1 std dev -- outermost, very light */}
          <Area
            type="monotone"
            dataKey="stdBand100"
            fill={chartColors.mutedForeground}
            fillOpacity={0.05}
            stroke="none"
            legendType="none"
          />
          {/* +/-0.5 std dev -- middle band */}
          <Area
            type="monotone"
            dataKey="stdBand050"
            fill={chartColors.mutedForeground}
            fillOpacity={0.1}
            stroke="none"
            legendType="none"
          />
          {/* +/-0.25 std dev -- innermost, darkest */}
          <Area
            type="monotone"
            dataKey="stdBand025"
            fill={chartColors.mutedForeground}
            fillOpacity={0.15}
            stroke="none"
            legendType="none"
          />

          {/* Ideal pace -- population mean curve */}
          <Line
            type="monotone"
            dataKey="ideal"
            stroke={chartColors.mutedForeground}
            strokeWidth={1.5}
            strokeDasharray="4 4"
            dot={false}
            name="Ideal Pace"
          />

          {/* Athlete line with colored dots */}
          <Line
            type="monotone"
            dataKey="athlete"
            stroke={chartColors.primary}
            strokeWidth={2}
            dot={(props) => {
              const { cx, cy, payload } = props;
              const fill = getDeviationColor(
                payload.athlete,
                payload.ideal,
                payload.std
              );
              return (
                <circle
                  key={payload.label}
                  cx={cx}
                  cy={cy}
                  r={4}
                  fill={fill}
                  stroke="none"
                />
              );
            }}
            activeDot={{ r: 6 }}
            name="Athlete"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};
