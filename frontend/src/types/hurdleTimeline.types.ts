import { z } from "zod";

export const hurdleTimelinePointSchema = z.object({
  time_s: z.number(),
  foot: z.enum(["left", "right"]),
  phase: z.enum(["ground", "air"]),
  gct_ms: z.number().nullable(),
  ft_ms: z.number().nullable(),
});

export const hurdleMarkerSchema = z.object({
  time_s: z.number(),
  hurdle_num: z.number(),
});

export const hurdleTimelineResponseSchema = z.object({
  points: z.array(hurdleTimelinePointSchema),
  hurdle_markers: z.array(hurdleMarkerSchema),
});

export type HurdleTimelinePoint = z.infer<typeof hurdleTimelinePointSchema>;
export type HurdleMarker = z.infer<typeof hurdleMarkerSchema>;
export type HurdleTimelineResponse = z.infer<
  typeof hurdleTimelineResponseSchema
>;
