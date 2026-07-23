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
  MetaBundle,
  OverviewBundle,
  SegmentBundle,
  ShareChartEntry,
  SourceRow,
} from "@/types/bundle";

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
