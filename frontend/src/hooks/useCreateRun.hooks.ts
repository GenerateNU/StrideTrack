import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { validateResponse } from "@/utils/validation";
import {
  createRunPayloadSchema,
  createRunResponseSchema,
} from "@/types/run.types";
import type { CreateRunPayload, CreateRunResponse } from "@/types/run.types";

export function useCreateRun() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (data: CreateRunPayload) => {
      const validated = createRunPayloadSchema.parse(data);
      const response = await api.post<CreateRunResponse>("/run", validated);
      return validateResponse(response.data, createRunResponseSchema);
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
