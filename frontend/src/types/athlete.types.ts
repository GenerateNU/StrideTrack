import { z } from "zod";

export const athleteResponseSchema = z.object({
  athlete_id: z.string(),
  coach_id: z.string(),
  name: z.string(),
  height_in: z.number().nullable(),
  weight_lbs: z.number().nullable(),
  gender: z.enum(["male", "female", "other"]),
  created_at: z.string(),
});

export type Athlete = z.infer<typeof athleteResponseSchema>;

export const createAthletePayloadSchema = z.object({
  name: z.string().min(1).max(255),
  height_in: z.number().positive().nullable(),
  weight_lbs: z.number().positive().nullable(),
  gender: z.enum(["male", "female", "other"]),
});

export type CreateAthletePayload = z.infer<typeof createAthletePayloadSchema>;
