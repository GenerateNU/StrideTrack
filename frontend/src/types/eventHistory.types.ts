// Type validation for useEventHistory hook
import { z } from "zod";

export const eventHistoryPointSchema = z.object({
  run_number: z.number(),
  run_id: z.string(),
  run_name: z.string(),
  date: z.string(),
  total_time_seconds: z.number(),
});

export const eventHistoryResponseSchema = z.object({
  event_type: z.string(),
  athlete_id: z.string(),
  data_points: z.array(eventHistoryPointSchema),
  best_time_seconds: z.number().nullable(),
  total_runs: z.number(),
});

export type EventHistoryPoint = z.infer<typeof eventHistoryPointSchema>;
export type EventHistoryResponse = z.infer<typeof eventHistoryResponseSchema>;

