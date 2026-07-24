import type { PriceLadderArtifact } from "@/types/analysis";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatSegmentName } from "@/lib/format";

const TIER_ORDER: Record<string, number> = { premium: 0, masstige: 1, mass: 2 };

/** India price ladder, optionally filtered to one segment (segment tab use). */
export function PriceLadderPanel({
  artifact,
  segment,
}: {
  artifact: PriceLadderArtifact | null;
  segment?: string;
}) {
  if (!artifact) {
    return (
      <p className="text-sm text-[var(--text-muted)]">
        Price-ladder analysis has not been generated yet.
      </p>
    );
  }
  const rungs = (segment ? artifact.rungs.filter((r) => r.segment === segment) : artifact.rungs)
    .slice()
    .sort((a, b) => (TIER_ORDER[a.tier] ?? 9) - (TIER_ORDER[b.tier] ?? 9));

  if (rungs.length === 0) {
    return (
      <p className="text-sm text-[var(--text-muted)]">
        No observed shelf-price points for this segment yet — see the corridor pricing sweep as it fills.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-[var(--text-muted)]">
        India (MRP-inclusive). Prices are quotes of existing retail-price DataPoints, not estimates.
      </p>
      <Table>
        <TableHeader>
          <TableRow>
            {!segment && <TableHead>Segment</TableHead>}
            <TableHead>Tier</TableHead>
            <TableHead>Price range</TableHead>
            <TableHead>Examples</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rungs.map((r, i) => (
            <TableRow key={i}>
              {!segment && (
                <TableCell className="font-medium">
                  {formatSegmentName(r.segment)}
                  {r.sub_segment ? ` · ${formatSegmentName(r.sub_segment)}` : ""}
                </TableCell>
              )}
              <TableCell className="capitalize">{r.tier}</TableCell>
              <TableCell className="font-medium">{r.price_range}</TableCell>
              <TableCell className="text-[var(--text-secondary)]">{r.examples.join("; ")}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {artifact.masstige_gap_note && (
        <p className="rounded-lg border border-[var(--series-4)]/40 bg-[color-mix(in_oklab,var(--series-4)_8%,transparent)] p-3 text-sm text-[var(--text-secondary)]">
          <span className="font-semibold text-[var(--text-primary)]">Masstige gap: </span>
          {artifact.masstige_gap_note}
        </p>
      )}
    </div>
  );
}
