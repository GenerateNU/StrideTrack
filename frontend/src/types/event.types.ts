import { z } from "zod";
export const eventTypeEnum = z.enum([
  "sprint_60m",
  "sprint_100m",
  "sprint_200m",
  "sprint_400m",
  "hurdles_60m",
  "hurdles_110m",
  "hurdles_100m",
  "hurdles_400m",
  "hurdles_partial",
  "long_jump",
  "triple_jump",
  "high_jump",
  "bosco_test",
  "reaction_time_test",
]);

export type EventTypeEnum = z.infer<typeof eventTypeEnum>;

export type HurdleTargetEvent =
  | "hurdles_60m"
  | "hurdles_110m"
  | "hurdles_100m"
  | "hurdles_400m";

export enum EventCategory {
  SPRINT = "sprint",
  HURDLES = "hurdles",
  BOSCO = "bosco",
}

export interface EventOption {
  value: EventTypeEnum;
  label: string;
}
