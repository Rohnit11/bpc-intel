import type { Reconciliation } from "@/types/bundle";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BasisBadge } from "@/components/basis-badge";
import { formatFigureValue } from "@/lib/format";

/**
 * Top-down vs bottom-up reconciliation. When the bases aren't comparable, the
 * system refuses to fake a number — that refusal is the feature, not an
 * error state, so it gets equal visual weight here.
 */
export function ReconciliationCallout({ reconciliation: r }: { reconciliation: Reconciliation }) {
  const hasMismatch = r.mismatches.length > 0;
  return (
    <Card className={hasMismatch ? "border-[var(--status-warning)]" : "border-[var(--status-good)]"}>
      <CardHeader>
        <CardTitle className="text-base">Top-down vs bottom-up reconciliation</CardTitle>
        <CardDescription>
          {r.gap_pct !== null
            ? `Gap: ${r.gap_pct}% ${r.publishable ? "(within the 20% publishable threshold)" : "(exceeds 20% — flagged, not published as reconciled)"}`
            : "Gap not computed — see mismatches below."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
              Top-down (best market size)
            </div>
            {r.top_down ? (
              <div className="space-y-1">
                <div className="font-serif text-xl font-semibold">
                  {formatFigureValue(r.top_down)}
                </div>
                <BasisBadge basis={r.top_down.value_basis} />
                <div className="text-xs text-[var(--text-muted)]">
                  {r.top_down.period} · {r.top_down.source}
                </div>
              </div>
            ) : (
              <span className="text-[var(--text-muted)]">No top-down figure</span>
            )}
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
              Bottom-up (summed listed players)
            </div>
            {r.bottom_up ? (
              <div className="space-y-1">
                <div className="font-serif text-xl font-semibold">
                  {formatFigureValue({ value: r.bottom_up.value, unit: r.bottom_up.unit })}
                </div>
                <BasisBadge basis={r.bottom_up.value_basis} />
              </div>
            ) : (
              <span className="text-[var(--text-muted)]">No bottom-up figure</span>
            )}
          </div>
        </div>

        {r.bottom_up?.qualifier && (
          <p className="text-sm text-[var(--text-secondary)] italic">{r.bottom_up.qualifier}</p>
        )}

        {hasMismatch && (
          <div className="rounded-lg border border-[var(--status-warning)] bg-[color-mix(in_oklab,var(--status-warning)_12%,transparent)] p-3">
            <div className="text-sm font-semibold mb-1">
              Not reconciled — the system will not fake a single number here
            </div>
            <ul className="list-disc list-inside text-sm text-[var(--text-secondary)] space-y-0.5">
              {r.mismatches.map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          </div>
        )}

        {r.note && <p className="text-sm text-[var(--text-secondary)]">{r.note}</p>}
      </CardContent>
    </Card>
  );
}
