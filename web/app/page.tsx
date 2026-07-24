import Link from "next/link";
import { getOverview, getMeta, getKoreaExportsChart, getIndiaSharesChart, getInsight } from "@/lib/data";
import { HeadlineComparisonCard } from "@/components/headline-comparison-card";
import { ReconciliationCallout } from "@/components/reconciliation-callout";
import { ChartCard } from "@/components/charts/chart-card";
import { KoreaExportsChart } from "@/components/charts/korea-exports-chart";
import { IndiaSharesChart } from "@/components/charts/india-shares-chart";
import { Legend } from "@/components/legend";
import { CombinedAnalystRead } from "@/components/analyst-read";

export default function OverviewPage() {
  const ov = getOverview();
  const meta = getMeta();
  const koreaExports = getKoreaExportsChart();
  const indiaShares = getIndiaSharesChart();
  const totalInsight = getInsight("total_bpc");

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-serif text-3xl font-semibold">South Korea × India — Beauty &amp; Personal Care</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          Generated {ov.generated}
          {meta.git_sha ? ` · commit ${meta.git_sha.slice(0, 7)}` : ""}. Every figure below carries its
          value basis, confidence, and source — hover any underlined number.
        </p>
        <nav className="flex flex-wrap gap-3 mt-4 text-sm">
          {[
            ["/korea", "Korea detail"],
            ["/india", "India detail"],
            ["/india/value-chain", "India value chain"],
            ["/corridor", "K-beauty corridor"],
            ["/sources", "Sources ledger"],
            ["/gaps", "Gaps register"],
            ["/methodology", "Methodology"],
          ].map(([href, label]) => (
            <Link key={href} href={href} className="underline text-[var(--series-1)]">
              {label} →
            </Link>
          ))}
        </nav>
      </div>

      <CombinedAnalystRead insight={totalInsight} />

      <section>
        <h2 className="font-serif text-xl font-semibold mb-4">Headline comparison</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <HeadlineComparisonCard
            title="Total BPC market size"
            kr={ov.korea.headline.market_size}
            india={ov.india.headline.market_size}
          />
          <HeadlineComparisonCard
            title="Growth (YoY)"
            kr={ov.korea.headline.growth_yoy}
            india={ov.india.headline.growth_yoy}
          />
          <HeadlineComparisonCard
            title="CAGR (forecast)"
            kr={ov.korea.headline.cagr_forecast}
            india={ov.india.headline.cagr_forecast}
          />
          <HeadlineComparisonCard
            title="Per-capita spend"
            kr={ov.korea.headline.per_capita_spend}
            india={ov.india.headline.per_capita_spend}
          />
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <ChartCard
          title="Korea exports by segment"
          description="Best available export_value figure per segment (EXPORT_FOB)"
        >
          <KoreaExportsChart data={koreaExports} />
        </ChartCard>
        <ChartCard
          title="India: listed-player revenue shares"
          description="Share of summed listed BRAND-OWNER revenue"
          caption="Amber bars are conglomerates (HUL/Godrej/LG H&H) whose reported revenue runs well beyond BPC — their share overstates true BPC position."
        >
          <IndiaSharesChart data={indiaShares} />
        </ChartCard>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <ReconciliationCallout reconciliation={ov.korea.reconciliation} />
        <ReconciliationCallout reconciliation={ov.india.reconciliation} />
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-4">Evidence legend</h2>
        <Legend meta={meta} />
      </section>
    </div>
  );
}
