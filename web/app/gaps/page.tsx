import { getGaps } from "@/lib/data";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export const metadata = { title: "Gaps register | bpc-intel" };

export default function GapsPage() {
  const gaps = getGaps();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-3xl font-semibold">Gaps register</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          {gaps.length} missing segment × geography × core-metric combinations, with a suggested source
          to fill each.
        </p>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Geography</TableHead>
            <TableHead>Segment</TableHead>
            <TableHead>Metric</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Suggested source</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {gaps.map((g, i) => (
            <TableRow key={i}>
              <TableCell>{g.geography}</TableCell>
              <TableCell>{g.segment}</TableCell>
              <TableCell>{g.metric}</TableCell>
              <TableCell className="text-[var(--text-secondary)]">{g.status}</TableCell>
              <TableCell>{g.suggested_source}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
