import { useQuery } from "@tanstack/react-query";
import { boscoMetricsSchema } from "@/types/bosco.types.ts";
import type { BoscoMetricsResponse } from "@/types/bosco.types.ts";
import apiClient from "@/lib/api";
import { validateResponse } from "@/utils/validation";

export function useBoscoMetrics(runId: string | null) {
  const query = useQuery({
    queryKey: ["bosco-metrics", runId],
    queryFn: async () => {
      if (!runId) return null;

      const response = await apiClient.get<BoscoMetricsResponse>(
        `/runs/${runId}/metrics/bosco`
      );
      return validateResponse(response.data, boscoMetricsSchema);
    },
    enabled: !!runId,
  });

  return {
    boscoMetrics: query.data ?? null,
    boscoMetricsIsLoading: query.isLoading,
    boscoMetricsError: query.error,
    boscoMetricsRefetch: query.refetch,
  };
}
