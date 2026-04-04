import api from "@/lib/api";
import type { SplitScoreData } from "@/types/splitScore.types";
import { splitScoreResponseSchema } from "@/types/splitScore.types";
import { validateResponse } from "@/utils/validation";
import { useQuery } from "@tanstack/react-query";

export function useSplitScore(runId: string) {
  const query = useQuery({
    queryKey: ["split-score", runId],
    queryFn: async () => {
      const response = await api.get<SplitScoreData>(`/split-score/${runId}`);
      return validateResponse(response.data, splitScoreResponseSchema);
    },
    enabled: !!runId,
  });

  return {
    splitScoreData: query.data ?? null,
    splitScoreLoading: query.isLoading,
    splitScoreError: query.error,
    refetchSplitScore: query.refetch,
  };
}
