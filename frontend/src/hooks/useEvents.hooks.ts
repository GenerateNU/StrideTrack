import type { EventTypeEnum, EventOption } from "../types/event.types";

const EVENT_DISPLAY_NAMES: Record<EventTypeEnum, string> = {
  sprint_60m: "60 Meter Sprint",
  sprint_100m: "100 Meter Sprint",
  sprint_200m: "200 Meter Sprint",
  sprint_400m: "400 Meter Sprint",
  hurdles_partial: "Partial Hurdles",
  hurdles_60m: "60 Meter Hurdles",
  hurdles_110m: "110 Meter Hurdles",
  hurdles_100m: "100 Meter Hurdles",
  hurdles_400m: "400 Meter Hurdles",
  long_jump: "Long Jump",
  triple_jump: "Triple Jump",
  high_jump: "High Jump",
  bosco_test: "Bosco Test",
  reaction_time_test: "Reaction Time Test",
};

export const EVENT_OPTIONS: EventOption[] = (
  Object.entries(EVENT_DISPLAY_NAMES) as [EventTypeEnum, string][]
).map(([value, label]) => ({ value, label }));

export const useEvents = (): EventOption[] => {
  return EVENT_OPTIONS;
};
