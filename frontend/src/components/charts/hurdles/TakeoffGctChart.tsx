import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useTakeoffGct } from "@/hooks/useHurdleMetrics.hooks";
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

export const TakeoffGctChart = ({ runId }: { runId: string }) => {
  const {
    takeoffGctData,
    takeoffGctLoading,
    takeoffGctError,
    refetchTakeoffGctData,
  } = useTakeoffGct(runId);

  if (takeoffGctLoading) {
    return <QueryLoading />;
  }

  if (takeoffGctError) {
    return (
      <QueryError
        error={takeoffGctError as Error}
        refetch={() => void refetchTakeoffGctData()}
      />
    );
  }

  if (!takeoffGctData) {
    return null;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={takeoffGctData}
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
          dataKey="takeoff_gct_ms"
          fill={chartColors.primary}
          radius={[6, 6, 0, 0]}
          name="Takeoff GCT"
        />
      </BarChart>
    </ResponsiveContainer>
  );
};
