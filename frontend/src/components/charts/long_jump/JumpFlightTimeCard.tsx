import {
    Card,
    CardHeader,
    CardDescription,
    CardTitle,
  } from "@/components/ui/card";
  import { GraphInfoCard } from "@/components/charts/GraphInfoCard";
  import { useLongJumpMetrics } from "@/hooks/useLongJumpMetrics.hooks";
  
  const HARDCODED_LJ_RUN_ID = "aaaaaaaa-0001-4000-8000-000000000001";
  
  export const JumpFlightTimeCard = () => {
    const { ljMetrics } = useLongJumpMetrics(HARDCODED_LJ_RUN_ID);
    const value = ljMetrics?.jump_ft_ms;
  
    return (
      <Card className="relative flex-1 min-w-[160px]">
        <GraphInfoCard description="Flight time of the final takeoff step — the actual jump. Longer flight time reflects a more powerful and effective takeoff, assuming good technique." />
        <CardHeader className="pb-2 text-center">
          <CardDescription className="text-xs uppercase tracking-wide">
            Jump Flight Time
          </CardDescription>
          <CardTitle className="text-3xl font-bold tabular-nums">
            {value != null ? value.toFixed(1) : "—"}
            <span className="text-sm font-normal text-muted-foreground ml-1">
              ms
            </span>
          </CardTitle>
        </CardHeader>
      </Card>
    );
  };
  