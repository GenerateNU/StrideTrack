import { useMutation } from "@tanstack/react-query";
import apiClient from "@/lib/api";
import type { EventTypeEnum } from "@/types/event.types";

const BASE_PATH = "/api";

interface CreateRunPayload {
  athlete_id: string;
  event_type: EventTypeEnum;
  elapsed_ms: number;
}

interface CreateRunResponse {
  run_id: string;
  athlete_id: string;
  event_type: string;
  elapsed_ms: number;
  created_at: string;
}

export function useCreateRun() {
  return useMutation<CreateRunResponse, Error, CreateRunPayload>({
    mutationFn: async (data) => {
      const response = await apiClient.post<CreateRunResponse>(
        `${BASE_PATH}/run`,
        data
      );
      return response.data;
    },
  });
}