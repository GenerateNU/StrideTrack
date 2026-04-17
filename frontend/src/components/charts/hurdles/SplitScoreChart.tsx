import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useSplitScore } from "@/hooks/useSplitScore.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
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
  band1090: [number, number];
  band2575: [number, number];
  diff_s: number;
  diff_pct: number;
}

function getDeviationColor(athletePct: number, p25: number, p75: number) {
  if (athletePct >= p25 && athletePct <= p75) return chartColors.primary;
  return athletePct > p75 ? "#ef4444" : "#22c55e";
}

function CustomTooltip(props: {
  active?: boolean;
  payload?: Array<{ payload: ChartDataPoint }>;
}) {
  const { active, payload } = props;
  if (!active || !payload?.length) return null;

  const data = payload[0]?.payload as ChartDataPoint | undefined;
  if (!data) return null;

  const { athlete, band2575, diff_s, label } = data;
  const [p25, p75] = band2575;
  const isOnPace = athlete >= p25 && athlete <= p75;
  const color = getDeviationColor(athlete, p25, p75);

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
        description="Compares split distribution to population average. Shaded bands = 25th–75th and 10th–90th percentile of elite athletes."
      >
        <QueryLoading />
      </ChartCard>
    );

  if (splitScoreError) {
    return (
      <ChartCard
        title="Split Score Analysis"
        description="Compares split distribution to population average. Shaded bands = 25th–75th and 10th–90th percentile of elite athletes."
      >
        <QueryError
          error={new Error(String(splitScoreError))}
          refetch={() => void splitScoreRefetch()}
        />
      </ChartCard>
    );
  }

  if (!splitScore) return null;

  const { segments, population_mean_pcts, population_percentiles } = splitScore;
  const { p10, p25, p75, p90 } = population_percentiles;

  const allPcts = [
    ...segments.map((s) => s.pct_of_total),
    ...population_mean_pcts,
    ...p10,
    ...p90,
  ];
  const pctMin = Math.min(...allPcts);
  const pctMax = Math.max(...allPcts);
  const pctRange = pctMax - pctMin || 1;
  const yDomain: [number, number] = [
    Math.max(0, pctMin - pctRange * 0.2),
    pctMax + pctRange * 0.1,
  ];

  const chartData: ChartDataPoint[] = segments.map((seg, i) => ({
    label: seg.label,
    athlete: parseFloat(seg.pct_of_total.toFixed(2)),
    ideal: parseFloat(population_mean_pcts[i].toFixed(2)),
    band1090: [parseFloat(p10[i].toFixed(2)), parseFloat(p90[i].toFixed(2))],
    band2575: [parseFloat(p25[i].toFixed(2)), parseFloat(p75[i].toFixed(2))],
    diff_s: seg.diff_s,
    diff_pct: seg.diff_pct,
  }));

  return (
    <ChartCard
      title="Split Score Analysis"
      description="Compares split distribution to population average. Shaded bands = 25th–75th and 10th–90th percentile of elite athletes."
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
            tickFormatter={(value: number) => `${value.toFixed(1)}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="line"
            wrapperStyle={{ fontSize: 11 }}
          />

          {/* 10th–90th percentile band — outer, light */}
          <Area
            type="monotone"
            dataKey="band1090"
            fill={chartColors.mutedForeground}
            fillOpacity={0.05}
            stroke="none"
            legendType="none"
          />

          {/* 25th–75th percentile band — inner, darker */}
          <Area
            type="monotone"
            dataKey="band2575"
            fill={chartColors.mutedForeground}
            fillOpacity={0.15}
            stroke="none"
            legendType="none"
          />

          {/* Population mean */}
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
                payload.band2575[0],
                payload.band2575[1]
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
            activeDot={(props) => {
              const { cx, cy, payload } = props;
              const fill = getDeviationColor(
                payload.athlete,
                payload.band2575[0],
                payload.band2575[1]
              );
              return (
                <circle
                  key={payload.label}
                  cx={cx}
                  cy={cy}
                  r={6}
                  fill={fill}
                  stroke="none"
                />
              );
            }}
            name="Athlete"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};
