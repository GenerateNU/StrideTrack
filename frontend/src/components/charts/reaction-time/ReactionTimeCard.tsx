import { useReactionTimeMetrics } from "@/hooks/useReactionTimeMetrics.hooks";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import { ChartCard } from "@/components/charts/shared/ChartCard";
import type { ChartProps } from "@/types/chart.types";

function getZoneStyles(zone: string | undefined): {
  label: string;
  value: string;
} {
  switch (zone) {
    case "green":
      return { label: "Excellent", value: "text-green-500" };
    case "yellow":
      return { label: "Average", value: "text-yellow-400" };
    case "red":
      return { label: "Slow", value: "text-red-500" };
    default:
      return { label: "—", value: "text-foreground" };
  }
}

export const ReactionTimeCard = ({ runId }: ChartProps) => {
  const {
    reactionTime,
    reactionTimeIsLoading,
    reactionTimeError,
    reactionTimeRefetch,
  } = useReactionTimeMetrics(runId);

  if (reactionTimeIsLoading) return <QueryLoading />;
  if (reactionTimeError)
    return (
      <QueryError
        error={reactionTimeError}
        refetch={() => void reactionTimeRefetch()}
      />
    );

  const value = reactionTime?.reaction_time_ms;
  const styles = getZoneStyles(reactionTime?.zone);

  return (
    <ChartCard
      title="Reaction Time"
      description="Time from start signal to first foot lift-off. Green < 200ms, Yellow 200-300ms, Red > 300ms."
    >
      <div className="flex flex-col items-center justify-center h-[200px] gap-1">
        <span className={`text-4xl font-bold ${styles.value}`}>
          {value != null ? value.toFixed(1) : "—"}
          <span className="text-sm font-normal text-muted-foreground ml-1">
            ms
          </span>
        </span>
        <span className={`text-xs font-medium ${styles.value}`}>
          {styles.label}
        </span>
        <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
          <span className="text-green-500">● &lt;200ms</span>
          <span className="text-yellow-400">● 200–300ms</span>
          <span className="text-red-500">● &gt;300ms</span>
        </div>
      </div>
    </ChartCard>
  );
};
