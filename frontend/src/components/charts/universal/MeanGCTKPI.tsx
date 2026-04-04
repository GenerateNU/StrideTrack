export const MeanGCTKPI = ({ mean }: { mean: number }) => (
  <div className="flex flex-col items-end">
    <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wide sm:text-xs">
      Mean GCT
    </span>
    <span className="text-base font-bold text-foreground sm:text-2xl">
      {mean.toFixed(1)}
      <span className="text-[10px] font-medium text-muted-foreground ml-0.5 sm:text-sm sm:ml-1">
        ms
      </span>
    </span>
  </div>
);
