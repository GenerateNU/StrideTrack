import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import api from "@/lib/api";

const runResponseSchema = z.object({
  run_id: z.string(),
  athlete_id: z.string(),
  event_type: z.string(),
  elapsed_ms: z.number().nullable().optional(),
  created_at: z.string(),
});

type Run = z.infer<typeof runResponseSchema>;

export type { Run };

export function useGetAllRuns() {
  const query = useQuery({
    queryKey: ["runs"],
    queryFn: async () => {
      const response = await api.get<Run[]>("/run");
      const parsed = z.array(runResponseSchema).safeParse(response.data);
      if (!parsed.success) {
        throw new Error("Invalid response format");
      }
      return parsed.data;
    },
  });

  return {
    runs: query.data ?? [],
    runsIsLoading: query.isLoading,
    runsError: query.error,
    runsRefetch: query.refetch,
  };
}