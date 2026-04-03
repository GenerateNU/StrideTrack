import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import type { ReactionTimeMetrics } from "@/types/reactionTime.types";
import { reactionTimeMetricsSchema } from "@/types/reactionTime.types";
import { validateResponse } from "@/utils/validation";

export function useReactionTimeMetrics(runId: string | null) {
  const query = useQuery({
    queryKey: ["reaction-time-metrics", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<ReactionTimeMetrics>(
        `/reaction-time/${runId}`
      );
      return validateResponse(response.data, reactionTimeMetricsSchema);
    },
    enabled: !!runId,
  });

  return {
    rtMetrics: query.data ?? null,
    rtLoading: query.isLoading,
    rtError: query.error,
    rtRefetch: query.refetch,
  };
}
