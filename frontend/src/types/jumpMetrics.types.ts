import { z } from "zod";

export const longJumpMetricRowSchema = z.object({
  takeoff_foot: z.enum(["left", "right"]).nullable(),
  takeoff_gct_ms: z.number().nullable(),
  penultimate_foot: z.enum(["left", "right"]).nullable(),
  penultimate_gct_ms: z.number().nullable(),
  jump_ft_ms: z.number().nullable(),
  clearance_start_ms: z.number().nullable(),
  clearance_end_ms: z.number().nullable(),
  approach_mean_gct_ms: z.number().nullable(),
  approach_mean_ft_ms: z.number().nullable(),
  approach_cv_pct: z.number().nullable(),
  approach_rsi: z.number().nullable(),
});

export const ljTakeoffDataSchema = z.object({
  takeoff_foot: z.enum(["left", "right"]).nullable(),
  takeoff_gct_ms: z.number().nullable(),
  penultimate_foot: z.enum(["left", "right"]).nullable(),
  penultimate_gct_ms: z.number().nullable(),
  jump_ft_ms: z.number().nullable(),
});

export const approachProfilePointSchema = z.object({
  stride_num: z.number(),
  foot: z.enum(["left", "right"]),
  ic_time: z.number(),
  gct_ms: z.number(),
  phase: z.string(),
});

export const stepSeriesPointSchema = z.object({
  stride_num: z.number(),
  foot: z.enum(["left", "right"]),
  ic_time: z.number(),
  gct_ms: z.number(),
  flight_ms: z.number().nullable(),
  step_time_ms: z.number().nullable(),
  rsi: z.number().nullable(),
  duty_factor: z.number().nullable(),
  contact_flight_index: z.number().nullable(),
  step_frequency_hz: z.number().nullable(),
});

export const tripleJumpMetricRowSchema = z.object({
  hop_gct_ms: z.number().nullable(),
  step_gct_ms: z.number().nullable(),
  jump_gct_ms: z.number().nullable(),
  hop_ft_ms: z.number().nullable(),
  step_ft_ms: z.number().nullable(),
  jump_ft_ms: z.number().nullable(),
  hop_takeoff_foot: z.enum(["left", "right"]).nullable(),
  phase_ratio_hop: z.number().nullable(),
  phase_ratio_step: z.number().nullable(),
  phase_ratio_jump: z.number().nullable(),
  contact_time_efficiency: z.number().nullable(),
  hop_clearance_start_ms: z.number().nullable(),
  hop_clearance_end_ms: z.number().nullable(),
  step_clearance_start_ms: z.number().nullable(),
  step_clearance_end_ms: z.number().nullable(),
  jump_clearance_start_ms: z.number().nullable(),
  jump_clearance_end_ms: z.number().nullable(),
});

export const phaseRatioDataSchema = z.object({
  phase: z.enum(["hop", "step", "jump"]),
  ft_ms: z.number().nullable(),
  gct_ms: z.number().nullable(),
  ratio_pct: z.number().nullable(),
});

export const tjContactEfficiencySchema = z.object({
  hop_gct_ms: z.number().nullable(),
  step_gct_ms: z.number().nullable(),
  jump_gct_ms: z.number().nullable(),
  hop_ft_ms: z.number().nullable(),
  step_ft_ms: z.number().nullable(),
  jump_ft_ms: z.number().nullable(),
  contact_time_efficiency: z.number().nullable(),
});

export type LongJumpMetricRow = z.infer<typeof longJumpMetricRowSchema>;
export type LjTakeoffData = z.infer<typeof ljTakeoffDataSchema>;
export type ApproachProfilePoint = z.infer<typeof approachProfilePointSchema>;
export type StepSeriesPoint = z.infer<typeof stepSeriesPointSchema>;
export type TripleJumpMetricRow = z.infer<typeof tripleJumpMetricRowSchema>;
export type PhaseRatioData = z.infer<typeof phaseRatioDataSchema>;
export type TjContactEfficiencyData = z.infer<typeof tjContactEfficiencySchema>;
