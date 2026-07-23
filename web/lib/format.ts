import type { Figure } from "@/types/bundle";

const UNIT_FMT: Record<string, (v: number) => string> = {
  usd_bn: (v) => `US$${v.toLocaleString("en-US", { maximumFractionDigits: 2 })}bn`,
  usd_mn: (v) => `US$${v.toLocaleString("en-US", { maximumFractionDigits: 1 })}mn`,
  usd: (v) => `US$${v.toLocaleString("en-US", { maximumFractionDigits: 2 })}`,
  krw_tn: (v) => `₩${v.toLocaleString("en-US", { maximumFractionDigits: 2 })}tn`,
  inr_cr: (v) => `₹${v.toLocaleString("en-US", { maximumFractionDigits: 0 })}cr`,
  inr_bn: (v) => `₹${v.toLocaleString("en-US", { maximumFractionDigits: 2 })}bn`,
  inr: (v) => `₹${v.toLocaleString("en-US", { maximumFractionDigits: 2 })}`,
  percent: (v) => `${v.toLocaleString("en-US", { maximumFractionDigits: 2 })}%`,
};

/** Renders a Figure's value with its unit, e.g. "US$13.0bn" or "6.61%". */
export function formatFigureValue(fig: Pick<Figure, "value" | "unit">): string {
  const fmt = UNIT_FMT[fig.unit];
  if (fmt) return fmt(fig.value);
  return `${fig.value.toLocaleString("en-US")} ${fig.unit}`;
}

export function formatSegmentName(segment: string): string {
  return segment
    .split("_")
    .map((w) => (w === "and" ? w : w[0].toUpperCase() + w.slice(1)))
    .join(" ");
}
