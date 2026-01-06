/**
 * API functions for training runs
 * Mirrors: backend/app/repositories/example_repository.py
 * Direct API calls to backend endpoints
 */

import { apiFetch } from './client';
import type {
  TrainingRunCreate,
  TrainingRunUpdate,
  TrainingRunResponse,
} from '../types/example_types';

const BASE_PATH = '/api/example/training-runs';

/**
 * Get all training runs
 * GET /api/example/training-runs
 */
export async function getAllTrainingRuns(): Promise<TrainingRunResponse[]> {
  return apiFetch<TrainingRunResponse[]>(BASE_PATH);
}

/**
 * Get a training run by ID
 * GET /api/example/training-runs/{id}
 */
export async function getTrainingRunById(
  id: string
): Promise<TrainingRunResponse> {
  return apiFetch<TrainingRunResponse>(`${BASE_PATH}/${id}`);
}

/**
 * Create a new training run
 * POST /api/example/training-runs
 */
export async function createTrainingRun(
  data: TrainingRunCreate
): Promise<TrainingRunResponse> {
  return apiFetch<TrainingRunResponse>(BASE_PATH, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Update a training run
 * PATCH /api/example/training-runs/{id}
 */
export async function updateTrainingRun(
  id: string,
  data: TrainingRunUpdate
): Promise<TrainingRunResponse> {
  return apiFetch<TrainingRunResponse>(`${BASE_PATH}/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * Delete a training run
 * DELETE /api/example/training-runs/{id}
 */
export async function deleteTrainingRun(id: string): Promise<void> {
  return apiFetch<void>(`${BASE_PATH}/${id}`, {
    method: 'DELETE',
  });
}

