import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useState } from "react";
import { chartColors } from "@/lib/chartColors";
import { useStackedBarData } from "@/hooks/useRunMetrics";
import "@/index.css";
import { CustomTooltip } from "@/components/charts/CustomToolTip";

export const StepTimeChart = ({ runId }: { runId: string }) => {
  const { stackedData } = useStackedBarData(runId);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const onMouseMove = (state: any) => {
    if (state.activeTooltipIndex !== undefined) {
      setActiveIndex(state.activeTooltipIndex);
    } else {
      setActiveIndex(null);
    }
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={stackedData}
        onMouseMove={onMouseMove}
        onMouseLeave={() => setActiveIndex(null)}
        margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
      >
        <CartesianGrid
          vertical={false}
          strokeDasharray="0"
          stroke={chartColors.border}
        />
        <XAxis
          dataKey="label"
          axisLine={false}
          tickLine={false}
          tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
          dy={10}
          label={{
            value: "Step (Stride Number + Foot)",
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
        <Tooltip content={<CustomTooltip />} cursor={false} />
        <Legend
          verticalAlign="bottom"
          align="center"
          wrapperStyle={{ paddingTop: 40, fontSize: 11, paddingLeft: 40 }}
          iconType="circle"
          iconSize={8}
        />

        <Bar
          dataKey="gct_ms"
          stackId="a"
          name="Ground Contact Time"
          fill={chartColors.primary}
          radius={[0, 0, 0, 0]}
        >
          {stackedData.map((_, i) => (
            <Cell
              key={`gct-${i}`}
              fill={
                i === activeIndex
                  ? chartColors.primaryHover
                  : chartColors.primary
              }
            />
          ))}
        </Bar>

        <Bar
          dataKey="flight_ms"
          stackId="a"
          name="Flight Time"
          fill={chartColors.mutedForeground}
          radius={[8, 8, 0, 0]}
        >
          {stackedData.map((_, i) => (
            <Cell
              key={`flight-${i}`}
              fill={
                i === activeIndex
                  ? chartColors.mutedForegroundHover
                  : chartColors.mutedForeground
              }
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};
