import { LROverlayLineChart } from "./LROverlayLineChart";

export const FlightTimeChart = ({ runId }: { runId: string }) => {
  return (
    <LROverlayLineChart
      runId={runId}
      metric="flight_ms"
      showMeanReferenceLine
    />
  );
};
