/**
 * React hooks for training runs
 * Mirrors: backend/app/services/example_service.py
 * Business logic layer - orchestrates API calls
 */

import { useState, useEffect, useCallback } from 'react';
import {
  getAllTrainingRuns,
  getTrainingRunById,
  createTrainingRun,
  updateTrainingRun,
  deleteTrainingRun,
} from '../api/example_api';
import type {
  TrainingRunCreate,
  TrainingRunUpdate,
  TrainingRunResponse,
} from '../types/example_types';
import { ApiClientError } from '../api/client';

interface UseTrainingRunsState {
  runs: TrainingRunResponse[];
  loading: boolean;
  error: string | null;
}

interface UseTrainingRunState {
  run: TrainingRunResponse | null;
  loading: boolean;
  error: string | null;
}

/**
 * Hook to fetch all training runs
 */
export function useGetAllTrainingRuns() {
  const [state, setState] = useState<UseTrainingRunsState>({
    runs: [],
    loading: true,
    error: null,
  });

  const fetchRuns = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const runs = await getAllTrainingRuns();
      setState({ runs, loading: false, error: null });
    } catch (error) {
      const message =
        error instanceof ApiClientError
          ? error.message
          : 'Failed to fetch training runs';
      setState({ runs: [], loading: false, error: message });
    }
  }, []);

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  return { ...state, refetch: fetchRuns };
}

/**
 * Hook to fetch a single training run by ID
 */
export function useGetTrainingRun(id: string | null) {
  const [state, setState] = useState<UseTrainingRunState>({
    run: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    if (!id) {
      setState({ run: null, loading: false, error: null });
      return;
    }

    setState((prev) => ({ ...prev, loading: true, error: null }));
    getTrainingRunById(id)
      .then((run) => {
        setState({ run, loading: false, error: null });
      })
      .catch((error) => {
        const message =
          error instanceof ApiClientError
            ? error.message
            : 'Failed to fetch training run';
        setState({ run: null, loading: false, error: message });
      });
  }, [id]);

  return state;
}

/**
 * Hook to create a training run
 */
export function useCreateTrainingRun() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = useCallback(async (data: TrainingRunCreate) => {
    setLoading(true);
    setError(null);
    try {
      const run = await createTrainingRun(data);
      setLoading(false);
      return run;
    } catch (err) {
      const message =
        err instanceof ApiClientError
          ? err.message
          : 'Failed to create training run';
      setError(message);
      setLoading(false);
      throw err;
    }
  }, []);

  return { create, loading, error };
}

/**
 * Hook to update a training run
 */
export function useUpdateTrainingRun() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = useCallback(
    async (id: string, data: TrainingRunUpdate) => {
      setLoading(true);
      setError(null);
      try {
        const run = await updateTrainingRun(id, data);
        setLoading(false);
        return run;
      } catch (err) {
        const message =
          err instanceof ApiClientError
            ? err.message
            : 'Failed to update training run';
        setError(message);
        setLoading(false);
        throw err;
      }
    },
    []
  );

  return { update, loading, error };
}

/**
 * Hook to delete a training run
 */
export function useDeleteTrainingRun() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const remove = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await deleteTrainingRun(id);
      setLoading(false);
    } catch (err) {
      const message =
        err instanceof ApiClientError
          ? err.message
          : 'Failed to delete training run';
      setError(message);
      setLoading(false);
      throw err;
    }
  }, []);

  return { remove, loading, error };
}

