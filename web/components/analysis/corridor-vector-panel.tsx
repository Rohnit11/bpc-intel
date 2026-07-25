import type { CorridorVectorArtifact } from "@/types/analysis";
import { EvidenceStrengthBadge } from "./evidence-strength-badge";

export function CorridorVectorPanel({ artifact }: { artifact: CorridorVectorArtifact | null }) {
  if (!artifact) return null;
  return (
    <section className="rounded-xl border border-[var(--series-7)]/40 bg-[color-mix(in_oklab,var(--series-7)_6%,var(--surface-1))] p-5 space-y-4">
      <div>
        <h2 className="font-serif text-xl font-semibold mb-1">Corridor as an entry vector</h2>
        <p className="text-sm text-[var(--text-secondary)]">{artifact.read}</p>
      </div>
      <div>
        <h3 className="text-sm font-semibold mb-2">Conduits ranked for entry</h3>
        <ol className="space-y-2">
          {artifact.conduit_ranking.map((c, i) => (
            <li key={i} className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3">
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold text-sm">{i + 1}. {c.conduit}</span>
                <EvidenceStrengthBadge strength={c.evidence_strength} />
              </div>
              <p className="text-sm text-[var(--text-secondary)] mt-1">{c.case}</p>
            </li>
          ))}
        </ol>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 text-sm">
        <div>
          <div className="font-semibold text-[var(--text-primary)]">Whitespace</div>
          <p className="text-[var(--text-secondary)]">{artifact.whitespace_read}</p>
        </div>
        <div>
          <div className="font-semibold text-[var(--text-primary)]">Friction</div>
          <p className="text-[var(--text-secondary)]">{artifact.friction_read}</p>
        </div>
      </div>
    </section>
  );
}
