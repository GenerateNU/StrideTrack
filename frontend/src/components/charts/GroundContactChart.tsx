import { LROverlayLineChart } from "./LROverlayLineChart";

export const GroundContactTimeChart = ({ runId }: { runId: string }) => {
  return <LROverlayLineChart runId={runId} metric="gct_ms" />;
};