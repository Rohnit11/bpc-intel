import type { CorridorBundle } from "@/types/bundle";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface KrBrand {
  brand: string;
  owner?: string;
  launched?: string | number;
  segment?: string;
  notes?: string;
}

interface StockRow {
  brand: string;
  owner?: string;
  skus_seen?: number;
  status?: string;
  note?: string;
}

export function CorridorMap({ corridor }: { corridor: CorridorBundle }) {
  const players = corridor.india_side_players as {
    dynamic?: string;
    indian_brands?: Array<{ name: string; type: string; angle: string; source_url?: string }>;
  };
  const qcommerce = corridor.qcommerce as {
    source?: string;
    insight?: string;
    stocked_deep?: StockRow[];
    thin_or_absent?: StockRow[];
  };

  return (
    <div className="space-y-8">
      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Conduits: how K-beauty reaches India</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {corridor.conduits.map((c) => (
            <Card key={c.name}>
              <CardHeader>
                <CardTitle className="text-base">{c.name}</CardTitle>
                <CardDescription>
                  {c.type}
                  {c.since ? ` · since ${c.since}` : ""}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {c.notes && <p className="text-sm text-[var(--text-secondary)]">{c.notes}</p>}
                {Array.isArray(c.kr_brands_carried) && c.kr_brands_carried.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {(c.kr_brands_carried as unknown as KrBrand[]).map((b, i) => (
                      <Badge key={i} variant="outline" title={b.notes ?? undefined}>
                        {b.brand}
                        {b.owner ? ` · ${b.owner}` : ""}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Whitespace ranking</h2>
        <ol className="list-decimal list-inside space-y-1 text-sm text-[var(--text-secondary)]">
          {corridor.whitespace.map((w, i) => (
            <li key={i}>{w}</li>
          ))}
        </ol>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">India-side players</h2>
        {players.dynamic && <p className="text-sm text-[var(--text-secondary)] mb-3">{players.dynamic}</p>}
        <div className="grid gap-3 sm:grid-cols-3">
          {players.indian_brands?.map((b) => (
            <Card key={b.name}>
              <CardHeader>
                <CardTitle className="text-sm">{b.name}</CardTitle>
                <CardDescription>{b.type}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-[var(--text-secondary)]">{b.angle}</p>
                {b.source_url && (
                  <a href={b.source_url} target="_blank" rel="noreferrer" className="text-xs text-[var(--series-1)] underline">
                    source
                  </a>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Q-commerce assortment</h2>
        {qcommerce.source && (
          <p className="text-xs text-[var(--text-muted)] mb-1">Source: {qcommerce.source}</p>
        )}
        {qcommerce.insight && <p className="text-sm text-[var(--text-secondary)] mb-4">{qcommerce.insight}</p>}
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <h3 className="text-sm font-semibold text-[var(--status-good)] mb-2">Stocked deep</h3>
            <ul className="space-y-2 text-sm">
              {qcommerce.stocked_deep?.map((r, i) => (
                <li key={i} className="border-b border-[var(--gridline)] pb-2">
                  <span className="font-medium">{r.brand}</span>
                  {r.owner ? ` (${r.owner})` : ""} — {r.skus_seen} SKUs
                  {r.note && <div className="text-[var(--text-muted)] text-xs">{r.note}</div>}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[var(--status-warning)] mb-2">Thin or absent</h3>
            <ul className="space-y-2 text-sm">
              {qcommerce.thin_or_absent?.map((r, i) => (
                <li key={i} className="border-b border-[var(--gridline)] pb-2">
                  <span className="font-medium">{r.brand}</span>
                  {r.owner ? ` (${r.owner})` : ""} — {r.status}
                  {r.note && <div className="text-[var(--text-muted)] text-xs">{r.note}</div>}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">CDSCO regulation</h2>
        <dl className="space-y-3 text-sm">
          {Object.entries(corridor.regulation).map(([k, v]) => (
            <div key={k}>
              <dt className="font-semibold text-[var(--text-primary)] capitalize">{k.replace(/_/g, " ")}</dt>
              <dd className="text-[var(--text-secondary)]">{v}</dd>
            </div>
          ))}
        </dl>
      </section>
    </div>
  );
}
