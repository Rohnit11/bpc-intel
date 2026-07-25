import fs from "node:fs";
import path from "node:path";
import { cache } from "react";

/**
 * Structured-first retrieval over the committed chat index.
 *
 * Deliberately no embeddings/vector store: the corpus is ~175k tokens and
 * already segmented by topic, so IDF-weighted term matching over (a) fully
 * provenanced facts and (b) prose passages beats chunked vector search here —
 * and critically, a fact is returned INTACT with its value_basis/confidence/
 * source rather than paraphrased, which is what the evidence rules require.
 */

export interface IndexedFact {
  id: string;
  kind: "fact";
  geography: "KR" | "IN";
  segment: string;
  sub_segment: string | null;
  metric: string;
  value: number;
  unit: string;
  currency: string;
  period: string;
  value_basis: string;
  confidence: string;
  source: string;
  url: string | null;
  notes: string | null;
  text: string;
}

export interface IndexedPassage {
  id: string;
  kind: "passage";
  title: string;
  text: string;
  source_ref: string;
  segment?: string;
  geography?: string;
}

interface ChatIndex {
  generated_at: string;
  facts: IndexedFact[];
  passages: IndexedPassage[];
}

const STOPWORDS = new Set([
  "the", "a", "an", "is", "are", "was", "were", "of", "for", "to", "in", "on",
  "and", "or", "what", "whats", "how", "why", "which", "who", "when", "where",
  "me", "my", "we", "our", "you", "your", "it", "its", "this", "that", "these",
  "do", "does", "did", "can", "could", "should", "would", "will", "about",
  "with", "from", "by", "at", "as", "be", "been", "have", "has", "had", "i",
  "tell", "give", "show", "explain", "much", "many", "there", "their", "they",
]);

/** Domain synonyms → index vocabulary. Cheap, high-yield query expansion. */
const SYNONYMS: Record<string, string[]> = {
  korea: ["kr", "korean", "south"],
  korean: ["kr", "korea"],
  kr: ["korea", "korean"],
  india: ["in", "indian"],
  indian: ["in", "india"],
  size: ["market_size", "market"],
  market: ["market_size"],
  growth: ["growth_yoy", "cagr_forecast"],
  cagr: ["cagr_forecast", "forecast"],
  forecast: ["cagr_forecast"],
  revenue: ["revenue", "net_realisation"],
  share: ["market_share", "channel_share"],
  export: ["export_value", "export_fob"],
  exports: ["export_value", "export_fob"],
  import: ["import_value", "import_cif"],
  imports: ["import_value", "import_cif"],
  price: ["retail_price", "mrp"],
  pricing: ["retail_price", "mrp", "price"],
  margin: ["gross_margin", "operating_margin", "trade_margin"],
  margins: ["gross_margin", "operating_margin", "trade_margin"],
  sunscreen: ["sun_care", "sun", "care", "sun_protection"],
  suncare: ["sun_care"],
  skincare: ["skincare", "skin"],
  serum: ["serums_ampoules", "serums"],
  serums: ["serums_ampoules"],
  mask: ["sheet_masks", "masks"],
  masks: ["sheet_masks"],
  toner: ["toners_essences"],
  cleanser: ["facial_cleansers"],
  moisturiser: ["facial_moisturisers"],
  moisturizer: ["facial_moisturisers"],
  makeup: ["colour_cosmetics", "colour", "cosmetics"],
  cosmetics: ["colour_cosmetics"],
  lipstick: ["lip_colour", "colour_cosmetics"],
  hair: ["hair_care"],
  shampoo: ["shampoo", "hair_care"],
  scalp: ["scalp_care", "hair_care"],
  fragrance: ["fragrances", "perfume"],
  perfume: ["fragrances"],
  derma: ["dermocosmetics"],
  dermatology: ["dermocosmetics"],
  men: ["mens_grooming", "mens_skincare"],
  mens: ["mens_grooming"],
  oral: ["oral_care"],
  baby: ["baby_child"],
  deodorant: ["deodorants"],
  kbeauty: ["corridor", "k-beauty"],
  corridor: ["corridor", "k-beauty"],
  channel: ["channel_share", "rtm", "route"],
  distribution: ["channel_share", "rtm"],
  regulation: ["cdsco", "mfds", "regulatory"],
  regulatory: ["cdsco", "mfds"],
  competitor: ["rivalry", "porter", "share"],
  competition: ["rivalry", "porter"],
  entry: ["entry", "scorecard", "entry_mode"],
  risk: ["risk", "severity"],
};

