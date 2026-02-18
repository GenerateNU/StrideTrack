import { useRunMetrics } from "@/hooks/useRunMetrics";
import {
  GroundContactTimeChart,
  FlightTimeChart,
  StepTimeChart,
} from "@/components/charts/TemporalCharts";
import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";

const HARDCODED_ATHLETE_ID = "00000000-0000-0000-0000-000000000002";

export default function VisualizationsPage() {
  const { metrics, metricsIsLoading, metricsError, metricsRefetch } =
    useRunMetrics(HARDCODED_ATHLETE_ID);

  if (metricsIsLoading) return <QueryLoading />;
  if (metricsError)
    return <QueryError error={metricsError} refetch={metricsRefetch} />;

  return (
    <div className="min-h-screen bg-white p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8" style={{ color: "#000000" }}>
          Performance Metrics
        </h1>

        <div className="space-y-8">
          <div>
            <h2 className="text-xl font-bold mb-3" style={{ color: "#FF6B35" }}>
              Ground Contact Time (GCT) - Left vs Right Foot
            </h2>
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <GroundContactTimeChart data={metrics} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3" style={{ color: "#FF6B35" }}>
              Flight Time (FT) - Left vs Right Foot
            </h2>
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <FlightTimeChart data={metrics} />
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold mb-3" style={{ color: "#FF6B35" }}>
              Step Time - Ground Contact + Flight (Stacked)
            </h2>
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <StepTimeChart data={metrics} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
