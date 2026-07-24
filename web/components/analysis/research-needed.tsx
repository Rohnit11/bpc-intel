import Link from "next/link";
import { FlaskConical } from "lucide-react";

/**
 * The designed empty-state of the analysis layer: data too thin to judge.
 * Rendered instead of a rating whenever evidence_strength is INSUFFICIENT —
 * a deliberate feature (the system refusing to guess), pointing at the gap
 * that would unlock the judgment.
 */
export function ResearchNeeded({ what }: { what?: string | null }) {
  return (
    <div className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--page-plane)] p-3 text-sm text-[var(--text-muted)]">
      <div className="flex items-center gap-1.5 font-semibold text-[var(--text-secondary)] mb-1">
        <FlaskConical className="h-3.5 w-3.5" aria-hidden />
        Research needed
      </div>
      <p>
        {what ??
          "The underlying data is too thin to support a judgment here — this system does not guess."}{" "}
        <Link href="/gaps" className="underline">
          See the gaps register.
        </Link>
      </p>
    </div>
  );
}
