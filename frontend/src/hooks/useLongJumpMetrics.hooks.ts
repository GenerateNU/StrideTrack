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
        `/runs/${runId}/metrics/long-jump`
      );
      return validateResponse(response.data, longJumpMetricRowSchema);
    },
    enabled: !!runId,
  });
  return {
    ljMetrics: query.data ?? null,
    ljMetricsIsLoading: query.isLoading,
    ljMetricsError: query.error,
    ljMetricsRefetch: query.refetch,
  };
}

export function useLjTakeoffData(runId: string | null) {
  const query = useQuery({
    queryKey: ["long-jump-takeoff", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<LjTakeoffData>(
        `/runs/${runId}/metrics/long-jump/takeoff`
      );
      return validateResponse(response.data, ljTakeoffDataSchema);
    },
    enabled: !!runId,
  });
  return {
    ljTakeoffData: query.data ?? null,
    ljTakeoffDataIsLoading: query.isLoading,
    ljTakeoffDataError: query.error,
    ljTakeoffDataRefetch: query.refetch,
  };
}

export function useLjApproachProfile(runId: string | null) {
  const query = useQuery({
    queryKey: ["long-jump-approach-profile", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<ApproachProfilePoint[]>(
        `/runs/${runId}/metrics/long-jump/approach-profile`
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
    approachDataIsLoading: query.isLoading,
    approachDataError: query.error,
    approachDataRefetch: query.refetch,
  };
}

export function useLjStepSeries(runId: string | null) {
  const query = useQuery({
    queryKey: ["long-jump-step-series", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<StepSeriesPoint[]>(
        `/runs/${runId}/metrics/long-jump/steps`
      );
      return validateResponse(response.data, z.array(stepSeriesPointSchema));
    },
    enabled: !!runId,
  });
  return {
    ljStepSeries: query.data ?? null,
    ljStepSeriesIsLoading: query.isLoading,
    ljStepSeriesError: query.error,
    ljStepSeriesRefetch: query.refetch,
  };
}
