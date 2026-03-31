import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useSplitScore } from "@/hooks/useSplitScore.hooks";
import { chartColors } from "@/lib/chartColors";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const ON_PACE_THRESHOLD = 0.1;

function getBarColor(diff_s: number): string {
  if (Math.abs(diff_s) <= ON_PACE_THRESHOLD) return chartColors.primary;
  return diff_s > 0 ? "#ef4444" : "#22c55e"; // red if slower, green if faster
}

export const SplitScoreChart = ({ runId }: { runId: string }) => {
  const { splitScoreData, loading, error } = useSplitScore(runId);

  if (loading) return <QueryLoading />;
  if (error)
    return <QueryError error={new Error(error)} refetch={() => void 0} />;
  if (!splitScoreData) return null;

  const { segments, coaching_notes } = splitScoreData;

  return (
    <div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={segments}
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
              value: "Diff vs Average (s)",
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
            formatter={(value, _name, props) => {
              const num = typeof value === "number" ? value : 0;
              const diff_pct = (props.payload as { diff_pct: number }).diff_pct;
              const sign = num > 0 ? "+" : "";
              const direction =
                Math.abs(num) <= ON_PACE_THRESHOLD
                  ? "on pace"
                  : num > 0
                    ? "slower"
                    : "faster";
              return [
                `${sign}${num.toFixed(2)}s (${Math.abs(diff_pct).toFixed(1)}% ${direction})`,
                "vs average",
              ];
            }}
          />
          <ReferenceLine
            y={0}
            stroke={chartColors.mutedForeground}
            strokeWidth={1}
          />
          <Bar dataKey="diff_s" radius={[6, 6, 0, 0]} name="Diff vs Average">
            {segments.map((seg, i) => (
              <Cell key={i} fill={getBarColor(seg.diff_s)} />
            ))}
          </Bar>
        </BarChart>
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
