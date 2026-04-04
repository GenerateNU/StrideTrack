import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useGctIncrease } from "@/hooks/useHurdleMetrics.hooks";
import type { ChartProps } from "@/types/chart.types";

const getColor = (value: number): string => {
  if (value < 10) return "#22c55e";
  if (value <= 15) return "#eab308";
  return "#ef4444";
};

const getLabel = (value: number): string => {
  if (value < 10) return "Minimal";
  if (value <= 15) return "Moderate";
  return "Significant";
};

export const GctIncreaseChart = ({ runId }: ChartProps) => {
  const {
    gctIncrease,
    gctIncreaseIsLoading,
    gctIncreaseError,
    gctIncreaseRefetch,
  } = useGctIncrease(runId);

  if (gctIncreaseIsLoading)
    return (
      <ChartCard
        title="GCT Increase"
        description="Ground contact time increase from takeoff to landing at each hurdle. Large increases suggest poor clearance mechanics."
      >
        <QueryLoading />
      </ChartCard>
    );
  if (gctIncreaseError)
    return (
      <ChartCard
        title="GCT Increase"
        description="Ground contact time increase from takeoff to landing at each hurdle. Large increases suggest poor clearance mechanics."
      >
        <QueryError
          error={gctIncreaseError}
          refetch={() => void gctIncreaseRefetch()}
        />
      </ChartCard>
    );
  if (!gctIncrease) return null;

  const validRows = gctIncrease.filter(
    (r) => r.gct_increase_hurdle_to_hurdle_pct != null
  );

  if (validRows.length === 0) return null;

  const lastRow = validRows[validRows.length - 1];
  const pct = lastRow.gct_increase_hurdle_to_hurdle_pct!;

  return (
    <ChartCard
      title="GCT Increase"
      description="Ground contact time increase from takeoff to landing at each hurdle. Large increases suggest poor clearance mechanics."
    >
      <div className="space-y-4 sm:space-y-5">
        <div className="rounded-lg border border-border bg-muted/30 px-4 py-5 text-center sm:px-6 sm:py-6">
          <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide mb-1 sm:text-xs">
            GCT Increase (First to Last Hurdle)
          </p>
          <p
            className="text-2xl font-bold sm:text-3xl"
            style={{ color: getColor(pct) }}
          >
            {pct > 0 ? "+" : ""}
            {pct.toFixed(1)}%
          </p>
          <p
            className="text-xs mt-1 sm:text-sm"
            style={{ color: getColor(pct) }}
          >
            {getLabel(pct)}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-2 sm:grid-cols-none sm:grid-flow-col sm:auto-cols-fr sm:gap-3">
          {validRows.map((r) => {
            const hurdlePct = r.gct_increase_hurdle_to_hurdle_pct!;
            return (
              <div
                key={r.hurdle_num}
                className="rounded-lg border border-border bg-muted/30 px-3 py-3 text-center sm:px-4 sm:py-4"
              >
                <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide mb-1.5 sm:text-xs">
                  Hurdle {r.hurdle_num}
                </p>
                <p className="text-sm font-semibold text-foreground sm:text-base">
                  {r.takeoff_gct_ms != null ? `${r.takeoff_gct_ms} ms` : "N/A"}
                </p>
                <p
                  className="text-[10px] mt-0.5 sm:text-xs"
                  style={{ color: getColor(hurdlePct) }}
                >
                  {hurdlePct > 0 ? "+" : ""}
                  {hurdlePct.toFixed(1)}%
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </ChartCard>
  );
};
