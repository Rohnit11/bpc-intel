import type { MetaBundle } from "@/types/bundle";
import type { Confidence, ValueBasis } from "@/types/schema";
import { ConfidenceBadge } from "@/components/confidence-badge";
import { BasisBadge } from "@/components/basis-badge";

const CONFIDENCE_ORDER: Confidence[] = ["HIGH", "MEDIUM", "LOW", "ESTIMATE"];
const BASIS_ORDER: ValueBasis[] = [
  "RETAIL", "NET_REALISATION", "WHOLESALE", "EXPORT_FOB",
  "PRODUCTION", "IMPORT_CIF", "MRP", "NA",
];

/** Persistent confidence + value-basis legend, driven by meta.json's legend text. */
export function Legend({ meta }: { meta: MetaBundle }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-2">
          Confidence
        </h3>
        <ul className="space-y-1.5">
          {CONFIDENCE_ORDER.map((c) => (
            <li key={c} className="flex items-start gap-2 text-sm">
              <ConfidenceBadge confidence={c} />
              <span className="text-[var(--text-secondary)]">{meta.confidence_legend[c]}</span>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-2">
          Value basis
        </h3>
        <ul className="space-y-1.5">
          {BASIS_ORDER.map((b) => (
            <li key={b} className="flex items-start gap-2 text-sm">
              <BasisBadge basis={b} />
              <span className="text-[var(--text-secondary)]">{meta.value_basis_legend[b]}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
