import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { BaseKPI } from "@/components/charts/shared/BaseKPI";
import { useHurdleProjection } from "@/hooks/useHurdleMetrics.hooks";
import type { ChartProps } from "@/types/chart.types";

const formatTime = (ms: number): string => {
  const seconds = ms / 1000;
  return `${seconds.toFixed(2)}s`;
};

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.7) {
    return "#22c55e";
  }

  if (confidence >= 0.4) {
    return "#eab308";
  }

  return "#ef4444";
};

const getConfidenceLabel = (confidence: number): string => {
  if (confidence >= 0.7) {
    return "High";
  }

  if (confidence >= 0.4) {
    return "Moderate";
  }

  return "Low";
};

export const ProjectedFinishKPI = ({ runId }: ChartProps) => {
  const {
    hurdleProjection,
    hurdleProjectionIsLoading,
    hurdleProjectionError,
    hurdleProjectionRefetch,
  } = useHurdleProjection(runId);

  if (hurdleProjectionIsLoading) {
    return (
      <BaseKPI description="Confidence is based on how many hurdles were completed, data quality, and how many race phases (acceleration, peak speed, fatigue) the data covers. It increases as the athlete completes more hurdles across more phases.">
        <QueryLoading />
      </BaseKPI>
    );
  }

  if (hurdleProjectionError) {
    return (
      <BaseKPI description="Confidence is based on how many hurdles were completed, data quality, and how many race phases (acceleration, peak speed, fatigue) the data covers. It increases as the athlete completes more hurdles across more phases.">
        <QueryError
          error={hurdleProjectionError as Error}
          refetch={() => void hurdleProjectionRefetch()}
        />
      </BaseKPI>
    );
  }

  if (!hurdleProjection || hurdleProjection.projected_total_ms == null) {
    return null;
  }

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
    <BaseKPI description="Confidence is based on how many hurdles were completed, data quality, and how many race phases (acceleration, peak speed, fatigue) the data covers. It increases as the athlete completes more hurdles across more phases.">
      <p className="text-sm text-muted-foreground mb-1">
        Projected Finish Time ({targetLabel})
      </p>
      <p className="text-4xl font-bold text-foreground">
        {formatTime(projected_total_ms)}
      </p>
      <div className="flex items-center justify-center gap-2 mt-2">
        <div
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: getConfidenceColor(confidence) }}
        />
        <p
          className="text-sm font-medium"
          style={{ color: getConfidenceColor(confidence) }}
        >
          {getConfidenceLabel(confidence)} confidence (
          {(confidence * 100).toFixed(0)}%)
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3 mt-3 w-full">
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <p className="text-xs text-muted-foreground mb-1">
            Completed Hurdles
          </p>
          <p className="text-xl font-bold text-foreground">
            {completed_splits.length}
          </p>
          <p className="text-xs text-muted-foreground">splits recorded</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <p className="text-xs text-muted-foreground mb-1">
            Projected Hurdles
          </p>
          <p className="text-xl font-bold text-foreground">
            {projected_splits.length}
          </p>
          <p className="text-xs text-muted-foreground">splits estimated</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <p className="text-xs text-muted-foreground mb-1">Final Segment</p>
          <p className="text-xl font-bold text-foreground">
            {formatTime(projected_final_segment_ms)}
          </p>
          <p className="text-xs text-muted-foreground">pace estimate</p>
        </div>
      </div>
    </BaseKPI>
  );
};
