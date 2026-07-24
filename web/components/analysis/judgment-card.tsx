import type { Judgment, ForceRating } from "@/types/analysis";
import { EvidenceStrengthBadge } from "./evidence-strength-badge";
import { ResearchNeeded } from "./research-needed";
import { cn } from "@/lib/utils";

const RATING_COLOR: Record<ForceRating, string> = {
  LOW: "var(--status-good)",
  MEDIUM: "var(--status-warning)",
  HIGH: "var(--status-critical)",
};

/**
 * One evidence-backed judgment (a Porter force, a scorecard criterion...).
 * Renders the rating + rationale + evidence list, or the ResearchNeeded
 * state when evidence_strength is INSUFFICIENT.
 *
 * `invertRating` flips the color read for judgments where HIGH is good news
 * (default assumes HIGH = adverse, the Porter convention).
 */
export function JudgmentCard({
  title,
  judgment,
  invertRating = false,
  className,
}: {
  title: string;
  judgment: Judgment;
  invertRating?: boolean;
  className?: string;
}) {
  if (judgment.evidence_strength === "INSUFFICIENT") {
    return (
      <div className={cn("rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3", className)}>
        <div className="text-sm font-semibold mb-2">{title}</div>
        <ResearchNeeded what={judgment.research_needed} />
      </div>
    );
  }

  const rating = judgment.rating ?? null;
  const color =
    rating === null
      ? "var(--text-muted)"
      : RATING_COLOR[invertRating ? (({ LOW: "HIGH", MEDIUM: "MEDIUM", HIGH: "LOW" } as const)[rating]) : rating];

  return (
    <div className={cn("rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3 space-y-2", className)}>
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-semibold">{title}</span>
        <span className="flex items-center gap-2">
          {rating !== null && (
            <span
              className="rounded-full px-2 py-0.5 text-xs font-bold text-white"
              style={{ backgroundColor: color }}
            >
              {rating}
            </span>
          )}
          {judgment.score !== null && judgment.score !== undefined && (
            <span className="font-serif text-lg font-semibold">{judgment.score}/5</span>
          )}
          <EvidenceStrengthBadge strength={judgment.evidence_strength} />
        </span>
      </div>
      <p className="text-sm text-[var(--text-secondary)]">{judgment.rationale}</p>
      {judgment.evidence.length > 0 && (
        <ul className="text-xs text-[var(--text-muted)] list-disc list-inside space-y-0.5">
          {judgment.evidence.map((e, i) => (
            <li key={i}>{e}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
