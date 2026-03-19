// TODO: Scope to authenticated coach — currently returns all runs regardless of user.
// Future ticket: pass coach_id as query param or use auth-scoped backend endpoint.
import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import api from "@/lib/api";
import { runResponseSchema } from "@/types/run.types";
import type { Run } from "@/types/run.types";

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
