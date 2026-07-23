"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatSegmentName } from "@/lib/format";

interface Row {
  label: string;
  segment: string;
  value_usd_mn: number;
  n_sources: number;
  sources: string[];
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: Row }> }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-3 py-2 text-xs shadow-lg max-w-xs">
      <div className="font-semibold">{formatSegmentName(row.segment)}</div>
      <div>US${row.value_usd_mn.toLocaleString()} mn (Korea → India, [CORRIDOR])</div>
      <div className="text-[var(--text-secondary)]">
        Summed from {row.n_sources} DataPoint{row.n_sources === 1 ? "" : "s"}: {row.sources.join(", ")}
      </div>
    </div>
  );
}

export function CorridorTradeChart({ data }: { data: Row[] }) {
  if (!data.length) {
    return <p className="text-sm text-[var(--text-muted)]">No corridor trade data available.</p>;
  }
  const chartData = data.map((d) => ({ ...d, name: formatSegmentName(d.segment) }));
  return (
    <ResponsiveContainer width="100%" height={Math.max(240, chartData.length * 36)}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--gridline)" horizontal={false} />
        <XAxis
          type="number"
          stroke="var(--text-muted)"
          tick={{ fill: "var(--text-muted)", fontSize: 12 }}
          label={{ value: "US$ mn (Comtrade)", position: "insideBottom", offset: -4, fill: "var(--text-muted)", fontSize: 12 }}
        />
        <YAxis
          type="category"
          dataKey="name"
          width={140}
          stroke="var(--text-muted)"
          tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
        />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--gridline)", opacity: 0.4 }} />
        <Bar dataKey="value_usd_mn" fill="var(--series-7)" radius={[0, 4, 4, 0]} maxBarSize={22} />
      </BarChart>
    </ResponsiveContainer>
  );
}
