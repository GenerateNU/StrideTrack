import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import type { HurdleTimelineResponse } from "@/types/hurdleTimeline.types";

export function useHurdleTimeline(runId: string) {
  const query = useQuery({
    queryKey: ["hurdle-timeline", runId],
    queryFn: async () => {
      const response = await api.get<HurdleTimelineResponse>(
        `/run/athletes/${runId}/metrics/hurdles/timeline`
      );
      return response.data;
    },
    enabled: !!runId,
  });

  return {
    timelineData: query.data ?? null,
    timelineLoading: query.isLoading,
    timelineError: query.error,
    refetchTimeline: query.refetch,
  };
}
