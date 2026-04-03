import { useEventHistory } from "@/hooks/useEventHistory.hooks";
import { chartColors } from "@/lib/chartColors";
import type { EventHistoryFilters } from "@/types/eventHistoryFilters.types";
import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";

interface EventHistoryChartProps {
  filters: EventHistoryFilters;
  enabled: boolean;
}

export const EventHistoryChart = ({
  filters,
  enabled,
}: EventHistoryChartProps) => {
  const {
    eventHistory,
    eventHistoryIsLoading,
    eventHistoryError,
    eventHistoryRefetch,
  } = useEventHistory(filters, enabled);
  if (eventHistoryIsLoading) return <QueryLoading />;
  if (eventHistoryError)
    return (
      <QueryError error={eventHistoryError} refetch={eventHistoryRefetch} />
    );
  if (!eventHistory || eventHistory.data_points.length === 0) return null;
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={eventHistory.data_points}>
        <CartesianGrid strokeDasharray="3 3" stroke={chartColors.border} />
        <XAxis
          dataKey="run_number"
          label={{
            value: "Run Number",
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
          label={{
            value: "Total Time (seconds)",
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
          formatter={(value) => [`${value}s`]}
          labelFormatter={(label) => {
            const point = eventHistory.data_points.find(
              (p) => p.run_number === label
            );
            return point ? `${point.run_name} — ${point.date}` : `Run ${label}`;
          }}
        />
        {eventHistory.best_time_seconds !== null && (
          <ReferenceLine
            y={eventHistory.best_time_seconds}
            stroke={chartColors.primary}
            strokeDasharray="5 3"
            label={{
              value: `Best: ${eventHistory.best_time_seconds}s`,
              position: "insideTopRight",
              style: {
                fill: chartColors.primary,
                fontSize: 10,
              },
            }}
          />
        )}
        <Line
          type="monotone"
          dataKey="total_time_seconds"
          stroke={chartColors.primary}
          strokeWidth={2}
          dot={{ fill: chartColors.primary }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
