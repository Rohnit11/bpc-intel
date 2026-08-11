"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { SensitivityRow } from "@/types/premium-skin";

/**
 * How much each input actually moves contribution margin, ranked.
 *
 * The model sweeps inputs it could not source rather than plugging them, so
 * this chart is the honest reading of what is unknown versus what is merely
 * undecided. Order size is coloured apart because it is the one bar that is a
 * decision the owner controls, not a research gap.
 */

interface Row {
  input: string;
  label: string;
  swing_pp: number;
  low: string;
  high: string;
  cm_low: number;
  cm_high: number;
  resolved: boolean;
}

function fmtBound(v: number | string): string {
  return typeof v === "number" ? v.toLocaleString() : v;
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: Row }> }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="max-w-xs rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-3 py-2 text-xs shadow-lg">
      <div className="font-semibold">{row.label}</div>
      <div className="text-[var(--text-secondary)]">
        Swept {row.low} to {row.high}
      </div>
      <div className="text-[var(--text-secondary)]">
        Contribution margin {row.cm_low}% to {row.cm_high}% — a {row.swing_pp}pp swing
      </div>
      <div className="mt-1 font-medium" style={{ color: row.resolved ? "var(--series-6)" : "var(--series-1)" }}>
        {row.resolved ? "A decision, not an unknown" : "Unresolved input — swept, not guessed"}
      </div>
    </div>
  );
}

export function SensitivityChart({ rows }: { rows: SensitivityRow[] }) {
  const data: Row[] = rows
    .map((r) => ({
      input: r.input,
      label: r.input.replace(/_/g, " ").replace(/ \(a decision, not an unknown\)$/, ""),
      swing_pp: r.swing_pp,
      low: fmtBound(r.low),
      high: fmtBound(r.high),
      cm_low: r.contribution_margin_at_low_pct,
      cm_high: r.contribution_margin_at_high_pct,
      resolved: r.resolved,
    }))
    .sort((a, b) => b.swing_pp - a.swing_pp);

  if (!data.length) {
    return <p className="text-sm text-[var(--text-muted)]">No sensitivity run on file.</p>;
  }

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--text-secondary)]">
        <span className="inline-flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: "var(--series-6)" }}
          />
          A decision the owner controls
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: "var(--series-1)" }}
          />
          Unresolved input, swept
        </span>
      </div>
      <ResponsiveContainer width="100%" height={Math.max(200, data.length * 34 + 40)}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 52, bottom: 8 }}>
          <CartesianGrid strokeDasharray="" stroke="var(--gridline)" horizontal={false} />
          <XAxis
            type="number"
            stroke="var(--text-muted)"
            tick={{ fill: "var(--text-muted)", fontSize: 12 }}
            label={{
              value: "Contribution-margin swing (pp)",
              position: "insideBottom",
              offset: -4,
              fill: "var(--text-muted)",
              fontSize: 12,
            }}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={190}
            stroke="var(--text-muted)"
            tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
          />
          <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--gridline)", opacity: 0.4 }} />
          <Bar dataKey="swing_pp" radius={[0, 4, 4, 0]} maxBarSize={18}>
            {data.map((d) => (
              <Cell key={d.input} fill={d.resolved ? "var(--series-6)" : "var(--series-1)"} />
            ))}
            <LabelList
              dataKey="swing_pp"
              position="right"
              formatter={(v: unknown) => `${v}pp`}
              style={{ fill: "var(--text-muted)", fontSize: 11 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
