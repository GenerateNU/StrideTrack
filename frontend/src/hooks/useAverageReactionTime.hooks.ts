import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import {
  averageReactionTimeSchema,
  type AverageReactionTime,
} from "@/types/reactionTime.types";
import { validateResponse } from "@/utils/validation";

export function useAverageReactionTime(athleteId: string | null) {
  const query = useQuery({
    queryKey: ["average-reaction-time", athleteId],
    queryFn: async () => {
      if (!athleteId) return null;
      const response = await api.get<AverageReactionTime>(
        `/runs/athletes/${athleteId}/metrics/reaction-time/average`
      );
      return validateResponse(response.data, averageReactionTimeSchema);
    },
    enabled: !!athleteId,
  });

  return {
    avgReactionTime: query.data ?? null,
    avgReactionTimeIsLoading: query.isLoading,
    avgReactionTimeError: query.error,
    avgReactionTimeRefetch: query.refetch,
  };
}
