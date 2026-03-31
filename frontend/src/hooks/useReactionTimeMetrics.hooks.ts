import { useEffect, useState } from "react";

interface ReactionTimeMetrics {
  reaction_time_ms: number;
  onset_timestamp_ms: number;
  stimulus_timestamp_ms: number;
  zone: "green" | "yellow" | "red";
  zone_description: string;
}

interface UseReactionTimeMetricsResult {
  rtMetrics: ReactionTimeMetrics | null;
  loading: boolean;
  error: string | null;
}

// Hardcoded mock payload — replace with real sensor data once pipeline is wired up.
const MOCK_REQUEST = {
  stimulus_timestamp_ms: 1000,
  sensor_data: [
    { timestamp_ms: 900, timestamp_iso: "", sensor_id: "left", value: 5 },
    { timestamp_ms: 1100, timestamp_iso: "", sensor_id: "left", value: 5 },
    { timestamp_ms: 1200, timestamp_iso: "", sensor_id: "left", value: 10 },
    { timestamp_ms: 1210, timestamp_iso: "", sensor_id: "left", value: 25 },
    { timestamp_ms: 1300, timestamp_iso: "", sensor_id: "left", value: 80 },
  ],
  force_threshold_n: 20,
};

export const useReactionTimeMetrics = (
  runId: string
): UseReactionTimeMetricsResult => {
  const [rtMetrics, setRtMetrics] = useState<ReactionTimeMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const res = await fetch("/api/reaction-time/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(MOCK_REQUEST),
        });
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        const data: ReactionTimeMetrics = await res.json();
        setRtMetrics(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [runId]);

  return { rtMetrics, loading, error };
};
