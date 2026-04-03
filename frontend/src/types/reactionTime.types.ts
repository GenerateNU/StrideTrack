import { z } from "zod";

export const reactionTimeMetricsSchema = z.object({
  run_id: z.string(),
  reaction_time_ms: z.number(),
  onset_timestamp_ms: z.number(),
  zone: z.enum(["green", "yellow", "red"]),
  zone_description: z.string(),
});

export type ReactionTimeMetrics = z.infer<typeof reactionTimeMetricsSchema>;
