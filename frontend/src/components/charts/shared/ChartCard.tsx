import { GraphInfoCard } from "@/components/charts/shared/GraphInfoCard";

interface ChartCardProps {
  title: string;
  description: string;
  headerRight?: React.ReactNode;
  children: React.ReactNode;
}

function SectionHeader({ title }: { title: string }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className="h-4 w-1 rounded-full sm:h-5"
        style={{ backgroundColor: "hsl(var(--primary))" }}
      />
      <h3 className="text-xs font-semibold text-foreground sm:text-sm">
        {title}
      </h3>
    </div>
  );
}

export const ChartCard = ({
  title,
  description,
  headerRight,
  children,
}: ChartCardProps) => {
  return (
    <div className="relative flex-1 rounded-xl border border-border bg-card p-3 shadow-sm shadow-foreground/[0.02] sm:rounded-2xl sm:p-5">
      <GraphInfoCard description={description} />
      <div className="flex items-start justify-between mb-4 sm:mb-6">
        <SectionHeader title={title} />
        {headerRight && <div className="mr-6 sm:mr-8">{headerRight}</div>}
      </div>
      <div className="-mx-2 sm:mx-0">{children}</div>
    </div>
  );
};
