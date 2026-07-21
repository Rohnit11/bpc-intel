# BPC-INTEL — Build Specification
## Beauty & Personal Care Market Intelligence System: South Korea × India
### Production-Grade Autonomous Build Spec for Claude Code

---

## 0. ABOUT THIS DOCUMENT

**This is the single source of truth for building the `bpc-intel` system.** Feed this entire file to Claude Code at the start of each session. Claude Code should read it fully before writing any code, resume from the last completed phase, and continue building autonomously — pausing ONLY at the decision points explicitly marked `⏸️ CHECKPOINT`.

**Owner:** Rohnit Aggarwal
**Platform:** Windows 11, Claude Code at `C:\Users\agraw\`
**Project root:** `C:\Users\agraw\Documents\bpc-intel\`
**Quality standard:** Production-grade. No stubs, no placeholder data, no `# TODO` blocks, no demo/mock data anywhere. Every function either works or does not exist yet. Every number in the system traces to a source URL or a script that fetched it.

---

## 1. PROJECT CONTEXT

### 1.1 What this system does
A market intelligence system focused exclusively on Beauty & Personal Care (BPC) across South Korea and India. It maintains a living, structured knowledge base covering 12 sub-segments × 2 geographies, fetches and normalises data from free public sources, accepts manual data drops from subscription databases (Euromonitor Passport, Capital IQ Pro, etc.), and generates consulting-grade snapshot reports on command.

### 1.2 What this system is NOT
- Not a generic multi-industry research tool (scope is locked to BPC × Korea × India)
- Not a web app or dashboard (it is a CLI-driven Claude Code project)
- Not dependent on any single paid data source (runs on free sources; paid sources are additive)
- Not a chatbot — the repo is the deliverable, not the conversation

### 1.3 Baseline knowledge
The system ships with a pre-researched baseline report (the deep research output included below as `data/baseline/deep-research-report.md`). This report contains ~10,000 words of sourced market intelligence. The system treats it as ground truth for claims that carry source citations, and as directional guidance for claims that don't. Every baseline claim should eventually be either confirmed by a fetcher script or flagged in the gaps register.

### 1.4 Key prior decisions (do not revisit)
- The Euromonitor-style 12-segment taxonomy is the canonical structure (see §3.2)
- "Model never types a number" — every quantitative claim comes from a fetcher, a manual data drop, or is explicitly labelled `[ESTIMATE]` with methodology
- India requires MRP vs. net-realisation normalisation (25–45% gap) — this is non-optional
- Korea requires retail vs. wholesale vs. export value distinction — these are three separate measures
- Fiscal year convention: India uses FY24 = Apr 2023–Mar 2024; Korea uses calendar year
- Currency: always record original currency + USD equivalent with exchange rate and date noted
- Tavily is already connected globally to Claude Code — do NOT add it to `.mcp.json`

---

## 2. ARCHITECTURE

### 2.1 Directory structure

```
bpc-intel/
├── CLAUDE.md                        # Constitution (§3 of this spec, verbatim)
├── BUILD-SPEC.md                    # This file (copy of the build spec for reference)
├── .mcp.json                        # MCP server connections
├── .claude/
│   └── settings.json                # Hooks configuration
│
├── config/
│   ├── taxonomy.yaml                # 12 sub-segments, locked definitions
│   ├── sources.yaml                 # Every validated source, per geography
│   ├── companies.yaml               # Named players per segment × geography
│   ├── exchange_rates.yaml          # Pinned FX rates with dates
│   └── access_status.yaml           # HEC database access status (user fills in)
│
├── lib/
│   ├── __init__.py
│   ├── fetchers/                    # Scripts that pull from free sources
│   │   ├── __init__.py
│   │   ├── korea_mfds.py            # MFDS production/export data
│   │   ├── korea_dart.py            # DART (Korean EDGAR) — company filings
│   │   ├── india_screener.py        # Screener.in — listed company financials
│   │   ├── india_mca.py             # MCA/Tofler — private company basics
│   │   ├── trade_comtrade.py        # UN Comtrade — bilateral trade flows
│   │   ├── news_tavily.py           # Tavily — structured news search
│   │   ├── academic_openalex.py     # OpenAlex — research papers
│   │   ├── trends_google.py         # Google Trends — demand signals
│   │   └── qcommerce_tracker.py     # Blinkit/Zepto price+assortment snapshots
│   │
│   ├── ingest/                      # Manual data drop processors
│   │   ├── __init__.py
│   │   ├── passport_csv.py          # Euromonitor Passport CSV → standard schema
│   │   ├── capitaliq_csv.py         # Capital IQ export → standard schema
│   │   ├── statista_csv.py          # Statista export → standard schema
│   │   └── generic_csv.py           # Freeform CSV with column mapping
│   │
│   ├── transforms/                  # Data normalisation
│   │   ├── __init__.py
│   │   ├── currency.py              # Multi-currency conversion with pinned rates
│   │   ├── mrp_normalise.py         # MRP ↔ net realisation (India-specific)
│   │   ├── value_basis.py           # Retail vs wholesale vs export tagging
│   │   ├── fiscal_year.py           # FY↔CY alignment
│   │   └── schema.py               # Canonical data schemas + validators
│   │
│   ├── analysis/                    # Analytical computations
│   │   ├── __init__.py
│   │   ├── sizing.py                # Top-down + bottom-up reconciliation
│   │   ├── growth.py                # CAGR, YoY, indexed growth calculations
│   │   ├── share.py                 # Market share computation with qualifiers
│   │   └── gaps.py                  # Gaps register builder
│   │
│   └── reports/                     # Report generation
│       ├── __init__.py
│       ├── snapshot.py              # Full report builder (Markdown → PDF-ready)
│       ├── segment_brief.py         # Single-segment one-pager
│       ├── comparison.py            # Korea vs India comparative tables
│       ├── charts.py                # matplotlib chart generation
│       └── templates/               # Jinja2 report templates
│           ├── full_report.md.j2
│           ├── segment_brief.md.j2
│           └── comparison.md.j2
│
├── data/
│   ├── baseline/
│   │   └── deep-research-report.md  # The pre-researched report (provided)
│   ├── raw/                         # Raw fetcher outputs (timestamped JSON)
│   ├── processed/                   # Normalised, schema-conforming JSON
│   ├── manual/                      # User-dropped files (Passport CSVs, etc.)
│   └── sources.csv                  # Master source ledger (every cited number)
│
├── reports/
│   ├── latest/                      # Most recent generated report + charts
│   └── archive/                     # Timestamped past reports
│
├── tests/                           # Validation tests
│   ├── test_schemas.py              # Schema conformance
│   ├── test_transforms.py           # Currency, MRP, fiscal year
│   ├── test_fetchers.py             # Fetcher smoke tests (do they return data?)
│   └── test_reconciliation.py       # Top-down vs bottom-up gap checks
│
├── commands/                        # Claude Code slash commands
│   ├── refresh.md                   # /refresh — re-fetch all live sources
│   ├── report.md                    # /report — generate full snapshot
│   ├── segment.md                   # /segment <name> — single segment deep-dive
│   ├── compare.md                   # /compare <metric> — KR vs IN
│   ├── gaps.md                      # /gaps — show the gaps register
│   ├── ingest.md                    # /ingest <filepath> — process a manual drop
│   └── verify.md                    # /verify — cross-check all sourced claims
│
└── requirements.txt                 # Python dependencies (pinned versions)
```

