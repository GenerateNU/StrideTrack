import { useHurdleSplits } from "@/hooks/useHurdleMetrics";
import { HurdleSplitBarChart } from "./HurdleSplitBarChart";

export const HurdleSplitChart = ({ eventId }: { eventId: string }) => {
  const { splitData, splitLoading } = useHurdleSplits(eventId);

  if (splitLoading || !splitData) return null;

  return (
    <div>
      <HurdleSplitBarChart
        splits={splitData.splits}
        meanSplitMs={splitData.mean_split_ms}
      />
      {/* KPI card for consistency */}
      <div className="mt-4 bg-card border border-border rounded-lg p-4 text-center">
        <p className="text-sm text-muted-foreground">Consistency (CV%)</p>
        <p className="text-2xl font-bold text-foreground">
          {splitData.consistency_cv.toFixed(1)}%
        </p>
      </div>
    </div>
  );
};
