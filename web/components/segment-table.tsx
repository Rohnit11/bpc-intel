import Link from "next/link";
import type { SegmentRow } from "@/types/bundle";
import { FigureValue } from "@/components/figure-value";
import { formatSegmentName } from "@/lib/format";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export function SegmentTable({ rows }: { rows: SegmentRow[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Segment</TableHead>
          <TableHead>Market size</TableHead>
          <TableHead>Growth (YoY)</TableHead>
          <TableHead>CAGR (forecast)</TableHead>
          <TableHead>Exports</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((row) => (
          <TableRow key={row.segment}>
            <TableCell className="font-medium">
              <Link href={`/segment/${row.segment}`} className="hover:underline">
                {formatSegmentName(row.segment)}
              </Link>
            </TableCell>
            <TableCell>
              <FigureValue figure={row.size} />
              {row.size?.value_usd_bn !== undefined && (
                <div className="text-xs text-[var(--text-muted)]">
                  ≈ US${row.size.value_usd_bn.toFixed(2)}bn
                </div>
              )}
            </TableCell>
            <TableCell><FigureValue figure={row.growth} /></TableCell>
            <TableCell><FigureValue figure={row.cagr} /></TableCell>
            <TableCell><FigureValue figure={row.export} /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
