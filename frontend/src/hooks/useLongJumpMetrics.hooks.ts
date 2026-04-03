import api from "@/lib/api";
import type {
  ApproachProfilePoint,
  LjTakeoffData,
  LongJumpMetricRow,
  StepSeriesPoint,
} from "@/types/jumpMetrics.types";
import {
  approachProfilePointSchema,
  ljTakeoffDataSchema,
  longJumpMetricRowSchema,
  stepSeriesPointSchema,
} from "@/types/jumpMetrics.types";
import { validateResponse } from "@/utils/validation";
import { useQuery } from "@tanstack/react-query";
import { z } from "zod";

export function useLongJumpMetrics(runId: string | null) {
  const query = useQuery({
    queryKey: ["long-jump-metrics", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<LongJumpMetricRow>(
        `/api/run/athletes/${runId}/metrics/long-jump`
      );
      return validateResponse(response.data, longJumpMetricRowSchema);
    },
    enabled: !!runId,
  });

  return {
    ljMetrics: query.data ?? null,
    ljMetricsLoading: query.isLoading,
    ljMetricsError: query.error,
    refetchLjMetrics: query.refetch,
  };
}

export function useLjTakeoffData(runId: string | null) {
  const query = useQuery({
    queryKey: ["long-jump-takeoff", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<LjTakeoffData>(
        `/api/run/athletes/${runId}/metrics/long-jump/takeoff`
      );
      return validateResponse(response.data, ljTakeoffDataSchema);
    },
    enabled: !!runId,
  });

  return {
    takeoffData: query.data ?? null,
    takeoffLoading: query.isLoading,
    takeoffError: query.error,
    refetchTakeoffData: query.refetch,
  };
}

export function useLjApproachProfile(runId: string | null) {
  const query = useQuery({
    queryKey: ["long-jump-approach-profile", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<ApproachProfilePoint[]>(
        `/api/run/athletes/${runId}/metrics/long-jump/approach-profile`
      );
      return validateResponse(
        response.data,
        z.array(approachProfilePointSchema)
      );
    },
    enabled: !!runId,
  });

  return {
    approachData: query.data ?? null,
    approachLoading: query.isLoading,
    approachError: query.error,
    refetchApproachData: query.refetch,
  };
}

export function useLjStepSeries(runId: string | null) {
  const query = useQuery({
    queryKey: ["long-jump-step-series", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<StepSeriesPoint[]>(
        `/api/run/athletes/${runId}/metrics/long-jump/universal/steps`
      );
      return validateResponse(response.data, z.array(stepSeriesPointSchema));
    },
    enabled: !!runId,
  });

  return {
    stepSeriesData: query.data ?? null,
    stepSeriesLoading: query.isLoading,
    stepSeriesError: query.error,
    refetchStepSeriesData: query.refetch,
  };
}
