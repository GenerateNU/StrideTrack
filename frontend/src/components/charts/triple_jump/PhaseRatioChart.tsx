import { QueryError } from "@/components/QueryError";
import { QueryLoading } from "@/components/QueryLoading";
import { useTjPhaseRatio } from "@/hooks/useTripleJumpMetrics.hooks";
import {
  Bar,
  BarChart,
  LabelList,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const PHASE_COLORS = { hop: "#3b82f6", step: "#8b5cf6", jump: "#10b981" };
const IDEAL_RATIOS = { hop: 35, step: 30, jump: 35 };

export const PhaseRatioChart = ({ runId }: { runId: string }) => {
  const {
    phaseRatioData,
    phaseRatioLoading,
    phaseRatioError,
    refetchPhaseRatioData,
  } = useTjPhaseRatio(runId);

  if (phaseRatioLoading) return <QueryLoading />;
  if (phaseRatioError)
    return (
      <QueryError
        error={phaseRatioError as Error}
        refetch={() => void refetchPhaseRatioData()}
      />
    );
  if (!phaseRatioData) return null;

  const chartData = [
    {
      name: "Actual",
      hop: phaseRatioData.find((d) => d.phase === "hop")?.ratio_pct ?? 0,
      step: phaseRatioData.find((d) => d.phase === "step")?.ratio_pct ?? 0,
      jump: phaseRatioData.find((d) => d.phase === "jump")?.ratio_pct ?? 0,
    },
    {
      name: "Ideal",
      hop: IDEAL_RATIOS.hop,
      step: IDEAL_RATIOS.step,
      jump: IDEAL_RATIOS.jump,
    },
  ];

  const hop = phaseRatioData.find((d) => d.phase === "hop");
  const step = phaseRatioData.find((d) => d.phase === "step");
  const jump = phaseRatioData.find((d) => d.phase === "jump");

  return (
    <div className="w-full space-y-4">
      <ResponsiveContainer width="100%" height={160}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 4, right: 40, left: 8, bottom: 4 }}
        >
          <XAxis
            type="number"
            domain={[0, 100]}
            unit="%"
            tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
            width={48}
          />
          <Tooltip
            contentStyle={{
              background: "var(--card)",
              border: "1px solid var(--border)",
              borderRadius: 6,
              fontSize: 12,
            }}
            formatter={(value: number | undefined, name: string) => [
              value != null ? `${value.toFixed(1)}%` : "N/A",
              name.charAt(0).toUpperCase() + name.slice(1),
            ]}
          />
          <Legend
            formatter={(v) => v.charAt(0).toUpperCase() + v.slice(1)}
            wrapperStyle={{ fontSize: 12 }}
          />
          <Bar dataKey="hop" stackId="a" fill={PHASE_COLORS.hop} name="hop">
            <LabelList
              dataKey="hop"
              position="center"
              formatter={(v: unknown) => `${Number(v).toFixed(0)}%`}
              style={{ fontSize: 11, fill: "#fff", fontWeight: 600 }}
            />
          </Bar>
          <Bar dataKey="step" stackId="a" fill={PHASE_COLORS.step} name="step">
            <LabelList
              dataKey="step"
              position="center"
              formatter={(v: unknown) => `${Number(v).toFixed(0)}%`}
              style={{ fontSize: 11, fill: "#fff", fontWeight: 600 }}
            />
          </Bar>
          <Bar dataKey="jump" stackId="a" fill={PHASE_COLORS.jump} name="jump">
            <LabelList
              dataKey="jump"
              position="center"
              formatter={(v: unknown) => `${Number(v).toFixed(0)}%`}
              style={{ fontSize: 11, fill: "#fff", fontWeight: 600 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="grid grid-cols-3 gap-3">
        {[
          { phase: "Hop", data: hop, color: PHASE_COLORS.hop },
          { phase: "Step", data: step, color: PHASE_COLORS.step },
          { phase: "Jump", data: jump, color: PHASE_COLORS.jump },
        ].map(({ phase, data, color }) => (
          <div
            key={phase}
            className="rounded-lg border border-border bg-card p-3 text-center"
          >
            <div
              className="text-xs font-semibold uppercase tracking-wide mb-1"
              style={{ color }}
            >
              {phase}
            </div>
            <div className="text-xl font-bold text-foreground">
              {data?.ft_ms ?? "—"}
              <span className="text-xs font-normal text-muted-foreground ml-1">ms</span>
            </div>
            <div className="text-xs text-muted-foreground">
              {data?.ratio_pct != null ? `${data.ratio_pct.toFixed(1)}% of total` : "—"}
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-muted-foreground text-center">
        Ideal ratio: 35% Hop · 30% Step · 35% Jump
      </p>
    </div>
  );
};
