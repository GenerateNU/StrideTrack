import { Card, CardHeader, CardDescription, CardTitle } from "@/components/ui/card";
import { GraphInfoCard } from "@/components/charts/GraphInfoCard";
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
    <Card className="relative flex-1 min-w-[160px]">
      <GraphInfoCard description="Ratio of total flight time to total ground contact time across all three phases. Higher values indicate better energy transfer through the hop, step, and jump sequence." />
      <CardHeader className="pb-2 text-center">
        <CardDescription className="text-xs uppercase tracking-wide">
          Contact Time Efficiency
        </CardDescription>
        <CardTitle className="text-3xl font-bold tabular-nums">
          {value != null ? value.toFixed(1) : "—"}
        </CardTitle>
      </CardHeader>
    </Card>
  );
};