function tokenize(s: string): string[] {
  const out: string[] = [];
  for (const raw of s.toLowerCase().split(/[^a-z0-9_]+/)) {
    if (!raw) continue;
    // Segment/artifact ids are snake_case ("sun_care", "entry_mode") but people
    // type them with spaces ("sun care"). Emit BOTH the compound token and its
    // parts, so an id matches whichever form the question used — without this,
    // every multi-word segment is unreachable by natural-language query.
    if (raw.includes("_")) {
      out.push(raw, ...raw.split("_"));
    } else {
      out.push(raw);
    }
  }
  return out.filter((t) => t.length > 1 && !STOPWORDS.has(t));
}

function expand(tokens: string[]): string[] {
  const out = new Set(tokens);
  for (const t of tokens) for (const syn of SYNONYMS[t] ?? []) out.add(syn);
  return [...out];
}

const loadIndex = cache((): ChatIndex => {
  const p = path.join(process.cwd(), "public", "data", "chat_index.json");
  return JSON.parse(fs.readFileSync(p, "utf-8")) as ChatIndex;
});

/** Every token that appears anywhere in the corpus. Used to test whether the
 * user's own words are represented at all — see coverage() below. */
const loadVocab = cache((): Set<string> => {
  const idx = loadIndex();
  const vocab = new Set<string>();
  for (const f of idx.facts) for (const t of tokenize(f.text)) vocab.add(t);
  for (const p of idx.passages) {
    for (const t of tokenize(`${p.title} ${p.text}`)) vocab.add(t);
  }
  return vocab;
});

/**
 * Fraction of the user's ORIGINAL words (pre-synonym-expansion) that exist in
 * the corpus at all.
 *
 * Without this, one incidental domain word carries an entirely out-of-scope
 * question past the relevance floor: "price of bitcoin mining rigs in brazil"
 * expands "price" into retail_price/mrp and matches hundreds of facts, while
 * bitcoin/mining/rigs/brazil match nothing. Coverage catches that — the
 * distinctive terms of a genuine question are in the vocabulary; the
 * distinctive terms of an off-topic one are not.
 */
function coverage(originalTokens: string[]): number {
  if (originalTokens.length === 0) return 0;
  const vocab = loadVocab();
  const hits = originalTokens.filter((t) => vocab.has(t)).length;
  return hits / originalTokens.length;
}

interface Scored<T> {
  item: T;
  score: number;
}

/** IDF-weighted overlap. Docs are short, so length normalisation is light. */
/**
 * Which geography the question is explicitly about, or null if it doesn't say.
 * Both records carry a structured `geography` field, so an explicit "India"
 * should be treated as a constraint rather than as one more low-IDF word that
 * happens to appear in Korean records too.
 */
function queryGeography(queryTokens: string[]): "KR" | "IN" | null {
  const t = new Set(queryTokens);
  const kr = t.has("korea") || t.has("korean") || t.has("kr");
  const inn = t.has("india") || t.has("indian");
  if (kr === inn) return null; // neither, or both — no constraint
  return kr ? "KR" : "IN";
}

/**
 * Segment ids the question names in full, e.g. "sun care" -> sun_care.
 * Requires every part to be present, so "sun care" does not match oral_care /
 * hair_care on the shared word "care" — which it otherwise does, since "care"
 * is one of the most common tokens in the corpus.
 */
function querySegments(queryTokens: string[], docs: { segment?: string }[]): Set<string> {
  const q = new Set(queryTokens);
  const hits = new Set<string>();
  for (const seg of new Set(docs.map((d) => d.segment).filter(Boolean) as string[])) {
    const parts = seg.split("_");
    if (parts.every((p) => q.has(p))) hits.add(seg);
  }
  return hits;
}

function scoreDocs<
  T extends { text: string; title?: string; geography?: string; segment?: string },
