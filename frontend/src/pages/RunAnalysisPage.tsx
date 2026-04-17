import api from "@/lib/api";
import { useGetRunMeta } from "@/hooks/useRuns.hooks";
import type { ChartSection } from "@/lib/runAnalysisVisualizations";
import { getSectionsForEventType } from "@/lib/runAnalysisVisualizations";
import { ArrowLeft, ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";

const TARGET_EVENT_OPTIONS = [
  { label: "60m Hurdles", value: "hurdles_60m" },
  { label: "100m Hurdles", value: "hurdles_100m" },
  { label: "110m Hurdles", value: "hurdles_110m" },
  { label: "400m Hurdles", value: "hurdles_400m" },
];

function AccordionSection({
  section,
  runId,
  hurdlesCompleted,
  targetEvent,
}: {
  section: ChartSection;
  runId: string;
  hurdlesCompleted?: number | null;
  targetEvent?: string | null;
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
            <ChartComponent
              key={i}
              runId={runId}
              hurdlesCompleted={hurdlesCompleted}
              targetEvent={targetEvent}
            />
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
  const isHurdlesPartial = runMeta?.event_type === "hurdles_partial";

  const [hurdleParams, setHurdleParams] = useState<{
    targetEvent: string | null;
    hurdlesCompleted: number | null;
    hasSubmitted: boolean;
  }>({ targetEvent: null, hurdlesCompleted: null, hasSubmitted: false });

  useEffect(() => {
    if (runMeta) {
      queueMicrotask(() => {
        const te = runMeta.target_event ?? null;
        const hc = runMeta.hurdles_completed ?? null;
        setHurdleParams({
          targetEvent: te,
          hurdlesCompleted: hc,
          hasSubmitted: !!(te && hc),
        });
      });
    }
  }, [runMeta]);

  const canSubmit =
    hurdleParams.targetEvent !== null && hurdleParams.hurdlesCompleted !== null;

  const queryClient = useQueryClient();

  const handleSubmit = async () => {
    if (hurdleParams.targetEvent && hurdleParams.hurdlesCompleted) {
      try {
        await api.patch(`/runs/${runId}`, {
          hurdles_completed: hurdleParams.hurdlesCompleted,
          target_event: hurdleParams.targetEvent,
        });
        await queryClient.invalidateQueries({ queryKey: ["runMeta", runId] });
        setHurdleParams((prev) => ({ ...prev, hasSubmitted: true }));
      } catch (error) {
        console.error("Failed to save hurdle params:", error);
      }
    }
  };

  const sections = runMeta?.event_type
    ? getSectionsForEventType(runMeta.event_type)
    : [];

  const showCharts = !isHurdlesPartial || hurdleParams.hasSubmitted;

  return (
    <div className="flex h-full flex-col pt-4">
      <div className="mb-6 flex items-center gap-3">
        <button
          onClick={() => navigate(`/athletes/${athleteId}`)}
          className="flex items-center text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex items-end justify-between">
          <div className="flex items-end gap-8">
            <div>
              <h2 className="text-xl font-bold text-foreground">
                Event Analysis
              </h2>
              {runMeta && (
                <p className="text-sm text-muted-foreground mt-1">
                  {runMeta.event_type
                    .replace(/_/g, " ")
                    .replace(/\b\w/g, (c) => c.toUpperCase())}{" "}
                  · {new Date(runMeta.created_at).toLocaleDateString()}
                  {` · ${(runMeta.elapsed_ms / 1000).toFixed(2)}s`}
                </p>
              )}
            </div>
            {isHurdlesPartial && (
              <>
                <div className="h-10 w-px bg-border" />
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-medium text-foreground">
                    Target Event
                  </label>
                  <select
                    value={hurdleParams.targetEvent ?? ""}
                    onChange={(e) =>
                      setHurdleParams((prev) => ({
                        ...prev,
                        targetEvent: e.target.value || null,
                        hasSubmitted: false,
                      }))
                    }
                    className="rounded-md border border-border bg-background px-2 py-1.5 text-xs"
                  >
                    <option value="">Select event...</option>
                    {TARGET_EVENT_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-medium text-foreground">
                    Hurdles Completed
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={hurdleParams.hurdlesCompleted ?? ""}
                    onChange={(e) =>
                      setHurdleParams((prev) => ({
                        ...prev,
                        hurdlesCompleted: e.target.value
                          ? Number(e.target.value)
                          : null,
                        hasSubmitted: false,
                      }))
                    }
                    className="rounded-md border border-border bg-background px-2 py-1.5 text-xs w-fit"
                  />
                </div>
                <button
                  onClick={handleSubmit}
                  disabled={!canSubmit}
                  className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
                >
                  Apply
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {runId && showCharts ? (
        <div className="flex flex-1 flex-col gap-4">
          {sections.map((section) => (
            <AccordionSection
              key={section.label}
              section={section}
              runId={runId}
              hurdlesCompleted={hurdleParams.hurdlesCompleted}
              targetEvent={hurdleParams.targetEvent}
            />
          ))}
        </div>
      ) : runId && !showCharts ? (
        <div className="rounded-2xl border border-dashed border-border p-12 text-center">
          <p className="text-sm font-medium text-muted-foreground">
            Select a target event and hurdles completed, then click Apply to
            view charts.
          </p>
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
