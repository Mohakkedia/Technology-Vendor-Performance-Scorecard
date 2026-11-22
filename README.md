# 📊 Technology Vendor Performance Scorecard

Scores 20 technology vendors on SLA compliance, on-time delivery,
incidents, and cost-vs-budget, combines them into a weighted composite
score, assigns each vendor a tier (**Strategic / Monitor / Replace**),
and includes a Quarterly Business Review deck ready to present to an
underperforming vendor — built with **SQL, Power BI (Power Query M +
DAX), and Excel**.

## The scoring formula (implemented 3 independent ways, on purpose)

```
composite_score = 0.30 × SLA_score + 0.25 × Delivery_score + 0.25 × Incident_score + 0.20 × Cost_score

Incident_score = MAX(0, 100 − incidents×8 − critical_incidents×20)
Cost_score     = MAX(0, 100 − |cost_variance_pct|×4)

Tier = Replace  if critical_incidents ≥ 3 (automatic override)
     = Strategic if composite_score ≥ 80
     = Monitor   if composite_score ≥ 60
     = Replace   otherwise
```

This exact formula is implemented **three times, independently** —
in SQL (`sql/scorecard_queries.sql`), in Python (`scripts/build_scorecard.py`),
and in DAX (`power-bi/vendor_scorecard_measures.dax`) — and all three
agree on every vendor's score to one decimal place. That's not an
accident: matching implementations across languages is how you catch a
scoring-logic bug before a vendor sees a number that doesn't reconcile.

## Results (real output from a 20-vendor, 240-month-row synthetic dataset)

| Tier | Count | Example vendors |
|---|---|---|
| Strategic | 6 | AWS (93.8), Workday (92.8), CrowdStrike (87.1) |
| Monitor | 9 | NetSuite (77.2), Okta (76.3), ADP (69.3) |
| Replace | 5 | SentinelOne, Cognizant, Verizon Business, Rackspace, Coupa |

3 of the 5 "Replace" vendors are flagged there **specifically because of
the critical-incident override** (SentinelOne, Cognizant, Verizon,
Rackspace all score 59–69 on the blended formula alone, which would
land them in "Monitor" — the override exists because repeated critical
incidents are a risk signal a blended average can dilute).

## Why Power BI + Excel, not Power BI alone

This environment can't run Power BI Desktop (Windows desktop software).
`power-bi/` contains the **real, correct Power Query M and DAX source**
— paste-ready into Power BI Desktop — plus a written report-page layout
spec (`report_layout.md`) describing exactly what visual goes where and
which measure drives it. `outputs/Vendor_Performance_Scorecard.xlsx` is
a fully **formula-driven Excel equivalent** (SUMIFS/AVERAGEIFS, not
pasted values) so the scorecard is usable by anyone without Power BI
installed, and its numbers are the cross-check for the DAX/SQL logic
above.

## Files

```
sql/schema.sql                       Vendors + vendor_monthly_metrics tables
sql/scorecard_queries.sql             Trailing-12mo aggregation + scoring logic (documented, source of truth)
scripts/generate_vendor_data.py        20 vendors x 12 months, persona-driven synthetic data
scripts/build_scorecard.py              Python scoring engine -> outputs/vendor_scorecard.csv
scripts/build_scorecard_workbook.py      Formula-driven Excel dashboard
scripts/build_qbr_deck.js                 QBR PowerPoint deck (Rackspace Managed Cloud, Replace tier)
power-bi/vendor_scorecard_powerquery.m    Power Query M (paste into Power BI Advanced Editor)
power-bi/vendor_scorecard_measures.dax     DAX measures (paste into Power BI as new measures)
power-bi/report_layout.md                  Report page layout spec (which visual, which measure, where)
outputs/                                    Generated scorecard CSV/JSON, Excel workbook, QBR deck
```

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/generate_vendor_data.py       # -> data/vendors.csv, vendor_monthly_metrics.csv, vendor_scorecard.db
python scripts/build_scorecard.py            # -> outputs/vendor_scorecard.csv, scorecard_summary.json
python scripts/build_scorecard_workbook.py   # -> outputs/Vendor_Performance_Scorecard.xlsx

npm install pptxgenjs
node scripts/build_qbr_deck.js               # -> outputs/QBR_Rackspace_Managed_Cloud.pptx
```

To use the real Power BI version: open Power BI Desktop, import
`data/vendors.csv` and `data/vendor_monthly_metrics.csv`, paste the
queries from `power-bi/vendor_scorecard_powerquery.m` into the Advanced
Editor, add each measure from `power-bi/vendor_scorecard_measures.dax`,
and build the two report pages per `power-bi/report_layout.md`.

## Key Technologies
Power BI (Power Query M, DAX), SQL (SQLite), Excel (formula-driven dashboard, conditional formatting, charts), Python (pandas), PowerPoint

## Disclaimer
Educational/portfolio project using fully synthetic vendor performance data.
