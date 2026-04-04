import type { ChartProps } from "@/types/chart.types";
import { BaseKPI } from "@/components/charts/shared/BaseKPI";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import { useAsymmetryData } from "@/hooks/useRunMetrics.hooks";

function getAsymmetryColor(value: number): string {
  if (value < 5) return "text-green-500";
  if (value < 10) return "text-yellow-500";
  return "text-red-500";
}

export const GCTAsymmetryKPI = ({ runId }: ChartProps) => {
  const { asymmetry, asymmetryIsLoading, asymmetryError, asymmetryRefetch } =
    useAsymmetryData(runId);

  if (asymmetryIsLoading) return <QueryLoading />;
  if (asymmetryError)
    return (
      <QueryError
        error={asymmetryError}
        refetch={() => void asymmetryRefetch()}
      />
    );
  if (!asymmetry) return null;

  const value = asymmetry.gct_asymmetry_pct;

  return (
    <BaseKPI description=">10% may indicate injury risk. Target <5%.">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        GCT Asymmetry
      </span>
      <span className={`text-4xl font-bold ${getAsymmetryColor(value)}`}>
        {value.toFixed(1)}%
      </span>
      <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
        <span className="text-green-500">&bull; &lt;5%</span>
        <span className="text-yellow-500">&bull; 5&ndash;10%</span>
        <span className="text-red-500">&bull; &gt;10%</span>
      </div>
    </BaseKPI>
  );
};
