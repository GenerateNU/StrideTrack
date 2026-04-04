import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceArea,
  ResponsiveContainer,
} from "recharts";
import { chartColors } from "@/lib/chartColors";
import { useStepFrequencyData } from "@/hooks/useRunMetrics.hooks";
import "@/index.css";
import { CustomTooltip } from "@/components/charts/shared/CustomToolTip";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import type { ChartProps } from "@/types/chart.types";
import { ChartCard } from "@/components/charts/shared/ChartCard";

export const StepFrequencyChart = ({ runId }: ChartProps) => {
  const {
    stepFrequency,
    stepFrequencyIsLoading,
    stepFrequencyError,
    stepFrequencyRefetch,
  } = useStepFrequencyData(runId);

  if (stepFrequencyIsLoading) return <QueryLoading />;
  if (stepFrequencyError)
    return (
      <QueryError error={stepFrequencyError} refetch={stepFrequencyRefetch} />
    );
  if (!stepFrequency) return null;

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

  const accelEndStride = strideNums[Math.floor(strideNums.length * 0.4)] ?? 0;

  return (
    <ChartCard
      title="Step Frequency"
      description="Steps per second (Hz) across the run. Optimal zone varies by event and athlete."
    >
      <div className="overflow-x-auto">
        <div style={{ minWidth: Math.max(chartData.length * 20, 0) }}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={chartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
            >
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
          <CartesianGrid
            vertical={false}
            strokeDasharray="0"
            stroke={chartColors.border}
          />
          <XAxis
            dataKey="stride_num"
            axisLine={false}
            tickLine={false}
            tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
            dy={10}
            label={{
              value: "Stride Number",
              position: "insideBottom",
              offset: -30,
              style: { fill: chartColors.mutedForeground, fontSize: 10 },
            }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
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
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            align="center"
            wrapperStyle={{ paddingTop: 40, fontSize: 11, paddingLeft: 40 }}
            iconType="circle"
            iconSize={8}
          />
          <Line
            type="monotone"
            dataKey="left"
            name="Left Foot"
            stroke={chartColors.primary}
            dot={false}
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="right"
            name="Right Foot"
            stroke={chartColors.mutedForeground}
            dot={false}
            strokeWidth={2}
          />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </ChartCard>
  );
};
