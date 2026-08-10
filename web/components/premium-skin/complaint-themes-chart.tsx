"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ThemeCount } from "@/types/premium-skin";

/**
 * Complaint themes with the negation split kept visible.
 *
 * "No white cast" is praise. Phase 2's headline inverts if asserted and negated
 * mentions are added together, so this chart never shows a combined bar — the
 * two are always separate series, with a legend so identity is never
 * colour-alone.
 *
 * Colour is the validated red/blue pair, not red/green: the obvious
 * bad/good reading fails CVD separation (ΔE 4.1 deutan, well under the 8 floor).
 * Red/blue clears it at ΔE 23.8 light / 25.7 dark.
 */

const THEME_LABEL: Record<string, string> = {
  white_cast: "White cast",
  tone_mismatch: "Tone mismatch",
  breakout_acne: "Breakouts / acne",
  heavy_greasy_humid: "Heavy in humidity",
  pilling: "Pilling",
  irritation: "Irritation / stinging",
  no_efficacy_pigmentation: "No visible effect",
  fragrance: "Fragrance",
  value_for_money: "Not worth the price",
  authenticity: "Authenticity doubt",
  packaging: "Packaging",
};

interface Row {
  theme: string;
  label: string;
  asserted_pct: number;
  negated_pct: number;
  asserted: number;
  negated: number;
}

function ChartTooltip({
  active,
  payload,
  nReviews,
}: {
  active?: boolean;
  payload?: Array<{ payload: Row }>;
  nReviews: number;
}) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-3 py-2 text-xs shadow-lg">
      <div className="font-semibold">{row.label}</div>
      <div style={{ color: "var(--status-critical)" }}>
        Complained of: {row.asserted_pct}% ({row.asserted} of {nReviews})
      </div>
      <div style={{ color: "var(--series-1)" }}>
        Explicitly absent: {row.negated_pct}% ({row.negated} of {nReviews})
      </div>
    </div>
  );
}

export function ComplaintThemesChart({
  themes,
  nReviews,
}: {
  themes: Record<string, ThemeCount>;
  nReviews: number;
}) {
  const data: Row[] = Object.entries(themes)
    .map(([theme, t]) => ({
      theme,
      label: THEME_LABEL[theme] ?? theme.replace(/_/g, " "),
      asserted_pct: t.asserted_pct,
      negated_pct: t.negated_pct,
      asserted: t.asserted,
      negated: t.negated,
    }))
    .filter((r) => r.asserted > 0 || r.negated > 0)
    .sort((a, b) => b.asserted_pct - a.asserted_pct || b.negated_pct - a.negated_pct);

  if (!data.length) {
    return <p className="text-sm text-[var(--text-muted)]">No themes fired in this cut.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(220, data.length * 38 + 56)}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 28, bottom: 8 }} barGap={2}>
        <CartesianGrid strokeDasharray="" stroke="var(--gridline)" horizontal={false} />
        <XAxis
          type="number"
          stroke="var(--text-muted)"
          tick={{ fill: "var(--text-muted)", fontSize: 12 }}
          unit="%"
        />
        <YAxis
          type="category"
          dataKey="label"
          width={150}
          stroke="var(--text-muted)"
          tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
        />
        <Tooltip
          content={<ChartTooltip nReviews={nReviews} />}
          cursor={{ fill: "var(--gridline)", opacity: 0.4 }}
        />
        <Legend
          verticalAlign="top"
          height={28}
          wrapperStyle={{ fontSize: 12, color: "var(--text-secondary)" }}
        />
        <Bar
          dataKey="asserted_pct"
          name="Complained of"
          fill="var(--status-critical)"
          radius={[0, 4, 4, 0]}
          maxBarSize={12}
        />
        <Bar
          dataKey="negated_pct"
          name="Explicitly absent (praise)"
          fill="var(--series-1)"
          radius={[0, 4, 4, 0]}
          maxBarSize={12}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
