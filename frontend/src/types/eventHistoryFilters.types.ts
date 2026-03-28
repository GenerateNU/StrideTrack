import type { EventTypeEnum } from "@/types/event.types";

export type AmountMode = "count" | "dateRange";

export interface EventHistoryFilters {
  athleteId: string;
  eventType: EventTypeEnum;
  amountMode: AmountMode;
  limit: number;
  dateFrom: string | null;
  dateTo: string | null;
}
