import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

interface Athlete {
  athlete_id: string;
  coach_id: string;
  name: string;
  height_in: number | null;
  weight_lbs: number | null;
  created_at: string;
}

export function useAthletes() {
    return useQuery<Athlete[]>({
      queryKey: ["athletes"],
      queryFn: async () => {
        const response = await api.get("/api/athletes");
        return response.data;
      },
    });
  }