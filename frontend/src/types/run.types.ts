import { z } from "zod";
import type { EventTypeEnum } from "@/types/event.types";

export const createRunPayloadSchema = z.object({
  athlete_id: z.string(),
  event_type: z.string(),
  elapsed_ms: z.number().positive(),
});

export const createRunResponseSchema = z.object({
  run_id: z.string(),
  athlete_id: z.string(),
  event_type: z.string(),
  elapsed_ms: z.number(),
  created_at: z.string(),
});

export interface CreateRunPayload {
  athlete_id: string;
  event_type: EventTypeEnum;
  elapsed_ms: number;
}

export type CreateRunResponse = z.infer<typeof createRunResponseSchema>;
