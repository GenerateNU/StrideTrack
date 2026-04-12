import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useStepsBetweenHurdles } from "@/hooks/useHurdleMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";

export const StepsBetweenHurdlesChart = ({ runId, hurdlesCompleted, targetEvent }: ChartProps) => {
  const {
    stepsBetween,
    stepsBetweenIsLoading,
    stepsBetweenError,
    stepsBetweenRefetch,
  } = useStepsBetweenHurdles(runId, hurdlesCompleted ?? null, targetEvent ?? null);

  if (stepsBetweenIsLoading)
    return (
      <ChartCard
        title="Steps Between Hurdles"
        description="Number of strides between each pair of hurdles. Consistent step count indicates good rhythm."
      >
        <QueryLoading />
      </ChartCard>
    );
  if (stepsBetweenError)
    return (
      <ChartCard
        title="Steps Between Hurdles"
        description="Number of strides between each pair of hurdles. Consistent step count indicates good rhythm."
      >
        <QueryError
          error={stepsBetweenError}
          refetch={() => void stepsBetweenRefetch()}
        />
      </ChartCard>
    );
  if (!stepsBetween) return null;

  const validSteps = stepsBetween.filter(
    (s) => s.steps_between_hurdles != null
  );

  if (validSteps.length === 0) return null;

  const counts = validSteps.map((s) => s.steps_between_hurdles!);
  const allSame = counts.every((c) => c === counts[0]);

  return (
    <ChartCard
      title="Steps Between Hurdles"
      description="Number of strides between each pair of hurdles. Consistent step count indicates good rhythm."
    >
      <div className="space-y-3 sm:space-y-4">
        <div className="rounded-lg border border-border bg-muted/30 px-4 py-4 text-center sm:px-6 sm:py-5">
          <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide mb-1 sm:text-xs">
            Step Consistency
          </p>
          <p
            className="text-base font-bold sm:text-lg"
            style={{
              color: allSame ? chartColors.primary : chartColors.foreground,
            }}
          >
            {allSame ? `Consistent (${counts[0]} steps)` : "Inconsistent"}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-2 sm:grid-cols-none sm:grid-flow-col sm:auto-cols-fr sm:gap-3">
          {validSteps.map((s) => (
            <div
              key={s.hurdle_num}
              className="rounded-lg border border-border bg-muted/30 px-3 py-3 text-center sm:px-4 sm:py-4"
            >
              <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide mb-1.5 sm:text-xs">
                H{s.hurdle_num}→H{s.hurdle_num + 1}
              </p>
              <p className="text-xl font-bold text-foreground sm:text-2xl">
                {s.steps_between_hurdles}
              </p>
            </div>
          ))}
        </div>
      </div>
    </ChartCard>
  );
};
