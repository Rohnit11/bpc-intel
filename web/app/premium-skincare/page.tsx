import Link from "next/link";
import { getAnalysisArtifact, getFindings } from "@/lib/data";
import { JudgmentCard } from "@/components/analysis/judgment-card";
import { ResearchNeeded } from "@/components/analysis/research-needed";
import { EvidenceStrengthBadge } from "@/components/analysis/evidence-strength-badge";
import { ChartCard } from "@/components/charts/chart-card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatTile } from "@/components/premium-skin/stat-tile";
import { BandRetentionTable, label } from "@/components/premium-skin/band-retention-table";
import { ComplaintThemesChart } from "@/components/premium-skin/complaint-themes-chart";
import { DriverRankingChart } from "@/components/premium-skin/driver-ranking-chart";
import { LandedCostChart } from "@/components/premium-skin/landed-cost-chart";
import { SensitivityChart } from "@/components/premium-skin/sensitivity-chart";
import { EntryLanes } from "@/components/premium-skin/entry-lanes";
import { FindingsList } from "@/components/premium-skin/findings-list";
import type {
  BandArtifact,
  DemandArtifact,
  EntryArtifact,
  FitArtifact,
  UnitEconomicsArtifact,
} from "@/types/premium-skin";

export const metadata = { title: "Premium skincare | bpc-intel" };

const SEVERITY_COLOR: Record<string, string> = {
  HIGH: "var(--status-critical)",
  MEDIUM: "var(--status-warning)",
  LOW: "var(--status-good)",
};

function inr(n: number): string {
  return `Rs${Math.round(n).toLocaleString("en-IN")}`;
}

/** A section that has no artifact yet says so, and says which phase writes it. */
function NotRun({ what }: { what: string }) {
  return (
    <p className="text-sm text-[var(--text-muted)]">
      Not in the bundle yet — {what} See{" "}
      <code className="text-xs">docs/premium-skincare-brief.md</code>.
    </p>
  );
}

