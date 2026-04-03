import { useReactionTimeMetrics } from "@/hooks/useReactionTimeMetrics.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";

interface ReactionTimeCardProps {
  runId: string;
}

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
      return { dot: "bg-muted", label: "—", value: "text-foreground" };
  }
}

export const ReactionTimeCard = ({ runId }: ReactionTimeCardProps) => {
  const { rtMetrics, rtLoading, rtError, rtRefetch } =
    useReactionTimeMetrics(runId);

  if (rtLoading) return <QueryLoading />;
  if (rtError)
    return <QueryError error={rtError} refetch={() => void rtRefetch()} />;
  if (!rtMetrics) return null;

  const value = rtMetrics.reaction_time_ms;
  const styles = getZoneStyles(rtMetrics.zone);

  return (
    <div className="flex flex-col items-center justify-center h-[300px] gap-2">
      <span className="text-sm text-muted-foreground uppercase tracking-widest">
        Reaction Time
      </span>
      <span className={`text-6xl font-bold ${styles.value}`}>
        {value != null ? value.toFixed(1) : "—"}
        <span className="text-lg font-normal text-muted-foreground ml-1">
          ms
        </span>
      </span>
      <span className={`text-sm font-medium ${styles.value}`}>
        {styles.label}
      </span>
      <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
        <span className="text-green-500">● &lt;200ms</span>
        <span className="text-yellow-400">● 200–300ms</span>
        <span className="text-red-500">● &gt;300ms</span>
      </div>
      <span className="text-xs text-muted-foreground mt-2 text-center max-w-[200px]">
        Time from start stimulus to first GCT onset
      </span>
    </div>
  );
};
