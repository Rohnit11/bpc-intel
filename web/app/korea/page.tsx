import { getKorea, getKoreaExportsChart, getInsight } from "@/lib/data";
import { SegmentTable } from "@/components/segment-table";
import { ReconciliationCallout } from "@/components/reconciliation-callout";
import { ChartCard } from "@/components/charts/chart-card";
import { KoreaExportsChart } from "@/components/charts/korea-exports-chart";
import { FigureValue } from "@/components/figure-value";
import { AnalystRead } from "@/components/analyst-read";

export const metadata = { title: "Korea | bpc-intel" };

export default function KoreaPage() {
  const kr = getKorea();
  const exports = getKoreaExportsChart();
  const insight = getInsight("total_bpc");

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-serif text-3xl font-semibold">South Korea — Beauty &amp; Personal Care</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          Domestic retail, export (FOB), and production value are three different measures — never
          conflated here. Duty-free is tracked as a distinct channel, not folded into domestic retail.
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
            Total market size
          </div>
          <FigureValue figure={kr.headline.market_size} emphasis />
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
            Growth (YoY)
          </div>
          <FigureValue figure={kr.headline.growth_yoy} emphasis />
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
            Total exports
          </div>
          <FigureValue figure={kr.headline.total_export} emphasis />
        </div>
      </section>

      <AnalystRead insight={insight} geography="KR" />

      <section>
        <h2 className="font-serif text-xl font-semibold mb-4">Segments</h2>
        <SegmentTable rows={kr.segments} />
      </section>

      <section>
        <ChartCard title="Exports by segment" description="Best export_value figure per segment (EXPORT_FOB)">
          <KoreaExportsChart data={exports} />
        </ChartCard>
      </section>

      <section>
        <ReconciliationCallout reconciliation={kr.reconciliation} />
      </section>
    </div>
  );
}