### 2.2 `.mcp.json`

```json
{
  "mcpServers": {
    "openalex": {
      "command": "npx",
      "args": ["-y", "openalex-research-mcp"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

**Note:** Tavily is already connected globally. Do NOT add it here. The `news_tavily.py` fetcher calls Tavily via Claude Code's built-in Tavily MCP, not via a separate server.

### 2.3 Hooks (`.claude/settings.json`)

```json
{
  "hooks": {
    "pre-commit": {
      "command": "python -c \"import sys; [sys.exit(1) for line in open(sys.argv[1]) if any(w in line.lower() for w in ['approximately','estimated at','roughly','around','about']) and '[ESTIMATE]' not in line and 'sources.csv' not in sys.argv[1] and line.strip().startswith(('$','₹','₩','KRW','INR','USD','Rs','US$'))]\" %f",
      "description": "Block unsourced quantitative claims — any line starting with a currency marker that contains hedging language without an [ESTIMATE] tag is rejected"
    }
  }
}
```

### 2.4 Technology stack

- **Python 3.11+** (confirm installed; `python --version`)
- **Dependencies** (pin in `requirements.txt`):
  ```
  requests>=2.31.0
  pyyaml>=6.0.1
  pandas>=2.1.0
  matplotlib>=3.8.0
  jinja2>=3.1.2
  pydantic>=2.5.0
  python-dateutil>=2.8.2
  ```
- **No database.** All state is YAML/JSON/CSV files in `data/`. This keeps the system portable, inspectable, and git-friendly.
- **No web framework.** This is a CLI/Claude-Code-driven system, not a web app.

---

## 3. CLAUDE.md — THE CONSTITUTION

Copy this verbatim into `bpc-intel/CLAUDE.md`:

```markdown
# bpc-intel

Beauty & Personal Care market intelligence system: South Korea × India.
The repo is the deliverable, not the chat. Write to files.

## Scope lock
This system covers Beauty & Personal Care ONLY, across South Korea and India ONLY.
The taxonomy is defined in config/taxonomy.yaml. Do not add segments or geographies
without updating taxonomy.yaml first.

## Non-negotiable evidence rules

1. NEVER state a market size, share, growth rate, price, or revenue from your own
   knowledge. Every number comes from: (a) a fetcher script in lib/fetchers/,
   (b) a manual data drop in data/manual/, (c) the baseline report in
   data/baseline/ with its original source citation preserved, or (d) is labelled
   [ESTIMATE] with methodology, assumptions, and sensitivity range shown.

2. Every quantitative claim gets a row in data/sources.csv:
   claim | value | unit | currency | geography | segment | period | period_type |
   value_basis | source_name | url | date_accessed | confidence | notes

3. VALUE BASIS is mandatory on every number:
   - RETAIL = consumer sell-through (MRP-inclusive for India)
   - NET_REALISATION = company revenue (ex-trade margins, for India)
   - WHOLESALE = trade/distributor price
   - EXPORT_FOB = customs/FOB value (Korea exports)
   - PRODUCTION = factory-gate output value
   Never compare numbers on different bases without normalising first.

4. CURRENCY: always record original currency (KRW / INR / USD) AND a USD
   equivalent. Pin the exchange rate used in config/exchange_rates.yaml.
   Never use a bare number without currency.

5. If a script in lib/ can fetch it, RUN THE SCRIPT. Do not reason to the answer.

6. Never cite a URL you have not actually fetched and verified.

7. Market sizes must be reconciled TOP-DOWN and BOTTOM-UP where data permits.
   Gap >20% = do not publish; find the definitional mismatch and document it.

