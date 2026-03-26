import { useBoscoMetrics } from "@/hooks/useBoscoMetrics";

function getColor(pct: number): string {
  if (Math.abs(pct) < 10) return "text-green-500";
  if (Math.abs(pct) <= 15) return "text-yellow-500";
  return "text-red-500";
}

function getLabel(pct: number): string {
  if (Math.abs(pct) < 10) return "Good";
  if (Math.abs(pct) <= 15) return "Moderate fatigue";
  return "Significant fatigue";
}

export const FatigueIndexKPI = ({ runId }: { runId: string }) => {
  const { boscoMetrics } = useBoscoMetrics(runId);

  if (!boscoMetrics) return null;

  const pct = boscoMetrics.fatigue_index_pct;
  const color = getColor(pct);
  const label = getLabel(pct);

  return (
    <div className="flex flex-col items-center justify-center h-[300px] gap-2">
      <span className="text-sm text-muted-foreground uppercase tracking-widest">
        Fatigue Index
      </span>
      <span className={`text-6xl font-bold ${color}`}>{pct.toFixed(1)}%</span>
      <span className={`text-sm font-medium ${color}`}>{label}</span>
      <span className="text-xs text-muted-foreground mt-2 text-center max-w-[200px]">
        Increase in ground contact time from first to last jump
      </span>
    </div>
  );
};
