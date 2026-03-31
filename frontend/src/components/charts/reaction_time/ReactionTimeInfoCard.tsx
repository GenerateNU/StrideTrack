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
          How fast an athlete reacts to the start signal, measured from the
          stimulus to their first foot movement. Elite sprinters: under 150ms.
          Under 100ms is a false start.
        </p>
      </CardContent>
    </Card>
  );
};