## India-specific rules (non-optional)

8. ORGANISED vs UNORGANISED: state which every India number covers.
9. FISCAL YEARS: always write FY24 (Apr-23 to Mar-24), never "2024" for Indian
   company data. Korean data uses calendar year — write CY2024 or 2024.
10. MRP vs NET REALISATION: MRP includes 25-45% trade margin. The normalisation
    function is lib/transforms/mrp_normalise.py. Use it before any reconciliation.

## Korea-specific rules (non-optional)

11. RETAIL vs EXPORT vs PRODUCTION: Korea's domestic retail (~US$13bn),
    export FOB (~US$11.4bn), and production value (KRW 17.9tn) are THREE
    DIFFERENT measures. Never conflate them. Tag each with value_basis.
12. DUTY-FREE is a distinct channel with its own dynamics (Chinese daigou decline).
    Do not include duty-free in "domestic retail" without flagging it.

## Confidence levels
- HIGH: primary source (company filing, government database, Euromonitor Passport)
- MEDIUM: credible secondary (Korea Herald, Business Standard, Statista, McKinsey)
- LOW: aggregator/estimate (Mordor Intelligence, Grand View, IMARC)
- ESTIMATE: model-derived with methodology shown

## Working style
- Write to files. Chat is for decisions only.
- Every fetcher returns timestamped JSON to data/raw/.
- Transforms write to data/processed/.
- Reports read ONLY from data/processed/ and data/baseline/.
- 3+ entities to profile = parallel subagents.
- Charts via lib/reports/charts.py only (matplotlib, saved to reports/latest/charts/).

## Vocabulary
Use precise industry terms. No "brand love", "engagement", "synergy".
Ehrenberg-Bass terms where relevant: Category Entry Points (CEPs), mental
availability, physical availability, Distinctive Brand Assets.
```

---

## 4. CANONICAL TAXONOMY

This goes in `config/taxonomy.yaml`. It is the backbone of the entire system — every data point, every chart, every report section maps to this tree.

```yaml
# config/taxonomy.yaml
# Beauty & Personal Care — Canonical Sub-Segment Taxonomy
# Based on Euromonitor Passport BPC category structure
# DO NOT modify without updating all downstream schemas

version: "1.0"
geographies:
  - code: KR
    name: South Korea
    currency: KRW
    fiscal_year: calendar  # Jan-Dec
  - code: IN
    name: India
    currency: INR
    fiscal_year: april     # Apr-Mar (FY25 = Apr 2024 - Mar 2025)

segments:
  - id: skincare
    name: Skincare
    sub_segments:
      - facial_moisturisers
      - facial_cleansers
      - toners_essences
      - serums_ampoules
      - sheet_masks
      - eye_care
      - body_care
      - hand_care
      - lip_care_non_colour

  - id: sun_care
    name: Sun Care
    sub_segments:
      - sun_protection
      - self_tanning
      - after_sun

  - id: colour_cosmetics
    name: Colour Cosmetics
    sub_segments:
      - face_makeup      # foundation, cushion, concealer, powder, blush
      - eye_makeup
      - lip_colour
      - nail

  - id: fragrances
    name: Fragrances
    sub_segments:
      - premium_fragrances
      - mass_fragrances
      - niche_artisanal

  - id: hair_care
    name: Hair Care
    sub_segments:
      - shampoo
      - conditioners_treatments
      - hair_colorants
      - styling
      - salon_professional
      - scalp_care

  - id: bath_shower
    name: Bath & Shower

  - id: deodorants
    name: Deodorants

  - id: oral_care
    name: Oral Care

  - id: mens_grooming
    name: "Men's Grooming"
    sub_segments:
      - mens_toiletries    # shave, deo
      - mens_skincare
      - mens_cosmetics

  - id: baby_child
    name: Baby & Child

  - id: dermocosmetics
    name: Dermocosmetics / Clinical Beauty

  - id: emerging_adjacencies
    name: Emerging Adjacencies
    sub_segments:
      - beauty_devices
      - ingestible_nutricosmetics
      - halal_certified       # India-relevant
      - ayurvedic_herbal       # India-relevant
      - clean_vegan
      - kbeauty_derivative     # glass skin derivatives etc.

tiers:
  - premium
  - masstige
  - mass
```

---

## 5. DATA SCHEMAS

### 5.1 `data/sources.csv` — Master source ledger

Every number in the system gets a row here. This is the audit trail.

```
claim,value,unit,currency,geography,segment,period,period_type,value_basis,source_name,url,date_accessed,confidence,notes
```

### 5.2 Processed data — canonical JSON schema

Every file in `data/processed/` conforms to this Pydantic model (defined in `lib/transforms/schema.py`):

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

class DataPoint(BaseModel):
    geography: Literal["KR", "IN"]
    segment: str                        # Must match taxonomy.yaml segment.id
    sub_segment: Optional[str] = None   # Must match taxonomy.yaml if present
    metric: Literal[
        "market_size", "growth_yoy", "cagr_historical", "cagr_forecast",
        "market_share", "revenue", "export_value", "production_value",
        "channel_share", "per_capita_spend", "penetration_rate"
    ]
    value: float
    unit: str                           # "usd_bn", "krw_tn", "inr_cr", "percent", "usd"
    currency: Literal["USD", "KRW", "INR"]
    period: str                         # "2024", "FY25", "2020-2024", "H1_2025"
    period_type: Literal["CY", "FY", "H1", "H2", "Q1", "Q2", "Q3", "Q4", "range"]
    value_basis: Literal[
        "RETAIL", "NET_REALISATION", "WHOLESALE", "EXPORT_FOB", "PRODUCTION"
    ]
    tier: Optional[Literal["premium", "masstige", "mass"]] = None
    source_name: str
    source_url: Optional[str] = None
    date_accessed: date
    confidence: Literal["HIGH", "MEDIUM", "LOW", "ESTIMATE"]
    methodology: Optional[str] = None   # Required if confidence == "ESTIMATE"
    notes: Optional[str] = None

class SegmentFile(BaseModel):
    """One file per segment × geography in data/processed/"""
    geography: Literal["KR", "IN"]
    segment: str
    last_updated: date
    data_points: list[DataPoint]
```

