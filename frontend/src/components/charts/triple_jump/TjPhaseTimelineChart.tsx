import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import {
  useTjStepSeries,
  useTripleJumpMetrics,
} from "@/hooks/useTripleJumpMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
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

interface ChartRow {
  index: number;
  gct_left: number | null;
  gct_right: number | null;
  ft_left: number | null;
  ft_right: number | null;
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

  const strideNums = [...new Set(stepSeriesData.map((d) => d.stride_num))].sort(
    (a, b) => a - b
  );
  const rows: ChartRow[] = strideNums.map((stride) => {
    const l = stepSeriesData.find(
      (d) => d.stride_num === stride && d.foot === "left"
    );
    const r = stepSeriesData.find(
      (d) => d.stride_num === stride && d.foot === "right"
    );
    return {
      index: stride,
      gct_left: l?.gct_ms ?? null,
      gct_right: r?.gct_ms ?? null,
      ft_left: l?.flight_ms ?? null,
      ft_right: r?.flight_ms ?? null,
    };
  });

  const lastStride = strideNums[strideNums.length - 1] ?? 0;
  const phaseLines = [
    { x: lastStride, label: "Board / Hop", color: "#3b82f6" },
    { x: lastStride + 1, label: "Step", color: "#8b5cf6" },
    { x: lastStride + 2, label: "Jump", color: "#10b981" },
  ];

  const sharedChart = (
    dataKeys: { left: string; right: string },
    leftLabel: string,
    rightLabel: string
  ) => (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={rows} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis
          dataKey="index"
          tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
          label={{
            value: "Stride",
            position: "insideBottomRight",
            offset: -4,
            fontSize: 11,
            fill: "var(--muted-foreground)",
          }}
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
          formatter={(value: number, name: string) => [
            `${value} ms`,
            name === dataKeys.left ? leftLabel : rightLabel,
          ]}
        />
        <Legend
          formatter={(v) => (v === dataKeys.left ? "Left" : "Right")}
          wrapperStyle={{ fontSize: 12 }}
        />
        {phaseLines.map(({ x, label, color }) => (
          <ReferenceLine
            key={label}
            x={x}
            stroke={color}
            strokeDasharray="4 2"
            label={{
              value: label,
              position: "insideTopRight",
              fontSize: 9,
              fill: color,
            }}
          />
        ))}
        <Line
          type="monotone"
          dataKey={dataKeys.left}
          stroke={chartColors.left}
          strokeWidth={2}
          dot={{ r: 3 }}
          connectNulls
          name={dataKeys.left}
        />
        <Line
          type="monotone"
          dataKey={dataKeys.right}
          stroke={chartColors.right}
          strokeWidth={2}
          dot={{ r: 3 }}
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
          "Right GCT"
        )}
      </div>
      <div>
        <h4 className="text-sm font-semibold text-foreground mb-2">
          Flight Time — Approach with Phase Labels
        </h4>
        {sharedChart(
          { left: "ft_left", right: "ft_right" },
          "Left FT",
          "Right FT"
        )}
      </div>
    </div>
  );
};
