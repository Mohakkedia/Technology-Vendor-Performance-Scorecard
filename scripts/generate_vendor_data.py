"""
generate_vendor_data.py
--------------------------
Generates 20 technology vendors across 6 categories with 12 months of
performance metrics each (SLA compliance, on-time delivery, incidents,
actual vs. budgeted cost). Vendor "personas" are baked in deliberately
(a few chronic underperformers, a couple of over-budget vendors, one
vendor with a cost-controlled-but-incident-prone profile) so the
resulting scorecard has a realistic mix of tiers rather than everyone
scoring the same.

Output:
  data/vendors.csv
  data/vendor_monthly_metrics.csv
  data/vendor_scorecard.db (SQLite, matches sql/schema.sql)
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

MONTHS = [f"2025-{m:02d}" for m in range(1, 13)]

CATEGORIES = ["Cloud Infrastructure", "Security", "Network", "SaaS-HR", "SaaS-Finance", "Managed Services"]
OWNERS = ["J. Alvarez", "M. Kim", "T. Osei", "R. Chen", "S. Patel"]

# vendor_name, category, annual_budget, persona
# persona drives the underlying performance distribution:
#   strong        -> consistently high SLA/delivery, low incidents, on-budget
#   solid         -> good but not perfect, occasional hiccup
#   inconsistent  -> wide month-to-month variance
#   underperformer -> chronically low SLA/delivery, frequent incidents
#   over_budget   -> fine on service, but consistently over budget
#   incident_prone -> decent SLA numbers but repeated incidents (esp. critical)
VENDORS = [
    ("Amazon Web Services",       "Cloud Infrastructure", 2_400_000, "strong"),
    ("Microsoft Azure",           "Cloud Infrastructure", 1_800_000, "solid"),
    ("Google Cloud Platform",     "Cloud Infrastructure",   950_000, "solid"),
    ("Rackspace Managed Cloud",   "Cloud Infrastructure",   420_000, "underperformer"),
    ("CrowdStrike",               "Security",               680_000, "strong"),
    ("Palo Alto Networks",        "Security",               560_000, "solid"),
    ("Okta",                      "Security",               310_000, "solid"),
    ("SentinelOne",               "Security",               240_000, "incident_prone"),
    ("Cisco Systems",             "Network",                890_000, "solid"),
    ("Juniper Networks",          "Network",                410_000, "inconsistent"),
    ("Zscaler",                   "Network",                350_000, "over_budget"),
    ("Verizon Business",          "Network",                720_000, "underperformer"),
    ("Workday",                   "SaaS-HR",                610_000, "strong"),
    ("ADP",                       "SaaS-HR",                380_000, "solid"),
    ("Greenhouse Software",       "SaaS-HR",                145_000, "inconsistent"),
    ("NetSuite",                  "SaaS-Finance",           520_000, "over_budget"),
    ("SAP Concur",                "SaaS-Finance",           290_000, "solid"),
    ("Coupa Software",            "SaaS-Finance",           260_000, "underperformer"),
    ("Accenture Managed Services","Managed Services",       1_450_000, "inconsistent"),
    ("Cognizant",                 "Managed Services",       980_000, "incident_prone"),
]

PERSONA_PARAMS = {
    "strong":         dict(sla=(97, 1.5), delivery=(96, 2.0), incident_lam=0.3, critical_p=0.02, cost_bias=0.00, cost_std=0.03),
    "solid":          dict(sla=(93, 2.5), delivery=(91, 3.0), incident_lam=0.7, critical_p=0.04, cost_bias=0.01, cost_std=0.04),
    "inconsistent":   dict(sla=(88, 7.0), delivery=(85, 8.0), incident_lam=1.2, critical_p=0.08, cost_bias=0.02, cost_std=0.09),
    "underperformer": dict(sla=(78, 5.0), delivery=(74, 6.0), incident_lam=2.2, critical_p=0.18, cost_bias=0.03, cost_std=0.06),
    "over_budget":    dict(sla=(92, 2.0), delivery=(90, 2.5), incident_lam=0.6, critical_p=0.03, cost_bias=0.16, cost_std=0.05),
    "incident_prone": dict(sla=(90, 2.5), delivery=(89, 3.0), incident_lam=1.8, critical_p=0.22, cost_bias=0.01, cost_std=0.04),
}


def generate_monthly_metrics(vendor_id: str, annual_budget: float, persona: str) -> list[dict]:
    p = PERSONA_PARAMS[persona]
    monthly_budget = annual_budget / 12
    rows = []
    for month in MONTHS:
        sla = float(np.clip(RNG.normal(*p["sla"]), 40, 100))
        delivery = float(np.clip(RNG.normal(*p["delivery"]), 40, 100))
        incidents = int(RNG.poisson(p["incident_lam"]))
        critical = int(RNG.binomial(incidents, p["critical_p"])) if incidents > 0 else 0
        cost_multiplier = 1 + p["cost_bias"] + RNG.normal(0, p["cost_std"])
        actual_cost = round(monthly_budget * max(cost_multiplier, 0.5), 2)
        rows.append({
            "vendor_id": vendor_id, "month": month,
            "sla_compliance_pct": round(sla, 1), "on_time_delivery_pct": round(delivery, 1),
            "incident_count": incidents, "critical_incident_count": critical,
            "actual_cost": actual_cost, "budgeted_cost": round(monthly_budget, 2),
        })
    return rows


def main():
    vendors_rows = []
    metrics_rows = []
    for i, (name, category, budget, persona) in enumerate(VENDORS, start=1):
        vendor_id = f"VND{i:03d}"
        vendors_rows.append({
            "vendor_id": vendor_id, "vendor_name": name, "category": category,
            "annual_budget": budget, "relationship_owner": RNG.choice(OWNERS),
            "contract_start": f"20{RNG.integers(20, 24)}-{RNG.integers(1,13):02d}-01",
        })
        metrics_rows.extend(generate_monthly_metrics(vendor_id, budget, persona))

    vendors_df = pd.DataFrame(vendors_rows)
    metrics_df = pd.DataFrame(metrics_rows)

    vendors_df.to_csv(DATA_DIR / "vendors.csv", index=False)
    metrics_df.to_csv(DATA_DIR / "vendor_monthly_metrics.csv", index=False)

    db_path = DATA_DIR / "vendor_scorecard.db"
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.executescript((ROOT / "sql" / "schema.sql").read_text())
    vendors_df.to_sql("vendors", conn, if_exists="append", index=False)
    metrics_df.insert(0, "metric_id", range(1, len(metrics_df) + 1))
    metrics_df.to_sql("vendor_monthly_metrics", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()

    print(f"Wrote {len(vendors_df)} vendors, {len(metrics_df)} monthly metric rows")
    print(f"-> {DATA_DIR / 'vendors.csv'}")
    print(f"-> {DATA_DIR / 'vendor_monthly_metrics.csv'}")
    print(f"-> {db_path}")


if __name__ == "__main__":
    main()
