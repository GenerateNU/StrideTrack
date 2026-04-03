import api from "@/lib/api";
import type {
  PhaseRatioData,
  StepSeriesPoint,
  TjContactEfficiencyData,
  TripleJumpMetricRow,
} from "@/types/jumpMetrics.types";
import {
  phaseRatioDataSchema,
  stepSeriesPointSchema,
  tjContactEfficiencySchema,
  tripleJumpMetricRowSchema,
} from "@/types/jumpMetrics.types";
import { validateResponse } from "@/utils/validation";
import { useQuery } from "@tanstack/react-query";
import { z } from "zod";

export function useTripleJumpMetrics(runId: string | null) {
  const query = useQuery({
    queryKey: ["triple-jump-metrics", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<TripleJumpMetricRow>(
        `/api/run/athletes/${runId}/metrics/triple-jump`
      );
      return validateResponse(response.data, tripleJumpMetricRowSchema);
    },
    enabled: !!runId,
  });

  return {
    tjMetrics: query.data ?? null,
    tjMetricsLoading: query.isLoading,
    tjMetricsError: query.error,
    refetchTjMetrics: query.refetch,
  };
}

export function useTjPhaseRatio(runId: string | null) {
  const query = useQuery({
    queryKey: ["triple-jump-phase-ratio", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<PhaseRatioData[]>(
        `/api/run/athletes/${runId}/metrics/triple-jump/phase-ratio`
      );
      return validateResponse(response.data, z.array(phaseRatioDataSchema));
    },
    enabled: !!runId,
  });

  return {
    phaseRatioData: query.data ?? null,
    phaseRatioLoading: query.isLoading,
    phaseRatioError: query.error,
    refetchPhaseRatioData: query.refetch,
  };
}

export function useTjContactEfficiency(runId: string | null) {
  const query = useQuery({
    queryKey: ["triple-jump-contact-efficiency", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<TjContactEfficiencyData>(
        `/api/run/athletes/${runId}/metrics/triple-jump/contact-efficiency`
      );
      return validateResponse(response.data, tjContactEfficiencySchema);
    },
    enabled: !!runId,
  });

  return {
    efficiencyData: query.data ?? null,
    efficiencyLoading: query.isLoading,
    efficiencyError: query.error,
    refetchEfficiencyData: query.refetch,
  };
}

export function useTjStepSeries(runId: string | null) {
  const query = useQuery({
    queryKey: ["triple-jump-step-series", runId],
    queryFn: async () => {
      if (!runId) return null;
      const response = await api.get<StepSeriesPoint[]>(
        `/api/run/athletes/${runId}/metrics/triple-jump/universal/steps`
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
