"use client";

import { useMemo, useState } from "react";
import type { ScorecardArtifact, ScorecardRow, Judgment } from "@/types/analysis";
import { SCORECARD_CRITERIA } from "@/types/analysis";
import { formatSegmentName } from "@/lib/format";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const CRIT_LABEL: Record<string, string> = {
  market_size_evidence: "Size",
  growth_evidence: "Growth",
  competitive_openness: "Openness",
  channel_access: "Channel",
  regulatory_friction: "Reg. ease",
  corridor_tailwind: "Corridor",
};

function scoreColor(s: number | null | undefined): string {
  if (s == null) return "var(--text-muted)";
  if (s >= 4) return "var(--status-good)";
  if (s >= 2.5) return "var(--status-warning)";
  return "var(--status-serious)";
}

function Cell({ j }: { j: Judgment | null }) {
  if (!j || j.score == null) {
    return <span className="text-[var(--text-muted)]" title={j?.research_needed ?? "Research needed"}>—</span>;
  }
  return (
    <span
      className="inline-flex h-6 w-6 items-center justify-center rounded text-xs font-bold text-white"
      style={{ backgroundColor: scoreColor(j.score) }}
      title={j.rationale}
    >
      {j.score}
    </span>
  );
}

export function ScorecardTable({ artifact }: { artifact: ScorecardArtifact }) {
  const [geo, setGeo] = useState<"" | "KR" | "IN">("");
  const rows = useMemo(() => {
    const filtered = geo ? artifact.rows.filter((r) => r.geography === geo) : artifact.rows;
    return [...filtered].sort((a, b) => (b.composite.score ?? -1) - (a.composite.score ?? -1));
  }, [artifact.rows, geo]);

  const btn = (v: "" | "KR" | "IN", label: string) => (
    <button
      onClick={() => setGeo(v)}
      className={`rounded-md px-3 py-1 text-sm font-medium ${
        geo === v ? "bg-[var(--text-primary)] text-[var(--page-plane)]" : "text-[var(--text-secondary)] border border-[var(--border)]"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="space-y-3">
      <div className="flex gap-2">{btn("", "Both")}{btn("KR", "South Korea")}{btn("IN", "India")}</div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Segment</TableHead>
            <TableHead>Geo</TableHead>
            {SCORECARD_CRITERIA.map((c) => (
              <TableHead key={c} className="text-center">{CRIT_LABEL[c]}</TableHead>
            ))}
            <TableHead className="text-right">Composite</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((r: ScorecardRow, i) => (
            <TableRow key={i}>
              <TableCell className="font-medium">{formatSegmentName(r.segment)}</TableCell>
              <TableCell>{r.geography}</TableCell>
              {SCORECARD_CRITERIA.map((c) => (
                <TableCell key={c} className="text-center"><Cell j={r.criteria[c]} /></TableCell>
              ))}
              <TableCell className="text-right">
                {r.composite.score != null ? (
                  <span className="font-serif text-lg font-semibold" style={{ color: scoreColor(r.composite.score) }}>
                    {r.composite.score}
                  </span>
                ) : (
                  <span className="text-[var(--text-muted)]">—</span>
                )}
                <div className="text-[10px] text-[var(--text-muted)]">
                  {r.composite.based_on}/{r.composite.of}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <p className="text-xs text-[var(--text-muted)]">{artifact.method_note}</p>
    </div>
  );
}
