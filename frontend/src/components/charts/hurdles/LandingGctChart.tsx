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

export const LandingGctChart = ({ runId }: ChartProps) => {
  const {
    landingGct,
    landingGctIsLoading,
    landingGctError,
    landingGctRefetch,
  } = useLandingGct(runId);

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
  const dataMin = Math.min(...values);
  const dataMax = Math.max(...values);
  const range = dataMax - dataMin || 1;
  const yDomain: [number, number] = [
    Math.max(0, dataMin - range * 0.2),
    dataMax + range * 0.1,
  ];

  return (
    <ChartCard
      title="Landing GCT"
      description="Ground contact time on the landing step after each hurdle clearance."
    >
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={landingGct}
          margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
        >
          <CartesianGrid vertical={false} stroke={chartColors.border} />
          <XAxis
            dataKey="hurdle_num"
            label={{
              value: "Hurdle Number",
              position: "insideBottom",
              offset: -30,
              style: {
                fill: chartColors.mutedForeground,
                fontSize: 10,
                textAnchor: "middle",
              },
            }}
            tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
          />
          <YAxis
            domain={yDomain}
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
            tick={{ fill: chartColors.mutedForeground, fontSize: 10 }}
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
