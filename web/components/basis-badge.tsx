import type { ValueBasis } from "@/types/schema";
import { VALUE_BASIS_COLOR, VALUE_BASIS_LABEL } from "@/lib/palette";
import { cn } from "@/lib/utils";

export function BasisBadge({ basis, className }: { basis: ValueBasis; className?: string }) {
  const color = VALUE_BASIS_COLOR[basis];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border border-[var(--border)] bg-[var(--surface-1)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]",
        className,
      )}
      title={`Value basis: ${VALUE_BASIS_LABEL[basis]}`}
    >
      <span className="inline-block h-2.5 w-2.5 rounded-full shrink-0" style={{ backgroundColor: color }} />
      {VALUE_BASIS_LABEL[basis]}
    </span>
  );
}
