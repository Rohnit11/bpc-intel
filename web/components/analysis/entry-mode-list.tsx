import type { EntryModeArtifact, EntryModeRead } from "@/types/analysis";
import { EvidenceStrengthBadge } from "./evidence-strength-badge";
import { ResearchNeeded } from "./research-needed";
import { formatSegmentName } from "@/lib/format";

const MODE_LABEL: Record<string, string> = {
  build: "Build",
  partner: "Partner with conduit",
  import_corridor: "Import via corridor",
  acquire: "Acquire",
};

export function EntryModeList({ artifact }: { artifact: EntryModeArtifact | null }) {
  if (!artifact) {
    return <p className="text-sm text-[var(--text-muted)]">Entry-mode reads not generated yet.</p>;
  }
  const withMode = artifact.reads.filter((r) => r.mode);
  const needsResearch = artifact.reads.filter((r) => !r.mode);

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        {withMode.map((r: EntryModeRead, i) => (
          <div key={i} className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3 space-y-1.5">
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-semibold">
                {formatSegmentName(r.segment)} · {r.geography}
              </span>
              <EvidenceStrengthBadge strength={r.evidence_strength} />
            </div>
            <span className="inline-block rounded-full bg-[var(--series-1)] px-2 py-0.5 text-xs font-bold text-white">
              {MODE_LABEL[r.mode!] ?? r.mode}
            </span>
            <p className="text-sm text-[var(--text-secondary)]">{r.rationale}</p>
            {r.alternatives_considered && (
              <p className="text-xs text-[var(--text-muted)]">Alternatives: {r.alternatives_considered}</p>
            )}
          </div>
        ))}
      </div>
      {needsResearch.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">
            Not yet recommendable ({needsResearch.length})
          </h3>
          <div className="flex flex-wrap gap-1.5 text-xs">
            {needsResearch.map((r, i) => (
              <span key={i} className="rounded-full border border-dashed border-[var(--border)] px-2 py-0.5 text-[var(--text-muted)]">
                {formatSegmentName(r.segment)} · {r.geography}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
