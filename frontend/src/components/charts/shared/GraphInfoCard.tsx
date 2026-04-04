import { Info } from "lucide-react";
import { useEffect, useRef, useState } from "react";

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
    <div ref={ref} className="absolute top-2.5 right-2.5 sm:top-3 sm:right-3">
      <button
        className="text-muted-foreground hover:text-foreground transition-colors p-1"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onClick={() => setOpen((o) => !o)}
        aria-label="Chart information"
      >
        <Info className="size-3.5 sm:size-4" />
      </button>
      {open && (
        <div className="absolute right-0 top-6 z-50 w-52 rounded-lg border border-border bg-card p-2.5 shadow-lg sm:w-64 sm:p-3">
          <p className="text-[11px] text-muted-foreground leading-relaxed sm:text-xs">
            {description}
          </p>
        </div>
      )}
    </div>
  );
};
