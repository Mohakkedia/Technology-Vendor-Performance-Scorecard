"""
build_scorecard.py
---------------------
Computes the trailing-12-month weighted vendor scorecard (SLA 30%,
On-Time Delivery 25%, Incident Score 25%, Cost Variance 20%), matching
the scoring logic documented in sql/scorecard_queries.sql exactly, and
assigns each vendor a tier: Strategic / Monitor / Replace, with an
automatic Replace override for vendors with 3+ critical incidents.

Run:
    python scripts/build_scorecard.py
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "vendor_scorecard.db"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(exist_ok=True)

WEIGHTS = {"sla": 0.30, "delivery": 0.25, "incident": 0.25, "cost": 0.20}


def compute_scorecard() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    # Create the trailing-12mo view (defined canonically in sql/scorecard_queries.sql)
    view_sql = """
    CREATE VIEW IF NOT EXISTS v_vendor_trailing12mo AS
    SELECT
        v.vendor_id, v.vendor_name, v.category, v.annual_budget, v.relationship_owner,
        ROUND(AVG(m.sla_compliance_pct), 1)      AS avg_sla_compliance_pct,
        ROUND(AVG(m.on_time_delivery_pct), 1)    AS avg_on_time_delivery_pct,
        SUM(m.incident_count)                      AS total_incidents,
        SUM(m.critical_incident_count)              AS total_critical_incidents,
        ROUND(SUM(m.actual_cost), 0)                 AS total_actual_cost,
        ROUND(SUM(m.budgeted_cost), 0)                AS total_budgeted_cost,
        ROUND(100.0 * (SUM(m.actual_cost) - SUM(m.budgeted_cost)) / SUM(m.budgeted_cost), 1) AS cost_variance_pct
    FROM vendors v
    JOIN vendor_monthly_metrics m ON m.vendor_id = v.vendor_id
    GROUP BY v.vendor_id, v.vendor_name, v.category, v.annual_budget, v.relationship_owner;
    """
    conn.executescript(view_sql)
    df = pd.read_sql("SELECT * FROM v_vendor_trailing12mo", conn)
    conn.close()

    df["sla_score"] = df["avg_sla_compliance_pct"]
    df["delivery_score"] = df["avg_on_time_delivery_pct"]
    df["incident_score"] = (100 - df["total_incidents"] * 8 - df["total_critical_incidents"] * 20).clip(lower=0)
    df["cost_score"] = (100 - df["cost_variance_pct"].abs() * 4).clip(lower=0)

    df["composite_score"] = (
        WEIGHTS["sla"] * df["sla_score"]
        + WEIGHTS["delivery"] * df["delivery_score"]
        + WEIGHTS["incident"] * df["incident_score"]
        + WEIGHTS["cost"] * df["cost_score"]
    ).round(1)

    def assign_tier(row):
        if row["total_critical_incidents"] >= 3:
            return "Replace"
        if row["composite_score"] >= 80:
            return "Strategic"
        if row["composite_score"] >= 60:
            return "Monitor"
        return "Replace"

    df["tier"] = df.apply(assign_tier, axis=1)
    df["tier_override_reason"] = df.apply(
        lambda r: "3+ critical incidents (auto-Replace override)" if r["total_critical_incidents"] >= 3 else "",
        axis=1,
    )
    return df.sort_values("composite_score", ascending=False).reset_index(drop=True)


def main():
    scorecard = compute_scorecard()
    scorecard.to_csv(OUT_DIR / "vendor_scorecard.csv", index=False)

    tier_counts = scorecard["tier"].value_counts().to_dict()
    summary = {
        "n_vendors": len(scorecard),
        "tier_counts": tier_counts,
        "avg_composite_score": round(scorecard["composite_score"].mean(), 1),
        "total_annual_spend": int(scorecard["total_actual_cost"].sum()),
        "vendors_over_budget_10pct": scorecard[scorecard["cost_variance_pct"] > 10]["vendor_name"].tolist(),
        "vendors_flagged_replace": scorecard[scorecard["tier"] == "Replace"][
            ["vendor_name", "composite_score", "tier_override_reason"]
        ].to_dict("records"),
    }
    (OUT_DIR / "scorecard_summary.json").write_text(json.dumps(summary, indent=2))

    print(scorecard[["vendor_name", "category", "composite_score", "tier"]].to_string(index=False))
    print(f"\nTier counts: {tier_counts}")
    print(f"Wrote {OUT_DIR / 'vendor_scorecard.csv'} and {OUT_DIR / 'scorecard_summary.json'}")


if __name__ == "__main__":
    main()
