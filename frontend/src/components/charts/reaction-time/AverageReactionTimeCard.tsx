import { useAverageReactionTime } from "@/hooks/useAverageReactionTime.hooks";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";

interface AverageReactionTimeCardProps {
  athleteId: string;
}

function getZoneColor(zone: string | undefined): string {
  switch (zone) {
    case "green":
      return "text-green-500";
    case "yellow":
      return "text-yellow-400";
    case "red":
      return "text-red-500";
    default:
      return "text-foreground";
  }
}

export const AverageReactionTimeCard = ({
  athleteId,
}: AverageReactionTimeCardProps) => {
  const {
    avgReactionTime,
    avgReactionTimeIsLoading,
    avgReactionTimeError,
    avgReactionTimeRefetch,
  } = useAverageReactionTime(athleteId);

  if (avgReactionTimeIsLoading) return <QueryLoading />;
  if (avgReactionTimeError)
    return (
      <QueryError
        error={avgReactionTimeError}
        refetch={() => void avgReactionTimeRefetch()}
      />
    );
  if (!avgReactionTime) return null;

  const colorClass = getZoneColor(avgReactionTime.zone);

  return (
    <div className="rounded-2xl border border-border bg-card p-4 shadow-sm shadow-foreground/[0.02]">
      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
        Avg Reaction Time
      </p>
      <p className={`text-2xl font-bold ${colorClass}`}>
        {avgReactionTime.average_reaction_time_ms.toFixed(1)}
        <span className="text-sm font-normal text-muted-foreground ml-1">
          ms
        </span>
      </p>
      <p className="text-xs text-muted-foreground mt-1">
        {avgReactionTime.zone_description} · {avgReactionTime.run_count} run
        {avgReactionTime.run_count !== 1 ? "s" : ""}
      </p>
    </div>
  );
};
