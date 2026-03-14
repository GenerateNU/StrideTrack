interface GCTDriftCardProps {
  value: number;
  thresholds?: { good: number; warn: number };
}

function getDriftColor(value: number, good: number, warn: number): string {
  const abs = Math.abs(value);
  if (abs < good) return "text-green-500";
  if (abs < warn) return "text-yellow-500";
  return "text-red-500";
}

export function GCTDriftCard({
  value,
  thresholds = { good: 5, warn: 10 },
}: GCTDriftCardProps) {
  const colorClass = getDriftColor(value, thresholds.good, thresholds.warn);
  const sign = value > 0 ? "+" : "";

  return (
    <div className="flex flex-col items-center justify-center rounded-lg bg-card border border-border p-5 gap-1 shadow-sm">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        GCT Drift
      </span>
      <span className={`text-4xl font-bold ${colorClass}`}>
        {sign}
        {value.toFixed(1)}%
      </span>
      <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
        <span className="text-green-500">● &lt;{thresholds.good}%</span>
        <span className="text-yellow-500">
          ● {thresholds.good}–{thresholds.warn}%
        </span>
        <span className="text-red-500">● &gt;{thresholds.warn}%</span>
      </div>
    </div>
  );
}
