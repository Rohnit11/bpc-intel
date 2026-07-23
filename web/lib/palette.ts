import type { Confidence, ValueBasis } from "@/types/schema";

/**
 * Value-basis -> categorical slot, in the dataviz skill's fixed order
 * (never cycled/reassigned). Eight bases map onto the eight validated slots.
 */
export const VALUE_BASIS_COLOR: Record<ValueBasis, string> = {
  RETAIL: "var(--series-1)",
  NET_REALISATION: "var(--series-2)",
  WHOLESALE: "var(--series-3)",
  EXPORT_FOB: "var(--series-4)",
  PRODUCTION: "var(--series-5)",
  IMPORT_CIF: "var(--series-6)",
  MRP: "var(--series-7)",
  NA: "var(--series-8)",
};

export const VALUE_BASIS_LABEL: Record<ValueBasis, string> = {
  RETAIL: "Retail",
  NET_REALISATION: "Net realisation",
  WHOLESALE: "Wholesale",
  EXPORT_FOB: "Export (FOB)",
  PRODUCTION: "Production",
  IMPORT_CIF: "Import (CIF)",
  MRP: "MRP",
  NA: "N/A",
};

/** Confidence -> status role (fixed, never themed). */
export const CONFIDENCE_COLOR: Record<Confidence, string> = {
  HIGH: "var(--status-good)",
  MEDIUM: "var(--status-warning)",
  LOW: "var(--status-muted)",
  ESTIMATE: "var(--series-7)",
};

export const SERIES_COLORS = [
  "var(--series-1)",
  "var(--series-2)",
  "var(--series-3)",
  "var(--series-4)",
  "var(--series-5)",
  "var(--series-6)",
  "var(--series-7)",
  "var(--series-8)",
];
