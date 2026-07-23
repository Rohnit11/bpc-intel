/**
 * AUTO-GENERATED from lib/transforms/schema.py (the Pydantic DataPoint /
 * SegmentFile models) via lib/web_export.py + web/scripts/gen-schema-ts.mjs.
 * Do not hand-edit — a schema change should surface here as a compile error,
 * not a silent bug. See web/types/bundle.ts for the flattened "Figure" shape
 * actually shipped in the JSON bundle (produced by _context.py's _fmt()).
 */

export type Geography = "KR" | "IN";
export type Segment = string;
export type LastUpdated = string;
export type Geography1 = "KR" | "IN";
export type Segment1 = string;
export type SubSegment = string | null;
export type Metric =
  | "market_size"
  | "growth_yoy"
  | "cagr_historical"
  | "cagr_forecast"
  | "market_share"
  | "revenue"
  | "export_value"
  | "production_value"
  | "channel_share"
  | "per_capita_spend"
  | "penetration_rate"
  | "import_value"
  | "import_dependence"
  | "retail_price"
  | "gross_margin"
  | "operating_margin"
  | "adspend_ratio"
  | "trade_margin";
export type Value = number;
export type Unit = string;
export type Currency = "USD" | "KRW" | "INR";
export type Period = string;
export type PeriodType = "CY" | "FY" | "H1" | "H2" | "Q1" | "Q2" | "Q3" | "Q4" | "range";
export type ValueBasis =
  "RETAIL" | "NET_REALISATION" | "WHOLESALE" | "EXPORT_FOB" | "PRODUCTION" | "IMPORT_CIF" | "MRP" | "NA";
export type Tier = ("premium" | "masstige" | "mass") | null;
export type SourceName = string;
export type SourceUrl = string | null;
export type DateAccessed = string;
export type Confidence = "HIGH" | "MEDIUM" | "LOW" | "ESTIMATE";
export type Methodology = string | null;
export type Notes = string | null;
export type DataPoints = DataPoint[];

/**
 * One file per segment × geography in data/processed/.
 */
export interface SegmentFile {
  geography: Geography;
  segment: Segment;
  last_updated: LastUpdated;
  data_points: DataPoints;
}
export interface DataPoint {
  geography: Geography1;
  segment: Segment1;
  sub_segment?: SubSegment;
  metric: Metric;
  value: Value;
  unit: Unit;
  currency: Currency;
  period: Period;
  period_type: PeriodType;
  value_basis: ValueBasis;
  tier?: Tier;
  source_name: SourceName;
  source_url?: SourceUrl;
  date_accessed: DateAccessed;
  confidence: Confidence;
  methodology?: Methodology;
  notes?: Notes;
}
