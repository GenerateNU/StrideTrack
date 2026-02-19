export type EventTypeEnum =
  | "sprint_60m"
  | "sprint_100m"
  | "sprint_200m"
  | "sprint_400m"
  | "hurdles_60m"
  | "hurdles_110m"
  | "hurdles_100m"
  | "hurdles_400m"
  | "long_jump"
  | "triple_jump"
  | "high_jump"
  | "bosco_test"
  | "reaction_time_test";

export interface EventOption {
  value: EventTypeEnum;
  label: string;
}
