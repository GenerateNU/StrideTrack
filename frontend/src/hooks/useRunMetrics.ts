import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import {
  runMetricSchema,
  lrOverlaySchema,
  stackedBarSchema,
  sprintDriftSchema,
  stepFrequencySchema,
} from "@/types/runMetrics.types.ts";
import type {
  RunMetric,
  LROverlayData,
  StackedBarData,
  SprintDriftData,
  StepFrequencyData,
} from "@/types/runMetrics.types.ts";
import { apiClient } from "@/axios.config";
import { validateResponse } from "@/utils/validation";

export function useRunMetrics(runId: string | null) {
  const query = useQuery({
    queryKey: ["run-metrics", runId],
    queryFn: async () => {
      if (!runId) return [];

      const response = await apiClient.get<RunMetric[]>(
        `/api/run/athletes/${runId}/metrics`
      );
      return validateResponse(response.data, z.array(runMetricSchema));
    },
    enabled: !!runId,
  });

  return {
    metrics: query.data ?? [],
    metricsIsLoading: query.isLoading,
    metricsError: query.error,
    metricsRefetch: query.refetch,
  };
}

export function useLROverlayData(
  runId: string | null,
  metric: "gct_ms" | "flight_ms"
) {
  const query = useQuery({
    queryKey: ["lr-overlay", runId, metric],
    queryFn: async () => {
      if (!runId) return [];
      const response = await apiClient.get<LROverlayData[]>(
        `/api/run/athletes/${runId}/metrics/lr-overlay`,
        { params: { metric } }
      );
      return validateResponse(response.data, z.array(lrOverlaySchema));
    },
    enabled: !!runId,
  });

  return {
    lrData: query.data ?? [],
    lrLoading: query.isLoading,
    lrError: query.error,
  };
}

export function useStackedBarData(runId: string | null) {
  const query = useQuery({
    queryKey: ["stacked-bar", runId],
    queryFn: async () => {
      if (!runId) return [];
      const response = await apiClient.get<StackedBarData[]>(
        `/api/run/athletes/${runId}/metrics/stacked-bar`
      );
      return validateResponse(response.data, z.array(stackedBarSchema));
    },
    enabled: !!runId,
  });

  return {
    stackedData: query.data ?? [],
    stackedLoading: query.isLoading,
    stackedError: query.error,
  };
}

export function useSprintDrift(runId: string | null) {
  const query = useQuery({
    queryKey: ["sprint-drift", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await apiClient.get<SprintDriftData>(
        `/api/run/athletes/${runId}/metrics/sprint-drift`
      );
      return validateResponse(response.data, sprintDriftSchema);
    },
    enabled: !!runId,
  });
  
  return {
    driftData: query.data ?? null,
    driftLoading: query.isLoading,
    driftError: query.error,
    driftRefetch: query.refetch,
  };
}

export function useStepFrequencyData(runId: string | null) {
  const query = useQuery({
    queryKey: ["step-frequency", runId],
    queryFn: async () => {
      if (!runId) return [];
      const response = await apiClient.get<StepFrequencyData[]>(
        `/api/run/athletes/${runId}/metrics/step-frequency`
      );
      return validateResponse(response.data, z.array(stepFrequencySchema));
    },
    enabled: !!runId,
  });

  return {
    stepFrequencyData: query.data ?? [],
    stepFrequencyLoading: query.isLoading,
    stepFrequencyError: query.error,
  };
}
