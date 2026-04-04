import api from "@/lib/api.ts";
import type {
  GctIncreaseData,
  HurdleProjectionResponse,
  HurdleSplitBarData,
  LandingGctBarData,
  StepsBetweenHurdlesData,
  TakeoffFtBarData,
  TakeoffGctBarData,
} from "@/types/hurdleMetrics.types";
import {
  gctIncreaseSchema,
  hurdleProjectionResponseSchema,
  hurdleSplitBarSchema,
  landingGctBarSchema,
  stepsBetweenHurdlesSchema,
  takeoffFtBarSchema,
  takeoffGctBarSchema,
} from "@/types/hurdleMetrics.types";
import { validateResponse } from "@/utils/validation";
import { useQuery } from "@tanstack/react-query";
import { z } from "zod";

export function useHurdleSplits(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-splits", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await api.get<HurdleSplitBarData[]>(
        `/runs/${runId}/metrics/hurdles/splits`
      );

      return validateResponse(response.data, z.array(hurdleSplitBarSchema));
    },
    enabled: !!runId,
  });

  return {
    hurdleSplits: query.data ?? null,
    hurdleSplitsIsLoading: query.isLoading,
    hurdleSplitsError: query.error,
    hurdleSplitsRefetch: query.refetch,
  };
}

export function useStepsBetweenHurdles(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-steps-between", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await api.get<StepsBetweenHurdlesData[]>(
        `/runs/${runId}/metrics/hurdles/steps-between`
      );

      return validateResponse(
        response.data,
        z.array(stepsBetweenHurdlesSchema)
      );
    },
    enabled: !!runId,
  });

  return {
    stepsBetween: query.data ?? null,
    stepsBetweenIsLoading: query.isLoading,
    stepsBetweenError: query.error,
    stepsBetweenRefetch: query.refetch,
  };
}

export function useTakeoffGct(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-takeoff-gct", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await api.get<TakeoffGctBarData[]>(
        `/runs/${runId}/metrics/hurdles/takeoff-gct`
      );

      return validateResponse(response.data, z.array(takeoffGctBarSchema));
    },
    enabled: !!runId,
  });

  return {
    takeoffGct: query.data ?? null,
    takeoffGctIsLoading: query.isLoading,
    takeoffGctError: query.error,
    takeoffGctRefetch: query.refetch,
  };
}

export function useLandingGct(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-landing-gct", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await api.get<LandingGctBarData[]>(
        `/runs/${runId}/metrics/hurdles/landing-gct`
      );

      return validateResponse(response.data, z.array(landingGctBarSchema));
    },
    enabled: !!runId,
  });

  return {
    landingGct: query.data ?? null,
    landingGctIsLoading: query.isLoading,
    landingGctError: query.error,
    landingGctRefetch: query.refetch,
  };
}

export function useTakeoffFt(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-takeoff-ft", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await api.get<TakeoffFtBarData[]>(
        `/runs/${runId}/metrics/hurdles/takeoff-ft`
      );

      return validateResponse(response.data, z.array(takeoffFtBarSchema));
    },
    enabled: !!runId,
  });

  return {
    takeoffFt: query.data ?? null,
    takeoffFtIsLoading: query.isLoading,
    takeoffFtError: query.error,
    takeoffFtRefetch: query.refetch,
  };
}

export function useGctIncrease(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-gct-increase", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await api.get<GctIncreaseData[]>(
        `/runs/${runId}/metrics/hurdles/gct-increase`
      );

      return validateResponse(response.data, z.array(gctIncreaseSchema));
    },
    enabled: !!runId,
  });

  return {
    gctIncrease: query.data ?? null,
    gctIncreaseIsLoading: query.isLoading,
    gctIncreaseError: query.error,
    gctIncreaseRefetch: query.refetch,
  };
}

export function useHurdleProjection(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-projection", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await api.get<HurdleProjectionResponse>(
        `/runs/${runId}/metrics/hurdles/projection`
      );

      return validateResponse(response.data, hurdleProjectionResponseSchema);
    },
    enabled: !!runId,
  });

  return {
    hurdleProjection: query.data ?? null,
    hurdleProjectionIsLoading: query.isLoading,
    hurdleProjectionError: query.error,
    hurdleProjectionRefetch: query.refetch,
  };
}
