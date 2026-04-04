import api from "@/lib/api";
import type { SplitScoreData } from "@/types/splitScore.types";
import { splitScoreResponseSchema } from "@/types/splitScore.types";
import { validateResponse } from "@/utils/validation";
import { useQuery } from "@tanstack/react-query";

export function useSplitScore(runId: string) {
  const query = useQuery({
    queryKey: ["split-score", runId],
    queryFn: async () => {
      const response = await api.get<SplitScoreData>(
        `/runs/${runId}/metrics/split-score`
      );
      return validateResponse(response.data, splitScoreResponseSchema);
    },
    enabled: !!runId,
  });

  return {
    splitScore: query.data ?? null,
    splitScoreIsLoading: query.isLoading,
    splitScoreError: query.error,
    splitScoreRefetch: query.refetch,
  };
}
