import { notFound } from "next/navigation";
import Link from "next/link";
import { getAnalysisArtifact, listAnalysisArtifacts } from "@/lib/data";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatSegmentName } from "@/lib/format";
import type { CompanyProfile } from "@/types/analysis";

function slugs(): string[] {
  return listAnalysisArtifacts()
    .filter((id) => id.startsWith("profiles/") && !id.endsWith("_not_profiled"))
    .map((id) => id.replace("profiles/", ""));
}

export function generateStaticParams() {
  return slugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const p = getAnalysisArtifact<CompanyProfile>(`profiles/${slug}`);
  return { title: `${p?.name ?? slug} | bpc-intel` };
}

export default async function PlayerPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const p = getAnalysisArtifact<CompanyProfile>(`profiles/${slug}`);
  if (!p) notFound();

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <Link href="/players" className="text-sm text-[var(--series-1)] underline">← All players</Link>
        <h1 className="font-serif text-3xl font-semibold mt-2">{p.name}</h1>
        <p className="text-[var(--text-secondary)]">
          {p.geography} · {p.role} · {p.segments.map(formatSegmentName).join(", ")}
        </p>
      </div>

      <p className="text-[var(--text-primary)]">{p.read}</p>

      {p.figures.length > 0 && (
        <section>
          <h2 className="font-serif text-lg font-semibold mb-2">Evidenced figures</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Metric</TableHead>
                <TableHead>Value</TableHead>
                <TableHead>Basis</TableHead>
                <TableHead>Period</TableHead>
                <TableHead>Conf.</TableHead>
                <TableHead>Source</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {p.figures.map((f, i) => (
                <TableRow key={i}>
                  <TableCell>{f.metric}</TableCell>
                  <TableCell className="font-medium">{f.value} {f.unit}</TableCell>
                  <TableCell>{f.value_basis}</TableCell>
                  <TableCell>{f.period}</TableCell>
                  <TableCell>{f.confidence}</TableCell>
                  <TableCell className="text-[var(--text-secondary)]">{f.source}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </section>
      )}

      {p.recent_moves.length > 0 && (
        <section>
          <h2 className="font-serif text-lg font-semibold mb-2">Recent moves</h2>
          <ul className="list-disc list-inside text-sm text-[var(--text-secondary)] space-y-1">
            {p.recent_moves.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </section>
      )}

      {p.corridor_involvement && (
        <section className="rounded-lg border border-[var(--series-7)]/40 bg-[color-mix(in_oklab,var(--series-7)_6%,transparent)] p-3">
          <h2 className="text-sm font-semibold mb-1">Corridor involvement</h2>
          <p className="text-sm text-[var(--text-secondary)]">{p.corridor_involvement}</p>
        </section>
      )}
    </div>
  );
}
