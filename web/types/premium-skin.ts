/**
 * Shapes of the [PREMIUM-SKIN] artifacts — the Rs1,500-3,000 India skincare
 * band thread (docs/premium-skincare-brief.md is the normative spec).
 *
 * Kept out of analysis.ts on purpose: that file mirrors the /entry-analysis
 * layer (commands/entry-analysis.md), these are written by the phase
 * transforms in lib/transforms/premium_skin_*.py and by Phase 4's hand-authored
 * entry artifact. The Judgment vocabulary (rating / rationale / evidence /
 * evidence_strength) is shared, so those types are imported rather than redefined.
 *
 * Every field here is produced upstream. The dashboard renders these values and
 * derives no figure of its own — a number the artifact does not carry is a
 * number this section does not show.
 */

import type { EvidenceStrength, ForceRating, Judgment } from "./analysis";

/* ---------- Phase 1 / Phase 4 price frames: premium_skin_band*.json ---------- */

export interface DiscountDepth {
  median: number;
  mean: number;
  max: number;
  zero_discount_skus: number;
  zero_discount_pct: number;
}

/** Band arithmetic for one cut of the sweep (a platform, a brand group, a format). */
export interface BandStats {
  skus_considered: number;
  in_band_by_mrp: number;
  held_band_at_street: number;
  fell_below_band: number;
  retention_pct: number;
  collapse_pct: number;
  listed_above_band: number;
  entrants_from_above: number;
  in_band_street_population: number;
  discount_depth_pct: DiscountDepth;
}

export interface BandArtifact {
  band: { low_inr: number; high_inr: number; definition: string };
  headline_by_platform: Record<string, BandStats>;
  by_brand_group: Record<string, BandStats>;
  by_format: Record<string, BandStats>;
  /** format -> brand group -> stats. The hero-product cut. */
  hero_formats_by_group: Record<string, Record<string, BandStats>>;
  generated_at: string;
  source_raw_file: string;
  geography: string;
  scope: string;
}

/* ---------- Phase 2 fit + complaints: premium_skin_fit.json ---------- */

/**
 * One complaint theme, counted with negation handling: "no white cast" is
 * praise, not a complaint. Conflating asserted with negated inverts the Phase 2
 * headline, so both are always carried and the UI always shows both.
 */
export interface ThemeCount {
  asserted: number;
  negated: number;
  mentioned: number;
  asserted_pct: number;
  negated_pct: number;
  mentioned_pct: number;
}

export interface ThemeBlock {
  n_reviews: number;
  themes: Record<string, ThemeCount>;
}

export interface FitArtifact {
  coverage: {
    skus_targeted: number;
    skus_with_any_review: number;
    skus_with_zero_reviews: number;
    skus_errored: number;
    reviews_analysed: number;
    reviews_negative_frame: number;
    reviews_most_useful_frame: number;
    reviews_with_declared_skin_tone: number;
    reviews_with_declared_skin_type: number;
    verified_buyer_share_pct: number;
  };
  rating_distribution: {
    skus_with_reviews: number;
    overall: {
      counts: Record<string, number>;
      written_reviews: number;
      negative_1_2_star: number;
      negative_share_pct: number;
    };
  };
  negative_frame: {
    overall: ThemeBlock;
    by_brand_group: Record<string, ThemeBlock>;
    by_format: Record<string, ThemeBlock>;
    by_tone_group: Record<string, ThemeBlock>;
  };
  most_useful_frame: {
    overall: ThemeBlock;
    by_brand_group: Record<string, ThemeBlock>;
    by_format: Record<string, ThemeBlock>;
    by_tone_group: Record<string, ThemeBlock>;
  };
  /** Sunscreen from Korean brands, positive/"most useful" review frame. */
  korean_sunscreen: ThemeBlock;
  korean_sunscreen_negative: ThemeBlock;
  pigmentation_serum_negative: ThemeBlock;
  /** brand group -> self-declared tone label -> review count (incl. "undeclared"). */
  tone_declaration_by_group: Record<string, Record<string, number>>;
  generated_at: string;
  source_raw_file: string;
  geography: string;
  scope: string;
}

/* ---------- Phase 3 demand: premium_skin_demand.json ---------- */

export interface DriverCount {
  driver: string;
  mentioned: number;
  mentioned_pct: number;
  asserted: number;
  negated: number;
}

export interface OriginContrast {
  n_reviews: number;
  korea_origin_mentions: number;
  korea_origin_pct: number;
  korean_aesthetic_mentions: number;
  korean_aesthetic_pct: number;
  other_origin_mentions: number;
  other_origin_pct: number;
  ingredient_actives_pct: number;
  /** null when origin mentions are zero — an undefined ratio, not a zero one. */
  actives_to_origin_ratio: number | null;
}

