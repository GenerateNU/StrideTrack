import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import api from "@/lib/api.ts";
import {
  trainingRunResponseSchema,
  trainingRunCreateSchema,
  trainingRunUpdateSchema,
  type TrainingRunCreate,
  type TrainingRunUpdate,
  type TrainingRunResponse,
} from "@/types/example.types";
import { validateResponse } from "@/utils/validation";

const BASE_PATH = "/api/example/training-runs";

export function useGetAllTrainingRuns() {
  const query = useQuery({
    queryKey: ["training-runs"],
    queryFn: async () => {
      const response = await api.get<TrainingRunResponse[]>(BASE_PATH);
      return validateResponse(
        response.data,
        z.array(trainingRunResponseSchema)
      );
    },
  });

  return {
    trainingRuns: query.data ?? [],
    trainingRunsIsLoading: query.isLoading,
    trainingRunsError: query.error,
    trainingRunsRefetch: query.refetch,
  };
}

export function useGetTrainingRun(id: string | null) {
  const query = useQuery({
    queryKey: ["training-runs", id],
    queryFn: async () => {
      if (!id) return null;

      const response = await api.get<TrainingRunResponse>(`${BASE_PATH}/${id}`);
      return validateResponse(response.data, trainingRunResponseSchema);
    },
    enabled: !!id,
  });

  return {
    trainingRun: query.data,
    trainingRunIsLoading: query.isLoading,
    trainingRunError: query.error,
    trainingRunRefetch: query.refetch,
  };
}

export function useCreateTrainingRun() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (data: TrainingRunCreate) => {
      const validated = trainingRunCreateSchema.parse(data);
      const response = await api.post<TrainingRunResponse>(
        BASE_PATH,
        validated
      );
      return validateResponse(response.data, trainingRunResponseSchema);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["training-runs"] });
    },
  });

  return {
    createTrainingRun: mutation.mutateAsync,
    createTrainingRunIsLoading: mutation.isPending,
    createTrainingRunError: mutation.error,
  };
}

export function useUpdateTrainingRun() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: string;
      data: TrainingRunUpdate;
    }) => {
      const validated = trainingRunUpdateSchema.parse(data);
      const response = await api.patch<TrainingRunResponse>(
        `${BASE_PATH}/${id}`,
        validated
      );
      return validateResponse(response.data, trainingRunResponseSchema);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["training-runs"] });
      queryClient.invalidateQueries({
        queryKey: ["training-runs", variables.id],
      });
    },
  });

  return {
    updateTrainingRun: mutation.mutateAsync,
    updateTrainingRunIsLoading: mutation.isPending,
    updateTrainingRunError: mutation.error,
  };
}

export function useDeleteTrainingRun() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`${BASE_PATH}/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["training-runs"] });
    },
  });

  return {
    deleteTrainingRun: mutation.mutateAsync,
    deleteTrainingRunIsLoading: mutation.isPending,
    deleteTrainingRunError: mutation.error,
  };
}