export default function PremiumSkincarePage() {
  const band = getAnalysisArtifact<BandArtifact>("premium_skin_band_frame2");
  const bandFrame1 = getAnalysisArtifact<BandArtifact>("premium_skin_band");
  const fit = getAnalysisArtifact<FitArtifact>("premium_skin_fit");
  const demand = getAnalysisArtifact<DemandArtifact>("premium_skin_demand");
  const econ = getAnalysisArtifact<UnitEconomicsArtifact>("premium_skin_unit_economics");
  const entry = getAnalysisArtifact<EntryArtifact>("premium_skin_entry");
  const fitFindings = getFindings("premium_skin_fit");
  const demandFindings = getFindings("premium_skin_demand");

  const porter = entry?.porter_band_level;
  const frames = entry?.price_frame_comparison;
  const econ1000 = econ?.scenarios?.cepa_no_units_1000;
  const econ5000 = econ?.scenarios?.cepa_no_units_5000;
  const originContrast = demand?.most_useful_frame?.origin_contrast ?? {};
  const encroachment = demand?.domestic_encroachment?.brand_neutral_queries;

  return (
    <div className="space-y-12">
      {/* ---------- Header ---------- */}
      <div>
        <h1 className="font-serif text-3xl font-semibold">Premium skincare — Rs1,500-3,000</h1>
        <p className="mt-1 max-w-3xl text-[var(--text-secondary)]">
          A build-a-brand thread, not a tier overview: can a Korean-formulated skincare range hold
          the Rs1,500-3,000 MRP band in India? The band is a literal MRP interval, not the
          taxonomy&apos;s word &quot;premium&quot; — see{" "}
          <Link href="/methodology" className="underline text-[var(--series-1)]">
            methodology
          </Link>{" "}
          and{" "}
          <Link href="/gaps" className="underline text-[var(--series-1)]">
            the gaps register
          </Link>
          .
        </p>
        <p className="mt-2 max-w-3xl text-xs text-[var(--text-muted)]">
          {band?.scope ??
            "Price evidence is ONLINE ONLY (Nykaa, Tira, Amazon.in) — the discount-heaviest channel in the market."}{" "}
          Organised retail only. All figures come from the phase artifacts; this page derives none
          of its own.
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-[var(--text-muted)]">
          <span>Evidence legend:</span>
          <EvidenceStrengthBadge strength="STRONG" />
          <EvidenceStrengthBadge strength="PARTIAL" />
          <EvidenceStrengthBadge strength="THIN" />
          <EvidenceStrengthBadge strength="INSUFFICIENT" />
        </div>
      </div>

      {/* ---------- The read ---------- */}
      <section>
        <h2 className="mb-3 font-serif text-xl font-semibold">The read</h2>
        {porter && entry ? (
          <div className="space-y-4">
            <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-5">
              <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
                Overall, at band level
              </div>
              <p className="font-serif text-lg font-semibold">{porter.overall.rating}</p>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">{porter.overall.rationale}</p>
              <div className="mt-3">
                <EvidenceStrengthBadge strength={porter.overall.evidence_strength} />
              </div>
            </div>
            <div className="rounded-xl border border-[var(--border)] bg-[var(--page-plane)] p-5">
              <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
                What decides it
              </div>
              <p className="text-sm text-[var(--text-secondary)]">
                {entry.unit_economics.headline}
              </p>
            </div>
          </div>
        ) : (
          <NotRun what="Phase 4 writes the entry read." />
        )}
      </section>

      {/* ---------- Phase 1 / 4: does the band hold? ---------- */}
      <section>
        <h2 className="font-serif text-xl font-semibold">Does the band hold under discounting?</h2>
        <p className="mb-4 mt-1 max-w-3xl text-sm text-[var(--text-secondary)]">
          The kill condition for the whole thread: SKUs list inside Rs1,500-3,000, but do they still
          transact there? Retention is the share of in-band-by-MRP SKUs whose street price is still
          in-band.
        </p>

        {band ? (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {Object.entries(band.headline_by_platform).map(([platform, s]) => (
                <StatTile
                  key={platform}
                  label={`${label(platform)} retention`}
                  value={`${s.retention_pct}%`}
                  tone={s.retention_pct >= 80 ? "good" : "warning"}
                  sub={`${s.held_band_at_street} of ${s.in_band_by_mrp} in-band SKUs held. Median discount ${s.discount_depth_pct.median}%.`}
                />
              ))}
              {frames && (
                <>
                  <StatTile
                    label="Frame 1 vs frame 2"
                    value={`${frames.frame_1.nykaa_retention_pct}% → ${frames.frame_2.nykaa_retention_pct}%`}
                    sub={`Nykaa retention, ${frames.frame_1.date} (sale live) vs ${frames.frame_2.date} (off-sale).`}
                  />
                  <StatTile
                    label="Zero-discount SKUs"
                    value={`${frames.frame_1.nykaa_zero_discount_pct}% → ${frames.frame_2.nykaa_zero_discount_pct}%`}
                    sub="Nykaa, across the same two frames."
                  />
                </>
              )}
            </div>

            {frames && (
              <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4">
                <p className="text-sm text-[var(--text-secondary)]">{frames.verdict}</p>
                <p className="mt-2 text-xs text-[var(--text-muted)]">{frames.note}</p>
              </div>
            )}

            <Tabs defaultValue="platform">
              <TabsList>
                <TabsTrigger value="platform">By platform</TabsTrigger>
                <TabsTrigger value="group">By brand group</TabsTrigger>
                <TabsTrigger value="format">By format</TabsTrigger>
                <TabsTrigger value="hero">Hero products</TabsTrigger>
              </TabsList>
              <TabsContent value="platform">
                <BandRetentionTable cuts={band.headline_by_platform} firstColumn="Platform" />
              </TabsContent>
              <TabsContent value="group">
                <BandRetentionTable cuts={band.by_brand_group} firstColumn="Brand group" />
              </TabsContent>
              <TabsContent value="format">
                <BandRetentionTable
                  cuts={band.by_format}
                  firstColumn="Format"
                  highlight={["sunscreen", "serum_pigmentation_brightening"]}
                />
              </TabsContent>
              <TabsContent value="hero">
                <div className="space-y-6">
                  {Object.entries(band.hero_formats_by_group).map(([format, groups]) => (
                    <div key={format}>
                      <h3 className="mb-2 text-sm font-semibold">{label(format)}</h3>
                      <BandRetentionTable cuts={groups} firstColumn="Brand group" />
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>

            <p className="text-xs text-[var(--text-muted)]">
              Frame 2 swept {band.generated_at} from <code>{band.source_raw_file}</code>
              {bandFrame1 && <> · frame 1 from <code>{bandFrame1.source_raw_file}</code></>}. Offline
              retail is not in this sweep and remains the thread&apos;s largest open channel risk.
            </p>
          </div>
        ) : (
          <NotRun what="Phase 1 and Phase 4 write the price frames." />
        )}
      </section>

      {/* ---------- Phase 2: fit & real problems ---------- */}
      <section>
        <h2 className="font-serif text-xl font-semibold">Fit, and what buyers actually complain about</h2>
        <p className="mb-4 mt-1 max-w-3xl text-sm text-[var(--text-secondary)]">
          Complaint themes are counted with negation handling — &quot;no white cast&quot; is praise,
          and reading it as a complaint inverts the finding. Both readings are always shown.
        </p>

        {fit ? (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatTile
                label="Reviews analysed"
                value={fit.coverage.reviews_analysed.toLocaleString()}
                sub={`${fit.coverage.skus_with_any_review} of ${fit.coverage.skus_targeted} in-band SKUs carried reviews. ${fit.coverage.verified_buyer_share_pct}% verified buyers.`}
              />
              <StatTile
                label="Negative-frame reviews"
                value={fit.coverage.reviews_negative_frame.toLocaleString()}
                sub={`${fit.rating_distribution.overall.negative_share_pct}% of ${fit.rating_distribution.overall.written_reviews.toLocaleString()} written reviews are 1-2 star.`}
              />
              <StatTile
                label="Declared a skin tone"
                value={fit.coverage.reviews_with_declared_skin_tone.toLocaleString()}
                sub="Self-declared on the review form, not observed."
              />
              <StatTile
                label="White cast, Korean sunscreen"
                value={`${fit.korean_sunscreen.themes.white_cast?.negated ?? 0} absent vs ${fit.korean_sunscreen.themes.white_cast?.asserted ?? 0} complained`}
                sub="Positive-frame mentions. The reputation is that it is solved, not that it fails."
              />
            </div>

            <Tabs defaultValue="ksun_neg">
              <TabsList>
                <TabsTrigger value="ksun_neg">Korean sunscreen — negatives</TabsTrigger>
                <TabsTrigger value="ksun_pos">Korean sunscreen — positives</TabsTrigger>
                <TabsTrigger value="pig_neg">Pigmentation serum — negatives</TabsTrigger>
              </TabsList>
              <TabsContent value="ksun_neg">
                <ChartCard
                  title="What goes wrong with Korean sunscreen in India"
                  description={`Share of ${fit.korean_sunscreen_negative.n_reviews} negative-frame reviews mentioning each theme`}
                  caption="Irritation and heaviness in humidity are the live failure modes — the climate/texture mismatch, not white cast."
                >
                  <ComplaintThemesChart
                    themes={fit.korean_sunscreen_negative.themes}
                    nReviews={fit.korean_sunscreen_negative.n_reviews}
                  />
                </ChartCard>
              </TabsContent>
              <TabsContent value="ksun_pos">
                <ChartCard
                  title="What buyers praise Korean sunscreen for"
                  description={`Share of ${fit.korean_sunscreen.n_reviews} positive-frame reviews mentioning each theme`}
                  caption="White cast is mentioned mostly to say it is absent — the single clearest case for keeping the negation split visible."
                >
                  <ComplaintThemesChart
                    themes={fit.korean_sunscreen.themes}
                    nReviews={fit.korean_sunscreen.n_reviews}
                  />
                </ChartCard>
              </TabsContent>
              <TabsContent value="pig_neg">
                <ChartCard
                  title="What goes wrong with pigmentation serums"
                  description={`Share of ${fit.pigmentation_serum_negative.n_reviews} negative-frame reviews mentioning each theme`}
                  caption="A different failure mode from sunscreen: breakouts and no visible effect, not texture."
                >
                  <ComplaintThemesChart
                    themes={fit.pigmentation_serum_negative.themes}
                    nReviews={fit.pigmentation_serum_negative.n_reviews}
                  />
                </ChartCard>
              </TabsContent>
            </Tabs>

            <div>
              <h3 className="mb-2 text-sm font-semibold">Self-declared skin tone, by brand group</h3>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Brand group</TableHead>
                    {Object.keys(fit.tone_declaration_by_group.korean ?? {}).map((tone) => (
                      <TableHead key={tone} className="text-right">
                        {tone}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(fit.tone_declaration_by_group).map(([group, tones]) => (
                    <TableRow key={group}>
                      <TableCell className="font-medium">{label(group)}</TableCell>
                      {Object.keys(fit.tone_declaration_by_group.korean ?? {}).map((tone) => (
                        <TableCell key={tone} className="text-right tabular-nums">
                          {tones[tone] ?? 0}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <p className="mt-2 text-xs text-[var(--text-muted)]">
                Tone is declared by the reviewer, and most reviewers declare nothing. It describes
                who writes reviews, not who buys. {fit.scope}
              </p>
            </div>

            <div>
              <h3 className="mb-3 text-sm font-semibold">Sourced findings — fit (Phase 2)</h3>
              <FindingsList findings={fitFindings} />
            </div>
          </div>
        ) : (
          <NotRun what="Phase 2 writes the fit artifact." />
        )}
      </section>

      {/* ---------- Phase 3: is "Korean" load-bearing? ---------- */}
      <section>
        <h2 className="font-serif text-xl font-semibold">Is &quot;Korean&quot; load-bearing?</h2>
        <p className="mb-4 mt-1 max-w-3xl text-sm text-[var(--text-secondary)]">
          A positioning input, not a go/no-go. If provenance is incidental, Korea is a
          manufacturing-quality decision and the brand leads on concern and mechanism instead.
        </p>

        {demand ? (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatTile
                label="Reviews mined"
                value={demand.corpus.reviews.toLocaleString()}
                sub={`${demand.corpus.by_origin.KR?.toLocaleString() ?? 0} Korean-origin, ${demand.corpus.by_origin.IN?.toLocaleString() ?? 0} Indian-origin. Median ${demand.corpus.median_word_count} words.`}
              />
              {originContrast.KR && (
                <StatTile
                  label="Korean origin named"
                  value={`${originContrast.KR.korea_origin_pct}%`}
                  sub={`of ${originContrast.KR.n_reviews.toLocaleString()} reviews of Korean-origin SKUs, against ${originContrast.KR.ingredient_actives_pct}% naming an active.`}
                />
              )}
              {originContrast.IN && (
                <StatTile
                  label="On Indian-origin SKUs"
                  value={`${originContrast.IN.korea_origin_mentions} of ${originContrast.IN.n_reviews}`}
                  sub="Reviews invoking Korea. Korea is not a benchmark buyers reach for."
                />
              )}
              <StatTile
                label="Provenance without mechanism"
                value={`${demand.most_useful_frame.provenance_only.origin_only_pct_of_corpus}%`}
                sub={`${demand.most_useful_frame.provenance_only.origin_only} of ${demand.most_useful_frame.provenance_only.n_reviews.toLocaleString()} reviews cite origin and nothing else.`}
              />
            </div>

            <ChartCard
              title="Why buyers say they bought"
              description={`Share of ${demand.most_useful_frame.n_reviews.toLocaleString()} positive-frame reviews mentioning each driver`}
              caption={demand.most_useful_frame.note}
            >
              <DriverRankingChart
                drivers={demand.most_useful_frame.driver_ranking}
                nReviews={demand.most_useful_frame.n_reviews}
              />
            </ChartCard>

            {encroachment && (
              <div>
                <h3 className="mb-2 text-sm font-semibold">
                  Who holds the band on brand-neutral searches
                </h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Manufacturer origin</TableHead>
                      <TableHead className="text-right">In-band observations</TableHead>
                      <TableHead className="text-right">Distinct brands</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {Object.entries(encroachment.by_origin)
                      .sort(([, a], [, b]) => b.in_band_observations - a.in_band_observations)
                      .map(([origin, v]) => (
                        <TableRow key={origin}>
                          <TableCell className="font-medium">{label(origin)}</TableCell>
                          <TableCell className="text-right tabular-nums">
                            {v.in_band_observations}
                          </TableCell>
                          <TableCell className="text-right tabular-nums">
                            {v.distinct_brands.length}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
                <p className="mt-2 text-xs text-[var(--text-muted)]">
                  {demand.domestic_encroachment.method}
                </p>
              </div>
            )}

            <div>
              <h3 className="mb-3 text-sm font-semibold">Sourced findings — demand (Phase 3)</h3>
              <FindingsList findings={demandFindings} />
            </div>
          </div>
        ) : (
          <NotRun what="Phase 3 writes the demand artifact." />
        )}
      </section>

      {/* ---------- Phase 4: unit economics ---------- */}
      <section>
        <h2 className="font-serif text-xl font-semibold">Unit economics</h2>
        <p className="mb-4 mt-1 max-w-3xl text-sm text-[var(--text-secondary)]">
          Every figure below is <strong>[ESTIMATE]</strong> — a model, not a measurement. Inputs that
          could not be sourced are swept across a range rather than plugged with a point value, and
          the sweep is ranked so it is visible which unknowns actually matter.
        </p>

        {econ && econ1000 && econ5000 ? (
          <div className="space-y-6">
            <ChartCard
              title="Landed COGS as a share of MRP, by order size"
              description="Rs2,400 MRP, no CEPA preference claimed. Both order sizes on one axis."
              caption={`FX pinned at Rs${econ.fx.inr_per_usd}/USD (${econ.fx.pinned}, ${econ.fx.source}). ${econ.method_note.split(". ")[0]}.`}
            >
              <LandedCostChart at1000={econ1000} at5000={econ5000} />
            </ChartCard>

            <ChartCard
              title="What moves the answer"
              description="Contribution-margin swing across each input's plausible range, ranked"
              caption="Unresolved inputs are swept, not guessed. Order size is the exception: it is a decision, and it outweighs every research gap."
            >
              <SensitivityChart rows={econ.decision_sensitivity} />
            </ChartCard>

            {entry && (
              <div>
                <div className="grid gap-4 sm:grid-cols-3">
                  {Object.entries(entry.unit_economics.launch_cash_at_risk_inr)
                    .filter(([, v]) => typeof v === "number")
                    .map(([key, v]) => (
                      <StatTile
                        key={key}
                        label={`Launch cash — ${key.replace(/_/g, " ")}`}
                        value={inr(v as number)}
                      />
                    ))}
                </div>
                {typeof entry.unit_economics.launch_cash_at_risk_inr.note === "string" && (
                  <p className="mt-2 text-xs text-[var(--text-muted)]">
                    {entry.unit_economics.launch_cash_at_risk_inr.note}
                  </p>
                )}
              </div>
            )}

            <div className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--page-plane)] p-4">
              <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                Inputs that could not be sourced ({econ.unresolved_inputs.length})
              </div>
              <p className="text-sm text-[var(--text-muted)]">
                {econ.unresolved_inputs.map((i) => i.replace(/_/g, " ")).join(" · ")}
              </p>
            </div>

            <details className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4">
              <summary className="cursor-pointer text-sm font-semibold">
                Model assumptions and their sources ({Object.keys(econ.assumptions).length})
              </summary>
              <div className="mt-3 overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Input</TableHead>
                      <TableHead className="text-right">Value</TableHead>
                      <TableHead className="text-right">Range</TableHead>
                      <TableHead>Source</TableHead>
                      <TableHead>Confidence</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {Object.entries(econ.assumptions).map(([key, a]) => (
                      <TableRow key={key}>
                        <TableCell className="font-medium">{key.replace(/_/g, " ")}</TableCell>
                        <TableCell className="text-right tabular-nums">
                          {typeof a.value === "number" ? a.value.toLocaleString() : a.value}
                        </TableCell>
                        <TableCell className="text-right tabular-nums text-[var(--text-muted)]">
                          {a.low !== null && a.low !== undefined ? `${a.low} – ${a.high}` : "—"}
                        </TableCell>
                        <TableCell className="text-xs text-[var(--text-secondary)]">
                          {a.url ? (
                            <a
                              href={a.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="underline text-[var(--series-1)]"
                            >
                              {a.source}
                            </a>
                          ) : (
                            a.source
                          )}
                        </TableCell>
                        <TableCell className="text-xs">{a.confidence}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </details>

            <p className="text-xs text-[var(--text-muted)]">{econ.method_note}</p>
          </div>
        ) : (
          <NotRun what="Phase 4 writes the unit-economics model." />
        )}
      </section>

      {/* ---------- Phase 4: lanes ---------- */}
      <section>
        <h2 className="font-serif text-xl font-semibold">Entry lanes</h2>
        <p className="mb-4 mt-1 max-w-3xl text-sm text-[var(--text-secondary)]">
          Four lanes compared evenly, with the case against the owner&apos;s preferred lane built
          out rather than assumed away.
        </p>
        {entry ? (
          <div className="space-y-6">
            <EntryLanes lanes={entry.entry_lanes} />

            <details className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-4">
              <summary className="cursor-pointer text-sm font-semibold">
                The case against lane (c), the primary lane —{" "}
                {entry.case_against_the_primary_lane.arguments.length} arguments
              </summary>
              <p className="mt-3 text-sm text-[var(--text-secondary)]">
                {entry.case_against_the_primary_lane.summary}
              </p>
              <ol className="mt-3 space-y-3">
                {entry.case_against_the_primary_lane.arguments.map((a, i) => (
                  <li key={i} className="text-sm">
                    <span className="font-semibold">{a.argument}</span>
                    <p className="mt-1 text-[var(--text-secondary)]">{a.detail}</p>
                  </li>
                ))}
              </ol>
              <p className="mt-4 text-sm">
                <span className="font-semibold">Strongest counter-argument for the lane: </span>
                <span className="text-[var(--text-secondary)]">
                  {entry.case_against_the_primary_lane.strongest_counter_argument_for_the_lane}
                </span>
              </p>
            </details>
          </div>
        ) : (
          <NotRun what="Phase 4 writes the entry lanes." />
        )}
      </section>

      {/* ---------- Porter at band level ---------- */}
      <section>
        <h2 className="font-serif text-xl font-semibold">Porter, re-rated at band level</h2>
        <p className="mb-4 mt-1 max-w-3xl text-sm text-[var(--text-secondary)]">
          The category-level read in{" "}
          <Link href="/segment/skincare" className="underline text-[var(--series-1)]">
            skincare
          </Link>{" "}
          is not the band-level read. Rated here against the Rs1,500-3,000 interval specifically.
        </p>
        {porter ? (
          <div className="grid gap-3 md:grid-cols-2">
            <JudgmentCard title="Rivalry" judgment={porter.rivalry} />
            <JudgmentCard title="Buyer power" judgment={porter.buyer_power} />
            <JudgmentCard title="Supplier power" judgment={porter.supplier_power} />
            <JudgmentCard title="Threat of new entrants" judgment={porter.new_entrant_threat} />
            <JudgmentCard title="Substitutes" judgment={porter.substitutes} className="md:col-span-2" />
          </div>
        ) : (
          <NotRun what="Phase 4 writes the band-level Porter read." />
        )}
      </section>

      {/* ---------- Risks & what is still open ---------- */}
      <section>
        <h2 className="mb-4 font-serif text-xl font-semibold">Risks, and what is still open</h2>
        {entry ? (
          <div className="space-y-6">
            <div>
              <h3 className="mb-2 text-sm font-semibold">Risk register</h3>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Risk</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Rationale</TableHead>
                    <TableHead>Mitigation</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {entry.risk_register.map((r, i) => (
                    <TableRow key={i}>
                      <TableCell className="font-medium">{r.risk}</TableCell>
                      <TableCell>
                        <span
                          className="rounded-full px-2 py-0.5 text-xs font-bold text-white"
                          style={{ backgroundColor: SEVERITY_COLOR[r.severity] ?? "var(--text-muted)" }}
                        >
                          {r.severity}
                        </span>
                      </TableCell>
                      <TableCell className="text-[var(--text-secondary)]">{r.rationale}</TableCell>
                      <TableCell className="text-[var(--text-secondary)]">{r.mitigation}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div>
              <h3 className="mb-2 text-sm font-semibold">
                Offline retail — {entry.offline.status}
              </h3>
              <ResearchNeeded what={entry.offline.research_needed} />
              <p className="mt-3 text-sm text-[var(--text-secondary)]">{entry.offline.rationale}</p>
              <ul className="mt-2 list-inside list-disc space-y-0.5 text-xs text-[var(--text-muted)]">
                {entry.offline.what_is_on_file.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="mb-2 text-sm font-semibold">
                Research needed next, in priority order
              </h3>
              <ol className="list-inside list-decimal space-y-1 text-sm text-[var(--text-secondary)]">
                {entry.research_needed_ranked.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ol>
            </div>

            <p className="text-xs text-[var(--text-muted)]">
              Entry artifact generated {entry.generated_at} · namespace {entry.namespace} ·{" "}
              {entry.method_note}
            </p>
          </div>
        ) : (
          <NotRun what="Phase 4 writes the risk register." />
        )}
      </section>
    </div>
  );
}
