import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { BandStats } from "@/types/premium-skin";

/**
 * Does the band survive discounting? One row per cut of the price sweep.
 *
 * Deliberately a table, not a chart: the decision-relevant number (retention)
 * sits beside the two that qualify it (how many SKUs it is computed over, and
 * how deep the discounting is), and a reader has to see all three at once. A
 * retention percentage over 12 SKUs is not the same fact as one over 267.
 */

const LABELS: Record<string, string> = {
  nykaa: "Nykaa",
  tira: "Tira",
  korean: "Korean",
  homegrown: "Homegrown (India)",
  other_foreign: "Other foreign",
  other_observed: "Other observed",
  cleanser: "Cleanser",
  eye_lip: "Eye & lip",
  mask_exfoliant: "Mask / exfoliant",
  moisturiser: "Moisturiser",
  other: "Other",
  serum_other: "Serum (other)",
  serum_pigmentation_brightening: "Serum — pigmentation / brightening",
  sunscreen: "Sunscreen",
  toner_essence: "Toner / essence",
};

export function label(key: string): string {
  return LABELS[key] ?? key.replace(/_/g, " ");
}

/** Retention reads as good news high, so the scale is inverted from the Porter
 * convention: a band that holds is the finding, a band that collapses is not. */
function retentionColor(pct: number): string {
  if (pct >= 80) return "var(--status-good)";
  if (pct >= 60) return "var(--status-warning)";
  return "var(--status-critical)";
}

export function BandRetentionTable({
  cuts,
  firstColumn,
  highlight,
}: {
  cuts: Record<string, BandStats>;
  firstColumn: string;
  /** Keys to mark as hero products — the two SKUs carrying the thesis. */
  highlight?: string[];
}) {
  const rows = Object.entries(cuts).sort(
    ([, a], [, b]) => b.in_band_by_mrp - a.in_band_by_mrp,
  );

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>{firstColumn}</TableHead>
          <TableHead className="text-right">In-band by MRP</TableHead>
          <TableHead className="text-right">Held at street</TableHead>
          <TableHead className="text-right">Retention</TableHead>
          <TableHead className="text-right">Median discount</TableHead>
          <TableHead className="text-right">Zero-discount SKUs</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map(([key, s]) => (
          <TableRow key={key}>
            <TableCell className="font-medium">
              {label(key)}
              {highlight?.includes(key) && (
                <span className="ml-2 text-xs font-normal text-[var(--text-muted)]">hero product</span>
              )}
            </TableCell>
            <TableCell className="text-right tabular-nums">{s.in_band_by_mrp}</TableCell>
            <TableCell className="text-right tabular-nums">{s.held_band_at_street}</TableCell>
            <TableCell className="text-right tabular-nums font-semibold">
              <span style={{ color: retentionColor(s.retention_pct) }}>{s.retention_pct}%</span>
            </TableCell>
            <TableCell className="text-right tabular-nums">{s.discount_depth_pct.median}%</TableCell>
            <TableCell className="text-right tabular-nums">
              {s.discount_depth_pct.zero_discount_skus}{" "}
              <span className="text-[var(--text-muted)]">
                ({s.discount_depth_pct.zero_discount_pct}%)
              </span>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
