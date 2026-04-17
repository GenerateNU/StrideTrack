import { useQuery } from "@tanstack/react-query";
import { eventHistoryResponseSchema } from "@/types/eventHistory.types";
import type { EventHistoryResponse } from "@/types/eventHistory.types";
import type { EventHistoryFilters } from "@/types/eventHistoryFilters.types";
import api from "@/lib/api";
import { validateResponse } from "@/utils/validation";

export function useEventHistory(
  filters: EventHistoryFilters | null,
  enabled: boolean
) {
  const query = useQuery({
    queryKey: ["event-history", filters],
    queryFn: async () => {
      if (!filters || !filters.eventType) return null;

      const params: Record<string, string> = {
        event_type: filters.eventType,
      };

      if (filters.amountMode === "dateRange") {
        if (filters.dateFrom) params.date_from = filters.dateFrom;
        if (filters.dateTo) params.date_to = filters.dateTo;
      } else {
        params.limit = String(filters.limit);
      }

      const response = await api.get<EventHistoryResponse>(
        `/athletes/${filters.athleteId}/event-history`,
        { params }
      );
      return validateResponse(response.data, eventHistoryResponseSchema);
    },
    enabled: enabled && !!filters,
  });

  return {
    eventHistory: query.data ?? null,
    eventHistoryIsLoading: query.isLoading,
    eventHistoryError: query.error,
    eventHistoryRefetch: query.refetch,
  };
}
