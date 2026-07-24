import type { RegulatoryArtifact } from "@/types/analysis";
import { EvidenceStrengthBadge } from "./evidence-strength-badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export function RegulatoryPanel({ artifact }: { artifact: RegulatoryArtifact | null }) {
  if (!artifact) {
    return <p className="text-sm text-[var(--text-muted)]">Regulatory readiness not generated yet.</p>;
  }
  return (
    <div className="space-y-3">
      <p className="text-sm text-[var(--text-secondary)]">{artifact.summary}</p>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Jurisdiction</TableHead>
            <TableHead>Step</TableHead>
            <TableHead>What</TableHead>
            <TableHead>Cost</TableHead>
            <TableHead>Timeline</TableHead>
            <TableHead>Evidence</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {artifact.steps.map((s, i) => (
            <TableRow key={i}>
              <TableCell>{s.jurisdiction}</TableCell>
              <TableCell className="font-medium">{s.step}</TableCell>
              <TableCell className="text-[var(--text-secondary)]">{s.what}</TableCell>
              <TableCell className={s.cost === "research needed" ? "text-[var(--text-muted)] italic" : ""}>{s.cost}</TableCell>
              <TableCell className={s.timeline === "research needed" ? "text-[var(--text-muted)] italic" : ""}>{s.timeline}</TableCell>
              <TableCell><EvidenceStrengthBadge strength={s.evidence_strength} /></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
