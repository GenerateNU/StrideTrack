import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useTakeoffFt } from "@/hooks/useHurdleMetrics";
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

export const TakeoffFtChart = ({ runId }: { runId: string }) => {
  const {
    takeoffFtData,
    takeoffFtLoading,
    takeoffFtError,
    refetchTakeoffFtData,
  } = useTakeoffFt(runId);

  if (takeoffFtLoading) {
    return <QueryLoading />;
  }

  if (takeoffFtError) {
    return (
      <QueryError
        error={takeoffFtError as Error}
        refetch={() => void refetchTakeoffFtData()}
      />
    );
  }

  if (!takeoffFtData) {
    return null;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={takeoffFtData}
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
            value: "Flight Time (ms)",
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
          formatter={(value) => [`${value} ms`]}
        />
        <Bar
          dataKey="takeoff_ft_ms"
          fill={chartColors.primary}
          radius={[6, 6, 0, 0]}
          name="Takeoff FT"
        />
      </BarChart>
    </ResponsiveContainer>
  );
};
