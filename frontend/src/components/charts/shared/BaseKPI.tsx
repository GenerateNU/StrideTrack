import { GraphInfoCard } from "@/components/charts/shared/GraphInfoCard";

interface BaseKPIProps {
  description: string;
  children: React.ReactNode;
}

export const BaseKPI = ({ description, children }: BaseKPIProps) => {
  return (
    <div className="relative flex flex-col items-center justify-center rounded-xl bg-card border border-border p-3 gap-1 shadow-sm shadow-foreground/[0.02] sm:rounded-2xl sm:p-5">
      <GraphInfoCard description={description} />
      {children}
    </div>
  );
};
