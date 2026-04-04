export const MeanRSIKPI = ({ mean }: { mean: number }) => (
  <div className="flex flex-col items-end">
    <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
      Mean RSI
    </span>
    <span className="text-2xl font-bold text-foreground">
      {mean.toFixed(2)}
    </span>
  </div>
);

