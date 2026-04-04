import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useLROverlayData } from "@/hooks/useRunMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import { useCallback, useRef, useState } from "react";
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
import type { CategoricalChartState } from "recharts/types/chart/types";

interface LROverlayLineChartProps {
  runId: string;
  metric: "gct_ms" | "flight_ms";
}

export const LROverlayLineChart = ({
  runId,
  metric,
}: LROverlayLineChartProps) => {
  const { lrOverlay, lrOverlayIsLoading, lrOverlayError, lrOverlayRefetch } =
    useLROverlayData(runId, metric);

  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = useCallback((state: CategoricalChartState) => {
    if (state?.activeTooltipIndex != null) {
      setActiveIndex(state.activeTooltipIndex);
    }
  }, []);

  const handleTouchMove = useCallback(
    (e: React.TouchEvent) => {
      if (!chartRef.current || !lrOverlay) return;

      const touch = e.touches[0];
      const plotArea = chartRef.current.querySelector(
        ".recharts-cartesian-grid"
      );
      if (!plotArea) return;

      const rect = plotArea.getBoundingClientRect();
      const x = touch.clientX - rect.left;
      const ratio = x / rect.width;

      if (ratio < 0 || ratio > 1) return;

      const index = Math.round(ratio * (lrOverlay.length - 1));
      setActiveIndex(Math.max(0, Math.min(lrOverlay.length - 1, index)));
    },
    [lrOverlay]
  );

  if (lrOverlayIsLoading) return <QueryLoading />;
  if (lrOverlayError)
    return (
      <QueryError
        error={lrOverlayError}
        refetch={() => void lrOverlayRefetch()}
      />
    );
  if (!lrOverlay || lrOverlay.length === 0) return null;

  const yValues: number[] = [];
  for (const d of lrOverlay) {
    if (d.left != null) yValues.push(d.left);
    if (d.right != null) yValues.push(d.right);
  }
  const yMin = Math.min(...yValues);
  const yMax = Math.max(...yValues);
  const yPadding = (yMax - yMin) * 0.1;

  const defaultIndex = Math.floor(lrOverlay.length / 2);
  const resolvedIndex = activeIndex ?? defaultIndex;
  const cursorStride = lrOverlay[resolvedIndex]?.stride_num;

  return (
    <div
      ref={chartRef}
      onTouchMove={handleTouchMove}
      style={{ touchAction: "none" }}
    >
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={lrOverlay} onMouseMove={handleMouseMove}>
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
              Math.max(0, Math.floor((yMin - yPadding) / 10) * 10),
              Math.ceil((yMax + yPadding) / 10) * 10,
            ]}
            label={{
              value: "Time (milliseconds)",
              angle: -90,
              position: "insideLeft",
              offset: 0,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
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
            formatter={(value) => [`${value} ms`]}
          />
          <Legend
            verticalAlign="bottom"
            align="center"
            wrapperStyle={{ paddingTop: 40, fontSize: 11, paddingLeft: 60 }}
            iconType="circle"
            iconSize={8}
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
            dataKey="left"
            stroke={chartColors.primary}
            strokeWidth={2}
            name="Left Foot"
            dot={false}
            activeDot={false}
          />
          <Line
            type="monotone"
            dataKey="right"
            stroke={chartColors.foreground}
            strokeWidth={2}
            name="Right Foot"
            dot={false}
            activeDot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
