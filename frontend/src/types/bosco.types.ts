import { z } from "zod";

export const boscoMetricsSchema = z.object({
  run_id: z.string(),
  jump_heights: z.array(z.number()),
  mean_jump_height: z.number(),
  peak_jump_height: z.number(),
  peak_jump_index: z.number(),
  jump_frequency: z.number(),
  rsi_per_jump: z.array(z.number()),
  fatigue_index_pct: z.number(),
});

export type BoscoMetricsResponse = z.infer<typeof boscoMetricsSchema>;