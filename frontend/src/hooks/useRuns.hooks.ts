// TODO: Scope to authenticated coach — currently returns all runs regardless of user.
// Future ticket: pass coach_id as query param or use auth-scoped backend endpoint.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import api from "@/lib/api";
import { runResponseSchema, runMetaSchema } from "@/types/run.types";
import type { Run, RunMeta } from "@/types/run.types";
import { validateResponse } from "@/utils/validation";

export function useGetAllRuns() {
  const query = useQuery({
    queryKey: ["runs"],
    queryFn: async () => {
      const response = await api.get<Run[]>("/runs");
      return validateResponse(response.data, z.array(runResponseSchema));
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
      const response = await api.get<RunMeta>(`/runs/${runId}/metadata`);
      return validateResponse(response.data, runMetaSchema);
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

export function useUpdateRun() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async ({
      runId,
      payload,
    }: {
      runId: string;
      payload: Record<string, unknown>;
    }) => {
      const response = await api.patch(`/runs/${runId}`, payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
      queryClient.invalidateQueries({ queryKey: ["runFeedback"] });
    },
  });

  return {
    updateRun: mutation.mutateAsync,
    updateRunIsLoading: mutation.isPending,
    updateRunError: mutation.error,
  };
}

export function useDeleteRun() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (runId: string) => {
      await api.delete(`/runs/${runId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
    },
  });

  return {
    deleteRun: mutation.mutateAsync,
    deleteRunIsLoading: mutation.isPending,
    deleteRunError: mutation.error,
  };
}
