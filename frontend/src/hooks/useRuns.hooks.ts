// TODO: Scope to authenticated coach — currently returns all runs regardless of user.
// Future ticket: pass coach_id as query param or use auth-scoped backend endpoint.
import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import api from "@/lib/api";
import { runResponseSchema, runMetaSchema } from "@/types/run.types";
import type { Run, RunMeta } from "@/types/run.types";

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

export function useGetRunMeta(runId: string | undefined) {
  const query = useQuery({
    queryKey: ["runMeta", runId],
    queryFn: async () => {
      const response = await api.get<RunMeta>(
        `/run/athletes/${runId}/metadata`
      );
      const parsed = runMetaSchema.safeParse(response.data);
      if (!parsed.success) {
        throw new Error("Invalid response format");
      }
      return parsed.data;
    },
    enabled: !!runId,
  });

  return {
    runMeta: query.data ?? null,
    runMetaIsLoading: query.isLoading,
    runMetaError: query.error,
    runMetaRefetch: query.refetch,
  };
}
