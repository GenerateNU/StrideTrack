import { useSprintDrift } from "@/hooks/useRunMetrics.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";

interface DriftCardProps {
  label: string;
  value: number;
  thresholds?: { good: number; warn: number };
}

function getDriftColor(value: number, good: number, warn: number): string {
  const abs = Math.abs(value);
  if (abs < good) return "text-green-500";
  if (abs < warn) return "text-yellow-500";
  return "text-red-500";
}

function DriftCard({
  label,
  value,
  thresholds = { good: 5, warn: 10 },
}: DriftCardProps) {
  const colorClass = getDriftColor(value, thresholds.good, thresholds.warn);
  const sign = value > 0 ? "+" : "";

  return (
    <div className="flex flex-col items-center justify-center rounded-lg bg-card border border-border p-5 gap-1 shadow-sm">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        {label}
      </span>
      <span className={`text-4xl font-bold ${colorClass}`}>
        {sign}
        {value.toFixed(1)}%
      </span>
      <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
        <span className="text-green-500">● &lt;{thresholds.good}%</span>
        <span className="text-yellow-500">
          ● {thresholds.good}–{thresholds.warn}%
        </span>
        <span className="text-red-500">● &gt;{thresholds.warn}%</span>
      </div>
    </div>
  );
}

export const SprintDriftKPIs = ({ runId }: { runId: string }) => {
  const { driftData, driftLoading, driftError, driftRefetch } =
    useSprintDrift(runId);

  if (driftLoading) return <QueryLoading />;
  if (driftError)
    return <QueryError error={driftError} refetch={driftRefetch} />;
  if (!driftData) return null;

  return (
    <div className="grid grid-cols-2 gap-3">
      <DriftCard label="GCT Drift" value={driftData.gct_drift_pct} />
      <DriftCard label="FT Drift" value={driftData.ft_drift_pct} />
    </div>
  );
};
