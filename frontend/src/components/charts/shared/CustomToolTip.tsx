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

export const CustomTooltip = ({
  active,
  payload,
  label,
}: CustomTooltipProps) => {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="bg-background rounded-xl px-4 py-3 shadow-lg border-none text-sm">
      <p className="font-semibold mb-1.5 text-foreground">Stride {label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.fill || p.color, margin: "2px 0" }}>
          {p.name}: {p.value} ms
        </p>
      ))}
    </div>
  );
};

/*
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
}; */

/*
export const GroundContactTimeChart = ({ runId }: { runId: string }) => {
  const { lrData } = useLROverlayData(runId, "gct_ms");
  return (
    <div
      className="w-full max-w-[900px] mx-auto my-10 bg-white p-6 rounded-2xl 
      shadow-sm border border-slate-100 font-['Inter',system-ui,sans-serif]"
    >
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
            wrapperStyle={{
              paddingTop: 40,
              fontSize: 11,
              paddingLeft: 60,
              color: chartColors.foreground,
            }}
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
    </div>
  );
};

export const FlightTimeChart = ({ runId }: { runId: string }) => {
  const { lrData } = useLROverlayData(runId, "flight_ms");

  return (
    <div className="w-full max-w-[900px] mx-auto my-10 bg-background p-6 rounded-2xl shadow-sm border border-slate-100 font-['Inter',system-ui,sans-serif]">
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
            wrapperStyle={{ paddingTop: 40, fontSize: 11, paddingLeft: 60, color: chartColors.foreground }}
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
    </div>
  );
};

export const StepTimeChart = ({ runId }: { runId: string }) => {
  const { stackedData } =
    useStackedBarData(runId);
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
    <div
      className="w-full max-w-[900px] mx-auto my-10 bg-background p-6 
      rounded-2xl shadow-sm border border-slate-100 font-['Inter',system-ui,sans-serif]"
    >
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
            wrapperStyle={{ paddingTop: 40, fontSize: 11, paddingLeft: 40, color: chartColors.foreground }}
            iconType="circle"
            iconSize={8}
          />

          <Bar
            dataKey="gct_ms"
            stackId="a"
            name="Ground Contact Time"
            fill={chartColors.destructive}
            radius={[0, 0, 0, 0]}
          >
            {stackedData.map((_, i) => (
              <Cell
                key={`gct-${i}`}
                fill={
                  i === activeIndex
                    ? chartColors.destructiveHover
                    : chartColors.destructive
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
    </div>
  );
};
*/
