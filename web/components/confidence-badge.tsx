import type { Confidence } from "@/types/schema";
import { CONFIDENCE_COLOR } from "@/lib/palette";
import { cn } from "@/lib/utils";

const LABEL: Record<Confidence, string> = {
  HIGH: "High",
  MEDIUM: "Medium",
  LOW: "Low",
  ESTIMATE: "Estimate",
};

/** HIGH/MEDIUM/LOW are solid status dots; ESTIMATE gets a hatched swatch
 * (per the plan's "ESTIMATE hatched" spec) so it never reads as measured fact. */
export function ConfidenceBadge({ confidence, className }: { confidence: Confidence; className?: string }) {
  const color = CONFIDENCE_COLOR[confidence];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border border-[var(--border)] bg-[var(--surface-1)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]",
        className,
      )}
      title={`Confidence: ${LABEL[confidence]}`}
    >
      <span
        className="inline-block h-2.5 w-2.5 rounded-full shrink-0"
        style={
          confidence === "ESTIMATE"
            ? {
                backgroundImage: `repeating-linear-gradient(45deg, ${color}, ${color} 1.5px, transparent 1.5px, transparent 3px)`,
                border: `1px solid ${color}`,
              }
            : { backgroundColor: color }
        }
      />
      {LABEL[confidence]}
    </span>
  );
}
