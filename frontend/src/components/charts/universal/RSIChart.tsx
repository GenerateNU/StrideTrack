import { ChartCard } from "@/components/charts/shared/ChartCard";
import { MeanRSIKPI } from "@/components/charts/universal/MeanRSIKPI";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
import { useCallback, useRef, useState } from "react";
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

export const RSIChart = ({ runId }: ChartProps) => {
  const {
    runMetrics,
    runMetricsIsLoading,
    runMetricsError,
    runMetricsRefetch,
  } = useRunMetrics(runId);

  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = useCallback((state: any) => {
    if (state?.activeTooltipIndex != null) {
      setActiveIndex(state.activeTooltipIndex);
    }
  }, []);

  const handleTouchMove = useCallback(
    (e: React.TouchEvent) => {
      if (!chartRef.current || !runMetrics) return;

      const touch = e.touches[0];
      const plotArea = chartRef.current.querySelector(
        ".recharts-cartesian-grid"
      );
      if (!plotArea) return;

      const rect = plotArea.getBoundingClientRect();
      const x = touch.clientX - rect.left;
      const ratio = x / rect.width;

      if (ratio < 0 || ratio > 1) return;

      const rsiByStride = new Map<number, number[]>();
      for (const m of runMetrics) {
        const rsi = m.gct_ms > 0 ? m.flight_ms / m.gct_ms : 0;
        const existing = rsiByStride.get(m.stride_num);
        if (existing) {
          existing.push(rsi);
        } else {
          rsiByStride.set(m.stride_num, [rsi]);
        }
      }
      const dataLength = rsiByStride.size;

      const index = Math.round(ratio * (dataLength - 1));
      setActiveIndex(Math.max(0, Math.min(dataLength - 1, index)));
    },
    [runMetrics]
  );

  if (runMetricsIsLoading) return <QueryLoading />;
  if (runMetricsError)
    return <QueryError error={runMetricsError} refetch={runMetricsRefetch} />;
  if (!runMetrics || runMetrics.length === 0) return null;

  const rsiByStride = new Map<number, number[]>();
  for (const m of runMetrics) {
    const rsi = m.gct_ms > 0 ? m.flight_ms / m.gct_ms : 0;
    const existing = rsiByStride.get(m.stride_num);
    if (existing) {
      existing.push(rsi);
    } else {
      rsiByStride.set(m.stride_num, [rsi]);
    }
  }

  const rsiData = Array.from(rsiByStride.entries())
    .sort(([a], [b]) => a - b)
    .map(([stride_num, values]) => ({
      stride_num,
      rsi: parseFloat(
        (values.reduce((s, v) => s + v, 0) / values.length).toFixed(3)
      ),
    }));

  const rsiValues = rsiData.map((d) => d.rsi);
  const yMin = Math.min(...rsiValues);
  const yMax = Math.max(...rsiValues);
  const yPadding = (yMax - yMin) * 0.1;

  const meanRSI =
    rsiData.length > 0
      ? rsiData.reduce((s, d) => s + d.rsi, 0) / rsiData.length
      : null;

  const defaultIndex = Math.floor(rsiData.length / 2);
  const resolvedIndex = activeIndex ?? defaultIndex;
  const cursorStride = rsiData[resolvedIndex]?.stride_num;

  return (
    <ChartCard
      title="Reactive Strength Index (RSI)"
      description="Flight time divided by ground contact time per stride. Elite sprinters target RSI > 1.0 at max velocity."
      headerRight={meanRSI != null ? <MeanRSIKPI mean={meanRSI} /> : undefined}
    >
      <div
        ref={chartRef}
        onTouchMove={handleTouchMove}
        style={{ touchAction: "none" }}
      >
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={rsiData}
            margin={{ top: 16, right: 24, left: 0, bottom: 24 }}
            onMouseMove={handleMouseMove}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={chartColors.border} />
            <XAxis
              dataKey="stride_num"
              label={{
                value: "Stride Number",
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
              domain={[
                Math.max(0, parseFloat((yMin - yPadding).toFixed(2))),
                parseFloat((yMax + yPadding).toFixed(2)),
              ]}
              tick={{ fontSize: 11, fill: chartColors.mutedForeground }}
              label={{
                value: "RSI",
                angle: -90,
                position: "insideLeft",
                offset: 10,
                style: {
                  fill: chartColors.mutedForeground,
                  fontSize: 11,
                  textAnchor: "middle",
                },
              }}
            />
            <Tooltip
              cursor={false}
              contentStyle={{
                borderRadius: 12,
                border: "none",
                boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                fontSize: 13,
                backgroundColor: chartColors.card,
                color: chartColors.foreground,
              }}
              formatter={(value) => [value, "RSI"]}
              labelFormatter={(stride) => `Stride ${stride}`}
            />
            <ReferenceLine
              y={1.0}
              stroke={chartColors.primary}
              strokeDasharray="6 3"
              strokeWidth={1.5}
              label={{
                value: "Elite (1.0)",
                position: "insideBottomRight",
                style: { fill: chartColors.primary, fontSize: 10 },
              }}
            />
            {cursorStride != null && (
              <ReferenceLine
                x={cursorStride}
                stroke={chartColors.mutedForeground}
                strokeDasharray="4 4"
                strokeWidth={1}
              />
            )}
            <Line
              type="monotone"
              dataKey="rsi"
              stroke={chartColors.foreground}
              strokeWidth={2}
              name="RSI"
              dot={false}
              activeDot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
};
