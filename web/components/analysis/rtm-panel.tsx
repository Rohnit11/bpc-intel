import type { RtmArtifact } from "@/types/analysis";
import { EvidenceStrengthBadge } from "./evidence-strength-badge";

export function RtmPanel({ artifact }: { artifact: RtmArtifact | null }) {
  if (!artifact) {
    return <p className="text-sm text-[var(--text-muted)]">Route-to-market map not generated yet.</p>;
  }
  return (
    <div className="space-y-3">
      <p className="text-sm text-[var(--text-secondary)]">{artifact.summary}</p>
      <div className="space-y-2">
        {artifact.channels.map((c, i) => (
          <div key={i} className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3">
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="font-semibold">{c.channel}</span>
              <EvidenceStrengthBadge strength={c.evidence_strength} />
            </div>
            <p className="text-sm text-[var(--text-secondary)]">{c.known}</p>
            <p className="text-sm text-[var(--text-primary)] mt-1">
              <span className="font-medium">Entry implication: </span>{c.entry_implications}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
