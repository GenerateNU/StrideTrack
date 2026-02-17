import {
  LineChart,
  Line,
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
import type { RunMetric } from "@/hooks/useAthleteRunMetrics";
import { useState } from "react";

const BRAND_COLORS = {
  darkOrange: "#FF6B35",
  lightOrange: "#FFB399",
  highlightDark: "#A52A2A",
  highlightLight: "#E07B5E",
  black: "#000000",
};

interface ChartProps {
  data: RunMetric[];
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    fill?: string;
    color?: string;
  }>;
  label?: string;
}

const transformDataForLROverlay = (
  data: RunMetric[],
  metric: "gct_ms" | "flight_ms"
) => {
  const strideMap = new Map<
    number,
    { stride_num: number; left?: number; right?: number }
  >();

  data.forEach((row) => {
    if (!strideMap.has(row.stride_num)) {
      strideMap.set(row.stride_num, { stride_num: row.stride_num });
    }
    const stride = strideMap.get(row.stride_num)!;
    stride[row.foot as "left" | "right"] = row[metric];
  });

  return Array.from(strideMap.values()).sort(
    (a, b) => a.stride_num - b.stride_num
  );
};

const transformDataForStackedBar = (data: RunMetric[]) => {
  return data
    .map((row) => ({
      stride_num: row.stride_num,
      foot: row.foot,
      label: `${row.stride_num}${row.foot === "left" ? "L" : "R"}`,
      gct_ms: row.gct_ms,
      flight_ms: row.flight_ms,
    }))
    .sort((a, b) => a.stride_num - b.stride_num);
};

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (!active || !payload || !payload.length) return null;
  return (
    <div
      style={{
        background: "white",
        borderRadius: 12,
        padding: "12px 16px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
        border: "none",
        fontSize: 13,
      }}
    >
      <p style={{ fontWeight: 600, marginBottom: 6, color: "#334155" }}>
        Stride {label}
      </p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.fill || p.color, margin: "2px 0" }}>
          {p.name}: {p.value} ms
        </p>
      ))}
    </div>
  );
};

export const GroundContactTimeChart = ({ data }: ChartProps) => {
  const chartData = transformDataForLROverlay(data, "gct_ms");

  return (
    <div
      className="w-full max-w-[900px] mx-auto my-10 bg-white p-6 rounded-2xl 
  shadow-sm border border-slate-100 font-['Inter',system-ui,sans-serif]"
    >
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis
            dataKey="stride_num"
            label={{
              value: "Stride Number",
              position: "insideBottom",
              offset: -5,
              style: { fill: "#64748B", fontSize: 12 },
            }}
          />
          <YAxis
            label={{
              value: "Time (milliseconds)",
              angle: -90,
              position: "insideLeft",
              offset: 0,
              style: { fill: "#64748B", fontSize: 12, textAnchor: "middle" },
            }}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: "none",
              boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
              fontSize: 13,
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
            stroke={BRAND_COLORS.darkOrange}
            strokeWidth={2}
            name="Left Foot"
            dot={{ fill: BRAND_COLORS.darkOrange }}
          />
          <Line
            type="monotone"
            dataKey="right"
            stroke={BRAND_COLORS.black}
            strokeWidth={2}
            name="Right Foot"
            dot={{ fill: BRAND_COLORS.black }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export const FlightTimeChart = ({ data }: ChartProps) => {
  const chartData = transformDataForLROverlay(data, "flight_ms");

  return (
    <div
      className="w-full max-w-[900px] mx-auto my-10 bg-white p-6 rounded-2xl 
  shadow-sm border border-slate-100 font-['Inter',system-ui,sans-serif]"
    >
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis
            dataKey="stride_num"
            label={{
              value: "Stride Number",
              position: "insideBottom",
              offset: -5,
              style: { fill: "#64748B", fontSize: 12 },
            }}
          />
          <YAxis
            label={{
              value: "Time (milliseconds)",
              angle: -90,
              position: "insideLeft",
              offset: 0,
              style: { fill: "#64748B", fontSize: 12, textAnchor: "middle" },
            }}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: "none",
              boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
              fontSize: 13,
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
            stroke={BRAND_COLORS.darkOrange}
            strokeWidth={2}
            name="Left Foot"
            dot={{ fill: BRAND_COLORS.darkOrange }}
          />
          <Line
            type="monotone"
            dataKey="right"
            stroke={BRAND_COLORS.black}
            strokeWidth={2}
            name="Right Foot"
            dot={{ fill: BRAND_COLORS.black }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export const StepTimeChart = ({ data }: ChartProps) => {
  const chartData = transformDataForStackedBar(data);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  const onMouseMove = (state: any) => {
    if (state.activeTooltipIndex !== undefined) {
      setActiveIndex(state.activeTooltipIndex);
    } else {
      setActiveIndex(null);
    }
  };

  return (
    <div
      className="w-full max-w-[900px] mx-auto my-10 bg-white p-6 
  rounded-2xl shadow-sm border border-slate-100 font-['Inter',system-ui,sans-serif]"
    >
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={chartData}
          onMouseMove={onMouseMove}
          onMouseLeave={() => setActiveIndex(null)}
          margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
        >
          <CartesianGrid
            vertical={false}
            strokeDasharray="0"
            stroke="#E2E8F0"
          />
          <XAxis
            dataKey="label"
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#64748B", fontSize: 12 }}
            dy={10}
            label={{
              value: "Step (Stride Number + Foot)",
              position: "insideBottom",
              offset: -30,
              style: { fill: "#64748B", fontSize: 12 },
            }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#64748B", fontSize: 12 }}
            label={{
              value: "Time (milliseconds)",
              angle: -90,
              position: "insideLeft",
              offset: 0,
              style: { fill: "#64748B", fontSize: 12, textAnchor: "middle" },
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
            fill={BRAND_COLORS.darkOrange}
            radius={[0, 0, 0, 0]}
          >
            {chartData.map((_, i) => (
              <Cell
                key={`gct-${i}`}
                fill={
                  i === activeIndex
                    ? BRAND_COLORS.highlightDark
                    : BRAND_COLORS.darkOrange
                }
              />
            ))}
          </Bar>

          <Bar
            dataKey="flight_ms"
            stackId="a"
            name="Flight Time"
            fill={BRAND_COLORS.lightOrange}
            radius={[8, 8, 0, 0]}
          >
            {chartData.map((_, i) => (
              <Cell
                key={`flight-${i}`}
                fill={
                  i === activeIndex
                    ? BRAND_COLORS.highlightLight
                    : BRAND_COLORS.lightOrange
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
