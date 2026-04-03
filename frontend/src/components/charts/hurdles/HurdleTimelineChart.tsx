import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useHurdleTimeline } from "@/hooks/useHurdleTimeline.hooks";
import { chartColors } from "@/lib/chartColors";
import type { HurdleTimelinePoint } from "@/types/hurdleTimeline.types";
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
import { useState } from "react";

const COLORS = {
  left: "#f97316",
  right: "#000000",
  hurdles: "#ef4444",
  gctLabels: "#22c55e",
  ftLabels: "#a855f7",
} as const;

const TOGGLE_STYLE = (active: boolean) =>
  `px-3 py-1.5 rounded-xl text-xs font-semibold border transition-colors ${
    active
      ? `border-transparent text-white`
      : "border-input bg-card text-muted-foreground hover:bg-secondary"
  }`;

const makeGctDot =
  (show: boolean, color: string) =>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (props: any) => {
    const { cx, cy, payload, index, data } = props as {
      cx: number;
      cy: number;
      payload: HurdleTimelinePoint;
      index: number;
      data: HurdleTimelinePoint[];
    };
    if (!show || payload.phase !== "ground" || !payload.gct_ms) return null;
    if (!data) return null;
    const prev = data[index - 1];
    if (prev && prev.foot === payload.foot && prev.phase === "ground")
      return null;
    return (
      <text
        key={`gct-${index}`}
        x={cx}
        y={cy + 14}
        textAnchor="middle"
        fontSize={9}
        fill={color}
      >
        {payload.gct_ms}
      </text>
    );
  };

const makeFtDot =
  (show: boolean, color: string) =>
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (props: any) => {
    const { cx, cy, payload, index, data } = props as {
      cx: number;
      cy: number;
      payload: HurdleTimelinePoint;
      index: number;
      data: HurdleTimelinePoint[];
    };
    if (!show || payload.phase !== "air" || !payload.ft_ms) return null;
    if (!data) return null;
    const prev = data[index - 1];
    if (prev && prev.foot === payload.foot && prev.phase === "air") return null;
    return (
      <text
        key={`ft-${index}`}
        x={cx}
        y={cy - 6}
        textAnchor="middle"
        fontSize={9}
        fill={color}
      >
        {payload.ft_ms}
      </text>
    );
  };

export const HurdleTimelineChart = ({ runId }: { runId: string }) => {
  const { timelineData, timelineLoading, timelineError, refetchTimeline } =
    useHurdleTimeline(runId);

  const [showLeft, setShowLeft] = useState(true);
  const [showRight, setShowRight] = useState(true);

  if (timelineLoading) return <QueryLoading />;
  if (timelineError)
    return (
      <QueryError
        error={timelineError as Error}
        refetch={() => void refetchTimeline()}
      />
    );
  if (!timelineData || timelineData.points.length === 0) return null;

  const toggleBtn = (
    label: string,
    active: boolean,
    onToggle: () => void,
    color: string
  ) => (
    <button
      type="button"
      onClick={onToggle}
      className={TOGGLE_STYLE(active)}
      style={active ? { backgroundColor: color, borderColor: color } : {}}
    >
      {label}
    </button>
  );

  return (
    <div>
      {/* Toggles */}
      <div className="mb-3 flex flex-wrap gap-2">
        {toggleBtn(
          "Left Foot",
          showLeft,
          () => setShowLeft((v) => !v),
          COLORS.left
        )}
        {toggleBtn(
          "Right Foot",
          showRight,
          () => setShowRight((v) => !v),
          COLORS.right
        )}
      </div>

      <div className="overflow-x-auto">
        <div style={{ minWidth: 1200 }}>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={timelineData.points}
              margin={{ top: 20, right: 40, left: 20, bottom: 40 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke={chartColors.border}
              />
              <XAxis
                dataKey="time_s"
                type="number"
                domain={["dataMin", "dataMax"]}
                tickFormatter={(v: number) => `${v.toFixed(1)}`}
                label={{
                  value: "Time (s)",
                  position: "insideBottom",
                  offset: -25,
                  style: {
                    fill: chartColors.mutedForeground,
                    fontSize: 10,
                    textAnchor: "middle",
                  },
                }}
                tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
              />
              <YAxis
                tickFormatter={(v: number) => (v === 0 ? "Ground" : `${v}ms`)}
                tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
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
                formatter={(_value, _name, props) => {
                  const point = props.payload as HurdleTimelinePoint;
                  const phase = point.phase === "air" ? "Air" : "Ground";
                  const footLabel = point.foot === "left" ? "Left" : "Right";
                  const duration =
                    point.phase === "air" && point.ft_ms != null
                      ? `FT: ${point.ft_ms}ms`
                      : point.gct_ms != null
                        ? `GCT: ${point.gct_ms}ms`
                        : "";
                  return [
                    `${footLabel}: ${phase}${duration ? ` — ${duration}` : ""}`,
                  ];
                }}
                labelFormatter={(label) => `${(label as number).toFixed(3)}s`}
              />

              {/* Hurdle reference lines */}
              {timelineData.hurdle_markers.map((m) => (
                <ReferenceLine
                  key={m.hurdle_num}
                  x={m.time_s}
                  stroke={COLORS.hurdles}
                  strokeDasharray="4 3"
                  label={{
                    value: `H${m.hurdle_num}`,
                    position: "top",
                    fill: COLORS.hurdles,
                    fontSize: 10,
                  }}
                />
              ))}

              {showLeft && (
                <Line
                  type="basis"
                  dataKey="left"
                  stroke={COLORS.left}
                  strokeWidth={2}
                  dot={makeGctDot(true, COLORS.gctLabels)}
                  connectNulls={false}
                  name="Left"
                />
              )}
              {showRight && (
                <Line
                  type="basis"
                  dataKey="right"
                  stroke={COLORS.right}
                  strokeWidth={2}
                  dot={makeFtDot(true, COLORS.ftLabels)}
                  connectNulls={false}
                  name="Right"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
