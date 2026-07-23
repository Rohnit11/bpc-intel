import { getMeta } from "@/lib/data";
import { Legend } from "@/components/legend";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export const metadata = { title: "Methodology | bpc-intel" };

export default function MethodologyPage() {
  const meta = getMeta();

  return (
    <div className="space-y-10 max-w-3xl">
      <div>
        <h1 className="font-serif text-3xl font-semibold">Methodology</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          The evidence constitution this dashboard is built on. Every number traces to a fetcher, a
          manual data drop, the baseline report, or an explicit [ESTIMATE] with methodology shown.
        </p>
      </div>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-4">Confidence &amp; value basis</h2>
        <Legend meta={meta} />
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">MRP vs. net realisation (India)</h2>
        <p className="text-sm text-[var(--text-secondary)]">
          India&apos;s MRP (maximum retail price) includes a 25-45% trade margin over net realisation —
          what the manufacturer actually books as revenue. A market size in RETAIL/MRP terms is not
          directly comparable to a company&apos;s reported NET_REALISATION revenue without normalising for
          that margin first (see the reconciliation panels on /korea and /india).
        </p>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Korea: three different measures</h2>
        <p className="text-sm text-[var(--text-secondary)]">
          Korea&apos;s domestic retail (~US$13bn), export FOB (~US$11.4bn), and production value (KRW
          17.9tn) are three different measures of the same industry and are never conflated on this
          dashboard — every figure is tagged with its value_basis. Duty-free is a distinct channel with
          its own dynamics (Chinese daigou decline) and is not folded into domestic retail.
        </p>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">FX rates used</h2>
        <p className="text-sm text-[var(--text-secondary)] mb-3">
          Every USD-equivalent figure on this dashboard is converted with one of these pinned rates —
          never a live/spot rate — so every conversion is reproducible and dated.
        </p>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Pair</TableHead>
              <TableHead>Rate</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Source</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {meta.exchange_rates.map((r, i) => (
              <TableRow key={i}>
                <TableCell>{r.base}/{r.quote}</TableCell>
                <TableCell>{r.rate}</TableCell>
                <TableCell>{r.date}</TableCell>
                <TableCell>{r.source}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Organised vs. unorganised (India)</h2>
        <p className="text-sm text-[var(--text-secondary)]">
          Every India market-size figure states which of organised/unorganised retail it covers where
          the source specifies it; listed-player revenue shares only ever cover the organised, listed
          segment and explicitly exclude unorganised and unlisted competitors (see the qualifier text
          on every shares chart).
        </p>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Fiscal years</h2>
        <p className="text-sm text-[var(--text-secondary)]">
          Indian company data is always tagged FY (e.g. FY25 = Apr 2024–Mar 2025), never a bare
          calendar year. Korean data uses the calendar year (CY2024).
        </p>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Licensing</h2>
        <p className="text-sm text-[var(--text-secondary)]">
          Figures sourced from Euromonitor Passport, Statista, and other licensed research are shown
          here under academic fair-use for personal research only. Do not redistribute this dashboard
          or its underlying data bundle publicly.
        </p>
      </section>
    </div>
  );
}
