import { BaseKPI } from "@/components/charts/shared/BaseKPI";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useLongJumpMetrics } from "@/hooks/useLongJumpMetrics.hooks";
import type { ChartProps } from "@/types/chart.types";

export const LastStepGctCard = ({ runId }: ChartProps) => {
  const { ljMetrics, ljMetricsIsLoading, ljMetricsError, ljMetricsRefetch } =
    useLongJumpMetrics(runId);

  if (ljMetricsIsLoading) return <QueryLoading />;
  if (ljMetricsError)
    return <QueryError error={ljMetricsError} refetch={ljMetricsRefetch} />;
  if (!ljMetrics) return null;

  const value = ljMetrics.penultimate_gct_ms;

  return (
    <BaseKPI description="Ground contact time of the penultimate (second-to-last) step. Critical for converting horizontal speed into vertical lift. Should be short and reactive.">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        Last Step GCT
      </span>
      <span className="text-3xl font-bold tabular-nums text-foreground">
        {value != null ? value.toFixed(1) : "—"}
        <span className="text-sm font-normal text-muted-foreground ml-1">
          ms
        </span>
      </span>
    </BaseKPI>
  );
};
