import { useLROverlayData } from "@/hooks/useRunMetrics";
import { chartColors } from "@/lib/chartColors";
import {
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid,
  Tooltip, 
  Legend, 
  ResponsiveContainer,
} from "recharts";

interface LROverlayLineChartProps {
  runId: string;
  metric: "gct_ms" | "flight_ms";
}

export const LROverlayLineChart = ({ runId, metric }: LROverlayLineChartProps) => {
  const { lrData } = useLROverlayData(runId, metric);

  return (
    <ResponsiveContainer width="100%" height={300}>
    <LineChart data={lrData}>
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
        <Line
        type="monotone"
        dataKey="left"
        stroke={chartColors.destructive}
        strokeWidth={2}
        name="Left Foot"
        dot={{ fill: chartColors.destructive }}
        />
        <Line
        type="monotone"
        dataKey="right"
        stroke={chartColors.foreground}
        strokeWidth={2}
        name="Right Foot"
        dot={{ fill: chartColors.foreground }}
        />
    </LineChart>
    </ResponsiveContainer>
  );
};