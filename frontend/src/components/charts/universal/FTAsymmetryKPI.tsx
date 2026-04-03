import { useAsymmetryData } from "@/hooks/useRunMetrics.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";

function getAsymmetryColor(value: number): string {
  if (value < 5) return "text-green-500";
  if (value < 10) return "text-yellow-500";
  return "text-red-500";
}

export const FTAsymmetryKPI = ({ runId }: { runId: string }) => {
  const { asymmetryData, asymmetryLoading, asymmetryError, asymmetryRefetch } =
    useAsymmetryData(runId);

  if (asymmetryLoading) return <QueryLoading />;
  if (asymmetryError)
    return <QueryError error={asymmetryError} refetch={asymmetryRefetch} />;
  if (!asymmetryData) return null;

  const value = asymmetryData.ft_asymmetry_pct;

  return (
    <div className="flex flex-col items-center justify-center rounded-lg bg-card border border-border p-5 gap-1 shadow-sm">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        FT Asymmetry
      </span>
      <span className={`text-4xl font-bold ${getAsymmetryColor(value)}`}>
        {value.toFixed(1)}%
      </span>
      <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
        <span className="text-green-500">● &lt;5%</span>
        <span className="text-yellow-500">● 5–10%</span>
        <span className="text-red-500">● &gt;10%</span>
      </div>
    </div>
  );
};
