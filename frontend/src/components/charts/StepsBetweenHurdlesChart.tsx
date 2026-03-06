import { useStepsBetweenHurdles } from "@/hooks/useHurdleMetrics";
import { chartColors } from "@/lib/chartColors";

export const StepsBetweenHurdlesChart = ({ runId }: { runId: string }) => {
  const { stepsData, stepsLoading } = useStepsBetweenHurdles(runId);

  if (stepsLoading || !stepsData) {
    return null;
  }

  const validSteps = stepsData.filter((s) => s.steps_between_hurdles != null);

  if (validSteps.length === 0) {
    return null;
  }

  // Are all intervals the same step count?
  const counts = validSteps.map((s) => s.steps_between_hurdles!);
  const allSame = counts.every((c) => c === counts[0]);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-3">
        {validSteps.map((s) => (
          <div
            key={s.hurdle_num}
            className="bg-card border border-border rounded-lg p-4 text-center min-w-[80px]"
          >
            <p
              className="text-xs mb-1"
              style={{ color: chartColors.mutedForeground }}
            >
              H{s.hurdle_num}→H{s.hurdle_num + 1}
            </p>
            <p className="text-2xl font-bold text-foreground">
              {s.steps_between_hurdles}
            </p>
          </div>
        ))}
      </div>
      <div className="bg-card border border-border rounded-lg p-4 text-center">
        <p className="text-sm text-muted-foreground">Step Consistency</p>
        <p
          className="text-lg font-bold"
          style={{
            color: allSame ? chartColors.primary : chartColors.foreground,
          }}
        >
          {allSame ? `Consistent (${counts[0]} steps)` : "Inconsistent"}
        </p>
      </div>
    </div>
  );
};
