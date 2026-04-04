import { z } from "zod";

// Base hurdle metric row
export const hurdleMetricRowSchema = z.object({
  hurdle_num: z.number(),
  clearance_start_ms: z.number(),
  clearance_end_ms: z.number(),
  takeoff_ft_ms: z.number(),
  hurdle_split_ms: z.number().nullable(),
  steps_between_hurdles: z.number().nullable(),
  takeoff_foot: z.enum(["left", "right"]).nullable(),
  takeoff_gct_ms: z.number().nullable(),
  landing_foot: z.enum(["left", "right"]).nullable(),
  landing_gct_ms: z.number().nullable(),
  gct_increase_hurdle_to_hurdle_pct: z.number().nullable(),
});

// Visualization-specific schemas
export const hurdleSplitBarSchema = z.object({
  hurdle_num: z.number(),
  hurdle_split_ms: z.number().nullable(),
});

export const stepsBetweenHurdlesSchema = z.object({
  hurdle_num: z.number(),
  steps_between_hurdles: z.number().nullable(),
});

export const takeoffGctBarSchema = z.object({
  hurdle_num: z.number(),
  takeoff_foot: z.enum(["left", "right"]).nullable(),
  takeoff_gct_ms: z.number().nullable(),
});

export const landingGctBarSchema = z.object({
  hurdle_num: z.number(),
  landing_foot: z.enum(["left", "right"]).nullable(),
  landing_gct_ms: z.number().nullable(),
});

export const takeoffFtBarSchema = z.object({
  hurdle_num: z.number(),
  takeoff_ft_ms: z.number(),
});

export const gctIncreaseSchema = z.object({
  hurdle_num: z.number(),
  takeoff_gct_ms: z.number().nullable(),
  gct_increase_hurdle_to_hurdle_pct: z.number().nullable(),
});

export const projectedSplitSchema = z.object({
  hurdle_num: z.number(),
  split_ms: z.number(),
});

export const hurdleProjectionResponseSchema = z.object({
  completed_splits: z.array(projectedSplitSchema),
  projected_splits: z.array(projectedSplitSchema),
  projected_final_segment_ms: z.number(),
  projected_total_ms: z.number().nullable(),
  confidence: z.number(),
  target_event: z.string(),
  total_hurdles: z.number(),
});

export type HurdleMetricRow = z.infer<typeof hurdleMetricRowSchema>;
export type HurdleSplitBarData = z.infer<typeof hurdleSplitBarSchema>;
export type StepsBetweenHurdlesData = z.infer<typeof stepsBetweenHurdlesSchema>;
export type TakeoffGctBarData = z.infer<typeof takeoffGctBarSchema>;
export type LandingGctBarData = z.infer<typeof landingGctBarSchema>;
export type TakeoffFtBarData = z.infer<typeof takeoffFtBarSchema>;
export type GctIncreaseData = z.infer<typeof gctIncreaseSchema>;
export type ProjectedSplit = z.infer<typeof projectedSplitSchema>;
export type HurdleProjectionResponse = z.infer<
  typeof hurdleProjectionResponseSchema
>;