export interface DemandArtifact {
  corpus: {
    reviews: number;
    skus_targeted: number;
    skus_with_any_review: number;
    by_origin: Record<string, number>;
    by_frame: Record<string, number>;
    by_year: Record<string, number>;
    verified_buyer_share_pct: number;
    median_word_count: number;
    reviews_with_declared_tone: number;
    fields_absent_from_platform: string[];
  };
  most_useful_frame: {
    note: string;
    n_reviews: number;
    driver_ranking: DriverCount[];
    origin_contrast: Record<string, OriginContrast>;
    provenance_only: {
      n_reviews: number;
      origin_citing_reviews: number;
      origin_citing_pct_of_corpus: number;
      origin_plus_mechanism: number;
      origin_only: number;
      origin_only_pct_of_citing: number;
      origin_only_pct_of_corpus: number;
    };
  };
  negative_frame: {
    note: string;
    n_reviews: number;
    driver_ranking: DriverCount[];
  };
  domestic_encroachment: {
    method: string;
    brand_neutral_queries: {
      n_queries: number;
      query_terms: string[];
      by_origin: Record<
        string,
        { in_band_observations: number; distinct_brands: string[] }
      >;
    };
  };
  generated_at: string;
  source_raw_file: string;
  geography: string;
  question: string;
  scope: string;
}

/* ---------- Phase 4 unit economics: premium_skin_unit_economics.json ---------- */

export interface EconAssumption {
  value: number | string;
  unit: string;
  low?: number | string | null;
  high?: number | string | null;
  source: string;
  url?: string;
  confidence: string;
  note?: string;
}

export interface ScenarioSku {
  landed_cogs_inr: number;
  /** COGS as a share of a Rs2,400 MRP — the mid rung of the band. */
  cogs_pct_of_mrp_2400: number;
  breakeven_discount_pct_after_cac: number;
  breakeven_discount_pct_before_cac: number;
  grid: Array<{
    mrp_inr: number;
    discount_pct: number;
    street_inr: number;
    in_band_at_street: boolean;
    gross_margin_pct: number;
    contribution_margin_pct: number;
    contribution_inr: number;
  }>;
}

export interface SensitivityRow {
  input: string;
  /** Swept inputs can be numeric bounds or a labelled pair ("20% (MFN)"). */
  low: number | string;
  high: number | string;
  contribution_margin_at_low_pct: number;
  contribution_margin_at_high_pct: number;
  swing_pp: number;
  /** false = an unresolved input, swept rather than plugged. */
  resolved: boolean;
}

export interface LaunchCash {
  units_per_sku: number;
  cepa_assumed: boolean;
  by_sku: Array<{
    sku: string;
    units: number;
    exw_unit_inr: number;
    goods_inr: number;
    freight_inr: number;
    sticking_duty_inr: number;
    oneoff_dev_test_inr: number;
    total_inr: number;
  }>;
  total_inr?: number;
}

export interface UnitEconomicsArtifact {
  generated_at: string;
  geography: string;
  segment: string;
  lane: string;
  band_inr: number[];
  fx: { inr_per_usd: number; pinned: string; source: string };
  assumptions: Record<string, EconAssumption>;
  unresolved_inputs: string[];
  /** scenario key ("cepa_no_units_1000") -> sku -> economics. */
  scenarios: Record<string, Record<string, ScenarioSku>>;
  decision_sensitivity: SensitivityRow[];
  launch_cash_at_risk: Record<string, LaunchCash>;
  method_note: string;
}

/* ---------- Phase 4 entry read: premium_skin_entry.json ---------- */

export interface EntryLane {
  lane: string;
  label: string;
  /** Free text, not a ForceRating: lanes carry a verdict sentence, not a scale. */
  rating: string;
  rationale: string;
  evidence: string[];
  evidence_strength: EvidenceStrength;
  research_needed?: string | null;
}

export interface BandPorter {
  rivalry: Judgment & { rating: ForceRating };
  buyer_power: Judgment & { rating: ForceRating };
  supplier_power: Judgment & { rating: ForceRating };
  new_entrant_threat: Judgment & { rating: ForceRating };
  substitutes: Judgment & { rating: ForceRating };
  /** overall.rating is a verdict sentence, not LOW/MEDIUM/HIGH. */
  overall: Omit<Judgment, "rating"> & { rating: string };
}

export interface PremiumSkinRisk {
  risk: string;
  severity: ForceRating;
  rationale: string;
  mitigation: string;
}

export interface PriceFrame {
  date: string;
  raw: string;
  nykaa_retention_pct: number;
  tira_retention_pct: number;
  nykaa_zero_discount_pct: number;
  tira_median_discount_pct: number;
}

export interface EntryArtifact {
  generated_at: string;
  geography: string;
  segment: string;
  band_inr: number[];
  namespace: string;
  scope: string;
  method_note: string;
  porter_band_level: BandPorter;
  entry_lanes: EntryLane[];
  case_against_the_primary_lane: {
    summary: string;
    arguments: Array<{ argument: string; detail: string; evidence: string[] }>;
    strongest_counter_argument_for_the_lane: string;
  };
  unit_economics: {
    artifact: string;
    model: string;
    tests: string;
    headline: string;
    launch_cash_at_risk_inr: Record<string, number | string>;
    value_basis_note: string;
  };
  offline: {
    status: string;
    rationale: string;
    what_is_on_file: string[];
    evidence_strength: EvidenceStrength;
    research_needed: string;
    consequence_for_the_verdict: string;
  };
  risk_register: PremiumSkinRisk[];
  price_frame_comparison: {
    note: string;
    frame_1: PriceFrame;
    frame_2: PriceFrame;
    verdict: string;
    corrections_made: string[];
  };
  research_needed_ranked: string[];
}

/* ---------- Qualitative findings: config/{key}_findings.yaml ---------- */

export interface Finding {
  text: string;
  source: string;
  url: string;
}

/** topic -> findings. Every url in here was actually fetched (CLAUDE.md rule 6). */
export type FindingsFile = Record<string, Finding[]>;
