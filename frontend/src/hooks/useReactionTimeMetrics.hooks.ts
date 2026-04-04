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
        `/runs/${runId}/metrics/reaction-time`
      );
      return validateResponse(response.data, reactionTimeMetricsSchema);
    },
    enabled: !!runId,
  });

  return {
    reactionTime: query.data ?? null,
    reactionTimeIsLoading: query.isLoading,
    reactionTimeError: query.error,
    reactionTimeRefetch: query.refetch,
  };
}
