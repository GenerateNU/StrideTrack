import { useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "@/lib/api";
import type { CreateRunPayload, CreateRunResponse } from "@/types/run.types";

export function useCreateRun() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (data: CreateRunPayload) => {
      const response = await apiClient.post<CreateRunResponse>("/run", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
    },
  });

  return {
    createRun: mutation.mutateAsync,
    createRunIsLoading: mutation.isPending,
    createRunError: mutation.error,
  };
}
