import { useParams, useNavigate, useLocation } from "react-router-dom";
import { getChartsForEventType } from "@/config/runVisualizations";
import { ArrowLeft } from "lucide-react";

function SectionHeader({ title }: { title: string }) {
  return (
    <div className="mb-3 flex items-center gap-2.5">
      <div
        className="h-5 w-1 rounded-full"
        style={{ backgroundColor: "hsl(var(--primary))" }}
      />
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
    </div>
  );
}

export default function RunAnalysisPage() {
  const { athleteId, runId } = useParams<{
    athleteId: string;
    runId: string;
  }>();
  const navigate = useNavigate();
  const location = useLocation();

  // ADD HERE: Replace with dedicated GET /api/run/:runId and GET /api/athletes/:athleteId
  // endpoints once they exist. Currently we only have the runId from the URL.
  const eventType: string = location.state?.eventType ?? "default";
  const charts = getChartsForEventType(eventType);
  return (
    <div className="flex h-full flex-col pt-4">
      <div className="mb-6">
        <button
          onClick={() => navigate(`/athletes/${athleteId}`)}
          className="mb-2 flex items-center gap-1 text-sm text-muted-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Athlete
        </button>
        <h2 className="text-xl font-bold text-foreground">Run Analysis</h2>
        {/* ADD HERE: Display run event_type, date, elapsed_ms once GET /api/run/:runId exists */}
      </div>

      {runId ? (
        <div className="flex flex-1 flex-col gap-6">
          {charts.map(({ title, component: ChartComponent }) => (
            <div
              key={title}
              className="flex-1 rounded-2xl border border-border bg-card p-5 shadow-sm shadow-foreground/[0.02]"
            >
              <SectionHeader title={title} />
              <div className="h-[calc(100%-2rem)]">
                <ChartComponent runId={runId} />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-border p-12 text-center">
          <p className="text-sm font-medium text-muted-foreground">
            Run not found.
          </p>
        </div>
      )}
    </div>
  );
}
