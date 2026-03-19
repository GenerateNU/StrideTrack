import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import {
  runMetricSchema,
  lrOverlaySchema,
  stackedBarSchema,
} from "@/types/runMetrics.types.ts";
import type {
  RunMetric,
  LROverlayData,
  StackedBarData,
} from "@/types/runMetrics.types.ts";
import api from "@/lib/api";
import { validateResponse } from "@/utils/validation";

export function useRunMetrics(runId: string | null) {
  const query = useQuery({
    queryKey: ["run-metrics", runId],
    queryFn: async () => {
      if (!runId) return [];

      const response = await api.get<RunMetric[]>(
        `/run/athletes/${runId}/metrics`
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
      const response = await api.get<LROverlayData[]>(
        `/run/athletes/${runId}/metrics/lr-overlay`,
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
      const response = await api.get<StackedBarData[]>(
        `/run/athletes/${runId}/metrics/stacked-bar`
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
