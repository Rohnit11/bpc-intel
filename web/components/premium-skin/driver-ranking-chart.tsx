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
import type { DriverCount } from "@/types/premium-skin";

/**
 * What buyers actually say they bought for, ranked. One series (share of
 * reviews), with the two Korea-provenance drivers held in a second colour
 * because where they land in the ranking IS the Phase 3 answer — colour follows
 * that entity, never its rank, so the pair keeps its hue whatever the sort does.
 */

const DRIVER_LABEL: Record<string, string> = {
  repurchase_loyalty: "Repurchase / loyalty",
  pigmentation_concern: "Pigmentation concern",
  ingredient_actives: "Ingredients & actives",
  efficacy_result: "Visible result",
  price_worth: "Worth the price",
  routine_multistep: "Routine / multi-step",
  price_resistance: "Too expensive",
  korea_origin: "Korean origin",
  climate_context: "Climate / humidity",
  social_hype: "Social / hype",
  derm_authority: "Dermatologist authority",
  korean_aesthetic: "Korean aesthetic (glass skin)",
  discount_mention: "Discount / offer",
  word_of_mouth: "Word of mouth",
  other_origin: "Other origin claim",
};

const KOREA_DRIVERS = new Set(["korea_origin", "korean_aesthetic"]);

interface Row {
  driver: string;
  label: string;
  mentioned_pct: number;
  mentioned: number;
  korea: boolean;
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
      <div className="text-[var(--text-secondary)]">
        {row.mentioned} of {nReviews} reviews ({row.mentioned_pct}%)
      </div>
      {row.korea && (
        <div className="mt-1 font-medium" style={{ color: "var(--series-6)" }}>
          Korean-provenance driver
        </div>
      )}
    </div>
  );
}

export function DriverRankingChart({
  drivers,
  nReviews,
}: {
  drivers: DriverCount[];
  nReviews: number;
}) {
  const data: Row[] = drivers
    .filter((d) => d.mentioned > 0)
    .map((d) => ({
      driver: d.driver,
      label: DRIVER_LABEL[d.driver] ?? d.driver.replace(/_/g, " "),
      mentioned_pct: d.mentioned_pct,
      mentioned: d.mentioned,
      korea: KOREA_DRIVERS.has(d.driver),
    }));

  if (!data.length) {
    return <p className="text-sm text-[var(--text-muted)]">No drivers fired in this corpus.</p>;
  }

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--text-secondary)]">
        <span className="inline-flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: "var(--series-1)" }}
          />
          Purchase driver
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: "var(--series-6)" }}
          />
          Korean provenance
        </span>
      </div>
      <ResponsiveContainer width="100%" height={Math.max(240, data.length * 30 + 40)}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 44, bottom: 8 }}>
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
            width={180}
            stroke="var(--text-muted)"
            tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
          />
          <Tooltip
            content={<ChartTooltip nReviews={nReviews} />}
            cursor={{ fill: "var(--gridline)", opacity: 0.4 }}
          />
          <Bar dataKey="mentioned_pct" radius={[0, 4, 4, 0]} maxBarSize={16}>
            {data.map((d) => (
              <Cell key={d.driver} fill={d.korea ? "var(--series-6)" : "var(--series-1)"} />
            ))}
            <LabelList
              dataKey="mentioned_pct"
              position="right"
              formatter={(v: unknown) => `${v}%`}
              style={{ fill: "var(--text-muted)", fontSize: 11 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
