import type { ChartProps } from "@/types/chart.types";
import { BaseKPI } from "@/components/charts/shared/BaseKPI";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";

export const TotalStepsKPI = ({ runId }: ChartProps) => {
  const {
    runMetrics,
    runMetricsIsLoading,
    runMetricsError,
    runMetricsRefetch,
  } = useRunMetrics(runId);

  if (runMetricsIsLoading) return <QueryLoading />;
  if (runMetricsError)
    return (
      <QueryError
        error={runMetricsError}
        refetch={() => void runMetricsRefetch()}
      />
    );
  if (!runMetrics) return null;

  const totalSteps = runMetrics.length;

  return (
    <BaseKPI description="Total number of strides recorded in this run.">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        Total Steps
      </span>
      <span className="text-4xl font-bold text-foreground">{totalSteps}</span>
    </BaseKPI>
  );
};
