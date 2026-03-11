import type { EventTypeEnum } from "@/types/event.types";

export interface CreateRunPayload {
  athlete_id: string;
  event_type: EventTypeEnum;
  elapsed_ms: number;
}

export interface CreateRunResponse {
  run_id: string;
  athlete_id: string;
  event_type: string;
  elapsed_ms: number;
  created_at: string;
}