import { useGetRunMeta } from "@/hooks/useRuns.hooks";
import type { ChartSection } from "@/lib/runAnalysisVisualizations";
import { getSectionsForEventType } from "@/lib/runAnalysisVisualizations";
import { ArrowLeft, ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

function AccordionSection({
  section,
  runId,
}: {
  section: ChartSection;
  runId: string;
}) {
  const [expanded, setExpanded] = useState(section.defaultExpanded ?? false);
  const [contentHeight, setContentHeight] = useState<number>(0);
  const innerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!innerRef.current) return;
    const el = innerRef.current;
    const update = () => setContentHeight(el.offsetHeight);
    update();
    const observer = new ResizeObserver(update);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between px-4 py-4 text-base font-medium text-foreground hover:bg-muted/50 transition-colors"
      >
        {section.label}
        <ChevronDown
          className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${
            expanded ? "rotate-180" : ""
          }`}
        />
      </button>
      <div
        className="transition-all duration-300 ease-in-out overflow-hidden"
        style={{
          maxHeight: expanded ? `${contentHeight}px` : "0px",
          opacity: expanded ? 1 : 0,
        }}
      >
        <div ref={innerRef} className="flex flex-col gap-6 px-4 pb-4">
          {section.charts.map((ChartComponent, i) => (
            <ChartComponent key={i} runId={runId} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function RunAnalysisPage() {
  const { athleteId, runId } = useParams<{
    athleteId: string;
    runId: string;
  }>();
  const navigate = useNavigate();

  const { runMeta } = useGetRunMeta(runId);
  const sections = runMeta?.event_type
    ? getSectionsForEventType(runMeta.event_type)
    : [];

  return (
    <div className="flex h-full flex-col pt-4">
      <div className="mb-6 flex items-center gap-3">
        <button
          onClick={() => navigate(`/athletes/${athleteId}`)}
          className="flex items-center text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        {runMeta && (
          <p className="text-sm text-muted-foreground">
            <span className="font-semibold text-foreground">
              {runMeta.event_type
                .replace(/_/g, " ")
                .replace(/\b\w/g, (c) => c.toUpperCase())}
            </span>
            {" · "}
            {new Date(runMeta.created_at).toLocaleDateString()}
            {` · ${(runMeta.elapsed_ms / 1000).toFixed(2)}s`}
          </p>
        )}
      </div>

      {runId ? (
        <div className="flex flex-1 flex-col gap-4">
          {sections.map((section) => (
            <AccordionSection
              key={section.label}
              section={section}
              runId={runId}
            />
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-border p-12 text-center">
          <p className="text-sm font-medium text-muted-foreground">
            Event not found.
          </p>
        </div>
      )}
    </div>
  );
}