---

## 6. SOURCE REGISTRY

This goes in `config/sources.yaml`. Every source the system can pull from, with access method, rate limits, and what it provides.

```yaml
# config/sources.yaml
free_sources:
  # --- KOREA ---
  korea_mfds:
    name: "MFDS (Ministry of Food and Drug Safety)"
    url: "https://www.mfds.go.kr"
    provides: [production_value, export_value, company_production_rankings]
    geography: KR
    access: web_fetch
    frequency: annual
    notes: "Primary source for Korea cosmetics production and export data. Published annually, usually Q1 for prior year."

  korea_dart:
    name: "DART (Data Analysis, Retrieval and Transfer)"
    url: "https://dart.fss.or.kr"
    provides: [company_financials, annual_reports]
    geography: KR
    access: api  # English API available
    frequency: quarterly
    notes: "Korean equivalent of EDGAR. Company filings for AmorePacific, LG H&H, Cosmax, Kolmar, etc."

  korea_customs:
    name: "Korea Customs Service / KITA TradeStats"
    url: "https://stat.kita.net"
    provides: [export_value_by_hs_code, export_by_destination]
    geography: KR
    access: web_fetch
    frequency: monthly
    notes: "HS codes 3303-3307 cover cosmetics. KITA provides English interface."

  # --- INDIA ---
  india_screener:
    name: "Screener.in"
    url: "https://www.screener.in"
    provides: [listed_company_financials, adspend_line, 10yr_history]
    geography: IN
    access: web_fetch
    frequency: quarterly
    notes: "Free 10-year P&L/BS/CF for all BSE/NSE listed companies. Key: HUL, Nykaa (FSN), Honasa, Godrej Consumer."

  india_mca_tofler:
    name: "Tofler / MCA21"
    url: "https://www.tofler.in"
    provides: [private_company_revenue_bands, directors]
    geography: IN
    access: web_fetch
    frequency: annual
    notes: "Free tier gives revenue bands for private companies (SUGAR, Plum pre-acquisition). Exact P&L paywalled."

  india_tradestat:
    name: "TradeStat (DGCI&S)"
    url: "https://tradestat.commerce.gov.in"
    provides: [import_export_by_hs_code]
    geography: IN
    access: web_fetch
    frequency: monthly
    notes: "HS 3303-3307 for cosmetics imports into India (including from Korea). Guest access may limit 8-digit granularity."

  # --- CROSS-GEOGRAPHY ---
  un_comtrade:
    name: "UN Comtrade"
    url: "https://comtradeplus.un.org"
    provides: [bilateral_trade_flows, mirror_data]
    geography: [KR, IN]
    access: api
    frequency: annual
    api_limit: "100 requests/day free tier"
    notes: "Use to cross-check Korea→India corridor trade data. HS 3304 (skincare), 3305 (hair), etc."

  google_trends:
    name: "Google Trends"
    url: "https://trends.google.com"
    provides: [demand_seasonality, regional_interest, relative_search_volume]
    geography: [KR, IN]
    access: api_unofficial  # pytrends
    frequency: real_time
    notes: "Relative index, not absolute volume. Use for directional signals only."

  openalex:
    name: "OpenAlex"
    url: "https://openalex.org"
    provides: [academic_papers, citation_data, research_trends]
    geography: [KR, IN]
    access: mcp  # via openalex MCP server
    frequency: real_time
    notes: "250M+ papers, free, no API key needed. Use for ingredient trends (PDRN, exosomes, niacinamide) and regulatory science."

  tavily:
    name: "Tavily"
    provides: [news_search, web_content]
    geography: [KR, IN]
    access: mcp_global  # Already connected, do NOT add to .mcp.json
    frequency: real_time
    notes: "Primary tool for structured news fetching. Use for M&A announcements, earnings releases, regulatory updates."

  meta_ad_library:
    name: "Meta Ad Library"
    url: "https://www.facebook.com/ads/library"
    provides: [active_creatives, ad_longevity]
    geography: [KR, IN]
    access: web_fetch
    frequency: real_time
    notes: "No spend data. Use for creative strategy analysis and brand positioning signals."

# Subscription sources (user configures access_status.yaml)
subscription_sources:
  euromonitor_passport:
    name: "Euromonitor Passport"
    provides: [market_size_by_segment, brand_shares, forecasts, premium_mass_split]
    priority: 1  # Most important subscription source
    ingest_format: csv
    ingest_handler: lib/ingest/passport_csv.py

  capitaliq_pro:
    name: "S&P Capital IQ Pro"
    provides: [company_financials, comparables, deal_data]
    priority: 2
    ingest_format: csv
    ingest_handler: lib/ingest/capitaliq_csv.py

  statista:
    name: "Statista"
    provides: [market_overview, consumer_survey_data]
    priority: 3
    ingest_format: csv
    ingest_handler: lib/ingest/statista_csv.py

  bmi_research:
    name: "BMI Research (Fitch)"
    provides: [country_risk, industry_forecasts]
    priority: 4
    ingest_format: csv
    ingest_handler: lib/ingest/generic_csv.py
```

