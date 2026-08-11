import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * A single figure with its qualifier. Used where the number IS the chart — a
 * one-bar bar chart is never the right answer.
 *
 * Sans face and proportional figures on the value on purpose: a serif or
 * tabular-nums display number reads as decoration and looks loose at this size.
 */
export function StatTile({
  label,
  value,
  sub,
  tone,
  className,
}: {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  /** Only for figures that genuinely carry a good/bad state. */
  tone?: "good" | "warning" | "critical";
  className?: string;
}) {
  const color =
    tone === "good"
      ? "var(--status-good)"
      : tone === "warning"
        ? "var(--status-warning)"
        : tone === "critical"
          ? "var(--status-critical)"
          : undefined;

  return (
    <div
      className={cn(
        "rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4",
        className,
      )}
    >
      <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
        {label}
      </div>
      <div className="text-2xl font-semibold leading-tight" style={color ? { color } : undefined}>
        {value}
      </div>
      {sub && <div className="mt-1 text-xs text-[var(--text-secondary)]">{sub}</div>}
    </div>
  );
}
