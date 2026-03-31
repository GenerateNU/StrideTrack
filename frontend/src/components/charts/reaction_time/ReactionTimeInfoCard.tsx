import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const ReactionTimeInfoCard = () => {
  return (
    <Card className="flex-1 min-w-[160px]">
      <CardHeader className="pb-2">
        <CardDescription className="text-xs uppercase tracking-wide">
          About This Metric
        </CardDescription>
        <CardTitle className="text-base font-semibold">Reaction Time</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground leading-snug">
          Pure neural response speed — time from the start stimulus to first
          detected ground contact (GCT onset). Elite sprinters react in under
          150ms. A reaction time below 100ms is flagged as a false start by
          World Athletics rules.
        </p>
      </CardContent>
    </Card>
  );
};
