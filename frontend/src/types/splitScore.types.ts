import { z } from "zod";

export const segmentScoreSchema = z.object({
  label: z.string(),
  raw_ms: z.number(),
  pct_of_total: z.number(),
  diff_s: z.number(),
  diff_pct: z.number(),
});

export const splitScoreResponseSchema = z.object({
  run_id: z.string(),
  event_type: z.string(),
  total_ms: z.number(),
  segments: z.array(segmentScoreSchema),
  coaching_notes: z.array(z.string()),
  population_mean_pcts: z.array(z.number()),
  population_std_pcts: z.array(z.number()),
});

export type SegmentScore = z.infer<typeof segmentScoreSchema>;
export type SplitScoreData = z.infer<typeof splitScoreResponseSchema>;
