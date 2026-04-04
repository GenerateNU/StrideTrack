// TODO: Scope to authenticated coach — currently returns all athletes regardless of user.
// Future ticket: pass coach_id as query param or use auth-scoped backend endpoint.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { z } from "zod";
import api from "@/lib/api";

const athleteResponseSchema = z.object({
  athlete_id: z.string(),
  coach_id: z.string(),
  name: z.string(),
  height_in: z.number().nullable(),
  weight_lbs: z.number().nullable(),
  created_at: z.string(),
});

type Athlete = z.infer<typeof athleteResponseSchema>;

export function useGetAllAthletes() {
  const query = useQuery({
    queryKey: ["athletes"],
    queryFn: async () => {
      const response = await api.get<Athlete[]>("/athletes");

      const parsed = z.array(athleteResponseSchema).safeParse(response.data);
      if (!parsed.success) {
        throw new Error("Invalid response format");
      }
      return parsed.data;
    },
  });

  return {
    athletes: query.data ?? [],
    athletesIsLoading: query.isLoading,
    athletesError: query.error,
    athletesRefetch: query.refetch,
  };
}

interface CreateAthletePayload {
  name: string;
  height_in: number | null;
  weight_lbs: number | null;
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
    },
  });

  return {
    deleteAthlete: mutation.mutateAsync,
    deleteAthleteIsLoading: mutation.isPending,
    deleteAthleteError: mutation.error,
  };
}
