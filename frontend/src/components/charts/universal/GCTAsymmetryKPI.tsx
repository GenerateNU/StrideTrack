import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";

function getAsymmetryColor(value: number): string {
  if (value < 5) return "text-green-500";
  if (value < 10) return "text-yellow-500";
  return "text-red-500";
}

export const GCTAsymmetryKPI = ({ runId }: { runId: string }) => {
  const { metrics, metricsIsLoading, metricsError, metricsRefetch } =
    useRunMetrics(runId);

  if (metricsIsLoading) return <QueryLoading />;
  if (metricsError)
    return <QueryError error={metricsError} refetch={metricsRefetch} />;
  if (!metrics) return null;

  const strideMap = new Map<
    number,
    { left_gct?: number; right_gct?: number }
  >();
  for (const m of metrics) {
    const entry = strideMap.get(m.stride_num) ?? {};
    if (m.foot.toLowerCase() === "left") entry.left_gct = m.gct_ms;
    else entry.right_gct = m.gct_ms;
    strideMap.set(m.stride_num, entry);
  }

  const asymmetries: number[] = [];
  for (const s of strideMap.values()) {
    if (s.left_gct != null && s.right_gct != null) {
      const avg = (s.left_gct + s.right_gct) / 2;
      if (avg > 0)
        asymmetries.push((Math.abs(s.left_gct - s.right_gct) / avg) * 100);
    }
  }

  const mean =
    asymmetries.length > 0
      ? asymmetries.reduce((s, v) => s + v, 0) / asymmetries.length
      : 0;

  return (
    <div className="flex flex-col items-center justify-center rounded-lg bg-card border border-border p-5 gap-1 shadow-sm">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        GCT Asymmetry
      </span>
      <span className={`text-4xl font-bold ${getAsymmetryColor(mean)}`}>
        {mean.toFixed(1)}%
      </span>
      <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
        <span className="text-green-500">● &lt;5%</span>
        <span className="text-yellow-500">● 5–10%</span>
        <span className="text-red-500">● &gt;10%</span>
      </div>
    </div>
  );
};
