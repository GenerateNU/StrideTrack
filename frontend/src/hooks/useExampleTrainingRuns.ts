import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { z } from 'zod';
import { apiClient } from '@/axios.config';
import {
  trainingRunResponseSchema,
  trainingRunCreateSchema,
  trainingRunUpdateSchema,
  type TrainingRunCreate,
  type TrainingRunUpdate,
  type TrainingRunResponse,
} from '@/types/example_types';
import { validateResponse } from '@/utils/validation';

const BASE_PATH = '/api/example/training-runs';

export function useGetAllTrainingRuns() {
  return useQuery({
    queryKey: ['training-runs'],
    queryFn: async () => {
      const response = await apiClient.get<TrainingRunResponse[]>(BASE_PATH);
      return validateResponse(response.data, z.array(trainingRunResponseSchema));
    },
  });
}

export function useGetTrainingRun(id: string | null) {
  return useQuery({
    queryKey: ['training-runs', id],
    queryFn: async () => {
      if (!id) return null;
      
      const response = await apiClient.get<TrainingRunResponse>(`${BASE_PATH}/${id}`);
      return validateResponse(response.data, trainingRunResponseSchema);
    },
    enabled: !!id,
  });
}

export function useCreateTrainingRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: TrainingRunCreate) => {
      const validated = trainingRunCreateSchema.parse(data);
      const response = await apiClient.post<TrainingRunResponse>(BASE_PATH, validated);
      return validateResponse(response.data, trainingRunResponseSchema);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['training-runs'] });
    },
  });
}

export function useUpdateTrainingRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: TrainingRunUpdate }) => {
      const validated = trainingRunUpdateSchema.parse(data);
      const response = await apiClient.patch<TrainingRunResponse>(`${BASE_PATH}/${id}`, validated);
      return validateResponse(response.data, trainingRunResponseSchema);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['training-runs'] });
      queryClient.invalidateQueries({ queryKey: ['training-runs', variables.id] });
    },
  });
}

export function useDeleteTrainingRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`${BASE_PATH}/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['training-runs'] });
    },
  });
}
