import { useParams, useNavigate } from "react-router-dom";
import { useRunMetrics } from "@/hooks/useRunMetrics.hooks";
import { GroundContactTimeChart } from "@/components/charts/GroundContactChart";
import { FlightTimeChart } from "@/components/charts/FlightTimeChart";
import { StepDataTable } from "@/components/charts/StepDataTable";
import { ArrowLeft } from "lucide-react";
import { TotalStepsKPI } from "@/components/charts/universal/TotalStepsKPI";
import { RSIChart } from "@/components/charts/universal/RSIChart";
import { GCTAsymmetryKPI } from "@/components/charts/universal/GCTAsymmetryKPI";
import { FTAsymmetryKPI } from "@/components/charts/universal/FTAsymmetryKPI";
import { MeanGCTKPI } from "@/components/charts/universal/MeanGCTKPI";
import { MeanFTKPI } from "@/components/charts/universal/MeanFTKPI";
import { MeanRSIKPI } from "@/components/charts/universal/MeanRSIKPI";
import { GCTRangePieChart } from "@/components/charts/universal/GCTRangePieChart";
import { InfoCard } from "@/components/charts/InfoCard";

function SectionHeader({ title }: { title: string }) {
  return (
    <div className="flex items-center gap-2.5">
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
  const { metrics, metricsIsLoading } = useRunMetrics(runId ?? null);

  const meanGCT =
    metrics && metrics.length > 0
      ? metrics.reduce((s, m) => s + m.gct_ms, 0) / metrics.length
      : null;

  const meanRSI =
    metrics && metrics.length > 0
      ? metrics.reduce(
          (s, m) => s + (m.gct_ms > 0 ? m.flight_ms / m.gct_ms : 0),
          0
        ) / metrics.length
      : null;

  const meanFT =
    metrics && metrics.length > 0
      ? metrics.reduce((s, m) => s + m.flight_ms, 0) / metrics.length
      : null;

  return (
    <div className="pt-4">
      <button
        onClick={() => navigate(`/athletes/${athleteId}`)}
        className="mb-5 flex items-center gap-1 text-sm text-muted-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Athlete
      </button>

      <div className="mb-8">
        <h2 className="text-xl font-bold text-foreground">Run Analysis</h2>
      </div>

      {runId ? (
        <div className="space-y-6">
          {/* Item 1 — Total Steps */}
          <TotalStepsKPI runId={runId} />
          <InfoCard text="Basic volume metric." />

          {/* Item 2 — Mean GCT */}
          <div className="rounded-2xl border border-border bg-card p-5 shadow-sm shadow-foreground/[0.02]">
            <div className="flex items-start justify-between mb-3">
              <SectionHeader title="Ground Contact Time — L vs R" />
              {meanGCT != null && <MeanGCTKPI mean={meanGCT} />}
            </div>
            <GroundContactTimeChart runId={runId} />
          </div>
          <InfoCard text="Lower is better at max velocity." />

          {/* Item 3 — Mean FT */}
          <div className="rounded-2xl border border-border bg-card p-5 shadow-sm shadow-foreground/[0.02]">
            <div className="flex items-start justify-between mb-3">
              <SectionHeader title="Flight Time — L vs R" />
              {meanFT != null && <MeanFTKPI mean={meanFT} />}
            </div>
            <FlightTimeChart runId={runId} />
          </div>
          <InfoCard text="Context-dependent (sprinting vs jumping)." />

          {/* Item 4 — RSI per step */}
          <div className="rounded-2xl border border-border bg-card p-5 shadow-sm shadow-foreground/[0.02]">
            <div className="flex items-start justify-between mb-3">
              <SectionHeader title="Reactive Strength Index (RSI)" />
              {meanRSI != null && <MeanRSIKPI mean={meanRSI} />}
            </div>
            <RSIChart runId={runId} />
          </div>
          <InfoCard text="Elite sprinters RSI > 1.0 at max velocity." />

          {/* Items 5 & 6 — Asymmetry */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <GCTAsymmetryKPI runId={runId} />
              <InfoCard text=">10% may indicate injury risk. Target <5%." />
            </div>
            <div className="space-y-2">
              <FTAsymmetryKPI runId={runId} />
              <InfoCard text="Push-off power imbalance between legs." />
            </div>
          </div>

          {/* Item 8 — GCT Range */}
          <div className="rounded-2xl border border-border bg-card p-5 shadow-sm shadow-foreground/[0.02]">
            <div className="flex items-start justify-between mb-3">
              <SectionHeader title="Steps in GCT Range" />
            </div>
            <GCTRangePieChart runId={runId} />
          </div>
          <InfoCard text="Bucketing done client-side from existing per-step gct_ms data." />

          <StepDataTable metrics={metrics ?? []} isLoading={metricsIsLoading} />
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