>(docs: T[], queryTokens: string[]): Scored<T>[] {
  const wantGeo = queryGeography(queryTokens);
  const wantSegs = querySegments(queryTokens, docs);
  const N = docs.length;
  const docTokens = docs.map((d) => tokenize(`${d.title ?? ""} ${d.text}`));
  const df = new Map<string, number>();
  for (const toks of docTokens) {
    for (const t of new Set(toks)) df.set(t, (df.get(t) ?? 0) + 1);
  }
  const scored: Scored<T>[] = [];
  for (let i = 0; i < docs.length; i++) {
    const toks = docTokens[i];
    if (toks.length === 0) continue;
    const tf = new Map<string, number>();
    for (const t of toks) tf.set(t, (tf.get(t) ?? 0) + 1);
    let score = 0;
    for (const q of queryTokens) {
      const f = tf.get(q);
      if (!f) continue;
      const idf = Math.log(1 + N / (1 + (df.get(q) ?? 0)));
      score += idf * (f / (f + 1.2)); // saturating tf
    }
    if (score <= 0) continue;
    // Length normalisation, but gentler than sqrt(n): a judgment's passage is
    // long precisely BECAUSE it carries more evidence, and sqrt penalised the
    // best-evidenced records hard enough to push them under the cut (the India
    // sun-care entry mode — STRONG, import_corridor — ranked 12th while the
    // Korean "research needed" stub ranked 4th).
    let final = score / Math.pow(toks.length, 0.35);
    // Honour an explicit geography in the question. Same-segment records for
    // the other geography are near-identical lexically, so without this the
    // wrong one wins on incidental term overlap.
    const geo = (docs[i] as { geography?: string }).geography;
    if (wantGeo && geo) final *= geo === wantGeo ? 1.35 : 0.45;
    // Same for an explicitly named segment: "sun care" must not lose to
    // "oral care" on the shared token "care".
    const seg = (docs[i] as { segment?: string }).segment;
    if (wantSegs.size > 0 && seg) final *= wantSegs.has(seg) ? 1.6 : 0.5;
    scored.push({ item: docs[i], score: final });
  }
  return scored.sort((a, b) => b.score - a.score);
}

export interface RetrievalResult {
  facts: IndexedFact[];
  passages: IndexedPassage[];
  generatedAt: string;
  /** True when nothing scored above the floor — the caller should treat the
   * question as out-of-corpus rather than answering from a weak match. */
  empty: boolean;
}

export function retrieve(
  query: string,
  opts: { maxFacts?: number; maxPassages?: number } = {},
): RetrievalResult {
  const { maxFacts = 24, maxPassages = 10 } = opts;
  const idx = loadIndex();
  const originalTokens = tokenize(query);
  const qTokens = expand(originalTokens);

  if (originalTokens.length === 0) {
    return { facts: [], passages: [], generatedAt: idx.generated_at, empty: true };
  }

  // Out-of-scope guard: if most of what the user actually typed doesn't appear
  // anywhere in the corpus, don't let synonym expansion manufacture a match.
  const MIN_COVERAGE = 0.34;
  if (coverage(originalTokens) < MIN_COVERAGE) {
    return { facts: [], passages: [], generatedAt: idx.generated_at, empty: true };
  }

  const facts = scoreDocs(idx.facts, qTokens).slice(0, maxFacts);
  const passages = scoreDocs(idx.passages, qTokens).slice(0, maxPassages);

  // Relevance floor: a single incidental term match shouldn't count as a hit.
  const FLOOR = 0.15;
  const keptFacts = facts.filter((f) => f.score >= FLOOR).map((f) => f.item);
  const keptPassages = passages.filter((p) => p.score >= FLOOR).map((p) => p.item);

  return {
    facts: keptFacts,
    passages: keptPassages,
    generatedAt: idx.generated_at,
    empty: keptFacts.length === 0 && keptPassages.length === 0,
  };
}

/** Renders retrieved context for the model — facts keep full provenance so
 * the answer can cite basis/confidence/source without inventing them. */
export function formatContext(r: RetrievalResult): string {
  const lines: string[] = [];

  if (r.facts.length > 0) {
    lines.push("## SOURCED DATA POINTS");
    lines.push(
      "Each line is a governed DataPoint. Cite value, unit, period, value_basis, confidence and source exactly as given.",
    );
    for (const f of r.facts) {
      const sub = f.sub_segment ? ` / ${f.sub_segment}` : "";
      lines.push(
        `- [${f.geography}] ${f.segment}${sub} · ${f.metric} = ${f.value} ${f.unit} ` +
          `(${f.currency}) · period ${f.period} · basis ${f.value_basis} · confidence ${f.confidence} ` +
          `· source: ${f.source}${f.url ? ` (${f.url})` : ""}` +
          `${f.notes ? ` · notes: ${f.notes}` : ""}`,
      );
    }
  }

  if (r.passages.length > 0) {
    lines.push("\n## ANALYSIS & COMMENTARY (interpretation, not raw figures)");
    for (const p of r.passages) {
      lines.push(`- ${p.title} [${p.source_ref}]: ${p.text}`);
    }
  }

  if (lines.length === 0) lines.push("(No matching data found in the repository.)");
  return lines.join("\n");
}
