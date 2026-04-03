import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useSplitScore } from "@/hooks/useSplitScore.hooks";
import { chartColors } from "@/lib/chartColors";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const ON_PACE_THRESHOLD = 0.1;

export const SplitScoreChart = ({ runId }: { runId: string }) => {
  const { splitScoreData, loading, error } = useSplitScore(runId);

  if (loading) return <QueryLoading />;
  if (error)
    return <QueryError error={new Error(error)} refetch={() => void 0} />;
  if (!splitScoreData) return null;

  const { segments, coaching_notes, population_mean_pcts } = splitScoreData;

  const data = segments.map((seg, i) => ({
    label: seg.label,
    athlete: parseFloat(seg.pct_of_total.toFixed(2)),
    ideal: parseFloat(population_mean_pcts[i].toFixed(2)),
    diff_s: seg.diff_s,
    diff_pct: seg.diff_pct,
  }));

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={data}
          margin={{ top: 20, right: 60, left: 20, bottom: 40 }}
        >
          <CartesianGrid vertical={false} stroke={chartColors.border} />
          <XAxis
            dataKey="label"
            label={{
              value: "Segment",
              position: "insideBottom",
              offset: -30,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
            tick={{ fill: chartColors.mutedForeground, fontSize: 9 }}
          />
          <YAxis
            label={{
              value: "% of Total Time",
              angle: -90,
              position: "insideLeft",
              offset: 0,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
            tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
            domain={["auto", "auto"]}
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
            formatter={(value, name, props) => {
              const num = typeof value === "number" ? value : 0;
              if (name === "ideal") return [`${num.toFixed(2)}%`, "Ideal Pace"];
              const diff_s = (props.payload as { diff_s: number }).diff_s;
              const diff_pct = (props.payload as { diff_pct: number }).diff_pct;
              const sign = diff_s > 0 ? "+" : "";
              const direction =
                Math.abs(diff_s) <= ON_PACE_THRESHOLD
                  ? "on pace"
                  : diff_s > 0
                    ? "slower"
                    : "faster";
              return [
                `${num.toFixed(2)}% (${sign}${diff_s.toFixed(2)}s, ${Math.abs(diff_pct).toFixed(1)}% ${direction})`,
                "Athlete",
              ];
            }}
            labelFormatter={(label) => `${label}`}
          />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="line"
            wrapperStyle={{ fontSize: 11 }}
          />
          {/* Ideal pace — population mean curve */}
          <Line
            type="monotone"
            dataKey="ideal"
            stroke={chartColors.mutedForeground}
            strokeWidth={1.5}
            strokeDasharray="4 4"
            dot={false}
            name="Ideal Pace"
          />
          {/* Athlete line with colored dots */}
          <Line
            type="monotone"
            dataKey="athlete"
            stroke={chartColors.primary}
            strokeWidth={2}
            dot={(props) => {
              const { cx, cy, payload } = props;
              const diff_s = payload.diff_s as number;
              const fill =
                Math.abs(diff_s) <= ON_PACE_THRESHOLD
                  ? chartColors.primary
                  : diff_s > 0
                    ? "#ef4444"
                    : "#22c55e";
              return (
                <circle
                  key={payload.label}
                  cx={cx}
                  cy={cy}
                  r={4}
                  fill={fill}
                  stroke="none"
                />
              );
            }}
            activeDot={{ r: 6 }}
            name="Athlete"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Coaching Notes */}
      <div className="mt-4 bg-card border border-border rounded-lg p-4 space-y-1">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
          Coaching Notes
        </p>
        {coaching_notes.map((note, i) => {
          const seg = segments[i];
          let color = "text-foreground";
          if (Math.abs(seg.diff_s) > ON_PACE_THRESHOLD) {
            color = seg.diff_s > 0 ? "text-red-500" : "text-green-500";
          }
          return (
            <p key={i} className={`text-xs leading-snug ${color}`}>
              {note}
            </p>
          );
        })}
      </div>
    </div>
  );
};
