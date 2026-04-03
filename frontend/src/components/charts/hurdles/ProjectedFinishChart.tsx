import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useHurdleProjection } from "@/hooks/useHurdleMetrics.hooks";

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

export const ProjectedFinishKPI = ({ runId }: { runId: string }) => {
  const {
    projectionData,
    projectionLoading,
    projectionError,
    refetchProjectionData,
  } = useHurdleProjection(runId);

  if (projectionLoading) {
    return <QueryLoading />;
  }

  if (projectionError) {
    return (
      <QueryError
        error={projectionError as Error}
        refetch={() => void refetchProjectionData()}
      />
    );
  }

  if (!projectionData || projectionData.projected_total_ms == null) {
    return null;
  }

  const {
    projected_total_ms,
    confidence,
    target_event,
    completed_splits,
    projected_splits,
    projected_final_segment_ms,
  } = projectionData;

  const targetLabel = target_event.replace("hurdles_", "").replace("m", "m H");

  return (
    <div className="space-y-3">
      <div className="bg-card border border-border rounded-lg p-6 text-center">
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
      </div>

      <div className="grid grid-cols-3 gap-3">
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
    </div>
  );
};
