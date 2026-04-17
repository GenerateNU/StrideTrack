import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import api from "@/lib/api";
import { validateResponse } from "@/utils/validation";

export const averageReactionTimeSchema = z.object({
  athlete_id: z.string(),
  average_reaction_time_ms: z.number(),
  run_count: z.number(),
  zone: z.enum(["green", "yellow", "red"]),
  zone_description: z.string(),
});

export type AverageReactionTime = z.infer<typeof averageReactionTimeSchema>;

export function useAverageReactionTime(athleteId: string | null) {
  const query = useQuery({
    queryKey: ["average-reaction-time", athleteId],
    queryFn: async () => {
      if (!athleteId) return null;
      const response = await api.get<AverageReactionTime>(
        `/athletes/${athleteId}/metrics/reaction-time/average`
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
