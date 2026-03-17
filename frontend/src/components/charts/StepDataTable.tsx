import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { RunMetric } from "@/types/runMetrics.types";
import { QueryLoading } from "@/components/QueryLoading";

interface StepDataTableProps {
  metrics: RunMetric[];
  isLoading: boolean;
}

export function StepDataTable({ metrics, isLoading }: StepDataTableProps) {
  const [expanded, setExpanded] = useState(false);

  if (isLoading) {
    return <QueryLoading />;
  }

  if (metrics.length === 0) return null;

  const sorted = [...metrics].sort((a, b) => a.ic_time - b.ic_time);

  return (
    <div className="rounded-2xl border border-border bg-card shadow-sm shadow-foreground/[0.02]">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between p-5 text-left"
      >
        <div className="flex items-center gap-2.5">
          <div
            className="h-5 w-1 rounded-full"
            style={{ backgroundColor: "hsl(var(--primary))" }}
          />
          <h3 className="text-sm font-semibold text-foreground">
            Step-by-Step Data
          </h3>
          <span className="rounded-lg bg-secondary px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
            {metrics.length} steps
          </span>
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {expanded && (
        <div className="border-t border-border overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-border bg-secondary/30">
                <th className="px-4 py-2.5 font-semibold text-muted-foreground">
                  #
                </th>
                <th className="px-4 py-2.5 font-semibold text-muted-foreground">
                  Foot
                </th>
                <th className="px-4 py-2.5 font-semibold text-muted-foreground text-right">
                  GCT (ms)
                </th>
                <th className="px-4 py-2.5 font-semibold text-muted-foreground text-right">
                  Flight (ms)
                </th>
                <th className="px-4 py-2.5 font-semibold text-muted-foreground text-right">
                  Step Time (ms)
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((step, i) => (
                <tr
                  key={`${step.stride_num}-${step.foot}`}
                  className={`border-b border-border last:border-b-0 ${
                    i % 2 === 0 ? "" : "bg-secondary/10"
                  }`}
                >
                  <td className="px-4 py-2.5 font-medium text-foreground">
                    {step.stride_num}
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className={`inline-block rounded-md px-2 py-0.5 text-[10px] font-semibold uppercase ${
                        step.foot.toLowerCase() === "left"
                          ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                          : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                      }`}
                    >
                      {step.foot}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-right font-medium text-foreground tabular-nums">
                    {step.gct_ms}
                  </td>
                  <td className="px-4 py-2.5 text-right font-medium text-foreground tabular-nums">
                    {step.flight_ms}
                  </td>
                  <td className="px-4 py-2.5 text-right font-medium text-foreground tabular-nums">
                    {step.step_time_ms}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
