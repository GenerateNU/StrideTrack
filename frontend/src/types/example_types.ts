/**
 * TypeScript types matching backend Pydantic schemas
 * Mirrors: backend/app/schemas/example_schemas.py
 */

export interface TrainingRunCreate {
  athlete_name: string;
  distance_meters: number;
  duration_seconds: number;
  avg_ground_contact_time_ms?: number | null;
}

export interface TrainingRunUpdate {
  athlete_name?: string | null;
  distance_meters?: number | null;
  duration_seconds?: number | null;
  avg_ground_contact_time_ms?: number | null;
}

export interface TrainingRunResponse {
  id: string; // UUID as string
  athlete_name: string;
  distance_meters: number;
  duration_seconds: number;
  avg_ground_contact_time_ms: number | null;
  created_at: string;
}

