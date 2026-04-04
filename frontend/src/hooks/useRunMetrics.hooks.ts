import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import {
  runMetricSchema,
  lrOverlaySchema,
  stackedBarSchema,
  sprintDriftSchema,
  stepFrequencySchema,
  asymmetrySchema,
  gctRangeSchema,
} from "@/types/runMetrics.types.ts";
import type {
  RunMetric,
  LROverlayData,
  StackedBarData,
  SprintDriftData,
  StepFrequencyData,
  AsymmetryData,
  GCTRangeData,
} from "@/types/runMetrics.types.ts";
import api from "@/lib/api";
import { validateResponse } from "@/utils/validation";

export function useRunMetrics(runId: string | null) {
  const query = useQuery({
    queryKey: ["run-metrics", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<RunMetric[]>(`/runs/${runId}/metrics`);
      return validateResponse(response.data, z.array(runMetricSchema));
    },
    enabled: !!runId,
  });

  return {
    runMetrics: query.data ?? null,
    runMetricsIsLoading: query.isLoading,
    runMetricsError: query.error,
    runMetricsRefetch: query.refetch,
  };
}

export function useLROverlayData(
  runId: string | null,
  metric: "gct_ms" | "flight_ms"
) {
  const query = useQuery({
    queryKey: ["lr-overlay", runId, metric],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<LROverlayData[]>(
        `/runs/${runId}/metrics/lr-overlay`,
        { params: { metric } }
      );
      return validateResponse(response.data, z.array(lrOverlaySchema));
    },
    enabled: !!runId,
  });

  return {
    lrOverlay: query.data ?? null,
    lrOverlayIsLoading: query.isLoading,
    lrOverlayError: query.error,
    lrOverlayRefetch: query.refetch,
  };
}

export function useStackedBarData(runId: string | null) {
  const query = useQuery({
    queryKey: ["stacked-bar", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<StackedBarData[]>(
        `/runs/${runId}/metrics/stacked-bar`
      );
      return validateResponse(response.data, z.array(stackedBarSchema));
    },
    enabled: !!runId,
  });

  return {
    stackedBar: query.data ?? null,
    stackedBarIsLoading: query.isLoading,
    stackedBarError: query.error,
    stackedBarRefetch: query.refetch,
  };
}

export function useSprintDrift(runId: string | null) {
  const query = useQuery({
    queryKey: ["sprint-drift", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<SprintDriftData>(
        `/runs/${runId}/metrics/sprint/drift`
      );
      return validateResponse(response.data, sprintDriftSchema);
    },
    enabled: !!runId,
  });

  return {
    sprintDrift: query.data ?? null,
    sprintDriftIsLoading: query.isLoading,
    sprintDriftError: query.error,
    sprintDriftRefetch: query.refetch,
  };
}

export function useStepFrequencyData(runId: string | null) {
  const query = useQuery({
    queryKey: ["step-frequency", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<StepFrequencyData[]>(
        `/runs/${runId}/metrics/sprint/step-frequency`
      );
      return validateResponse(response.data, z.array(stepFrequencySchema));
    },
    enabled: !!runId,
  });

  return {
    stepFrequency: query.data ?? null,
    stepFrequencyIsLoading: query.isLoading,
    stepFrequencyError: query.error,
    stepFrequencyRefetch: query.refetch,
  };
}

export function useAsymmetryData(runId: string | null) {
  const query = useQuery({
    queryKey: ["asymmetry", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<AsymmetryData>(
        `/runs/${runId}/metrics/asymmetry`
      );
      return validateResponse(response.data, asymmetrySchema);
    },
    enabled: !!runId,
  });

  return {
    asymmetry: query.data ?? null,
    asymmetryIsLoading: query.isLoading,
    asymmetryError: query.error,
    asymmetryRefetch: query.refetch,
  };
}

export function useGCTRangeData(
  runId: string | null,
  minMs: number,
  maxMs: number
) {
  const query = useQuery({
    queryKey: ["gct-range", runId, minMs, maxMs],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<GCTRangeData>(
        `/runs/${runId}/metrics/gct-range`,
        { params: { min_ms: minMs, max_ms: maxMs } }
      );
      return validateResponse(response.data, gctRangeSchema);
    },
    enabled: !!runId,
  });

  return {
    gctRange: query.data ?? null,
    gctRangeIsLoading: query.isLoading,
    gctRangeError: query.error,
    gctRangeRefetch: query.refetch,
  };
}
