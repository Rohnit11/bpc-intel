import { EvidenceStrengthBadge } from "@/components/analysis/evidence-strength-badge";
import { ResearchNeeded } from "@/components/analysis/research-needed";
import type { EntryLane } from "@/types/premium-skin";

/**
 * The four entry lanes, compared evenly.
 *
 * A lane's `rating` is a verdict sentence, not a LOW/MEDIUM/HIGH scale, so it
 * is rendered as text rather than mapped onto a coloured pill — inventing a
 * scale the artifact does not carry would be the dashboard asserting something
 * the analysis did not. Evidence strength is the only graded signal here, and
 * an INSUFFICIENT lane renders as research needed rather than a hedged rating.
 */
export function EntryLanes({ lanes }: { lanes: EntryLane[] }) {
  if (!lanes.length) {
    return (
      <p className="text-sm text-[var(--text-muted)]">
        No entry lanes on file — Phase 4 has not been run.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {lanes.map((lane) => (
        <div
          key={lane.lane}
          className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4 space-y-3"
        >
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
                Lane ({lane.lane})
              </div>
              <h3 className="font-serif text-lg font-semibold">{lane.label}</h3>
            </div>
            <EvidenceStrengthBadge strength={lane.evidence_strength} />
          </div>

          <div className="text-sm font-semibold text-[var(--text-primary)]">{lane.rating}</div>

          {lane.evidence_strength === "INSUFFICIENT" ? (
            <ResearchNeeded what={lane.research_needed} />
          ) : (
            <>
              <p className="text-sm text-[var(--text-secondary)]">{lane.rationale}</p>
              {lane.evidence.length > 0 && (
                <ul className="list-inside list-disc space-y-0.5 text-xs text-[var(--text-muted)]">
                  {lane.evidence.map((e, i) => (
                    <li key={i}>{e}</li>
                  ))}
                </ul>
              )}
              {lane.research_needed && (
                <p className="text-xs text-[var(--text-muted)]">
                  <span className="font-semibold text-[var(--text-secondary)]">Still open: </span>
                  {lane.research_needed}
                </p>
              )}
            </>
          )}
        </div>
      ))}
    </div>
  );
}
