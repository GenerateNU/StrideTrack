import { ChartCard } from "@/components/charts/shared/ChartCard";
import { QueryError } from "@/components/ui/QueryError";
import { QueryLoading } from "@/components/ui/QueryLoading";
import { useLandingGct } from "@/hooks/useHurdleMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import type { ChartProps } from "@/types/chart.types";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const LandingGctChart = ({ runId, hurdlesCompleted, targetEvent }: ChartProps) => {
  const {
    landingGct,
    landingGctIsLoading,
    landingGctError,
    landingGctRefetch,
  } = useLandingGct(runId, hurdlesCompleted ?? null, targetEvent ?? null);

  if (landingGctIsLoading)
    return (
      <ChartCard
        title="Landing GCT"
        description="Ground contact time on the landing step after each hurdle clearance."
      >
        <QueryLoading />
      </ChartCard>
    );
  if (landingGctError)
    return (
      <ChartCard
        title="Landing GCT"
        description="Ground contact time on the landing step after each hurdle clearance."
      >
        <QueryError
          error={landingGctError}
          refetch={() => void landingGctRefetch()}
        />
      </ChartCard>
    );
  if (!landingGct) return null;

  const values = landingGct
    .map((d) => d.landing_gct_ms)
    .filter((v): v is number => v != null);

  const yMin = Math.min(...values);
  const yMax = Math.max(...values);
  const yPadding = (yMax - yMin) * 0.2 || 1;

  return (
    <ChartCard
      title="Landing GCT"
      description="Ground contact time on the landing step after each hurdle clearance."
    >
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={landingGct}>
          <CartesianGrid strokeDasharray="3 3" stroke={chartColors.border} />
          <XAxis
            dataKey="hurdle_num"
            label={{
              value: "Hurdle Number",
              position: "insideBottom",
              offset: -5,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
          />
          <YAxis
            domain={[
              Math.max(0, Math.floor((yMin - yPadding) / 10) * 10),
              Math.ceil((yMax + yPadding) / 10) * 10,
            ]}
            label={{
              value: "Ground Contact Time (ms)",
              angle: -90,
              position: "insideLeft",
              offset: 0,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: "none",
              boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
              fontSize: 13,
              backgroundColor: chartColors.card,
              color: chartColors.foreground,
            }}
            formatter={(value) => [value != null ? `${value} ms` : "N/A"]}
          />
          <Bar
            dataKey="landing_gct_ms"
            fill={chartColors.primary}
            radius={[6, 6, 0, 0]}
            name="Landing GCT"
          />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
};
