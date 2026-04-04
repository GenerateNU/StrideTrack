import type { ChartProps } from "@/types/chart.types";
import { BaseKPI } from "@/components/charts/shared/BaseKPI";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import { useReactionTimeMetrics } from "@/hooks/useReactionTimeMetrics.hooks";

function getZoneStyles(zone: string | undefined): {
  dot: string;
  label: string;
  value: string;
} {
  switch (zone) {
    case "green":
      return {
        dot: "bg-green-500",
        label: "Excellent",
        value: "text-green-500",
      };
    case "yellow":
      return {
        dot: "bg-yellow-400",
        label: "Average",
        value: "text-yellow-400",
      };
    case "red":
      return { dot: "bg-red-500", label: "Slow", value: "text-red-500" };
    default:
      return { dot: "bg-muted", label: "\u2014", value: "text-foreground" };
  }
}

export const ReactionTimeCard = ({ runId }: ChartProps) => {
  const { reactionTime, reactionTimeIsLoading, reactionTimeError, reactionTimeRefetch } =
    useReactionTimeMetrics(runId);

  if (reactionTimeIsLoading) return <QueryLoading />;
  if (reactionTimeError)
    return <QueryError error={reactionTimeError} refetch={() => void reactionTimeRefetch()} />;
  if (!reactionTime) return null;

  const value = reactionTime.reaction_time_ms;
  const styles = getZoneStyles(reactionTime.zone);

  return (
    <BaseKPI description="Time from start stimulus to first ground contact onset. Green < 200ms, Yellow 200-300ms, Red > 300ms.">
      <div className="flex flex-col items-center justify-center h-[300px] gap-2">
        <span className="text-sm text-muted-foreground uppercase tracking-widest">
          Reaction Time
        </span>
        <span className={`text-6xl font-bold ${styles.value}`}>
          {value != null ? value.toFixed(1) : "\u2014"}
          <span className="text-lg font-normal text-muted-foreground ml-1">
            ms
          </span>
        </span>
        <span className={`text-sm font-medium ${styles.value}`}>
          {styles.label}
        </span>
        <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
          <span className="text-green-500">&bull; &lt;200ms</span>
          <span className="text-yellow-400">&bull; 200&ndash;300ms</span>
          <span className="text-red-500">&bull; &gt;300ms</span>
        </div>
        <span className="text-xs text-muted-foreground mt-2 text-center max-w-[200px]">
          Time from start stimulus to first GCT onset
        </span>
      </div>
    </BaseKPI>
  );
};
