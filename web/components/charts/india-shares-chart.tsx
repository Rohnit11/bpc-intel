"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface Row {
  label: string;
  company: string;
  revenue: number;
  period: string;
  share_pct: number;
  non_pure_play: boolean;
  currency?: string;
  unit?: string;
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: Row }> }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-3 py-2 text-xs shadow-lg">
      <div className="font-semibold">{row.company}</div>
      <div>{row.share_pct}% of summed listed-player revenue</div>
      <div className="text-[var(--text-secondary)]">
        Revenue: {row.revenue.toLocaleString()} {row.unit} ({row.period})
      </div>
      {row.non_pure_play && (
        <div className="text-[var(--status-warning)] font-medium mt-1">
          Conglomerate — reports non-BPC revenue too
        </div>
      )}
    </div>
  );
}

/** Bar color flags a status (conglomerate/non-pure-play), not series identity —
 * every bar is one company already labelled on the axis. */
export function IndiaSharesChart({ data }: { data: Row[] }) {
  if (!data.length) {
    return <p className="text-sm text-[var(--text-muted)]">No listed-player revenue available.</p>;
  }
  return (
    <ResponsiveContainer width="100%" height={Math.max(240, data.length * 36)}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--gridline)" horizontal={false} />
        <XAxis
          type="number"
          stroke="var(--text-muted)"
          tick={{ fill: "var(--text-muted)", fontSize: 12 }}
          label={{ value: "Share of summed revenue (%)", position: "insideBottom", offset: -4, fill: "var(--text-muted)", fontSize: 12 }}
        />
        <YAxis
          type="category"
          dataKey="company"
          width={160}
          stroke="var(--text-muted)"
          tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
        />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--gridline)", opacity: 0.4 }} />
        <Bar dataKey="share_pct" radius={[0, 4, 4, 0]} maxBarSize={22}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.non_pure_play ? "var(--status-warning)" : "var(--series-1)"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
