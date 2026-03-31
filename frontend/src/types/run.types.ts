import type { EventTypeEnum, HurdleTargetEvent } from "@/types/event.types";
import { z } from "zod";

export const runResponseSchema = z.object({
  run_id: z.string(),
  athlete_id: z.string(),
  event_type: z.string(),
  target_event: z.string().nullable().optional(),
  elapsed_ms: z.number().nullable().optional(),
  created_at: z.string(),
});

export type Run = z.infer<typeof runResponseSchema>;

export const createRunPayloadSchema = z.object({
  athlete_id: z.string(),
  event_type: z.string(),
  elapsed_ms: z.number().positive(),
  target_event: z.string().optional(),
});

export const createRunResponseSchema = z.object({
  run_id: z.string(),
  athlete_id: z.string(),
  event_type: z.string(),
  target_event: z.string().nullable().optional(),
  elapsed_ms: z.number(),
  created_at: z.string(),
});

export interface CreateRunPayload {
  athlete_id: string;
  event_type: EventTypeEnum;
  elapsed_ms: number;
  target_event?: HurdleTargetEvent;
}

export type CreateRunResponse = z.infer<typeof createRunResponseSchema>;
