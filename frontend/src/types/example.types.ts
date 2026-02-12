/**
 * Example Types
 * Types validation using Zod
 */
import { z } from "zod";

/**
 * Training Run Create Schema
 * Validation for creating a new training run
 */
export const trainingRunCreateSchema = z.object({
  athlete_name: z
    .string()
    .min(1, "Athlete name is required")
    .max(255, "Athlete name must be 255 characters or less"),
  distance_meters: z
    .number()
    .int("Distance must be an integer")
    .positive("Distance must be greater than 0"),
  duration_seconds: z.number().positive("Duration must be greater than 0"),
  avg_ground_contact_time_ms: z
    .union([
      z.number().positive("Ground contact time must be greater than 0"),
      z.null(),
    ])
    .optional(),
});

/**
 * Training Run Update Schema
 * Validation for updating an existing training run
 */
export const trainingRunUpdateSchema = z.object({
  athlete_name: z
    .string()
    .min(1, "Athlete name must be at least 1 character")
    .max(255, "Athlete name must be 255 characters or less")
    .nullable()
    .optional(),
  distance_meters: z
    .number()
    .int("Distance must be an integer")
    .positive("Distance must be greater than 0")
    .nullable()
    .optional(),
  duration_seconds: z
    .number()
    .positive("Duration must be greater than 0")
    .nullable()
    .optional(),
  avg_ground_contact_time_ms: z
    .union([
      z.number().positive("Ground contact time must be greater than 0"),
      z.null(),
    ])
    .optional(),
});

/**
 * Training Run Response Schema
 * Validation for the response from the API
 */
export const trainingRunResponseSchema = z.object({
  id: z.string().uuid("Invalid UUID format"),
  athlete_name: z.string(),
  distance_meters: z.number().int(),
  duration_seconds: z.number(),
  avg_ground_contact_time_ms: z.number().nullable(),
  created_at: z.string(),
});

/**
 * Training Run Create Type
 * Type inferred from the trainingRunCreateSchema
 */
export type TrainingRunCreate = z.infer<typeof trainingRunCreateSchema>;
export type TrainingRunUpdate = z.infer<typeof trainingRunUpdateSchema>;
export type TrainingRunResponse = z.infer<typeof trainingRunResponseSchema>;
