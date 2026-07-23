"use client";

import { useMemo, useState } from "react";
import type { SourceRow } from "@/types/bundle";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

type SortKey = keyof SourceRow;

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean))).sort();
}

export function SourcesTable({ rows }: { rows: SourceRow[] }) {
  const [query, setQuery] = useState("");
  const [geo, setGeo] = useState("");
  const [segment, setSegment] = useState("");
  const [confidence, setConfidence] = useState("");
  const [basis, setBasis] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("claim");
  const [sortAsc, setSortAsc] = useState(true);

  const geographies = useMemo(() => uniqueSorted(rows.map((r) => r.geography)), [rows]);
  const segments = useMemo(() => uniqueSorted(rows.map((r) => r.segment)), [rows]);
  const confidences = useMemo(() => uniqueSorted(rows.map((r) => r.confidence)), [rows]);
  const bases = useMemo(() => uniqueSorted(rows.map((r) => r.value_basis)), [rows]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let out = rows.filter((r) => {
      if (geo && r.geography !== geo) return false;
      if (segment && r.segment !== segment) return false;
      if (confidence && r.confidence !== confidence) return false;
      if (basis && r.value_basis !== basis) return false;
      if (q) {
        const hay = `${r.claim} ${r.source_name} ${r.notes}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
    out = [...out].sort((a, b) => {
      const av = a[sortKey] ?? "";
      const bv = b[sortKey] ?? "";
      const cmp = String(av).localeCompare(String(bv), undefined, { numeric: true });
      return sortAsc ? cmp : -cmp;
    });
    return out;
  }, [rows, query, geo, segment, confidence, basis, sortKey, sortAsc]);

  function toggleSort(key: SortKey) {
    if (key === sortKey) setSortAsc((a) => !a);
    else {
      setSortKey(key);
      setSortAsc(true);
    }
  }

  const selectClass =
    "rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-2 py-1.5 text-sm";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search claim, source, notes…"
          className="flex-1 min-w-[200px] rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-3 py-1.5 text-sm"
        />
        <select value={geo} onChange={(e) => setGeo(e.target.value)} className={selectClass}>
          <option value="">All geographies</option>
          {geographies.map((g) => <option key={g} value={g}>{g}</option>)}
        </select>
        <select value={segment} onChange={(e) => setSegment(e.target.value)} className={selectClass}>
          <option value="">All segments</option>
          {segments.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={confidence} onChange={(e) => setConfidence(e.target.value)} className={selectClass}>
          <option value="">All confidence</option>
          {confidences.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={basis} onChange={(e) => setBasis(e.target.value)} className={selectClass}>
          <option value="">All value basis</option>
          {bases.map((b) => <option key={b} value={b}>{b}</option>)}
        </select>
      </div>
      <p className="text-xs text-[var(--text-muted)]">
        {filtered.length} of {rows.length} rows
      </p>
      <Table>
        <TableHeader>
          <TableRow>
            {(["claim", "value", "geography", "segment", "period", "value_basis", "confidence", "source_name"] as SortKey[]).map(
              (key) => (
                <TableHead key={key} className="cursor-pointer select-none" onClick={() => toggleSort(key)}>
                  {key.replace(/_/g, " ")}
                  {sortKey === key ? (sortAsc ? " ▲" : " ▼") : ""}
                </TableHead>
              ),
            )}
          </TableRow>
        </TableHeader>
        <TableBody>
          {filtered.map((r, i) => (
            <TableRow key={i}>
              <TableCell className="max-w-xs">{r.claim}</TableCell>
              <TableCell>
                {r.value} {r.unit}
              </TableCell>
              <TableCell>{r.geography}</TableCell>
              <TableCell>{r.segment}</TableCell>
              <TableCell>{r.period}</TableCell>
              <TableCell>{r.value_basis}</TableCell>
              <TableCell>{r.confidence}</TableCell>
              <TableCell>
                {r.url ? (
                  <a href={r.url} target="_blank" rel="noreferrer" className="text-[var(--series-1)] underline">
                    {r.source_name}
                  </a>
                ) : (
                  r.source_name
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
