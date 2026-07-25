import type { RiskArtifact, ForceRating } from "@/types/analysis";

const SEV_COLOR: Record<ForceRating, string> = {
  LOW: "var(--status-good)",
  MEDIUM: "var(--status-warning)",
  HIGH: "var(--status-critical)",
};

export function RiskRegister({ artifact }: { artifact: RiskArtifact | null }) {
  if (!artifact) {
    return <p className="text-sm text-[var(--text-muted)]">Risk register not generated yet.</p>;
  }
  const order: Record<ForceRating, number> = { HIGH: 0, MEDIUM: 1, LOW: 2 };
  const risks = [...artifact.risks].sort((a, b) => order[a.severity] - order[b.severity]);
  return (
    <div className="space-y-2">
      {risks.map((r, i) => (
        <div key={i} className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3">
          <div className="flex items-center gap-2 mb-1">
            <span
              className="rounded-full px-2 py-0.5 text-xs font-bold text-white"
              style={{ backgroundColor: SEV_COLOR[r.severity] }}
            >
              {r.severity}
            </span>
            <span className="font-semibold text-sm">{r.risk}</span>
            <span className="text-xs text-[var(--text-muted)]">· {r.geography}</span>
          </div>
          <p className="text-sm text-[var(--text-secondary)]">{r.rationale}</p>
          <p className="text-sm text-[var(--text-primary)] mt-1">
            <span className="font-medium">Mitigation: </span>{r.mitigation}
          </p>
        </div>
      ))}
    </div>
  );
}
