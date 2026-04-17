import { BaseKPI } from "@/components/charts/shared/BaseKPI";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useTripleJumpMetrics } from "@/hooks/useTripleJumpMetrics.hooks";
import type { ChartProps } from "@/types/chart.types";

export const ContactTimeEfficiencyCard = ({ runId }: ChartProps) => {
  const { tjMetrics, tjMetricsIsLoading, tjMetricsError, tjMetricsRefetch } =
    useTripleJumpMetrics(runId);

  if (tjMetricsIsLoading) return <QueryLoading />;
  if (tjMetricsError)
    return <QueryError error={tjMetricsError} refetch={tjMetricsRefetch} />;
  if (!tjMetrics) return null;

  const value = tjMetrics.contact_time_efficiency;

  return (
    <BaseKPI description="Ratio of total flight time to total ground contact time across all three phases. Higher values indicate better energy transfer through the hop, step, and jump sequence.">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        Contact Time Efficiency
      </span>
      <span className="text-3xl font-bold tabular-nums text-foreground">
        {value != null ? value.toFixed(2) : "—"}
      </span>
    </BaseKPI>
  );
};
