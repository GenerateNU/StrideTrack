import { Card, CardContent, CardHeader, CardDescription, CardTitle } from "@/components/ui/card";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useLongJumpMetrics } from "@/hooks/useLongJumpMetrics.hooks";
import type { ChartProps } from "@/types/chart.types";

export const LastStepFtCard = ({ runId }: ChartProps) => {
  const { ljMetrics, ljMetricsIsLoading, ljMetricsError, ljMetricsRefetch } =
    useLongJumpMetrics(runId);

  if (ljMetricsIsLoading) return <QueryLoading />;
  if (ljMetricsError)
    return <QueryError error={ljMetricsError} refetch={ljMetricsRefetch} />;
  if (!ljMetrics) return null;

  const value = ljMetrics.jump_ft_ms;

  return (
    <Card className="flex-1 min-w-[160px]">
      <CardHeader className="pb-2">
        <CardDescription className="text-xs uppercase tracking-wide">
          Last Step FT
        </CardDescription>
        <CardTitle className="text-3xl font-bold tabular-nums">
          {value != null ? value.toFixed(1) : "—"}
          <span className="text-sm font-normal text-muted-foreground ml-1">ms</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground leading-snug">
          Flight time of the final takeoff step — the actual jump. Longer flight time reflects a more powerful and effective takeoff, assuming good technique.
        </p>
      </CardContent>
    </Card>
  );
};