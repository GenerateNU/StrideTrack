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
      if (!runId) ret