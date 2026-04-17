import api from "@/lib/api";
import { feedbackResponseSchema } from "@/types/feedback.types";
import { validateResponse } from "@/utils/validation";
import { useQuery } from "@tanstack/react-query";

export function useGetRunFeedback(runId: string | null) {
  const query = useQuery({
    queryKey: ["run-feedback", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get(`/runs/${runId}/feedback`);
      return validateResponse(response.data, feedbackResponseSchema);
    },
    enabled: !!runId,
    gcTime: 0,
  });

  return {
    runFeedback: query.data?.feedback ?? null,
    runFeedbackIsLoading: query.isLoading,
    runFeedbackError: query.error,
    runFeedbackRefetch: query.refetch,
  };
}
