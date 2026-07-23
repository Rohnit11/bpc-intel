import { getCorridor, getCorridorTradeChart } from "@/lib/data";
import { CorridorMap } from "@/components/corridor-map";
import { ChartCard } from "@/components/charts/chart-card";
import { CorridorTradeChart } from "@/components/charts/corridor-trade-chart";
import { FigureValue } from "@/components/figure-value";
import { formatSegmentName } from "@/lib/format";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export const metadata = { title: "K-beauty corridor | bpc-intel" };

export default function CorridorPage() {
  const corridor = getCorridor();
  const trade = getCorridorTradeChart();

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-serif text-3xl font-semibold">K-beauty Corridor: Korea → India</h1>
        {corridor.headline.trade_base && (
          <p className="text-[var(--text-secondary)] mt-1">{corridor.headline.trade_base}</p>
        )}
        {corridor.headline.momentum && (
          <p className="text-[var(--text-secondary)] mt-2 text-sm">{corridor.headline.momentum}</p>
        )}
        {corridor.headline.entry_barrier && (
          <p className="text-[var(--text-secondary)] mt-2 text-sm">
            <span className="font-semibold">Entry barrier: </span>
            {corridor.headline.entry_barrier}
          </p>
        )}
      </div>

      <section>
        <ChartCard
          title="Korea → India trade by segment"
          description="[CORRIDOR]-tagged export_value DataPoints, summed per segment (UN Comtrade)"
        >
          <CorridorTradeChart data={trade} />
        </ChartCard>
      </section>

      {corridor.sizing.length > 0 && (
        <section>
          <h2 className="font-serif text-xl font-semibold mb-4">Corridor sizing</h2>
          <ul className="grid gap-2 sm:grid-cols-2 text-sm">
            {corridor.sizing.map((f, i) => (
              <li key={i} className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3">
                <div className="font-medium">
                  {formatSegmentName(f.segment)}
                  <span className="text-[var(--text-muted)] font-normal"> · {f.metric.replace(/_/g, " ")}</span>
                </div>
                <FigureValue figure={f} />
              </li>
            ))}
          </ul>
        </section>
      )}

      {corridor.pricing.length > 0 && (
        <section>
          <h2 className="font-serif text-xl font-semibold mb-4">Shelf pricing (India, K-beauty SKUs)</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Segment</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {corridor.pricing.map((f, i) => (
                <TableRow key={i}>
                  <TableCell>{formatSegmentName(f.segment)}</TableCell>
                  <TableCell><FigureValue figure={f} /></TableCell>
                  <TableCell className="text-[var(--text-secondary)]">{f.notes}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </section>
      )}

      <CorridorMap corridor={corridor} />
    </div>
  );
}
