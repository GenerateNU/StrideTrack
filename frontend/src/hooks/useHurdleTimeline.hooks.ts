import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import type { HurdleTimelineResponse } from "@/types/hurdleTimeline.types";
import { hurdleTimelineResponseSchema } from "@/types/hurdleTimeline.types";
import { validateResponse } from "@/utils/validation";

export function useHurdleTimeline(runId: string, hurdlesCompleted: number | null, targetEvent: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-timeline", runId],
    queryFn: async () => {

      const params = new URLSearchParams();
      if (hurdlesCompleted) params.append("hurdles_completed", String(hurdlesCompleted));
      if (targetEvent) params.append("target_event", targetEvent);

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
