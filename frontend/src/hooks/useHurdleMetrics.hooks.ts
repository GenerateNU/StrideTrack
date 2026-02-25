import { useQuery } from "@tanstack/react-query";
import { hurdleSplitResponseSchema } from "@/types/hurdleMetrics.types";
import type { HurdleSplitResponse } from "@/types/hurdleMetrics.types";
import { apiClient } from "@/axios.config";
import { validateResponse } from "@/utils/validation";

export function useHurdleSplits(eventId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-splits", eventId],
    queryFn: async () => {
      if (!eventId) return null;
      const response = await apiClient.get<HurdleSplitResponse>(
        `/api/hurdles/events/${eventId}/hurdle-splits`
      );
      return validateResponse(response.data, hurdleSplitResponseSchema);
    },
    enabled: !!eventId,
  });

  return {
    splitData: query.data ?? null,
    splitLoading: query.isLoading,
    splitError: query.error,
  };
}
