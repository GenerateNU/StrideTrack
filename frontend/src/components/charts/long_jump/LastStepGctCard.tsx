import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useLongJumpMetrics } from "@/hooks/useLongJumpMetrics.hooks";

const HARDCODED_LJ_RUN_ID = "aaaaaaaa-0001-4000-8000-000000000001";

export const LastStepGctCard = () => {
  const { ljMetrics } = useLongJumpMetrics(HARDCODED_LJ_RUN_ID);
  const value = ljMetrics?.penultimate_gct_ms;

  return (
    <Card className="flex-1 min-w-[160px]">
      <CardHeader className="pb-2">
        <CardDescription className="text-xs uppercase tracking-wide">
          Last Step GCT
        </CardDescription>
        <CardTitle className="text-3xl font-bold tabular-nums">
          {value != null ? value.toFixed(1) : "—"}
          <span className="text-sm font-normal text-muted-foreground ml-1">
            ms
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground leading-snug">
          Ground contact time of the penultimate (second-to-last) step. Critical
          for converting horizontal speed into vertical lift. Should be short
          and reactive.
        </p>
      </CardContent>
    </Card>
  );
};
