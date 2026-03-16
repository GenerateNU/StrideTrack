import { useState } from "react";

interface GraphInfoCardProps {
  description: string;
}

export const GraphInfoCard = ({ description }: GraphInfoCardProps) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="absolute top-4 right-4">
      <button
        className="text-muted-foreground hover:text-foreground transition-colors"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onClick={() => setOpen((o) => !o)}
        aria-label="Chart information"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 top-6 z-50 w-64 rounded-lg border border-border bg-card p-3 shadow-lg">
          <p className="text-xs text-muted-foreground leading-relaxed">
            {description}
          </p>
        </div>
      )}
    </div>
  );
};
