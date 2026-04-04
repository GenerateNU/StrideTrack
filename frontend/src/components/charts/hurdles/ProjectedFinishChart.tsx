import { BaseKPI } from "@/components/charts/shared/BaseKPI";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useHurdleProjection } from "@/hooks/useHurdleMetrics.hooks";
import type { ChartProps } from "@/types/chart.types";

const formatTime = (ms: number): string => {
  const seconds = ms / 1000;
  return `${seconds.toFixed(2)}s`;
};

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.7) return "#22c55e";
  if (confidence >= 0.4) return "#eab308";
  return "#ef4444";
};

const getConfidenceLabel = (confidence: number): string => {
  if (confidence >= 0.7) return "High";
  if (confidence >= 0.4) return "Moderate";
  return "Low";
};

export const ProjectedFinishKPI = ({ runId }: ChartProps) => {
  const {
    hurdleProjection,
    hurdleProjectionIsLoading,
    hurdleProjectionError,
    hurdleProjectionRefetch,
  } = useHurdleProjection(runId);

  const description =
    "Confidence is based on how many hurdles were completed, data quality, and how many race phases (acceleration, peak speed, fatigue) the data covers. It increases as the athlete completes more hurdles across more phases.";

  if (hurdleProjectionIsLoading)
    return (
      <BaseKPI description={description}>
        <QueryLoading />
      </BaseKPI>
    );

  if (hurdleProjectionError)
    return (
      <BaseKPI description={description}>
        <QueryError
          error={hurdleProjectionError as Error}
          refetch={() => void hurdleProjectionRefetch()}
        />
      </BaseKPI>
    );

  if (!hurdleProjection || hurdleProjection.projected_total_ms == null)
    return null;

  const {
    projected_total_ms,
    confidence,
    target_event,
    completed_splits,
    projected_splits,
    projected_final_segment_ms,
  } = hurdleProjection;

  const targetLabel = target_event.replace("hurdles_", "").replace("m", "m H");

  return (
    <BaseKPI description={description}>
      <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide sm:text-xs">
        Projected Finish Time ({targetLabel})
      </p>
      <p className="text-3xl font-bold text-foreground sm:text-4xl">
        {formatTime(projected_total_ms)}
      </p>
      <div className="flex items-center justify-center gap-1.5 mt-1 sm:gap-2 sm:mt-2">
        <div
          className="w-1.5 h-1.5 rounded-full sm:w-2 sm:h-2"
          style={{ backgroundColor: getConfidenceColor(confidence) }}
        />
        <p
          className="text-xs font-medium sm:text-sm"
          style={{ color: getConfidenceColor(confidence) }}
        >
          {getConfidenceLabel(confidence)} confidence (
          {(confidence * 100).toFixed(0)}%)
        </p>
      </div>

      <div className="grid grid-cols-3 gap-2 mt-3 w-full sm:gap-3">
        <div className="rounded-lg border border-border bg-muted/30 px-2 py-3 text-center sm:px-4 sm:py-4">
          <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide mb-1 sm:text-xs">
            Completed
          </p>
          <p className="text-base font-bold text-foreground sm:text-xl">
            {completed_splits.length}
          </p>
          <p className="text-[10px] text-muted-foreground sm:text-xs">
            splits recorded
          </p>
        </div>
        <div className="rounded-lg border border-border bg-muted/30 px-2 py-3 text-center sm:px-4 sm:py-4">
          <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide mb-1 sm:text-xs">
            Projected
          </p>
          <p className="text-base font-bold text-foreground sm:text-xl">
            {projected_splits.length}
          </p>
          <p className="text-[10px] text-muted-foreground sm:text-xs">
            splits estimated
          </p>
        </div>
        <div className="rounded-lg border border-border bg-muted/30 px-2 py-3 text-center sm:px-4 sm:py-4">
          <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide mb-1 sm:text-xs">
            Final Segment
          </p>
          <p className="text-base font-bold text-foreground sm:text-xl">
            {formatTime(projected_final_segment_ms)}
          </p>
          <p className="text-[10px] text-muted-foreground sm:text-xs">
            pace estimate
          </p>
        </div>
      </div>
    </BaseKPI>
  );
};
