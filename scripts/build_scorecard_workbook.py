"""
build_scorecard_workbook.py
------------------------------
Builds Vendor_Performance_Scorecard.xlsx — a fully formula-driven Excel
equivalent of the Power BI report (same weighted-scoring formula, same
tier logic), so the scorecard is genuinely usable by anyone without
Power BI Desktop installed. Every score and tier on the Scorecard sheet
is a live SUMIFS/AVERAGEIFS/formula computed from the raw Vendors and
Monthly_Metrics sheets — nothing is pasted-in from the Python output.
"""

from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs"
OUT_PATH = OUT_DIR / "Vendor_Performance_Scorecard.xlsx"

FONT_NAME = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(name=FONT_NAME, bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(name=FONT_NAME, bold=True, size=16, color="1F4E78")
BODY_FONT = Font(name=FONT_NAME, size=10)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

STRATEGIC_FILL = PatternFill("solid", fgColor="DFF5E8")
MONITOR_FILL = PatternFill("solid", fgColor="FFF4CE")
REPLACE_FILL = PatternFill("solid", fgColor="FBE4E1")


def style_header(ws, row, n_cols, start_col=1):
    for c in range(start_col, start_col + n_cols):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


wb = Workbook()
wb.remove(wb.active)

# === README ==================================================================
ws_read = wb.create_sheet("README", 0)
ws_read.sheet_view.showGridLines = False
ws_read["B2"] = "Technology Vendor Performance Scorecard"
ws_read["B2"].font = TITLE_FONT
lines = [
    "",
    "Excel equivalent of the Power BI vendor scorecard report (see power-bi/ for the",
    "Power Query M + DAX source) -- every score here is a live formula, not pasted values.",
    "",
    "Sheets:",
    "  - Scorecard: weighted score (SLA 30% / Delivery 25% / Incidents 25% / Cost 20%),",
    "    tier assignment, conditional formatting, and 2 charts -- all formula-driven from",
    "    the raw data below.",
    "  - Vendors: 20-vendor reference table (category, budget, relationship owner).",
    "  - Monthly_Metrics: 240 rows (20 vendors x 12 months) of SLA/delivery/incidents/cost.",
    "",
    "Scoring formula (matches sql/scorecard_queries.sql and power-bi/*.dax exactly):",
    "  composite = 0.30*SLA + 0.25*Delivery + 0.25*IncidentScore + 0.20*CostScore",
    "  IncidentScore = MAX(0, 100 - incidents*8 - critical_incidents*20)",
    "  CostScore = MAX(0, 100 - ABS(cost_variance_pct)*4)",
    "  Tier = Replace if critical_incidents>=3, else Strategic (>=80) / Monitor (>=60) / Replace",
]
for i, line in enumerate(lines):
    cell = ws_read.cell(4 + i, 2, line)
    cell.font = Font(name=FONT_NAME, bold=line.startswith("Sheets:") or line.startswith("Scoring"), size=11)
ws_read.column_dimensions["B"].width = 100

# === Vendors ==================================================================
ws_vendors = wb.create_sheet("Vendors")
vendor_rows = list(csv.DictReader(open(DATA_DIR / "vendors.csv")))
headers = list(vendor_rows[0].keys())
ws_vendors.append(headers)
style_header(ws_vendors, 1, len(headers))
for i, row in enumerate(vendor_rows):
    r = i + 2
    for c, h in enumerate(headers, start=1):
        val = row[h]
        if h == "annual_budget":
            val = float(val)
        cell = ws_vendors.cell(r, c, val)
        cell.font = BODY_FONT
        cell.border = BORDER
        if h == "annual_budget":
            cell.number_format = '$#,##0'
n_vendors = len(vendor_rows)
for i, w in enumerate([10, 26, 20, 15, 18, 14]):
    ws_vendors.column_dimensions[get_column_letter(i + 1)].width = w
ws_vendors.freeze_panes = "A2"

# === Monthly_Metrics ===========================================================
ws_metrics = wb.create_sheet("Monthly_Metrics")
metric_rows = list(csv.DictReader(open(DATA_DIR / "vendor_monthly_metrics.csv")))
m_headers = list(metric_rows[0].keys())
ws_metrics.append(m_headers)
style_header(ws_metrics, 1, len(m_headers))
for i, row in enumerate(metric_rows):
    r = i + 2
    for c, h in enumerate(m_headers, start=1):
        val = row[h]
        if h in ("sla_compliance_pct", "on_time_delivery_pct", "actual_cost", "budgeted_cost"):
            val = float(val)
        elif h in ("incident_count", "critical_incident_count"):
            val = int(val)
        cell = ws_metrics.cell(r, c, val)
        cell.font = BODY_FONT
        cell.border = BORDER
        if h in ("actual_cost", "budgeted_cost"):
            cell.number_format = '$#,##0'
n_metrics = len(metric_rows)
for i, w in enumerate([12, 10, 16, 16, 14, 18, 14, 14]):
    ws_metrics.column_dimensions[get_column_letter(i + 1)].width = w
ws_metrics.freeze_panes = "A2"

# === Scorecard =================================================================
ws_sc = wb.create_sheet("Scorecard", 0)
ws_sc.sheet_view.showGridLines = False
ws_sc["B2"] = "Technology Vendor Performance Scorecard"
ws_sc["B2"].font = TITLE_FONT
ws_sc["B3"] = "Trailing 12 months (2025) -- every score below is a live formula, see README for the exact weighting."
ws_sc["B3"].font = Font(name=FONT_NAME, italic=True, size=10, color="595959")

MET_VID = f"Monthly_Metrics!$A$2:$A${n_metrics + 1}"
MET_SLA = f"Monthly_Metrics!$C$2:$C${n_metrics + 1}"
MET_DELIV = f"Monthly_Metrics!$D$2:$D${n_metrics + 1}"
MET_INC = f"Monthly_Metrics!$E$2:$E${n_metrics + 1}"
MET_CRIT = f"Monthly_Metrics!$F$2:$F${n_metrics + 1}"
MET_ACTUAL = f"Monthly_Metrics!$G$2:$G${n_metrics + 1}"
MET_BUDGET = f"Monthly_Metrics!$H$2:$H${n_metrics + 1}"

headers2 = [
    "Vendor", "Category", "Avg SLA %", "Avg Delivery %", "Total Incidents",
    "Critical Incidents", "Actual Cost", "Budgeted Cost", "Cost Variance %",
    "SLA Score", "Delivery Score", "Incident Score", "Cost Score",
    "Composite Score", "Tier",
]
hdr_row = 5
for i, h in enumerate(headers2):
    ws_sc.cell(hdr_row, 2 + i, h)
style_header(ws_sc, hdr_row, len(headers2), start_col=2)

for i, vrow in enumerate(vendor_rows):
    r = hdr_row + 1 + i
    vid_cell = f"Vendors!$A${i + 2}"
    ws_sc.cell(r, 2, f"=Vendors!B{i+2}")   # vendor_name
    ws_sc.cell(r, 3, f"=Vendors!C{i+2}")   # category

    ws_sc.cell(r, 4, f"=ROUND(AVERAGEIF({MET_VID},{vid_cell},{MET_SLA}),1)")
    ws_sc.cell(r, 5, f"=ROUND(AVERAGEIF({MET_VID},{vid_cell},{MET_DELIV}),1)")
    ws_sc.cell(r, 6, f"=SUMIF({MET_VID},{vid_cell},{MET_INC})")
    ws_sc.cell(r, 7, f"=SUMIF({MET_VID},{vid_cell},{MET_CRIT})")
    ws_sc.cell(r, 8, f"=ROUND(SUMIF({MET_VID},{vid_cell},{MET_ACTUAL}),0)")
    ws_sc.cell(r, 9, f"=ROUND(SUMIF({MET_VID},{vid_cell},{MET_BUDGET}),0)")
    ws_sc.cell(r, 10, f"=ROUND(100*(H{r}-I{r})/I{r},1)")

    ws_sc.cell(r, 11, f"=D{r}")
    ws_sc.cell(r, 12, f"=E{r}")
    ws_sc.cell(r, 13, f"=MAX(0,100-F{r}*8-G{r}*20)")
    ws_sc.cell(r, 14, f"=MAX(0,100-ABS(J{r})*4)")
    ws_sc.cell(r, 15, f"=ROUND(0.3*K{r}+0.25*L{r}+0.25*M{r}+0.2*N{r},1)")
    ws_sc.cell(r, 16, f'=IF(G{r}>=3,"Replace",IF(O{r}>=80,"Strategic",IF(O{r}>=60,"Monitor","Replace")))')

    for c in range(2, 17):
        cell = ws_sc.cell(r, c)
        cell.font = BODY_FONT
        cell.border = BORDER
        if c in (8, 9):
            cell.number_format = '$#,##0'
        if c in (4, 5, 11, 12, 13, 14, 15):
            cell.number_format = "0.0"
    ws_sc.cell(r, 10).number_format = '+0.0"%";-0.0"%"'

last_data_row = hdr_row + len(vendor_rows)

tier_col_letter = "P"
tier_range = f"{tier_col_letter}{hdr_row+1}:{tier_col_letter}{last_data_row}"
ws_sc.conditional_formatting.add(
    tier_range, CellIsRule(operator="equal", formula=['"Strategic"'], fill=STRATEGIC_FILL)
)
ws_sc.conditional_formatting.add(
    tier_range, CellIsRule(operator="equal", formula=['"Monitor"'], fill=MONITOR_FILL)
)
ws_sc.conditional_formatting.add(
    tier_range, CellIsRule(operator="equal", formula=['"Replace"'], fill=REPLACE_FILL)
)

col_widths = [24, 20, 11, 13, 12, 12, 13, 13, 13, 10, 11, 11, 10, 13, 11]
for i, w in enumerate(col_widths):
    ws_sc.column_dimensions[get_column_letter(2 + i)].width = w
ws_sc.freeze_panes = "B6"

# ---- Summary KPI cards ----
kpi_row2 = last_data_row + 3
ws_sc.cell(kpi_row2, 2, "Summary").font = Font(name=FONT_NAME, bold=True, size=12, color="1F4E78")
labels_formulas = [
    ("Total Vendors", f"=COUNTA(C{hdr_row+1}:C{last_data_row})", "1F4E78"),
    ("Strategic", f'=COUNTIF(P{hdr_row+1}:P{last_data_row},"Strategic")', "2E7D32"),
    ("Replace", f'=COUNTIF(P{hdr_row+1}:P{last_data_row},"Replace")', "C0392B"),
]
for i, (label, formula, color) in enumerate(labels_formulas):
    c = 2 + i * 2
    ws_sc.merge_cells(start_row=kpi_row2 + 1, start_column=c, end_row=kpi_row2 + 1, end_column=c + 1)
    lbl = ws_sc.cell(kpi_row2 + 1, c, label)
    lbl.font = Font(name=FONT_NAME, bold=True, color="FFFFFF", size=10)
    lbl.fill = PatternFill("solid", fgColor=color)
    lbl.alignment = Alignment(horizontal="center")
    ws_sc.merge_cells(start_row=kpi_row2 + 2, start_column=c, end_row=kpi_row2 + 3, end_column=c + 1)
    val = ws_sc.cell(kpi_row2 + 2, c, formula)
    val.font = Font(name=FONT_NAME, bold=True, size=20, color="FFFFFF")
    val.fill = PatternFill("solid", fgColor=color)
    val.alignment = Alignment(horizontal="center", vertical="center")

# ---- Tier distribution pie chart + spend by category bar chart ----
tier_summary_row = kpi_row2 + 6
ws_sc.cell(tier_summary_row, 2, "Tier").font = HEADER_FONT
ws_sc.cell(tier_summary_row, 2).fill = HEADER_FILL
ws_sc.cell(tier_summary_row, 3, "Count").font = HEADER_FONT
ws_sc.cell(tier_summary_row, 3).fill = HEADER_FILL
for i, tier in enumerate(["Strategic", "Monitor", "Replace"]):
    r = tier_summary_row + 1 + i
    ws_sc.cell(r, 2, tier).font = BODY_FONT
    ws_sc.cell(r, 3, f'=COUNTIF(P{hdr_row+1}:P{last_data_row},"{tier}")').font = BODY_FONT
tier_last_row = tier_summary_row + 3

pie = PieChart()
pie.title = "Vendor Tier Distribution"
data = Reference(ws_sc, min_col=3, min_row=tier_summary_row, max_row=tier_last_row)
cats = Reference(ws_sc, min_col=2, min_row=tier_summary_row + 1, max_row=tier_last_row)
pie.add_data(data, titles_from_data=True)
pie.set_categories(cats)
pie.height, pie.width = 8, 10
ws_sc.add_chart(pie, f"B{tier_last_row + 2}")

cat_summary_row = tier_last_row + 2
categories = sorted(set(v["category"] for v in vendor_rows))
ws_sc.cell(cat_summary_row, 6, "Category").font = HEADER_FONT
ws_sc.cell(cat_summary_row, 6).fill = HEADER_FILL
ws_sc.cell(cat_summary_row, 7, "Total Spend").font = HEADER_FONT
ws_sc.cell(cat_summary_row, 7).fill = HEADER_FILL
for i, cat in enumerate(categories):
    r = cat_summary_row + 1 + i
    ws_sc.cell(r, 6, cat).font = BODY_FONT
    ws_sc.cell(r, 7, f'=SUMIF($C${hdr_row+1}:$C${last_data_row},F{r},$H${hdr_row+1}:$H${last_data_row})')
    ws_sc.cell(r, 7).number_format = '$#,##0'
cat_last_row = cat_summary_row + len(categories)

bar = BarChart()
bar.type = "bar"
bar.title = "Total Spend by Category"
data2 = Reference(ws_sc, min_col=7, min_row=cat_summary_row, max_row=cat_last_row)
cats2 = Reference(ws_sc, min_col=6, min_row=cat_summary_row + 1, max_row=cat_last_row)
bar.add_data(data2, titles_from_data=True)
bar.set_categories(cats2)
bar.height, bar.width = 8, 14
ws_sc.add_chart(bar, f"F{cat_last_row + 2}")

wb.save(OUT_PATH)
print(f"Wrote {OUT_PATH}")
