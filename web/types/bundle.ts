/**
 * The actual shapes of web/public/data/*.json, as emitted by lib/web_export.py.
 * Hand-written (not generated) because _context.py's _fmt() flattens/renames
 * DataPoint fields (source_name -> source, source_url -> url) before they
 * reach the bundle — see web/types/schema.ts for the raw Pydantic shape these
 * are derived from.
 */
import type { Confidence, ValueBasis } from "./schema";

/** One evidence-carrying figure: a value plus everything needed to cite it. */
export interface Figure {
  value: number;
  unit: string;
  currency: "USD" | "KRW" | "INR";
  period: string;
  value_basis: ValueBasis;
  confidence: Confidence;
  source: string;
  url: string | null;
  notes: string | null;
  metric: string;
  tier: "premium" | "masstige" | "mass" | null;
  /** market_size figures only: same value_basis, converted to a common USD-bn
   * scale via lib/transforms/currency.py's pinned rates (see fx_note). */
  value_usd_bn?: number;
  fx_note?: string;
}

export interface Headline {
  geography: "KR" | "IN";
  market_size: Figure | null;
  growth_yoy: Figure | null;
  cagr_forecast: Figure | null;
  per_capita_spend: Figure | null;
  total_export: Figure | null;
}

export interface SegmentRow {
  segment: string;
  size: Figure | null;
  growth: Figure | null;
  cagr: Figure | null;
  export: Figure | null;
}

export interface CompanyShare {
  company: string;
  revenue: number;
  period: string;
  share_pct: number;
  non_pure_play: boolean;
}

export interface Shares {
  geography: "KR" | "IN";
  segment: string;
  currency?: "USD" | "KRW" | "INR";
  unit?: string;
  base?: number;
  shares: CompanyShare[];
  qualifier: string;
}

export interface ReconciliationSide {
  value: number;
  unit: string;
  currency: "USD" | "KRW" | "INR";
  value_basis: ValueBasis;
  confidence?: Confidence;
  period: string;
  source?: string;
}

export interface BottomUp {
  geography: "KR" | "IN";
  segment: string;
  value: number;
  currency: "USD" | "KRW" | "INR";
  unit: string;
  value_basis: ValueBasis;
  companies: Record<string, number>;
  non_pure_play: string[];
  excluded_value_chain: Record<string, string>;
  qualifier: string;
}

export interface Reconciliation {
  top_down: ReconciliationSide | null;
  bottom_up: BottomUp | null;
  gap_pct: number | null;
  publishable: boolean;
  mismatches: string[];
  date: string;
  note?: string;
}

export interface GeographyBundle {
  geography: "KR" | "IN";
  headline: Headline;
  segments: SegmentRow[];
  shares: Shares;
  reconciliation: Reconciliation;
}

export interface OverviewBundle {
  generated: string;
  korea: {
    headline: Headline;
    segments: SegmentRow[];
    shares: Shares;
    reconciliation: Reconciliation;
  };
  india: {
    headline: Headline;
    segments: SegmentRow[];
    shares: Shares;
    reconciliation: Reconciliation;
  };
  corridor: CorridorBundle;
  gaps_md: string;
}

export interface CorridorConduit {
  name: string;
  type: string;
  since?: number;
  notes?: string;
  kr_brands_carried?: Array<Record<string, unknown>>;
}

export interface CorridorBundle {
  headline: Record<string, string>;
  conduits: CorridorConduit[];
  india_side_players: Record<string, unknown>;
  qcommerce: Record<string, unknown>;
  whitespace: string[];
  regulation: Record<string, string>;
  sizing: Array<Figure & { segment: string }>;
  pricing: Array<Figure & { segment: string }>;
  trade: Array<Figure & { segment: string }>;
}

export interface IndiaValueChainSegment {
  segment: string;
  size: Figure | null;
  growth: Figure[];
  imports: { World: Figure | null; Korea: Figure | null; China: Figure | null };
  import_dependence: Figure | null;
  prices: Figure[];
  margins: Figure[];
}

export interface OperatingMargin {
  company: string;
  value: number;
  period: string;
}

export interface IndiaValueChainBundle {
  generated: string;
  segments: IndiaValueChainSegment[];
  operating_margins: OperatingMargin[];
  findings: Record<string, Array<{ text: string; source: string; url: string }>>;
}

export interface SegmentGeoBlock extends SegmentRow {
  points: Figure[];
}

export interface SegmentBundle {
  segment: string;
  KR: SegmentGeoBlock;
  IN: SegmentGeoBlock;
}

export interface SourceRow {
  claim: string;
  value: string;
  unit: string;
  currency: string;
  geography: string;
  segment: string;
  period: string;
  period_type: string;
  value_basis: string;
  source_name: string;
  url: string;
  date_accessed: string;
  confidence: string;
  notes: string;
}

export interface Gap {
  geography: string;
  segment: string;
  metric: string;
  status: string;
  suggested_source: string;
}

export interface ChartFigure extends Figure {
  label: string;
  segment: string;
}

export interface ShareChartEntry extends CompanyShare {
  label: string;
  currency?: string;
  unit?: string;
}

export interface CorridorTradeChartEntry {
  label: string;
  segment: string;
  value_usd_mn: number;
  n_sources: number;
  sources: string[];
}

/** One geography's analyst read, written by /insights (commands/insights.md). */
export interface InsightRead {
  read: string;
  trend: string;
  caveats: string;
}

/**
 * A segment's (or total_bpc's) analyst insight — commentary on figures
 * already in the bundle, never a new source of numbers. Optional: a segment
 * with no data/manual/insights/<id>.json yet simply has none.
 */
export interface Insight {
  segment: string;
  generated_at: string;
  KR: InsightRead;
  IN: InsightRead;
  combined: { read: string };
}

export interface MetaBundle {
  generated_at: string;
  git_sha: string | null;
  segments: Array<{ id: string; name: string }>;
  geographies: Array<{ code: string; name: string; currency: string; fiscal_year: string }>;
  exchange_rates: Array<{ base: string; quote: string; rate: number; date: string; source: string }>;
  confidence_legend: Record<Confidence, string>;
  value_basis_legend: Record<string, string>;
}
