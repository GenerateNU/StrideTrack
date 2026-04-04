import { GraphInfoCard } from "@/components/charts/shared/GraphInfoCard";

interface ChartCardProps {
  title: string;
  description: string;
  headerRight?: React.ReactNode;
  children: React.ReactNode;
}

function SectionHeader({ title }: { title: string }) {
  return (
    <div className="flex items-center gap-2.5">
      <div
        className="h-5 w-1 rounded-full"
        style={{ backgroundColor: "hsl(var(--primary))" }}
      />
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
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
    <div className="relative flex-1 rounded-2xl border border-border bg-card p-5 shadow-sm shadow-foreground/[0.02]">
      <GraphInfoCard description={description} />
      <div className="flex items-start justify-between mb-6">
        <SectionHeader title={title} />
        {headerRight && <div className="mr-8">{headerRight}</div>}
      </div>
      <div>{children}</div>
    </div>
  );
};
