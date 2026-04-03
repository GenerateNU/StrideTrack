import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";

export const TotalStepsKPI = ({ runId }: { runId: string }) => {
  const { metrics, metricsIsLoading, metricsError, metricsRefetch } =
    useRunMetrics(runId);

  if (metricsIsLoading) return <QueryLoading />;
  if (metricsError)
    return <QueryError error={metricsError} refetch={metricsRefetch} />;
  if (!metrics) return null;

  const totalSteps = metrics.length;

  return (
    <div className="flex flex-col items-center justify-center rounded-lg bg-card border border-border p-5 gap-1 shadow-sm">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        Total Steps
      </span>
      <span className="text-4xl font-bold text-foreground">{totalSteps}</span>
    </div>
  );
};
