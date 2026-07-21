# BUILD-SPEC Addendum 1 — K-beauty × India Corridor Focus
**Added:** 2026-07-21, at Rohnit's request, between Phase 3 and Phase 4.

## What changed
The Korea → India corridor (baseline report §4.1) is promoted from a
cross-cutting module to a **first-class research axis**. Same evidence rules,
same schemas — corridor data is not a new geography or segment, it is a tagged
slice across the existing ones.

## Conventions
1. **Tagging:** any DataPoint about K-beauty *inside India* (K-brand India
   revenue, K-brand share of an India segment, K-beauty channel data on
   Nykaa/Blinkit) carries `[CORRIDOR]` in `notes`.
2. **Trade flows:** KR exports with destination India remain `geography: KR`,
   `value_basis: EXPORT_FOB`, destination stated in `notes` (already the
   Phase 3 convention).
3. **Registry:** `config/corridor.yaml` holds the conduit → brand map
   (Nykaa/AmorePacific 8 brands, Tira/Mixsoon, Amazon K-brands), whitespace
   ranking, CDSCO regulatory friction, and the corridor monitoring queries.

## Phase 4 impact (fetchers)
Every query-driven fetcher includes the corridor query set from
`config/corridor.yaml` in addition to its per-geography defaults:
- `news_tavily.py` — corridor Tavily queries (K-beauty India launches, CDSCO,
  Nykaa/Tira K-brand news)
- `trade_comtrade.py` — HS 3303–3307 Korea→India bilateral flow is a
  standing query, not an option
- `trends_google.py` — "Korean skincare" / "K-beauty" / "Korean sunscreen" /
  "glass skin" interest in India, including state-level breakdown
- `qcommerce_tracker.py` — when enabled, tracks K-brand assortment
  (Anua, COSRX, Beauty of Joseon, etc.) on Blinkit specifically
- `india_screener.py` / `korea_dart.py` — unchanged (company-keyed), but
  Nykaa and AmorePacific results feed corridor analysis

## Phase 7 impact (reports)
`lib/reports/` gains a corridor brief: `corridor_brief.md.j2` +
`corridor.py` — trade flow trend, conduit map, K-brand India footprint,
whitespace tracker. (Built in Phase 7, not now.)
