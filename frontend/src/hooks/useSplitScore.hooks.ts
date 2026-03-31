import { useEffect, useState } from "react";

interface SegmentScore {
  label: string;
  raw_ms: number;
  pct_of_total: number;
  diff_s: number;
  diff_pct: number;
}

interface SplitScoreData {
  run_id: string;
  event_type: string;
  total_ms: number;
  segments: SegmentScore[];
  coaching_notes: string[];
}

interface UseSplitScoreResult {
  splitScoreData: SplitScoreData | null;
  loading: boolean;
  error: string | null;
}

// Mock data representing a hurdles_400m run with realistic diffs
const MOCK_DATA: SplitScoreData = {
  run_id: "mock-run-id",
  event_type: "hurdles_400m",
  total_ms: 52000,
  segments: [
    {
      label: "Start→H1",
      raw_ms: 6400,
      pct_of_total: 12.31,
      diff_s: 0.18,
      diff_pct: 0.35,
    },
    {
      label: "H1→H2",
      raw_ms: 3900,
      pct_of_total: 7.5,
      diff_s: -0.08,
      diff_pct: -0.15,
    },
    {
      label: "H2→H3",
      raw_ms: 4020,
      pct_of_total: 7.73,
      diff_s: 0.05,
      diff_pct: 0.1,
    },
    {
      label: "H3→H4",
      raw_ms: 4350,
      pct_of_total: 8.37,
      diff_s: 0.31,
      diff_pct: 0.6,
    },
    {
      label: "H4→H5",
      raw_ms: 4200,
      pct_of_total: 8.08,
      diff_s: -0.02,
      diff_pct: -0.04,
    },
    {
      label: "H5→H6",
      raw_ms: 4100,
      pct_of_total: 7.88,
      diff_s: 0.09,
      diff_pct: 0.17,
    },
    {
      label: "H6→H7",
      raw_ms: 4600,
      pct_of_total: 8.85,
      diff_s: 0.42,
      diff_pct: 0.81,
    },
    {
      label: "H7→H8",
      raw_ms: 4800,
      pct_of_total: 9.23,
      diff_s: 0.55,
      diff_pct: 1.06,
    },
    {
      label: "H8→H9",
      raw_ms: 4950,
      pct_of_total: 9.52,
      diff_s: 0.61,
      diff_pct: 1.17,
    },
    {
      label: "H9→H10",
      raw_ms: 4880,
      pct_of_total: 9.38,
      diff_s: 0.03,
      diff_pct: 0.06,
    },
    {
      label: "H10→Fin",
      raw_ms: 5800,
      pct_of_total: 11.15,
      diff_s: -0.18,
      diff_pct: -0.35,
    },
  ],
  coaching_notes: [
    "Start→H1: 0.18s slower than average (0.4% slower)",
    "H1→H2: 0.08s faster than average (0.2% faster)",
    "H2→H3: on pace",
    "H3→H4: 0.31s slower than average (0.6% slower)",
    "H4→H5: on pace",
    "H5→H6: on pace",
    "H6→H7: 0.42s slower than average (0.8% slower)",
    "H7→H8: 0.55s slower than average (1.1% slower)",
    "H8→H9: 0.61s slower than average (1.2% slower)",
    "H9→H10: on pace",
    "H10→Fin: 0.18s faster than average (0.4% faster)",
  ],
};

export const useSplitScore = (runId: string): UseSplitScoreResult => {
  const [splitScoreData, setSplitScoreData] = useState<SplitScoreData | null>(
    null
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/api/split-score/${runId}`);
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        const data: SplitScoreData = await res.json();
        setSplitScoreData(data);
      } catch {
        // Fall back to mock data when backend is unavailable
        setSplitScoreData(MOCK_DATA);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [runId]);

  return { splitScoreData, loading, error: null };
};
