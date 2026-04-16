import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import api from "@/lib/api";

const feedbackResponseSchema = z.object({
  feedback: z.string(),
});

export function useGetRunFeedback(runId: string | undefined) {
  const query = useQuery({
    queryKey: ["runFeedback", runId],
    queryFn: async () => {
      const response = await api.get(`/runs/${runId}/feedback`);
      const parsed = feedbackResponseSchema.safeParse(response.data);
      if (!parsed.success) {
        throw new Error("Invalid response format");
      }
      return parsed.data;
    },
    enabled: !!runId,
    gcTime: 0,
  });

  return {
    feedback: query.data?.feedback ?? null,
    feedbackIsLoading: query.isLoading,
    feedbackError: query.error,
  };
}
