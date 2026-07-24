"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FigureValue } from "@/components/figure-value";
import { BasisBadge } from "@/components/basis-badge";
import { ConfidenceBadge } from "@/components/confidence-badge";
import { AnalystRead, CombinedAnalystRead } from "@/components/analyst-read";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { SubSegmentTable } from "./sub-segment-table";
import { PorterPanel } from "./porter-panel";
import { PositioningPanel } from "./positioning-panel";
import { PriceLadderPanel } from "./price-ladder-panel";
import type { Insight, SegmentBundle, SegmentGeoBlock } from "@/types/bundle";
import type { PorterArtifact, PositioningSegment, PriceLadderArtifact } from "@/types/analysis";

function GeoBlock({
  label,
  block,
  geography,
  insight,
}: {
  label: string;
  block: SegmentGeoBlock;
  geography: "KR" | "IN";
  insight: Insight | null;
}) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4 space-y-4">
      <h3 className="font-serif text-lg font-semibold">{label}</h3>
      <AnalystRead insight={insight} geography={geography} />
      <div className="grid grid-cols-2 gap-3 text-sm">
        {(["size", "growth", "cagr", "export"] as const).map((k) => (
          <div key={k}>
            <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
              {k === "cagr" ? "CAGR" : k[0].toUpperCase() + k.slice(1)}
            </div>
            <FigureValue figure={block[k]} />
          </div>
        ))}
      </div>
      <SubSegmentTable points={block.points} label={label} />
      {block.points.length > 0 ? (
        <details className="text-sm">
          <summary className="cursor-pointer text-[var(--text-secondary)] font-medium">
            All {block.points.length} underlying DataPoints
          </summary>
          <div className="mt-2">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Metric</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Basis</TableHead>
                  <TableHead>Conf.</TableHead>
                  <TableHead>Period</TableHead>
                  <TableHead>Source</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {block.points.map((p, i) => (
                  <TableRow key={i}>
                    <TableCell>{p.metric}</TableCell>
                    <TableCell><FigureValue figure={p} /></TableCell>
                    <TableCell><BasisBadge basis={p.value_basis} /></TableCell>
                    <TableCell><ConfidenceBadge confidence={p.confidence} /></TableCell>
                    <TableCell>{p.period}</TableCell>
                    <TableCell>
                      {p.url ? (
                        <a href={p.url} target="_blank" rel="noreferrer" className="text-[var(--series-1)] underline">
                          {p.source}
                        </a>
                      ) : p.source}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </details>
      ) : (
        <p className="text-sm text-[var(--text-muted)]">No DataPoints for this segment × geography yet.</p>
      )}
    </div>
  );
}

export function SegmentTabs({
  bundle,
  insight,
  porter,
  positioning,
  priceLadder,
}: {
  bundle: SegmentBundle;
  insight: Insight | null;
  porter: PorterArtifact | null;
  positioning: PositioningSegment | null;
  priceLadder: PriceLadderArtifact | null;
}) {
  return (
    <Tabs defaultValue="overview">
      <TabsList className="flex-wrap">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="porter">Porter</TabsTrigger>
        <TabsTrigger value="positioning">Positioning</TabsTrigger>
        <TabsTrigger value="prices">Prices</TabsTrigger>
      </TabsList>

      <TabsContent value="overview">
        <div className="space-y-4">
          <CombinedAnalystRead insight={insight} />
          <div className="grid gap-4 lg:grid-cols-2">
            <GeoBlock label="South Korea" block={bundle.KR} geography="KR" insight={insight} />
            <GeoBlock label="India" block={bundle.IN} geography="IN" insight={insight} />
          </div>
        </div>
      </TabsContent>
      <TabsContent value="porter"><PorterPanel artifact={porter} /></TabsContent>
      <TabsContent value="positioning"><PositioningPanel segment={positioning} /></TabsContent>
      <TabsContent value="prices">
        <PriceLadderPanel artifact={priceLadder} segment={bundle.segment} />
      </TabsContent>
    </Tabs>
  );
}
