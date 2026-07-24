import type { PositioningSegment, PositioningCell } from "@/types/analysis";

const TIERS: Array<PositioningCell["tier"]> = ["premium", "masstige", "mass"];

function Grid({ label, cells }: { label: string; cells: PositioningCell[] }) {
  const byTier = (t: string) => cells.filter((c) => c.tier === t);
  return (
    <div>
      <h4 className="font-serif text-lg font-semibold mb-2">{label}</h4>
      <div className="space-y-2">
        {TIERS.map((tier) => {
          const rows = byTier(tier);
          return (
            <div key={tier} className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3">
              <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1.5">
                {tier}
              </div>
              {rows.length === 0 ? (
                <p className="text-sm text-[var(--text-muted)]">No players placed here on current evidence.</p>
              ) : (
                <ul className="space-y-1 text-sm">
                  {rows.map((c, i) => (
                    <li key={i}>
                      <span className="text-[var(--text-muted)]">{c.role}:</span>{" "}
                      {c.players.join(", ")}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function PositioningPanel({ segment }: { segment: PositioningSegment | null }) {
  if (!segment) {
    return (
      <p className="text-sm text-[var(--text-muted)]">
        Positioning map for this segment has not been generated yet.
      </p>
    );
  }
  return (
    <div className="space-y-4">
      <p className="text-xs text-[var(--text-muted)]">
        Players placed on tier × role from evidenced price points and company roles. Empty cells
        mean no evidence, not no players.
      </p>
      {segment.note && <p className="text-sm text-[var(--text-secondary)]">{segment.note}</p>}
      <div className="grid gap-6 lg:grid-cols-2">
        <Grid label="South Korea" cells={segment.KR} />
        <Grid label="India" cells={segment.IN} />
      </div>
    </div>
  );
}
