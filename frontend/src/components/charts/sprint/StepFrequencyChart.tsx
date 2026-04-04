import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useStepFrequencyData } from "@/hooks/useRunMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
import { useCallback, useRef, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const StepFrequencyChart = ({ runId }: ChartProps) => {
  const {
    stepFrequency,
    stepFrequencyIsLoading,
    stepFrequencyError,
    stepFrequencyRefetch,
  } = useStepFrequencyData(runId);

  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = useCallback((state: any) => {
    if (state?.activeTooltipIndex != null) {
      setActiveIndex(state.activeTooltipIndex);
    }
  }, []);

  const handleTouchMove = useCallback(
    (e: React.TouchEvent) => {
      if (!chartRef.current || !stepFrequency) return;

      const touch = e.touches[0];
      const plotArea = chartRef.current.querySelector(
        ".recharts-cartesian-grid"
      );
      if (!plotArea) return;

      const rect = plotArea.getBoundingClientRect();
      const x = touch.clientX - rect.left;
      const ratio = x / rect.width;

      if (ratio < 0 || ratio > 1) return;

      const strideCount = new Set(stepFrequency.map((d) => d.stride_num)).size;
      const index = Math.round(ratio * (strideCount - 1));
      setActiveIndex(Math.max(0, Math.min(strideCount - 1, index)));
    },
    [stepFrequency]
  );

  if (stepFrequencyIsLoading) return <QueryLoading />;
  if (stepFrequencyError)
    return (
      <QueryError error={stepFrequencyError} refetch={stepFrequencyRefetch} />
    );
  if (!stepFrequency || stepFrequency.length === 0) return null;

  const strideNums = [...new Set(stepFrequency.map((d) => d.stride_num))];

  const chartData = strideNums.map((strideNum) => {
    const leftStep = stepFrequency.find(
      (d) => d.stride_num === strideNum && d.foot === "left"
    );
    const rightStep = stepFrequency.find(
      (d) => d.stride_num === strideNum && d.foot === "right"
    );
    return {
      stride_num: strideNum,
      left: leftStep?.step_frequency_hz,
      right: rightStep?.step_frequency_hz,
    };
  });

  const yValues: number[] = [];
  for (const d of chartData) {
    if (d.left != null) yValues.push(d.left);
    if (d.right != null) yValues.push(d.right);
  }
  const yMin = Math.min(...yValues);
  const yMax = Math.max(...yValues);
  const yPadding = (yMax - yMin) * 0.1;

  const accelEndStride = strideNums[Math.floor(strideNums.length * 0.4)] ?? 0;

  const defaultIndex = Math.floor(chartData.length / 2);
  const resolvedIndex = activeIndex ?? defaultIndex;
  const cursorStride = chartData[resolvedIndex]?.stride_num;

  return (
    <ChartCard
      title="Step Frequency"
      description="Steps per second (Hz) across the run. Optimal zone varies by event and athlete."
    >
      <div
        ref={chartRef}
        onTouchMove={handleTouchMove}
        style={{ touchAction: "none" }}
      >
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} onMouseMove={handleMouseMove}>
            <ReferenceArea
              x1={strideNums[0]}
              x2={accelEndStride}
              fill={chartColors.primary}
              fillOpacity={0.08}
              label={{
                value: "Acceleration Phase",
                position: "insideTopLeft",
                fontSize: 10,
                fill: chartColors.mutedForeground,
              }}
            />
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
              label={{
                value: "Frequency (Hz)",
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
              formatter={(value) => [`${value} Hz`]}
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
              name="Left Foot"
              stroke={chartColors.primary}
              strokeWidth={2}
              dot={false}
              activeDot={false}
            />
            <Line
              type="monotone"
              dataKey="right"
              name="Right Foot"
              stroke={chartColors.foreground}
              strokeWidth={2}
              dot={false}
              activeDot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
};
