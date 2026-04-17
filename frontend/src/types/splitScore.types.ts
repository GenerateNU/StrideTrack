import { z } from "zod";

export const segmentScoreSchema = z.object({
  label: z.string(),
  raw_ms: z.number(),
  pct_of_total: z.number(),
  diff_s: z.number(),
  diff_pct: z.number(),
});

export const populationPercentilesSchema = z.object({
  p10: z.array(z.number()),
  p25: z.array(z.number()),
  p75: z.array(z.number()),
  p90: z.array(z.number()),
});

export const splitScoreResponseSchema = z.object({
  run_id: z.string(),
  event_type: z.string(),
  total_ms: z.number(),
  segments: z.array(segmentScoreSchema),
  coaching_notes: z.array(z.string()),
  population_mean_pcts: z.array(z.number()),
  population_std_pcts: z.array(z.number()),
  population_percentiles: populationPercentilesSchema,
});

export type SegmentScore = z.infer<typeof segmentScoreSchema>;
export type PopulationPercentiles = z.infer<typeof populationPercentilesSchema>;
export type SplitScoreData = z.infer<typeof splitScoreResponseSchema>;