---

## 7. BUILD PHASES

Each phase is a self-contained unit of work. Claude Code should complete each phase fully — all files written, all tests passing — before moving to the next. Phases are designed so that earlier phases produce value even if later phases are not yet built.

---

### PHASE 1: Scaffold + Constitution
**Estimated work: ~15 minutes**

1. Create the full directory structure from §2.1
2. Write `CLAUDE.md` verbatim from §3
3. Write `.mcp.json` from §2.2
4. Write `.claude/settings.json` with hooks from §2.3
5. Write `config/taxonomy.yaml` from §4
6. Write `config/sources.yaml` from §6
7. Write `requirements.txt` from §2.4
8. Create `config/exchange_rates.yaml` with current KRW/USD and INR/USD rates (fetch live)
9. Create `config/access_status.yaml` as a template for Rohnit to fill in:
   ```yaml
   # Fill in your access status for each HEC database
   # Options: remote_access | on_campus_only | no_access | not_checked
   euromonitor_passport: not_checked
   capitaliq_pro: not_checked
   statista: not_checked
   bmi_research: not_checked
   business_source_complete: not_checked
   orbis: not_checked
   factiva: not_checked
   ```
10. Create `config/companies.yaml` — the named-player registry for both geographies, seeded from the baseline report:
    ```yaml
    KR:
      conglomerates:
        - { name: "AmorePacific", ticker: "090430.KS", type: listed, segments: [skincare, colour_cosmetics, fragrances, hair_care] }
        - { name: "LG H&H", ticker: "051900.KS", type: listed, segments: [skincare, colour_cosmetics, oral_care, bath_shower] }
      odm_oem:
        - { name: "Cosmax", ticker: "192820.KS", type: listed }
        - { name: "Kolmar Korea", ticker: "161890.KS", type: listed }
        - { name: "Cosmecca Korea", ticker: "241710.KQ", type: listed }
      indie_brands:
        - { name: "APR (Medicube)", ticker: "278470.KQ", type: listed }
        - { name: "The Founders (Anua)", type: private }
        - { name: "Gudai Global (Beauty of Joseon)", type: private }
      retailers:
        - { name: "CJ Olive Young", parent: "CJ Corp", type: subsidiary_unlisted }
    IN:
      incumbents:
        - { name: "Hindustan Unilever", ticker: "HINDUNILVR.NS", type: listed, segments: [skincare, hair_care, colour_cosmetics, deodorants] }
        - { name: "Godrej Consumer Products", ticker: "GODREJCP.NS", type: listed }
        - { name: "L'Oréal India", type: subsidiary_unlisted }
      platforms:
        - { name: "Nykaa (FSN E-Commerce)", ticker: "NYKAA.NS", type: listed }
        - { name: "Purplle", type: private, last_valuation: "US$1.1bn" }
      d2c_brands:
        - { name: "Honasa Consumer (Mamaearth)", ticker: "HONASA.NS", type: listed }
        - { name: "Minimalist (Uprising Science)", type: acquired, acquirer: "HUL" }
        - { name: "SUGAR Cosmetics", type: private }
        - { name: "Plum", type: private, acquirer: "Unilever (reported)" }
    ```
11. Copy the deep research report into `data/baseline/deep-research-report.md`
12. Create empty `data/sources.csv` with the header row from §5.1
13. Run `pip install -r requirements.txt` and confirm no errors

**Completion test:** All files exist, `python -c "import yaml, pandas, pydantic, jinja2, matplotlib"` succeeds, directory structure matches §2.1.

---

### PHASE 2: Core Library — Schemas + Transforms
**Estimated work: ~30 minutes**

Build the data foundation. No fetchers yet — just the structures that all data flows through.

1. **`lib/transforms/schema.py`** — Pydantic models from §5.2, plus:
   - `validate_segment(segment_id)` — checks against taxonomy.yaml
   - `validate_data_point(dp: DataPoint)` — full validation including segment existence
   - `load_segment_file(path) -> SegmentFile`
   - `save_segment_file(sf: SegmentFile, path)`

2. **`lib/transforms/currency.py`**:
   - `convert(amount, from_currency, to_currency, rate_date=None) -> tuple[float, str]` — returns (converted_amount, rate_used)
   - Reads rates from `config/exchange_rates.yaml`
   - Always returns both the converted value AND the rate+date used (for auditability)

3. **`lib/transforms/mrp_normalise.py`** (India-specific):
   - `mrp_to_net_realisation(mrp_value, category, margin_assumption=None) -> tuple[float, float, str]`
   - Returns (net_value, margin_used, methodology_note)
   - Default margins by category from industry benchmarks:
     ```python
     DEFAULT_MARGINS = {
         "skincare": 0.35, "colour_cosmetics": 0.40, "hair_care": 0.30,
         "fragrances": 0.45, "bath_shower": 0.25, "deodorants": 0.30,
         "oral_care": 0.25, "mens_grooming": 0.35, "baby_child": 0.30,
         "dermocosmetics": 0.38, "sun_care": 0.35, "emerging_adjacencies": 0.40
     }
     ```
   - `net_realisation_to_mrp(net_value, category, margin_assumption=None)` — inverse

