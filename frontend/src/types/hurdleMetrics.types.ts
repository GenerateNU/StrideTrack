import { z } from "zod";

export const hurdleSplitSchema = z.object({
  hurdle_number: z.number(),
  split_time_ms: z.number(),
});

export const hurdleSplitResponseSchema = z.object({
  splits: z.array(hurdleSplitSchema),
  mean_split_ms: z.number(),
  consistency_cv: z.number(),
});

export type HurdleSplit = z.infer<typeof hurdleSplitSchema>;
export type HurdleSplitResponse = z.infer<typeof hurdleSplitResponseSchema>;
