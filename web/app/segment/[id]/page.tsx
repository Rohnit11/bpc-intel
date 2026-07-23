import { notFound } from "next/navigation";
import { getSegment, listSegmentIds } from "@/lib/data";
import { FigureValue } from "@/components/figure-value";
import { formatSegmentName } from "@/lib/format";
import { BasisBadge } from "@/components/basis-badge";
import { ConfidenceBadge } from "@/components/confidence-badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { SegmentGeoBlock } from "@/types/bundle";

export function generateStaticParams() {
  return listSegmentIds().map((id) => ({ id }));
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return { title: `${formatSegmentName(id)} | bpc-intel` };
}

function GeoBlock({ label, block }: { label: string; block: SegmentGeoBlock }) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4">
      <h3 className="font-serif text-lg font-semibold mb-3">{label}</h3>
      <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">Size</div>
          <FigureValue figure={block.size} />
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">Growth</div>
          <FigureValue figure={block.growth} />
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">CAGR</div>
          <FigureValue figure={block.cagr} />
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">Exports</div>
          <FigureValue figure={block.export} />
        </div>
      </div>
      {block.points.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Metric</TableHead>
              <TableHead>Value</TableHead>
              <TableHead>Basis</TableHead>
              <TableHead>Confidence</TableHead>
              <TableHead>Period</TableHead>
              <TableHead>Source</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {block.points.map((p, i) => (
              <TableRow key={i}>
                <TableCell>{p.metric}</TableCell>
                <TableCell><FigureValue figure={p} /></TableCell>
                <TableCell><BasisBadge basis={p.value_basis} /></TableCell>
                <TableCell><ConfidenceBadge confidence={p.confidence} /></TableCell>
                <TableCell>{p.period}</TableCell>
                <TableCell>
                  {p.url ? (
                    <a href={p.url} target="_blank" rel="noreferrer" className="text-[var(--series-1)] underline">
                      {p.source}
                    </a>
                  ) : (
                    p.source
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <p className="text-sm text-[var(--text-muted)]">No DataPoints for this segment × geography yet.</p>
      )}
    </div>
  );
}

export default async function SegmentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const ids = listSegmentIds();
  if (!ids.includes(id)) notFound();
  const bundle = getSegment(id);

  return (
    <div className="space-y-8">
      <h1 className="font-serif text-3xl font-semibold">{formatSegmentName(bundle.segment)}</h1>
      <div className="grid gap-4 lg:grid-cols-2">
        <GeoBlock label="South Korea" block={bundle.KR} />
        <GeoBlock label="India" block={bundle.IN} />
      </div>
    </div>
  );
}
