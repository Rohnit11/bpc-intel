import { notFound } from "next/navigation";
import { getInsight, getSegment, listSegmentIds, getAnalysisArtifact } from "@/lib/data";
import { formatSegmentName } from "@/lib/format";
import { SegmentTabs } from "@/components/analysis/segment-tabs";
import type { PorterArtifact, PositioningArtifact, PriceLadderArtifact } from "@/types/analysis";

export function generateStaticParams() {
  return listSegmentIds().map((id) => ({ id }));
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return { title: `${formatSegmentName(id)} | bpc-intel` };
}

export default async function SegmentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const ids = listSegmentIds();
  if (!ids.includes(id)) notFound();

  const bundle = getSegment(id);
  const insight = getInsight(id);
  const porter = getAnalysisArtifact<PorterArtifact>(`porter_${id}`);
  const positioningAll = getAnalysisArtifact<PositioningArtifact>("positioning");
  const positioning = positioningAll?.segments.find((s) => s.segment === id) ?? null;
  const priceLadder = getAnalysisArtifact<PriceLadderArtifact>("price_ladder");

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-semibold">{formatSegmentName(bundle.segment)}</h1>
      <SegmentTabs
        bundle={bundle}
        insight={insight}
        porter={porter}
        positioning={positioning}
        priceLadder={priceLadder}
      />
    </div>
  );
}
