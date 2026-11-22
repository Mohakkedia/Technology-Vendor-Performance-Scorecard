# Power BI Report Layout — Vendor Performance Scorecard

Two report pages, built from the model in `vendor_scorecard_powerquery.m`
and the measures in `vendor_scorecard_measures.dax`.

## Page 1 — Executive Scorecard

**KPI card row** (top, 4 cards):
- `[Vendor Count]` — "Total Vendors"
- `[Strategic Vendor Count]` — "Strategic Tier" (green)
- `[Replace Vendor Count]` — "Replace Tier" (red)
- `[Avg Composite Score (All Vendors)]` — "Avg Score"

**Main table** (center-left, ~60% width): one row per vendor —
`Vendors[vendor_name]`, `Vendors[category]`, `[Avg SLA Compliance %]`,
`[Avg On-Time Delivery %]`, `[Total Incidents]`, `[Cost Variance %]`,
`[Composite Score]`, `[Vendor Tier]`. Conditional formatting on
`[Vendor Tier]` using `[Tier Color]` as a "Format by field" color rule.
Sort by `[Composite Score]` descending.

**Tier distribution donut chart** (top-right): `Vendors[vendor_id]`
(count) by `[Vendor Tier]`, colors bound to `[Tier Color]`, legend
ordered by `[Vendor Tier Sort Order]`.

**Spend by category bar chart** (bottom-right): `Vendors[category]` on
the axis, `[Total Actual Cost]` as the value, sorted descending.

**Slicers** (left rail): `Vendors[category]`, `Vendors[relationship_owner]`,
`[Vendor Tier]` — all cross-filtering the whole page.

## Page 2 — Vendor Detail / Trend

**Vendor selector**: a single-select slicer on `Vendors[vendor_name]`.

**SLA & delivery trend line chart** (top): `VendorMonthlyMetrics[month_date]`
on the axis, `[Avg SLA Compliance %]` and `[Avg On-Time Delivery %]` as two
lines, filtered to the selected vendor.

**Incident trend column chart** (middle-left): `VendorMonthlyMetrics[month_date]`
on the axis, `Total Incidents` and `Total Critical Incidents` as stacked
columns.

**Cost vs. budget line chart** (middle-right): `VendorMonthlyMetrics[month_date]`
on the axis, `[Total Actual Cost]` and `[Total Budgeted Cost]` as two lines.

**Score breakdown table** (bottom): a single-row table showing
`[SLA Score]`, `[Delivery Score]`, `[Incident Score]`, `[Cost Score]`, and
`[Composite Score]` for the selected vendor — the exact inputs to the
weighted formula, so a reviewer can see precisely why a vendor landed in
its tier without re-deriving the math.

## Report-level settings
- Theme: a custom JSON theme (`#1F4E78` primary, `#2E7D32`/`#B7791F`/`#C0392B`
  for tier colors) applied via View -> Themes -> Browse for themes.
- Page size: 16:9, optimized for a conference-room display during the QBR.
