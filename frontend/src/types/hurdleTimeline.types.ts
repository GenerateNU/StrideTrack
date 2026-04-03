export interface HurdleTimelinePoint {
  time_s: number;
  foot: "left" | "right";
  phase: "ground" | "air";
  gct_ms: number | null;
  ft_ms: number | null;
}

export interface HurdleMarker {
  time_s: number;
  hurdle_num: number;
}

export interface HurdleTimelineResponse {
  points: HurdleTimelinePoint[];
  hurdle_markers: HurdleMarker[];
}
