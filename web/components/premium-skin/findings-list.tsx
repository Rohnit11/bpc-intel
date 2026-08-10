import type { FindingsFile } from "@/types/premium-skin";

/**
 * Qualitative findings from config/{key}_findings.yaml, grouped by topic.
 *
 * Every entry carries the source and the exact URL that was fetched to write it
 * (CLAUDE.md rule 6), and the link is always shown — a finding a reader cannot
 * trace back is a finding they cannot check. Figures appear inside this prose
 * for context only; the numbers themselves are DataPoints in the sources ledger.
 */
export function FindingsList({ findings }: { findings: FindingsFile | null }) {
  if (!findings || !Object.keys(findings).length) {
    return (
      <p className="text-sm text-[var(--text-muted)]">
        No findings file in the bundle for this phase.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      {Object.entries(findings).map(([topic, items]) => (
        <div key={topic}>
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-[var(--text-muted)]">
            {topic.replace(/_/g, " ")}
          </h3>
          <ul className="space-y-3">
            {(items ?? []).map((f, i) => (
              <li
                key={i}
                className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3"
              >
                <p className="text-sm text-[var(--text-secondary)]">{f.text}</p>
                <p className="mt-2 text-xs text-[var(--text-muted)]">
                  {f.source}
                  {f.url && (
                    <>
                      {" — "}
                      <a
                        href={f.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline break-all text-[var(--series-1)]"
                      >
                        {f.url}
                      </a>
                    </>
                  )}
                </p>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
