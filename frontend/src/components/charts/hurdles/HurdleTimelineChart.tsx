import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useHurdleTimeline } from "@/hooks/useHurdleTimeline.hooks";
import { chartColors } from "@/lib/chartColors";
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

const TOGGLE_STYLE = (active: boolean, _color: string) =>
  `px-3 py-1.5 rounded-xl text-xs font-semibold border transition-colors ${
    active
      ? `border-transparent text-white`
      : "border-input bg-card text-muted-foreground hover:bg-secondary"
  }`;

export const HurdleTimelineChart = ({ runId }: { runId: string }) => {
  const { timelineData, timelineLoading, timelineError, refetchTimeline } =
    useHurdleTimeline(runId);

  const [showLeft, setShowLeft] = useState(true);
  const [showRight, setShowRight] = useState(true);
  const [showHurdles, setShowHurdles] = useState(true);
  const [showGctLabels, setShowGctLabels] = useState(true);

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
      className={TOGGLE_STYLE(active, color)}
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
          "#3b82f6"
        )}
        {toggleBtn(
          "Right Foot",
          showRight,
          () => setShowRight((v) => !v),
          "#f97316"
        )}
        {toggleBtn(
          "Hurdles",
          showHurdles,
          () => setShowHurdles((v) => !v),
          "#ef4444"
        )}
        {toggleBtn(
          "GCT Labels",
          showGctLabels,
          () => setShowGctLabels((v) => !v),
          "#22c55e"
        )}
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={timelineData.points}
          margin={{ top: 10, right: 40, left: 20, bottom: 40 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={chartColors.border} />
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
            ticks={[0, 1]}
            tickFormatter={(v: number) => (v === 0 ? "Ground" : "Air")}
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
              const point = props.payload;
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
          {showHurdles &&
            timelineData.hurdle_markers.map((m) => (
              <ReferenceLine
                key={m.hurdle_num}
                x={m.time_s}
                stroke="#ef4444"
                strokeDasharray="4 3"
                label={
                  showGctLabels
                    ? {
                        value: `H${m.hurdle_num}`,
                        position: "top",
                        fill: "#ef4444",
                        fontSize: 10,
                      }
                    : undefined
                }
              />
            ))}

          {showLeft && (
            <Line
              type="stepAfter"
              dataKey="left"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              connectNulls={false}
              name="Left"
            />
          )}
          {showRight && (
            <Line
              type="stepAfter"
              dataKey="right"
              stroke="#f97316"
              strokeWidth={2}
              dot={false}
              connectNulls={false}
              name="Right"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
