import { z } from "zod";
import type { EventTypeEnum } from "@/types/event.types";

export const runResponseSchema = z.object({
  run_id: z.string(),
  athlete_id: z.string(),
  event_type: z.string(),
  elapsed_ms: z.number(),
  created_at: z.string(),
});

export type Run = z.infer<typeof runResponseSchema>;

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

export const runMetaSchema = z.object({
  run_id: z.string().uuid(),
  athlete_id: z.string().uuid(),
  event_type: z.string(),
  created_at: z.string(),
  name: z.string().nullable(),
  elapsed_ms: z.number(),
});

export type RunMeta = z.infer<typeof runMetaSchema>;
