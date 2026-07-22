# /compare <metric>

Korea vs India side-by-side for one metric (default: market_size).

Renders `comparison.md.j2` across all segments. Notes that Korea (CY) and
India (FY) are not period-aligned and value bases differ — comparisons are
directional.

Run: `python -m lib.reports.snapshot comparison market_size`
