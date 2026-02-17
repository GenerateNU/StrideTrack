import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import { apiClient } from "@/axios.config";
import { validateResponse } from "@/utils/validation";

const runMetricSchema = z.object({
  stride_num: z.number(),
  foot: z.string(),
  ic_time: z.number(),
  gct_ms: z.number(),
  flight_ms: z.number(),
  step_time_ms: z.number(),
});

export type RunMetric = z.infer<typeof runMetricSchema>;

export function useAthleteRunMetrics(athleteId: string | null) {
  const query = useQuery({
    queryKey: ["run-metrics", athleteId],
    queryFn: async () => {
      if (!athleteId) return [];

      const response = await apiClient.get<RunMetric[]>(
        `/api/run/athletes/${athleteId}/metrics`
      );
      return validateResponse(response.data, z.array(runMetricSchema));
    },
    enabled: !!athleteId,
  });

  return {
    metrics: query.data ?? [],
    metricsIsLoading: query.isLoading,
    metricsError: query.error,
    metricsRefetch: query.refetch,
  };
}
