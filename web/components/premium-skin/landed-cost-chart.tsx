"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ScenarioSku } from "@/types/premium-skin";

/**
 * Landed COGS as a share of a Rs2,400 MRP, at both order sizes, on one axis.
 * The 100% rule is the whole point: a bar past it is a SKU that loses money at
 * full price with no discount and no marketing at all.
 */

const SKU_LABEL: Record<string, string> = {
  pigmentation_serum: "Pigmentation serum",
  sunscreen: "Sunscreen",
  cleanser: "Cleanser",
  moisturiser: "Moisturiser",
};

interface Row {
  sku: string;
  label: string;
  at_1000: number;
  at_5000: number;
  cogs_1000: number;
  cogs_5000: number;
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: Row }> }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className="rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-3 py-2 text-xs shadow-lg">
      <div className="font-semibold">{row.label}</div>
      <div style={{ color: "var(--series-1)" }}>
        1,000 units: Rs{row.cogs_1000.toLocaleString()} landed — {row.at_1000}% of MRP
      </div>
      <div style={{ color: "var(--series-5)" }}>
        5,000 units: Rs{row.cogs_5000.toLocaleString()} landed — {row.at_5000}% of MRP
      </div>
    </div>
  );
}

export function LandedCostChart({
  at1000,
  at5000,
}: {
  at1000: Record<string, ScenarioSku>;
  at5000: Record<string, ScenarioSku>;
}) {
  const data: Row[] = Object.keys(at1000).map((sku) => ({
    sku,
    label: SKU_LABEL[sku] ?? sku.replace(/_/g, " "),
    at_1000: at1000[sku].cogs_pct_of_mrp_2400,
    at_5000: at5000[sku]?.cogs_pct_of_mrp_2400 ?? 0,
    cogs_1000: at1000[sku].landed_cogs_inr,
    cogs_5000: at5000[sku]?.landed_cogs_inr ?? 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(240, data.length * 60 + 60)}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 44, bottom: 8 }} barGap={2}>
        <CartesianGrid strokeDasharray="" stroke="var(--gridline)" horizontal={false} />
        <XAxis
          type="number"
          stroke="var(--text-muted)"
          tick={{ fill: "var(--text-muted)", fontSize: 12 }}
          unit="%"
          domain={[0, (max: number) => Math.max(110, Math.ceil(max / 10) * 10)]}
        />
        <YAxis
          type="category"
          dataKey="label"
          width={150}
          stroke="var(--text-muted)"
          tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
        />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--gridline)", opacity: 0.4 }} />
        <Legend
          verticalAlign="top"
          height={28}
          wrapperStyle={{ fontSize: 12, color: "var(--text-secondary)" }}
        />
        <ReferenceLine
          x={100}
          stroke="var(--status-critical)"
          strokeWidth={2}
          label={{
            value: "100% of MRP",
            position: "top",
            fill: "var(--status-critical)",
            fontSize: 11,
          }}
        />
        <Bar
          dataKey="at_1000"
          name="1,000 units per SKU"
          fill="var(--series-1)"
          radius={[0, 4, 4, 0]}
          maxBarSize={16}
        >
          <LabelList
            dataKey="at_1000"
            position="right"
            formatter={(v: unknown) => `${v}%`}
            style={{ fill: "var(--text-muted)", fontSize: 11 }}
          />
        </Bar>
        <Bar
          dataKey="at_5000"
          name="5,000 units per SKU"
          fill="var(--series-5)"
          radius={[0, 4, 4, 0]}
          maxBarSize={16}
        >
          <LabelList
            dataKey="at_5000"
            position="right"
            formatter={(v: unknown) => `${v}%`}
            style={{ fill: "var(--text-muted)", fontSize: 11 }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
