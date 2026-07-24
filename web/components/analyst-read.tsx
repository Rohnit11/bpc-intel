import { Sparkles } from "lucide-react";
import type { Insight } from "@/types/bundle";

/**
 * Renders one segment/geography's analyst read. Visually distinct from
 * Figure/data cards on purpose — this is interpretation of figures already
 * shown elsewhere on the page, never a sourced number itself, so it must
 * never be mistaken for one (see commands/insights.md, CLAUDE.md's "Analyst
 * insights" section).
 */
function Disclaimer() {
  return (
    <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-wide text-[var(--series-7)] font-semibold mb-2">
      <Sparkles className="h-3.5 w-3.5" aria-hidden />
      Analyst read — interpretation, not a sourced figure
    </div>
  );
}

const PANEL_CLASS =
  "rounded-xl border border-dashed border-[var(--series-7)]/40 bg-[color-mix(in_oklab,var(--series-7)_6%,var(--surface-1))] p-4";

export function AnalystRead({
  insight,
  geography,
}: {
  insight: Insight | null;
  geography: "KR" | "IN";
}) {
  if (!insight) return null;
  const section = insight[geography];
  return (
    <div className={PANEL_CLASS}>
      <Disclaimer />
      <p className="text-sm text-[var(--text-primary)] mb-2">{section.read}</p>
      <p className="text-sm text-[var(--text-secondary)] mb-2">
        <span className="font-semibold text-[var(--text-primary)]">Trend: </span>
        {section.trend}
      </p>
      <p className="text-xs text-[var(--text-muted)] italic">{section.caveats}</p>
    </div>
  );
}

export function CombinedAnalystRead({ insight }: { insight: Insight | null }) {
  if (!insight) return null;
  return (
    <div className={PANEL_CLASS}>
      <Disclaimer />
      <p className="text-sm text-[var(--text-primary)]">{insight.combined.read}</p>
    </div>
  );
}