4. **`lib/transforms/value_basis.py`**:
   - `tag_value_basis(value, basis: str) -> dict` — wraps a number with its basis metadata
   - `are_comparable(dp1: DataPoint, dp2: DataPoint) -> tuple[bool, str]` — returns whether two data points can be directly compared and why/why not
   - `normalise_to_basis(dp: DataPoint, target_basis: str) -> DataPoint` — uses mrp_normalise for India retail↔net, flags Korea export↔retail as non-convertible

5. **`lib/transforms/fiscal_year.py`**:
   - `parse_period(period_str) -> dict` — parses "FY24", "CY2024", "H1_2025", "2020-2024" into structured period metadata
   - `align_periods(kr_period, in_period) -> str` — notes the overlap/gap when comparing Korea CY vs India FY data
   - `fy_to_cy_range(fy_str) -> tuple[str, str]` — "FY24" → ("2023-04", "2024-03")

6. **`lib/analysis/gaps.py`**:
   - `scan_gaps(taxonomy_path, processed_dir) -> list[dict]` — walks every segment × geography × metric combination in the taxonomy, checks what exists in processed data, returns a list of missing data points
   - `format_gaps_register(gaps) -> str` — renders as a Markdown table
   - `suggest_source(gap) -> str` — suggests which source (from sources.yaml) could fill each gap

7. **Tests:**
   - `tests/test_schemas.py` — create 5+ valid DataPoints, 3+ invalid ones, assert validation passes/fails correctly
   - `tests/test_transforms.py` — test currency conversion, MRP normalisation (round-trip), fiscal year parsing

**Completion test:** `python -m pytest tests/test_schemas.py tests/test_transforms.py` — all pass.

---

### PHASE 3: Baseline Ingest
**Estimated work: ~45 minutes**

Parse the deep research report into structured data. This is the most intellectually demanding phase — it requires reading the baseline report, extracting every quantitative claim, and writing each one into the canonical schema with proper source attribution.

1. **`lib/ingest/baseline_parser.py`**:
   - `parse_baseline_report(md_path) -> list[DataPoint]`
   - Reads the deep research markdown, extracts every quantitative claim
   - Maps each to a DataPoint with: the original source cited in the report, confidence level based on that source, correct value_basis and currency
   - Returns structured data, not guesses — if a claim is ambiguous about value basis, flag it as `notes: "value_basis_uncertain"`

2. Run the parser on `data/baseline/deep-research-report.md`

3. Write outputs:
   - One JSON file per segment × geography in `data/processed/` (e.g., `data/processed/KR_skincare.json`, `data/processed/IN_colour_cosmetics.json`)
   - Append every extracted claim to `data/sources.csv`

4. Run `lib/analysis/gaps.py` to produce the initial gaps register
   - Write to `reports/latest/gaps_register.md`

