import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import type { HurdleTimelineResponse } from "@/types/hurdleTimeline.types";
import { hurdleTimelineResponseSchema } from "@/types/hurdleTimeline.types";
import { validateResponse } from "@/utils/validation";

export function useHurdleTimeline(runId: string) {
  const query = useQuery({
    queryKey: ["hurdle-timeline", runId],
    queryFn: async () => {
      const response = await api.get<HurdleTimelineResponse>(
        `/runs/${runId}/metrics/hurdles/timeline`
      );
      return validateResponse(response.data, hurdleTimelineResponseSchema);
    },
    enabled: !!runId,
  });

  return {
    hurdleTimeline: query.data ?? null,
    hurdleTimelineIsLoading: query.isLoading,
    hurdleTimelineError: query.error,
    hurdleTimelineRefetch: query.refetch,
  };
}
