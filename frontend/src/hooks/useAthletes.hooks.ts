import { useQuery } from "@tanstack/react-query";
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