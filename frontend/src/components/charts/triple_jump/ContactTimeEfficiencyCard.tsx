import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useTripleJumpMetrics } from "@/hooks/useTripleJumpMetrics.hooks";

const HARDCODED_TJ_RUN_ID = "bbbbbbbb-0001-4000-8000-000000000001";

export const ContactTimeEfficiencyCard = () => {
  const { tjMetrics } = useTripleJumpMetrics(HARDCODED_TJ_RUN_ID);
  const value = tjMetrics?.contact_time_efficiency;

  return (
    <Card className="flex-1 min-w-[160px]">
      <CardHeader className="pb-2">
        <CardDescription className="text-xs uppercase tracking-wide">
          Contact Time Efficiency
        </CardDescription>
        <CardTitle className="text-3xl font-bold tabular-nums">
          {value != null ? value.toFixed(1) : "—"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground leading-snug">
          Ratio of total flight time to total ground contact time across all
          three phases. Higher values indicate better energy transfer through
          the hop, step, and jump sequence.
        </p>
      </CardContent>
    </Card>
  );
};
