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
      const response = await api.get<RunMetric[]>(
        `/run/athletes/${runId}/metrics`
      );
      return validateResponse(response.data, z.array(runMetricSchema));
    },
    enabled: !!runId,
  });

  return {
    metrics: query.data ?? null,
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
      if (!runId) return null;
      const response = await api.get<LROverlayData[]>(
        `/run/athletes/${runId}/metrics/lr-overlay`,
        { params: { metric } }
      );
      return validateResponse(response.data, z.array(lrOverlaySchema));
    },
    enabled: !!runId,
  });

  return {
    lrData: query.data ?? null,
    lrLoading: query.isLoading,
    lrError: query.error,
  };
}

export function useStackedBarData(runId: string | null) {
  const query = useQuery({
    queryKey: ["stacked-bar", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<StackedBarData[]>(
        `/run/athletes/${runId}/metrics/stacked-bar`
      );
      return validateResponse(response.data, z.array(stackedBarSchema));
    },
    enabled: !!runId,
  });

  return {
    stackedData: query.data ?? null,
    stackedLoading: query.isLoading,
    stackedError: query.error,
  };
}

export function useSprintDrift(runId: string | null) {
  const query = useQuery({
    queryKey: ["sprint-drift", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<SprintDriftData>(
        `/run/athletes/${runId}/metrics/sprint-drift`
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
      if (!runId) return null;
      const response = await api.get<StepFrequencyData[]>(
        `/run/athletes/${runId}/metrics/step-frequency`
      );
      return validateResponse(response.data, z.array(stepFrequencySchema));
    },
    enabled: !!runId,
  });

  return {
    stepFrequencyData: query.data ?? null,
    stepFrequencyLoading: query.isLoading,
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
        `/run/athletes/${runId}/metrics/asymmetry`
      );
      return validateResponse(response.data, asymmetrySchema);
    },
    enabled: !!runId,
  });

  return {
    asymmetryData: query.data ?? null,
    asymmetryLoading: query.isLoading,
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
        `/run/athletes/${runId}/metrics/gct-range`,
        { params: { min_ms: minMs, max_ms: maxMs } }
      );
      return validateResponse(response.data, gctRangeSchema);
    },
    enabled: !!runId,
  });

  return {
    gctRangeData: query.data ?? null,
    gctRangeLoading: query.isLoading,
    gctRangeError: query.error,
    gctRangeRefetch: query.refetch,
  };
}
