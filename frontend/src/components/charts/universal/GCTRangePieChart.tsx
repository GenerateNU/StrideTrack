import { useState } from "react";
import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";
import { QueryLoading } from "@/components/QueryLoading";
import { QueryError } from "@/components/QueryError";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const COLORS = {
  below: "#22c55e", // green
  in: "#f59e0b", // yellow
  above: "#ef4444", // red
};

export const GCTRangePieChart = ({ runId }: { runId: string }) => {
  const { metrics, metricsIsLoading, metricsError, metricsRefetch } =
    useRunMetrics(runId);

  const [minMs, setMinMs] = useState(100);
  const [maxMs, setMaxMs] = useState(200);

  if (metricsIsLoading) return <QueryLoading />;
  if (metricsError)
    return <QueryError error={metricsError} refetch={metricsRefetch} />;
  if (!metrics) return null;

  const below = metrics.filter((m) => m.gct_ms < minMs).length;
  const inRange = metrics.filter(
    (m) => m.gct_ms >= minMs && m.gct_ms <= maxMs
  ).length;
  const above = metrics.filter((m) => m.gct_ms > maxMs).length;

  const data = [
    { name: `Below ${minMs}ms`, value: below, key: "below" },
    { name: `${minMs}–${maxMs}ms`, value: inRange, key: "in" },
    { name: `Above ${maxMs}ms`, value: above, key: "above" },
  ].filter((d) => d.value > 0);

  return (
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
            data={data}
            cx="50%"
            cy="55%"
            innerRadius={70}
            outerRadius={110}
            paddingAngle={3}
            dataKey="value"
            label={({ value }) => `${value}`}
            labelLine={false}
          >
            {data.map((entry) => (
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
  );
};
