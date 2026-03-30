export const MeanFTKPI = ({ mean }: { mean: number }) => (
    <div className="flex flex-col items-end">
      <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
        Mean FT
      </span>
      <span className="text-2xl font-bold text-foreground">
        {mean.toFixed(1)}
        <span className="text-sm font-medium text-muted-foreground ml-1">ms</span>
      </span>
    </div>
  );
  