import { useEffect, useState } from "react";
import api from "@/lib/api";

interface ReactionTimeMetrics {
  run_id: string;
  reaction_time_ms: number;
  onset_timestamp_ms: number;
  zone: "green" | "yellow" | "red";
  zone_description: string;
}

interface UseReactionTimeMetricsResult {
  rtMetrics: ReactionTimeMetrics | null;
  loading: boolean;
  error: string | null;
}

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
        const res = await api.get<ReactionTimeMetrics>(
          `/reaction-time/${runId}`
        );
        setRtMetrics(res.data);
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
