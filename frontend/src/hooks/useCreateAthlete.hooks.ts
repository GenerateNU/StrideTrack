import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

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
