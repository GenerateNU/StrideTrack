import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useLandingGct } from "@/hooks/useHurdleMetrics.hooks";
import { chartColors } from "@/lib/chartColors";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export const LandingGctChart = ({ runId }: { runId: string }) => {
  const {
    landingGctData,
    landingGctLoading,
    landingGctError,
    refetchLandingGctData,
  } = useLandingGct(runId);

  if (landingGctLoading) {
    return <QueryLoading />;
  }

  if (landingGctError) {
    return (
      <QueryError
        error={landingGctError as Error}
        refetch={() => void refetchLandingGctData()}
      />
    );
  }

  if (!landingGctData) {
    return null;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={landingGctData}
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
          domain={["auto", "auto"]}
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
  );
};
