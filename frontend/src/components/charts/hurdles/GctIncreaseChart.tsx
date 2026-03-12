import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useGctIncrease } from "@/hooks/useHurdleMetrics";

export const GctIncreaseChart = ({ runId }: { runId: string }) => {
  const {
    gctIncreaseData,
    gctIncreaseLoading,
    gctIncreaseError,
    refetchGctIncreaseData,
  } = useGctIncrease(runId);

  if (gctIncreaseLoading) {
    return <QueryLoading />;
  }

  if (gctIncreaseError) {
    return (
      <QueryError
        error={gctIncreaseError as Error}
        refetch={() => void refetchGctIncreaseData()}
      />
    );
  }

  if (!gctIncreaseData) {
    return null;
  }

  // Last hurdle with a valid percentage is the overall increase
  const validRows = gctIncreaseData.filter(
    (r) => r.gct_increase_hurdle_to_hurdle_pct != null
  );

  if (validRows.length === 0) {
    return null;
  }

  const lastRow = validRows[validRows.length - 1];
  const pct = lastRow.gct_increase_hurdle_to_hurdle_pct!;

  // Threshold coloring from metrics reference
  const getColor = (value: number): string => {
    if (value < 10) {
      return "#22c55e";
    }

    if (value <= 15) {
      return "#eab308";
    }

    return "#ef4444";
  };

  const getLabel = (value: number): string => {
    if (value < 10) {
      return "Minimal";
    }

    if (value <= 15) {
      return "Moderate";
    }

    return "Significant";
  };

  return (
    <div className="space-y-3">
      <div className="bg-card border border-border rounded-lg p-6 text-center">
        <p className="text-sm text-muted-foreground mb-1">
          GCT Increase (First to Last Hurdle)
        </p>
        <p className="text-3xl font-bold" style={{ color: getColor(pct) }}>
          {pct > 0 ? "+" : ""}
          {pct.toFixed(1)}%
        </p>
        <p className="text-sm mt-1" style={{ color: getColor(pct) }}>
          {getLabel(pct)}
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        {validRows.map((r) => (
          <div
            key={r.hurdle_num}
            className="bg-card border border-border rounded-lg p-3 text-center min-w-[80px]"
          >
            <p className="text-xs text-muted-foreground mb-1">
              Hurdle {r.hurdle_num}
            </p>
            <p className="text-sm font-semibold text-foreground">
              {r.takeoff_gct_ms != null ? `${r.takeoff_gct_ms} ms` : "N/A"}
            </p>
            <p
              className="text-xs"
              style={{
                color: getColor(r.gct_increase_hurdle_to_hurdle_pct!),
              }}
            >
              {r.gct_increase_hurdle_to_hurdle_pct! > 0 ? "+" : ""}
              {r.gct_increase_hurdle_to_hurdle_pct!.toFixed(1)}%
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
