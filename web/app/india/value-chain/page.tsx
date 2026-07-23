import { getIndiaValueChain } from "@/lib/data";
import { FigureValue } from "@/components/figure-value";
import { formatSegmentName } from "@/lib/format";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export const metadata = { title: "India value chain | bpc-intel" };

const FINDING_SECTIONS: Array<[string, string]> = [
  ["supply_chain", "Supply chain"],
  ["import_make", "Import vs. make"],
  ["new_players", "New players"],
  ["demand", "Demand"],
];

export default function IndiaValueChainPage() {
  const vc = getIndiaValueChain();

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-serif text-3xl font-semibold">India — Value Chain</h1>
        <p className="text-[var(--text-secondary)] mt-1">Generated {vc.generated}</p>
      </div>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-4">Imports, pricing &amp; margins by segment</h2>
        <div className="space-y-4">
          {vc.segments.map((s) => (
            <Card key={s.segment}>
              <CardHeader>
                <CardTitle className="text-base">{formatSegmentName(s.segment)}</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 sm:grid-cols-2">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
                    Market size
                  </div>
                  <FigureValue figure={s.size} />
                  <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mt-3 mb-1">
                    Import dependence
                  </div>
                  <FigureValue figure={s.import_dependence} />
                  <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mt-3 mb-1">
                    Imports by origin
                  </div>
                  <ul className="text-sm space-y-0.5">
                    <li>World: <FigureValue figure={s.imports.World} /></li>
                    <li>Korea: <FigureValue figure={s.imports.Korea} /></li>
                    <li>China: <FigureValue figure={s.imports.China} /></li>
                  </ul>
                </div>
                <div>
                  {s.prices.length > 0 && (
                    <>
                      <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
                        Shelf prices (MRP)
                      </div>
                      <ul className="text-sm space-y-0.5 mb-3">
                        {s.prices.map((p, i) => (
                          <li key={i}><FigureValue figure={p} /> — {p.notes}</li>
                        ))}
                      </ul>
                    </>
                  )}
                  {s.margins.length > 0 && (
                    <>
                      <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
                        Gross margins
                      </div>
                      <ul className="text-sm space-y-0.5">
                        {s.margins.map((m, i) => (
                          <li key={i}><FigureValue figure={m} /> — {m.notes}</li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-4">Company operating margins</h2>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Company</TableHead>
              <TableHead>Operating margin</TableHead>
              <TableHead>Period</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {vc.operating_margins.map((m) => (
              <TableRow key={m.company}>
                <TableCell className="font-medium">{m.company}</TableCell>
                <TableCell>{m.value}%</TableCell>
                <TableCell>{m.period}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>

      <section className="space-y-6">
        <h2 className="font-serif text-xl font-semibold">Qualitative findings</h2>
        {FINDING_SECTIONS.map(([key, label]) => {
          const items = vc.findings[key] ?? [];
          if (!items.length) return null;
          return (
            <div key={key}>
              <h3 className="font-semibold mb-2">{label}</h3>
              <ul className="space-y-2 text-sm">
                {items.map((f, i) => (
                  <li key={i} className="border-b border-[var(--gridline)] pb-2">
                    <p className="text-[var(--text-secondary)]">{f.text}</p>
                    <a href={f.url} target="_blank" rel="noreferrer" className="text-xs text-[var(--series-1)] underline">
                      {f.source}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </section>
    </div>
  );
}
