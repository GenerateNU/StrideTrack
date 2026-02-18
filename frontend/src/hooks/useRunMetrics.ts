import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import { apiClient } from "@/axios.config";
import { validateResponse } from "@/utils/validation";

const runMetricSchema = z.object({
  stride_num: z.number(),
  foot: z.string(),
  ic_time: z.number(),
  gct_ms: z.number(),
  flight_ms: z.number(),
  step_time_ms: z.number(),
});

const lrOverlaySchema = z.object({
  stride_num: z.number(),
  left: z.number().nullable(),
  right: z.number().nullable(),
});

const stackedBarSchema = z.object({
  stride_num: z.number(),
  foot: z.string(),
  label: z.string(),
  gct_ms: z.number(),
  flight_ms: z.number(),
});


export type RunMetric = z.infer<typeof runMetricSchema>;
export type LROverlayData = z.infer<typeof lrOverlaySchema>;
export type StackedBarData = z.infer<typeof stackedBarSchema>;

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