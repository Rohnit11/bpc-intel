import fs from "node:fs";
import path from "node:path";
import { cache } from "react";
import type {
  ChartFigure,
  CorridorBundle,
  CorridorTradeChartEntry,
  Gap,
  GeographyBundle,
  IndiaValueChainBundle,
  Insight,
  MetaBundle,
  OverviewBundle,
  SegmentBundle,
  ShareChartEntry,
  SourceRow,
} from "@/types/bundle";
import type { FindingsFile } from "@/types/premium-skin";

const DATA_DIR = path.join(process.cwd(), "public", "data");

function readJson<T>(relPath: string): T {
  const full = path.join(DATA_DIR, relPath);
  const raw = fs.readFileSync(full, "utf-8");
  return JSON.parse(raw) as T;
}

export const getOverview = cache((): OverviewBundle => readJson("overview.json"));
export const getKorea = cache((): GeographyBundle => readJson("korea.json"));
export const getIndia = cache((): GeographyBundle => readJson("india.json"));
export const getCorridor = cache((): CorridorBundle => readJson("corridor.json"));
export const getIndiaValueChain = cache((): IndiaValueChainBundle =>
  readJson("india_value_chain.json"),
);
export const getSources = cache((): SourceRow[] => readJson("sources.json"));
export const getGaps = cache((): Gap[] => readJson("gaps.json"));
export const getMeta = cache((): MetaBundle => readJson("meta.json"));

export const getSegment = cache((id: string): SegmentBundle =>
  readJson(`segments/${id}.json`),
);

export function listSegmentIds(): string[] {
  const dir = path.join(DATA_DIR, "segments");
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""));
}

/** The analyst read for a segment (or "total_bpc"), if /insights has been run
 * for it yet — null otherwise. Never throws on a missing file. */
export const getInsight = cache((id: string): Insight | null => {
  const full = path.join(DATA_DIR, "insights", `${id}.json`);
  if (!fs.existsSync(full)) return null;
  return JSON.parse(fs.readFileSync(full, "utf-8")) as Insight;
});

/** An /entry-analysis artifact by bundle-relative id (e.g. "porter_skincare",
 * "entry_scorecard", "profiles/amorepacific") — null until it's been
 * generated. Pages must render a "not yet analyzed" state on null, never 404. */
export const getAnalysisArtifact = cache(<T>(rel: string): T | null => {
  const full = path.join(DATA_DIR, "analysis", `${rel}.json`);
  if (!fs.existsSync(full)) return null;
  return JSON.parse(fs.readFileSync(full, "utf-8")) as T;
});

/** A qualitative findings file by key ("korea", "premium_skin_fit"), as exported
 * from config/{key}_findings.yaml — null if that file isn't in the bundle. */
export const getFindings = cache((key: string): FindingsFile | null => {
  const full = path.join(DATA_DIR, "findings", `${key}.json`);
  if (!fs.existsSync(full)) return null;
  return JSON.parse(fs.readFileSync(full, "utf-8")) as FindingsFile;
});

/** All artifact ids currently in the bundle (recursive, "/"-joined). */
export function listAnalysisArtifacts(): string[] {
  const dir = path.join(DATA_DIR, "analysis");
  if (!fs.existsSync(dir)) return [];
  const out: string[] = [];
  const walk = (sub: string) => {
    for (const entry of fs.readdirSync(path.join(dir, sub), { withFileTypes: true })) {
      const rel = sub ? `${sub}/${entry.name}` : entry.name;
      if (entry.isDirectory()) walk(rel);
      else if (entry.name.endsWith(".json")) out.push(rel.replace(/\.json$/, ""));
    }
  };
  walk("");
  return out.sort();
}

export const getKoreaExportsChart = cache((): ChartFigure[] =>
  readJson("charts/korea_exports_by_segment.json"),
);

export const getIndiaSharesChart = cache((): ShareChartEntry[] =>
  readJson("charts/india_listed_shares.json"),
);

export const getIndiaSharesQualifier = cache((): string =>
  readJson("charts/india_shares_qualifier.json"),
);

export const getCorridorTradeChart = cache((): CorridorTradeChartEntry[] =>
  readJson("charts/corridor_trade_by_segment.json"),
);
