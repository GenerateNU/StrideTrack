import { GraphInfoCard } from "@/components/charts/shared/GraphInfoCard";

interface BaseKPIProps {
  description: string;
  children: React.ReactNode;
}

export const BaseKPI = ({ description, children }: BaseKPIProps) => {
  return (
    <div className="relative flex flex-col items-center justify-center rounded-lg bg-card border border-border p-5 gap-1 shadow-sm">
      <GraphInfoCard description={description} />
      {children}
    </div>
  );
};
