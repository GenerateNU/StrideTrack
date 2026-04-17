import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import {
  athleteResponseSchema,
  type Athlete,
  type CreateAthletePayload,
} from "@/types/athlete.types";
import { validateResponse } from "@/utils/validation";
import { z } from "zod";

export function useGetAllAthletes() {
  const query = useQuery({
    queryKey: ["athletes"],
    queryFn: async () => {
      const response = await api.get<Athlete[]>("/athletes");
      return validateResponse(response.data, z.array(athleteResponseSchema));
    },
  });

  return {
    athletes: query.data ?? [],
    athletesIsLoading: query.isLoading,
    athletesError: query.error,
    athletesRefetch: query.refetch,
  };
}

export function useCreateAthlete() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (payload: CreateAthletePayload) => {
      const response = await api.post("/athletes", payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athletes"] });
    },
  });

  return {
    createAthlete: mutation.mutateAsync,
    createAthleteIsLoading: mutation.isPending,
    createAthleteError: mutation.error,
  };
}

export function useUpdateAthlete() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async ({
      athleteId,
      payload,
    }: {
      athleteId: string;
      payload: Partial<Athlete>;
    }) => {
      const response = await api.patch(`/athletes/${athleteId}`, payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athletes"] });
    },
  });

  return {
    updateAthlete: mutation.mutateAsync,
    updateAthleteIsLoading: mutation.isPending,
    updateAthleteError: mutation.error,
  };
}

export function useDeleteAthlete() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (athleteId: string) => {
      await api.delete(`/athletes/${athleteId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["athletes"] });
      queryClient.invalidateQueries({ queryKey: ["runs"] });
    },
  });

  return {
    deleteAthlete: mutation.mutateAsync,
    deleteAthleteIsLoading: mutation.isPending,
    deleteAthleteError: mutation.error,
  };
}
