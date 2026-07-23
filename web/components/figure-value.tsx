"use client";

import type { Figure } from "@/types/bundle";
import { formatFigureValue } from "@/lib/format";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { BasisBadge } from "@/components/basis-badge";
import { ConfidenceBadge } from "@/components/confidence-badge";

/**
 * Renders a value + unit with a hover card carrying period, basis,
 * confidence, source, URL, and notes — the evidence trail for every figure
 * on the dashboard. Mirrors the fig() Jinja macro in lib/reports/templates.
 */
export function FigureValue({
  figure,
  className,
  emphasis = false,
}: {
  figure: Figure | null | undefined;
  className?: string;
  emphasis?: boolean;
}) {
  if (!figure) {
    return <span className="text-[var(--text-muted)]">—</span>;
  }

  return (
    <Tooltip delayDuration={150}>
      <TooltipTrigger asChild>
        <span
          className={`cursor-help underline decoration-dotted decoration-[var(--baseline)] underline-offset-4 ${
            emphasis ? "font-serif text-3xl font-semibold" : "font-medium"
          } ${className ?? ""}`}
        >
          {formatFigureValue(figure)}
        </span>
      </TooltipTrigger>
      <TooltipContent>
        <div className="space-y-1.5">
          <div className="flex flex-wrap gap-1">
            <BasisBadge basis={figure.value_basis} />
            <ConfidenceBadge confidence={figure.confidence} />
          </div>
          <div className="text-[var(--text-secondary)]">
            Period: <span className="text-[var(--text-primary)]">{figure.period}</span>
          </div>
          <div className="text-[var(--text-secondary)]">
            Source:{" "}
            {figure.url ? (
              <a
                href={figure.url}
                target="_blank"
                rel="noreferrer"
                className="text-[var(--series-1)] underline"
              >
                {figure.source}
              </a>
            ) : (
              <span className="text-[var(--text-primary)]">{figure.source}</span>
            )}
          </div>
          {figure.notes && (
            <div className="text-[var(--text-secondary)] italic">{figure.notes}</div>
          )}
        </div>
      </TooltipContent>
    </Tooltip>
  );
}