⏸️ **CHECKPOINT:** Pause here. Show Rohnit:
- The count of data points extracted per segment × geography
- The gaps register (what's missing)
- Any data points flagged as value_basis_uncertain
- Ask: "Before I build fetchers, review `config/access_status.yaml` — have you checked your HEC database access yet?"

---

### PHASE 4: Fetchers — Free Sources
**Estimated work: ~90 minutes**

Build the scripts that pull live data from free sources. Each fetcher follows the same contract:

```python
# Every fetcher must implement:
def fetch() -> list[dict]:
    """Fetch data, return list of raw records."""
    pass

def to_data_points(raw_records: list[dict]) -> list[DataPoint]:
    """Convert raw records to canonical DataPoints."""
    pass

def run(output_dir: str = "data/raw/") -> str:
    """Full pipeline: fetch → save raw → convert → save processed. Returns path to output."""
    pass
```

Build in this order (highest-value first):

1. **`lib/fetchers/news_tavily.py`** — Tavily-powered news search
   - Predefined queries per segment × geography (e.g., "South Korea skincare market 2025", "India beauty D2C funding 2026")
   - Extracts structured facts (company, metric, value, date, source_url)
   - Deduplicates against existing `data/sources.csv`
   - Saves raw results to `data/raw/tavily_{timestamp}.json`

2. **`lib/fetchers/korea_dart.py`** — Korean company filings via DART
   - Targets: AmorePacific (090430), LG H&H (051900), Cosmax (192820), Kolmar (161890)
   - Fetches latest annual report data (revenue, operating profit, segment breakdowns)
   - DART has an English-language open API (api key free to register at https://opendart.fss.or.kr)
   - If API key not yet configured, create `config/api_keys.yaml.template` and log instructions

3. **`lib/fetchers/india_screener.py`** — Screener.in scraper
   - Targets: HINDUNILVR, NYKAA, HONASA, GODREJCP
   - Fetches 10-year P&L including the Advertising & Sales Promotion line
   - Parse HTML tables → DataPoints
   - Respect rate limits (2-second delay between requests)

4. **`lib/fetchers/trade_comtrade.py`** — UN Comtrade bilateral trade
   - HS codes: 3303 (fragrances), 3304 (skincare/makeup), 3305 (hair), 3306 (oral), 3307 (other)
   - Reporter: Korea, Partner: India (and vice versa) — the Korea→India corridor
   - Reporter: Korea, Partner: World — total Korean exports by HS
   - Free tier: 100 requests/day, so batch wisely

5. **`lib/fetchers/trends_google.py`** — Google Trends via pytrends
   - Comparative interest: "Korean skincare" in India, "K-beauty" in India
   - Category-level: "sunscreen" India vs Korea, "serum" India vs Korea
   - State-level for India (top 10 states by interest)
   - Note: pytrends is unofficial and can break; wrap in try/except with clear error messages

6. **`lib/fetchers/academic_openalex.py`** — via OpenAlex MCP
   - Search for recent papers on: PDRN skincare, exosome cosmetics, ayurvedic beauty clinical trials, Korean cosmetics regulation
   - Extract publication counts by year as a proxy for ingredient-trend momentum
   - No API key needed

7. **`lib/fetchers/qcommerce_tracker.py`** — Blinkit/Zepto assortment snapshot
   - Search beauty/skincare categories on Blinkit web
   - Capture: product names, brands, MRP, selling price, rating count (as demand proxy)
   - This is ToS-sensitive — implement with respectful rate limiting (5+ second delays), user-agent identification, and a `config/qcommerce_enabled.yaml` flag that defaults to `false`
   - The user must explicitly set `enabled: true` to activate this fetcher

**For each fetcher:**
- Write a smoke test in `tests/test_fetchers.py` that verifies the fetcher can connect and return data (or gracefully handle unavailability)
- Handle network errors, rate limits, and API changes gracefully — log the error, return empty list, never crash
- Every fetcher logs what it did to stdout: "Fetched 47 records from DART for AmorePacific CY2025"

**Completion test:** `python -m pytest tests/test_fetchers.py` — all smoke tests pass (some may skip if API keys aren't configured, which is acceptable).

---

### PHASE 5: Manual Ingest Pipeline
**Estimated work: ~30 minutes**

Build the processors that handle manually-dropped subscription data.

1. **`lib/ingest/passport_csv.py`**:
   - Euromonitor Passport exports as CSV with a specific header structure (category, geography, year columns, brand rows)
   - Auto-detect whether the CSV is a market-size table, brand-share table, or forecast table
   - Map Passport category names to taxonomy.yaml segment IDs
   - Convert to DataPoints with `confidence: HIGH`, `source_name: "Euromonitor Passport"`

2. **`lib/ingest/capitaliq_csv.py`**:
   - Capital IQ exports financials as CSV (company, metric, year columns)
   - Map to DataPoints with company linkage to companies.yaml

3. **`lib/ingest/statista_csv.py`**:
   - Statista chart data exports as CSV (simple two-column: year, value)
   - Requires user to specify segment, geography, metric, and unit at ingest time

4. **`lib/ingest/generic_csv.py`**:
   - For any other CSV (BMI Research, IBEF downloads, etc.)
   - Interactive column mapping: prompt user (via a mapping config) for which column is what
   - Validate against schema before writing

5. **The `/ingest` command** (`commands/ingest.md`):
   ```markdown
   # /ingest <filepath>

   Process a manually-dropped data file into the system.

   ## Steps
   1. Detect file type and select handler (passport_csv, capitaliq_csv, statista_csv, or generic_csv)
   2. Run the handler to extract DataPoints
   3. Validate all DataPoints against schema.py
   4. Check for conflicts with existing data in data/processed/ — if a data point already exists
      with a LOWER confidence source, replace it; if SAME or HIGHER, keep both and flag
   5. Write to data/processed/ and append to data/sources.csv
   6. Re-run gaps analysis and update reports/latest/gaps_register.md
   7. Report: "Ingested N data points from {filename}. M new, K updated, J conflicts flagged."
   ```

**Completion test:** Create a mock Passport-format CSV with 5 rows, run `/ingest` on it, verify data appears correctly in `data/processed/` and `data/sources.csv`.

---

### PHASE 6: Analysis Layer
**Estimated work: ~30 minutes**

1. **`lib/analysis/sizing.py`**:
   - `top_down_size(geography, segment) -> DataPoint` — pulls the best available total-market figure
   - `bottom_up_size(geography, segment) -> DataPoint` — sums company revenues (with coverage qualifier)
   - `reconcile(td: DataPoint, bu: DataPoint) -> dict` — compares, calculates gap %, flags if >20%, explains likely causes

2. **`lib/analysis/growth.py`**:
   - `cagr(start_value, end_value, years) -> float`
   - `yoy_growth(current, prior) -> float`
   - `indexed_growth(series: list[DataPoint], base_year) -> list[dict]` — rebases a time series to 100

3. **`lib/analysis/share.py`**:
   - `compute_shares(geography, segment) -> list[dict]` — takes all company revenues in a segment, computes shares
   - Always appends the qualifier: "Based on summed listed-company revenues; does not include unorganised/unlisted players. Coverage ratio: X%."

**Completion test:** Run sizing reconciliation for at least one segment (e.g., India skincare) using baseline data — verify gap calculation works.

---

### PHASE 7: Report Generation
**Estimated work: ~45 minutes**

1. **`lib/reports/templates/`** — Jinja2 Markdown templates:
   - `full_report.md.j2` — mirrors the structure of the deep research report but populated from `data/processed/`
   - `segment_brief.md.j2` — one-page per segment × geography
   - `comparison.md.j2` — Korea vs India side-by-side for a given metric

2. **`lib/reports/snapshot.py`**:
   - `generate_full_report() -> str` — reads all processed data, renders full_report.md.j2, saves to `reports/latest/snapshot_{date}.md`
   - Embeds charts (see charts.py)
   - Appends the gaps register as an appendix
   - Returns the path to the generated report

3. **`lib/reports/segment_brief.py`**:
   - `generate_brief(geography, segment) -> str` — one-page brief for a single segment

4. **`lib/reports/comparison.py`**:
   - `generate_comparison(metric, segments=None) -> str` — Korea vs India comparison table

5. **`lib/reports/charts.py`**:
   - `market_size_bar(geography) -> str` — stacked bar chart of segment sizes
   - `growth_comparison() -> str` — Korea vs India growth rates by segment
   - `export_treemap() -> str` — Korea exports by destination
   - `share_pie(geography, segment) -> str` — market share pie
   - `corridor_sankey() -> str` — Korea→India trade flow (if data available)
   - All charts save to `reports/latest/charts/` as PNG, return the file path

6. **Slash commands:**
   - `/report` — runs `snapshot.py`, outputs the path
   - `/segment skincare KR` — runs `segment_brief.py`
   - `/compare market_size` — runs `comparison.py`
   - `/gaps` — runs `gaps.py`, shows the register
   - `/refresh` — re-runs all fetchers, re-processes, regenerates report
   - `/verify` — cross-checks every claim in the latest report against `data/sources.csv`

**Completion test:** Run `/report` and get a complete Markdown report with embedded chart paths. Run `/gaps` and get a current gaps register.

⏸️ **CHECKPOINT:** Pause here. Show Rohnit the generated report and gaps register. Ask:
- "Does this report structure match what you'd hand to a client?"
- "Have you filled in `config/access_status.yaml` yet? If you have Passport access, drop a CSV into `data/manual/` and run `/ingest`."
- "Any segments or data points you want prioritised for the next fetch cycle?"

---

### PHASE 8: Integration Tests + Hardening
**Estimated work: ~30 minutes**

1. **`tests/test_reconciliation.py`**:
   - For every segment where both top-down and bottom-up data exist, run reconciliation
   - Assert gap is documented in the report
   - Assert no number appears in the report without a corresponding row in `data/sources.csv`

2. **End-to-end test:**
   - Run `/refresh` → `/report` → `/verify`
   - Confirm: zero unsourced claims, zero schema violations, report generates without errors

3. **Error handling audit:**
   - Every fetcher handles network timeouts (30s default)
   - Every ingest handler rejects malformed CSVs with a clear error message
   - Every analysis function handles missing data gracefully (returns None + logs warning, never fabricates)

4. **Documentation:**
   - `README.md` at project root: what this is, how to run it, prerequisites
   - Each command in `commands/` has full usage instructions
   - `CONTRIBUTING.md` (optional): how to add a new fetcher or segment

---

## 8. CODING STANDARDS (NON-NEGOTIABLE)

These apply to every line of code in the system:

1. **Type hints everywhere.** Every function has full type annotations. Use `from __future__ import annotations` at the top of every file.

2. **Docstrings on every public function.** Google-style docstrings with Args, Returns, Raises sections.

3. **No bare `except`.** Always catch specific exceptions. Log the exception with `logging.exception()`.

4. **Logging, not print.** Use Python's `logging` module. Set up a project-level logger in `lib/__init__.py`. Level: INFO for normal operations, WARNING for missing data, ERROR for failures.

5. **No hardcoded paths.** All paths are relative to project root or configurable. Use `pathlib.Path` throughout.

6. **No hardcoded values.** Exchange rates, margin assumptions, API endpoints — all in config YAML files.

7. **Timestamps on everything.** Raw data files include fetch timestamp. Source ledger includes `date_accessed`. Reports include generation timestamp.

8. **Idempotent operations.** Running a fetcher twice does not duplicate data. Running `/report` twice overwrites `reports/latest/`, archives the previous version.

9. **Fail loudly, never silently.** If a fetcher can't reach its source, it logs an ERROR and returns an empty list — it does not return stale data or fabricated data. The gaps register will show the hole.

10. **Git-friendly.** No binary files in the repo except generated chart PNGs. All data is JSON/CSV/YAML. `.gitignore` excludes `data/raw/` (large, regenerable) but includes `data/processed/` and `data/baseline/`.

---

## 9. SESSION MANAGEMENT

Claude Code should handle multi-session builds as follows:

**At the start of every session:**
1. Read `CLAUDE.md` and `BUILD-SPEC.md`
2. Check which phases are complete by verifying: directory structure exists, tests pass, key files present
3. Resume from the first incomplete phase
4. Log to stdout: "Resuming from Phase N: {phase_name}"

**At the end of every session:**
1. Run all existing tests: `python -m pytest tests/ -v`
2. Log which phases are complete and which are next
3. If a phase is partially complete, note exactly where in the phase work stopped (e.g., "Phase 4: completed fetchers 1-3 of 7")

**Decision points that require user input** (and ONLY these):
- ⏸️ CHECKPOINT markers in this spec (after Phase 3 and Phase 7)
- If `config/access_status.yaml` shows "not_checked" for all databases and Phase 5 needs to configure ingest handlers
- If a fetcher discovers an API requires registration (e.g., DART) — log the registration URL and instructions, then continue with other fetchers

---

## 10. FIRST-RUN INSTRUCTIONS FOR ROHNIT

```
1. Open terminal (PowerShell or CMD)
2. cd C:\Users\agraw\Documents
3. mkdir bpc-intel
4. cd bpc-intel
5. Open Claude Code: claude
6. Paste this entire build spec as the first message
7. Say: "Build Phase 1 through Phase 4. Pause at the Phase 3 checkpoint."
8. After reviewing the Phase 3 checkpoint output, say: "Continue to Phase 7 checkpoint."
9. Review the generated report, then say: "Complete Phase 8."

Between sessions:
- Check your HEC database access (see instructions in §0 of this chat)
- Fill in config/access_status.yaml
- If you have Passport access, export a BPC market-size CSV for South Korea
  and drop it in data/manual/, then run /ingest on next session
```

---

*End of build spec. This document is the complete, self-contained instruction set for building bpc-intel.*
