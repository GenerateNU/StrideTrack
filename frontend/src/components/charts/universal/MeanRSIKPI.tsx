export const MeanRSIKPI = ({ mean }: { mean: number }) => (
  <div className="flex flex-col items-end">
    <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide sm:text-xs">
      Mean RSI
    </span>
    <span className="text-base font-bold text-foreground sm:text-2xl">
      {mean.toFixed(2)}
    </span>
  </div>
);
