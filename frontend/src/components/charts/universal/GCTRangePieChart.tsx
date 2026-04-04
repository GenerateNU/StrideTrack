import { useState } from "react";
import { useGCTRangeData } from "@/hooks/useRunMetrics.hooks";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { QueryError } from "@/components/ui/QueryError";
import type { ChartProps } from "@/types/chart.types";
import { ChartCard } from "@/components/charts/shared/ChartCard";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const COLORS = {
  below: "#22c55e",
  in_range: "#f59e0b",
  above: "#ef4444",
};

export const GCTRangePieChart = ({ runId }: ChartProps) => {
  const [minMs, setMinMs] = useState(100);
  const [maxMs, setMaxMs] = useState(200);

  const {
    gctRange,
    gctRangeIsLoading,
    gctRangeError,
    gctRangeRefetch,
  } = useGCTRangeData(runId, minMs, maxMs);

  if (gctRangeIsLoading) return <QueryLoading />;
  if (gctRangeError)
    return <QueryError error={gctRangeError} refetch={gctRangeRefetch} />;
  if (!gctRange) return null;

  const pieData = [
    { name: `Below ${minMs}ms`, value: gctRange.below, key: "below" },
    {
      name: `${minMs}–${maxMs}ms`,
      value: gctRange.in_range,
      key: "in_range",
    },
    { name: `Above ${maxMs}ms`, value: gctRange.above, key: "above" },
  ].filter((d) => d.value > 0);

  return (
    <ChartCard
      title="Steps in GCT Range"
      description="Bucketing of steps by ground contact time range. Adjust thresholds to analyze GCT distribution."
    >
      <div className="space-y-4">
      {/* Threshold inputs */}
      <div className="flex items-center gap-4 justify-center">
        <div className="flex items-center gap-2">
          <label className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
            Min
          </label>
          <input
            type="number"
            value={minMs}
            onChange={(e) => setMinMs(Number(e.target.value))}
            className="w-20 rounded-md border border-border bg-background px-2 py-1 text-sm text-foreground text-center"
          />
          <span className="text-xs text-muted-foreground">ms</span>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
            Max
          </label>
          <input
            type="number"
            value={maxMs}
            onChange={(e) => setMaxMs(Number(e.target.value))}
            className="w-20 rounded-md border border-border bg-background px-2 py-1 text-sm text-foreground text-center"
          />
          <span className="text-xs text-muted-foreground">ms</span>
        </div>
      </div>

      {/* Pie chart */}
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="55%"
            innerRadius={70}
            outerRadius={110}
            paddingAngle={3}
            dataKey="value"
            label={({ value }) => `${value}`}
            labelLine={false}
          >
            {pieData.map((entry) => (
              <Cell
                key={entry.key}
                fill={COLORS[entry.key as keyof typeof COLORS]}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: "none",
              boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
              fontSize: 13,
            }}
            formatter={(value, name) => [`${value} steps`, name]}
          />
          <Legend
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: 12 }}
          />
        </PieChart>
      </ResponsiveContainer>
      </div>
    </ChartCard>
  );
};
