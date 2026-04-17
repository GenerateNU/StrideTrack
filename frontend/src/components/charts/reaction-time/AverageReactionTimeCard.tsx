import { useAverageReactionTime } from "@/hooks/useAverageReactionTime.hooks";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import axios from "axios";
import { Timer } from "lucide-react";

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

  if (avgReactionTimeError) {
    const is404 =
      axios.isAxiosError(avgReactionTimeError) &&
      avgReactionTimeError.response?.status === 404;
    if (is404) return null;
    return (
      <QueryError
        error={avgReactionTimeError}
        refetch={() => void avgReactionTimeRefetch()}
      />
    );
  }

  if (!avgReactionTime) return null;

  const colorClass = getZoneColor(avgReactionTime.zone);

  return (
    <div className="rounded-2xl border border-border bg-card p-4 shadow-sm shadow-foreground/[0.02]">
      <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-secondary">
        <Timer className="h-4 w-4 text-foreground" />
      </div>
      <div className={`text-2xl font-bold ${colorClass}`}>
        {avgReactionTime.average_reaction_time_ms.toFixed(1)}
        <span className="text-sm font-normal text-muted-foreground ml-1">
          ms
        </span>
      </div>
      <div className="text-xs text-muted-foreground">Avg Reaction Time</div>
      <div className="text-xs text-muted-foreground mt-1">
        {avgReactionTime.zone_description} · {avgReactionTime.run_count} run
        {avgReactionTime.run_count !== 1 ? "s" : ""}
      </div>
    </div>
  );
};
