import { useState, useRef, useEffect } from "react";
import { Info } from "lucide-react";

interface GraphInfoCardProps {
  description: string;
}

export const GraphInfoCard = ({ description }: GraphInfoCardProps) => {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    function handleClickOutside(e: MouseEvent | TouchEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("touchstart", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
    };
  }, [open]);

  return (
    <div ref={ref} className="absolute top-3 right-3">
      <button
        className="text-muted-foreground hover:text-foreground transition-colors"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onClick={() => setOpen((o) => !o)}
        aria-label="Chart information"
      >
        <Info size={16} />
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
