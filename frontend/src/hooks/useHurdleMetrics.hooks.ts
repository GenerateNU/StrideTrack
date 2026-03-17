import { apiClient } from "@/axios.config";
import type {
  GctIncreaseData,
  HurdleSplitBarData,
  LandingGctBarData,
  StepsBetweenHurdlesData,
  TakeoffFtBarData,
  TakeoffGctBarData,
} from "@/types/hurdleMetrics.types";
import {
  gctIncreaseSchema,
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

      const response = await apiClient.get<HurdleSplitBarData[]>(
        `/api/run/athletes/${runId}/metrics/hurdles/splits`
      );

      return validateResponse(response.data, z.array(hurdleSplitBarSchema));
    },
    enabled: !!runId,
  });

  return {
    splitData: query.data ?? null,
    splitLoading: query.isLoading,
    splitError: query.error,
    refetchSplitData: query.refetch,
  };
}

export function useStepsBetweenHurdles(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-steps-between", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await apiClient.get<StepsBetweenHurdlesData[]>(
        `/api/run/athletes/${runId}/metrics/hurdles/steps-between`
      );

      return validateResponse(
        response.data,
        z.array(stepsBetweenHurdlesSchema)
      );
    },
    enabled: !!runId,
  });

  return {
    stepsData: query.data ?? null,
    stepsLoading: query.isLoading,
    stepsError: query.error,
    refetchStepsData: query.refetch,
  };
}

export function useTakeoffGct(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-takeoff-gct", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await apiClient.get<TakeoffGctBarData[]>(
        `/api/run/athletes/${runId}/metrics/hurdles/takeoff-gct`
      );

      return validateResponse(response.data, z.array(takeoffGctBarSchema));
    },
    enabled: !!runId,
  });

  return {
    takeoffGctData: query.data ?? null,
    takeoffGctLoading: query.isLoading,
    takeoffGctError: query.error,
    refetchTakeoffGctData: query.refetch,
  };
}

export function useLandingGct(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-landing-gct", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await apiClient.get<LandingGctBarData[]>(
        `/api/run/athletes/${runId}/metrics/hurdles/landing-gct`
      );

      return validateResponse(response.data, z.array(landingGctBarSchema));
    },
    enabled: !!runId,
  });

  return {
    landingGctData: query.data ?? null,
    landingGctLoading: query.isLoading,
    landingGctError: query.error,
    refetchLandingGctData: query.refetch,
  };
}

export function useTakeoffFt(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-takeoff-ft", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await apiClient.get<TakeoffFtBarData[]>(
        `/api/run/athletes/${runId}/metrics/hurdles/takeoff-ft`
      );

      return validateResponse(response.data, z.array(takeoffFtBarSchema));
    },
    enabled: !!runId,
  });

  return {
    takeoffFtData: query.data ?? null,
    takeoffFtLoading: query.isLoading,
    takeoffFtError: query.error,
    refetchTakeoffFtData: query.refetch,
  };
}

export function useGctIncrease(runId: string | null) {
  const query = useQuery({
    queryKey: ["hurdle-gct-increase", runId],
    queryFn: async () => {
      if (!runId) {
        return null;
      }

      const response = await apiClient.get<GctIncreaseData[]>(
        `/api/run/athletes/${runId}/metrics/hurdles/gct-increase`
      );

      return validateResponse(response.data, z.array(gctIncreaseSchema));
    },
    enabled: !!runId,
  });

  return {
    gctIncreaseData: query.data ?? null,
    gctIncreaseLoading: query.isLoading,
    gctIncreaseError: query.error,
    refetchGctIncreaseData: query.refetch,
  };
}
