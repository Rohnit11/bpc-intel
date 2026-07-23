"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { VALUE_BASIS_COLOR } from "@/lib/palette";
import { formatSegmentName } from "@/lib/format";

interface Row {
  label: string;
  segment: string;
  value: number;
  unit: string;
  value_basis: keyof typeof VALUE_BASIS_COLOR;
  confidence: string;
  source: string;
  period: string;
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: Row }> }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-3 py-2 text-xs shadow-lg">
      <div className="font-semibold">{formatSegmentName(row.segment)}</div>
      <div>{row.value.toLocaleString()} {row.unit.replace("_", " ")}</div>
      <div className="text-[var(--text-secondary)]">
        {row.value_basis} · {row.confidence} · {row.period}
      </div>
      <div className="text-[var(--text-secondary)]">{row.source}</div>
    </div>
  );
}

export function KoreaExportsChart({ data }: { data: Row[] }) {
  if (!data.length) {
    return <p className="text-sm text-[var(--text-muted)]">No export data available.</p>;
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
          label={{ value: "US$ bn, FOB", position: "insideBottom", offset: -4, fill: "var(--text-muted)", fontSize: 12 }}
        />
        <YAxis
          type="category"
          dataKey="name"
          width={140}
          stroke="var(--text-muted)"
          tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
        />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--gridline)", opacity: 0.4 }} />
        <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={22}>
          {chartData.map((d, i) => (
            <Cell key={i} fill={VALUE_BASIS_COLOR[d.value_basis] ?? "var(--series-1)"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
