import Link from "next/link";
import { getAnalysisArtifact } from "@/lib/data";
import { ScorecardTable } from "@/components/analysis/scorecard-table";
import { EntryModeList } from "@/components/analysis/entry-mode-list";
import { RtmPanel } from "@/components/analysis/rtm-panel";
import { RegulatoryPanel } from "@/components/analysis/regulatory-panel";
import { RiskRegister } from "@/components/analysis/risk-register";
import { EvidenceStrengthBadge } from "@/components/analysis/evidence-strength-badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type {
  ScorecardArtifact,
  EntryModeArtifact,
  RtmArtifact,
  RegulatoryArtifact,
  RiskArtifact,
} from "@/types/analysis";

export const metadata = { title: "Market entry | bpc-intel" };

export default function EntryPage() {
  const scorecard = getAnalysisArtifact<ScorecardArtifact>("entry_scorecard");
  const entryMode = getAnalysisArtifact<EntryModeArtifact>("entry_mode");
  const rtmIN = getAnalysisArtifact<RtmArtifact>("rtm_IN");
  const rtmKR = getAnalysisArtifact<RtmArtifact>("rtm_KR");
  const regulatory = getAnalysisArtifact<RegulatoryArtifact>("regulatory");
  const risk = getAnalysisArtifact<RiskArtifact>("risk_register");

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-serif text-3xl font-semibold">Market entry</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          Where to enter, and how — scored from this system&apos;s evidence only. Every judgment
          shows its evidence strength; thin-data cells read &quot;research needed&quot; rather than a
          guess. See{" "}
          <Link href="/methodology" className="underline text-[var(--series-1)]">methodology</Link>{" "}
          and{" "}
          <Link href="/gaps" className="underline text-[var(--series-1)]">the gaps register</Link>.
        </p>
        <div className="mt-2 flex items-center gap-2 text-xs text-[var(--text-muted)]">
          <span>Evidence legend:</span>
          <EvidenceStrengthBadge strength="STRONG" />
          <EvidenceStrengthBadge strength="PARTIAL" />
          <EvidenceStrengthBadge strength="THIN" />
          <EvidenceStrengthBadge strength="INSUFFICIENT" />
        </div>
      </div>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Entry scorecard</h2>
        {scorecard ? (
          <ScorecardTable artifact={scorecard} />
        ) : (
          <p className="text-sm text-[var(--text-muted)]">Scorecard not generated yet — run <code>/entry-analysis</code>.</p>
        )}
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Recommended entry mode</h2>
        <EntryModeList artifact={entryMode} />
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Route to market</h2>
        <Tabs defaultValue="IN">
          <TabsList>
            <TabsTrigger value="IN">India</TabsTrigger>
            <TabsTrigger value="KR">South Korea</TabsTrigger>
          </TabsList>
          <TabsContent value="IN"><RtmPanel artifact={rtmIN} /></TabsContent>
          <TabsContent value="KR"><RtmPanel artifact={rtmKR} /></TabsContent>
        </Tabs>
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Regulatory readiness</h2>
        <RegulatoryPanel artifact={regulatory} />
      </section>

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">Risk register</h2>
        <RiskRegister artifact={risk} />
      </section>
    </div>
  );
}
