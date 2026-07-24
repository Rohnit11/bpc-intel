import type { EvidenceStrength } from "@/types/analysis";
import { cn } from "@/lib/utils";

const LABEL: Record<EvidenceStrength, string> = {
  STRONG: "Strong evidence",
  PARTIAL: "Partial evidence",
  THIN: "Thin evidence",
  INSUFFICIENT: "Research needed",
};

const COLOR: Record<EvidenceStrength, string> = {
  STRONG: "var(--status-good)",
  PARTIAL: "var(--status-warning)",
  THIN: "var(--status-serious)",
  INSUFFICIENT: "var(--status-muted)",
};

/** Same badge language as ConfidenceBadge, but for the analysis layer's
 * evidence_strength — how much sourced data a judgment actually rests on. */
export function EvidenceStrengthBadge({
  strength,
  className,
}: {
  strength: EvidenceStrength;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border border-[var(--border)] bg-[var(--surface-1)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]",
        className,
      )}
      title={`Evidence: ${LABEL[strength]}`}
    >
      <span
        className="inline-block h-2.5 w-2.5 rounded-full shrink-0"
        style={
          strength === "INSUFFICIENT"
            ? {
                border: `1.5px dashed ${COLOR[strength]}`,
                backgroundColor: "transparent",
              }
            : { backgroundColor: COLOR[strength] }
        }
      />
      {LABEL[strength]}
    </span>
  );
}
