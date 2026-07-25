import type { PorterArtifact, PorterGeoRead, PorterForce } from "@/types/analysis";
import { JudgmentCard } from "./judgment-card";

const FORCES: Array<[keyof Omit<PorterGeoRead, "overall" | "sub_segment_overrides">, string]> = [
  ["rivalry", "Competitive rivalry"],
  ["buyer_power", "Buyer power"],
  ["supplier_power", "Supplier power"],
  ["new_entrant_threat", "Threat of new entrants"],
  ["substitutes", "Threat of substitutes"],
];

function GeoForces({ label, read }: { label: string; read: PorterGeoRead | null }) {
  if (!read) {
    return (
      <div>
        <h4 className="font-serif text-lg font-semibold mb-2">{label}</h4>
        <p className="text-sm text-[var(--text-muted)]">No competitive-structure read for this geography yet.</p>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      <h4 className="font-serif text-lg font-semibold">{label}</h4>
      <JudgmentCard
        title="Overall attractiveness"
        judgment={read.overall}
        className="border-[var(--series-1)]"
      />
      <div className="grid gap-2 sm:grid-cols-2">
        {FORCES.map(([key, title]) => (
          <JudgmentCard key={key} title={title} judgment={read[key] as PorterForce} />
        ))}
      </div>
    </div>
  );
}

export function PorterPanel({ artifact }: { artifact: PorterArtifact | null }) {
  if (!artifact) {
    return (
      <p className="text-sm text-[var(--text-muted)]">
        Porter analysis for this segment has not been generated yet. Run{" "}
        <code>/entry-analysis</code>.
      </p>
    );
  }
  return (
    <div className="space-y-6">
      <p className="text-xs text-[var(--text-muted)]">
        Five-forces read, rated from this repo&apos;s evidence only. Higher force = less
        attractive; every rating shows the evidence it rests on.
      </p>
      <div className="grid gap-6 lg:grid-cols-2">
        <GeoForces label="South Korea" read={artifact.KR} />
        <GeoForces label="India" read={artifact.IN} />
      </div>
    </div>
  );
}
