import Link from "next/link";
import { getIndia, getIndiaSharesChart, getIndiaSharesQualifier, getInsight } from "@/lib/data";
import { SegmentTable } from "@/components/segment-table";
import { ReconciliationCallout } from "@/components/reconciliation-callout";
import { ChartCard } from "@/components/charts/chart-card";
import { IndiaSharesChart } from "@/components/charts/india-shares-chart";
import { FigureValue } from "@/components/figure-value";
import { AnalystRead } from "@/components/analyst-read";

export const metadata = { title: "India | bpc-intel" };

export default function IndiaPage() {
  const india = getIndia();
  const shares = getIndiaSharesChart();
  const qualifier = getIndiaSharesQualifier();
  const insight = getInsight("total_bpc");

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-serif text-3xl font-semibold">India — Beauty &amp; Personal Care</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          MRP includes a 25-45% trade margin over net realisation — see{" "}
          <Link href="/india/value-chain" className="underline text-[var(--series-1)]">
            the value-chain page
          </Link>{" "}
          for pricing, sourcing, and margin detail.
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
            Total market size
          </div>
          <FigureValue figure={india.headline.market_size} emphasis />
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
            Growth (YoY)
          </div>
          <FigureValue figure={india.headline.growth_yoy} emphasis />
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
            Per-capita spend
          </div>
          <FigureValue figure={india.headline.per_capita_spend} emphasis />
        </div>
      </section>

      <AnalystRead insight={insight} geography="IN" />

      <section>
        <h2 className="font-serif text-xl font-semibold mb-4">Segments</h2>
        <SegmentTable rows={india.segments} />
      </section>

      <section>
        <ChartCard
          title="Listed-player revenue shares"
          description="Share of summed listed BRAND-OWNER revenue (does not include unorganised/unlisted players)"
          caption={qualifier}
        >
          <IndiaSharesChart data={shares} />
        </ChartCard>
      </section>

      <section>
        <ReconciliationCallout reconciliation={india.reconciliation} />
      </section>
    </div>
  );
}
