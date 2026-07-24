/**
 * Shapes of web/public/data/analysis/*.json — the /entry-analysis artifacts
 * (commands/entry-analysis.md is the normative spec; extend fields there and
 * here together, never rename). All judgment carries rationale + evidence +
 * evidence_strength; INSUFFICIENT means the UI renders "research needed".
 */

export type EvidenceStrength = "STRONG" | "PARTIAL" | "THIN" | "INSUFFICIENT";
export type ForceRating = "LOW" | "MEDIUM" | "HIGH";

/** One evidence-backed judgment: the unit of the whole analysis layer. */
export interface Judgment {
  rating?: ForceRating | null;
  score?: number | null;
  rationale: string;
  evidence: string[];
  evidence_strength: EvidenceStrength;
  research_needed?: string | null;
}

export interface PorterForce extends Judgment {
  rating: ForceRating | null;
}

export interface PorterGeoRead {
  rivalry: PorterForce;
  buyer_power: PorterForce;
  supplier_power: PorterForce;
  new_entrant_threat: PorterForce;
  substitutes: PorterForce;
  overall: Judgment;
  sub_segment_overrides?: Record<string, Partial<Record<string, PorterForce>>>;
}

export interface PorterArtifact {
  segment: string;
  generated_at: string;
  KR: PorterGeoRead | null;
  IN: PorterGeoRead | null;
}

export interface EntrantEvent {
  actor: string;
  action: string;
  target?: string | null;
  date_or_period: string;
  segments: string[];
  geography: "KR" | "IN" | "KR_to_IN";
  source: string;
  what_it_signals: string;
  corridor: boolean;
}

export interface EntrantsArtifact {
  generated_at: string;
  events: EntrantEvent[];
}

export interface PositioningCell {
  tier: "premium" | "masstige" | "mass";
  role: string;
  players: string[];
  evidence: string[];
}

export interface PositioningSegment {
  segment: string;
  KR: PositioningCell[];
  IN: PositioningCell[];
  note?: string;
}

export interface PositioningArtifact {
  generated_at: string;
  segments: PositioningSegment[];
}

export const SCORECARD_CRITERIA = [
  "market_size_evidence",
  "growth_evidence",
  "competitive_openness",
  "channel_access",
  "regulatory_friction",
  "corridor_tailwind",
] as const;
export type ScorecardCriterion = (typeof SCORECARD_CRITERIA)[number];

export interface ScorecardRow {
  segment: string;
  geography: "KR" | "IN";
  criteria: Record<ScorecardCriterion, Judgment | null>;
  composite: {
    score: number | null;
    based_on: number;
    of: number;
    read: string;
  };
}

export interface ScorecardArtifact {
  generated_at: string;
  method_note: string;
  rows: ScorecardRow[];
}

export interface RtmChannel {
  channel: string;
  known: string;
  entry_implications: string;
  evidence: string[];
  evidence_strength: EvidenceStrength;
}

export interface RtmArtifact {
  geography: "KR" | "IN";
  generated_at: string;
  channels: RtmChannel[];
  summary: string;
}

export interface PriceLadderRung {
  segment: string;
  sub_segment: string | null;
  tier: string;
  price_range: string;
  examples: string[];
  evidence: string[];
}

export interface PriceLadderArtifact {
  generated_at: string;
  geography: "IN";
  rungs: PriceLadderRung[];
  masstige_gap_note: string;
}

export interface RegulatoryStep {
  jurisdiction: "IN" | "KR";
  step: string;
  what: string;
  cost: string;
  timeline: string;
  evidence: string[];
  evidence_strength: EvidenceStrength;
}

export interface RegulatoryArtifact {
  generated_at: string;
  steps: RegulatoryStep[];
  summary: string;
}

export interface DemandDriver {
  driver: string;
  geography: "KR" | "IN";
  segments_touched: string[];
  evidence: string[];
  read: string;
}

export interface DemandArtifact {
  generated_at: string;
  drivers: DemandDriver[];
}

export interface ValueChainArtifact {
  generated_at: string;
  sections: Array<{
    topic: string;
    read: string;
    evidence: string[];
    evidence_strength: EvidenceStrength;
  }>;
}

export interface CorridorVectorArtifact {
  generated_at: string;
  read: string;
  conduit_ranking: Array<{
    conduit: string;
    case: string;
    evidence: string[];
    evidence_strength: EvidenceStrength;
  }>;
  whitespace_read: string;
  friction_read: string;
}

export interface CompanyProfile {
  slug: string;
  name: string;
  geography: "KR" | "IN";
  role: string;
  segments: string[];
  figures: Array<{
    metric: string;
    value: number;
    unit: string;
    period: string;
    value_basis: string;
    confidence: string;
    source: string;
  }>;
  recent_moves: string[];
  corridor_involvement: string | null;
  read: string;
}

export interface RiskItem {
  risk: string;
  geography: "KR" | "IN" | "BOTH";
  severity: ForceRating;
  rationale: string;
  evidence: string[];
  mitigation: string;
}

export interface RiskArtifact {
  generated_at: string;
  risks: RiskItem[];
}

export interface EntryModeRead {
  segment: string;
  geography: "KR" | "IN";
  mode: "build" | "partner" | "import_corridor" | "acquire" | null;
  rationale: string;
  alternatives_considered: string;
  evidence: string[];
  evidence_strength: EvidenceStrength;
  research_needed?: string | null;
}

export interface EntryModeArtifact {
  generated_at: string;
  reads: EntryModeRead[];
}
