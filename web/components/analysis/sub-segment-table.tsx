"use client";

import type { Figure } from "@/types/bundle";
import { FigureValue } from "@/components/figure-value";
import { formatSegmentName } from "@/lib/format";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

/** Groups a geography block's raw points by sub_segment and shows the best
 * size/growth/cagr per sub-segment. Surfaces the sub-segment research that
 * lands in the bundle but isn't otherwise visible on the segment page. */
export function SubSegmentTable({ points, label }: { points: Figure[]; label: string }) {
  const subs = new Map<string, Figure[]>();
  for (const p of points) {
    const sub = (p as Figure & { sub_segment?: string | null }).sub_segment;
    if (!sub) continue;
    if (!subs.has(sub)) subs.set(sub, []);
    subs.get(sub)!.push(p);
  }
  if (subs.size === 0) return null;

  const pick = (ps: Figure[], metric: string) =>
    ps.filter((p) => p.metric === metric).sort((a, b) => (b.value_usd_bn ?? 0) - (a.value_usd_bn ?? 0))[0] ?? null;

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold text-[var(--text-secondary)]">{label} — sub-segments</h4>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Sub-segment</TableHead>
            <TableHead>Size</TableHead>
            <TableHead>Growth</TableHead>
            <TableHead>CAGR (fcast)</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {[...subs.entries()].map(([sub, ps]) => (
            <TableRow key={sub}>
              <TableCell className="font-medium">{formatSegmentName(sub)}</TableCell>
              <TableCell><FigureValue figure={pick(ps, "market_size")} /></TableCell>
              <TableCell><FigureValue figure={pick(ps, "growth_yoy")} /></TableCell>
              <TableCell><FigureValue figure={pick(ps, "cagr_forecast")} /></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
