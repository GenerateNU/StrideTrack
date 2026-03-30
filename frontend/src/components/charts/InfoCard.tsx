export const InfoCard = ({ text }: { text: string }) => (
  <div className="rounded-xl border border-border bg-muted/40 px-4 py-3">
    <p className="text-xs text-muted-foreground leading-relaxed">{text}</p>
  </div>
);
