import { z } from "zod";

export const reactionTimeMetricsSchema = z.object({
  run_id: z.string(),
  reaction_time_ms: z.number(),
  onset_timestamp_ms: z.number(),
  zone: z.enum(["green", "yellow", "red"]),
  zone_description: z.string(),
});

export type ReactionTimeMetrics = z.infer<typeof reactionTimeMetricsSchema>;

export const averageReactionTimeSchema = z.object({
  athlete_id: z.string(),
  average_reaction_time_ms: z.number(),
  run_count: z.number(),
  zone: z.enum(["green", "yellow", "red"]),
  zone_description: z.string(),
});

export type AverageReactionTime = z.infer<typeof averageReactionTimeSchema>;
