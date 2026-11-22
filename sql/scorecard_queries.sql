-- scorecard_queries.sql
-- ------------------------
-- Aggregates the trailing 12 months of vendor_monthly_metrics into a
-- single weighted performance score per vendor. Run against the SQLite
-- DB built by scripts/generate_vendor_data.py, via scripts/run_sql_queries.py
-- (a pure-Python runner, since this sandbox has no sqlite3 CLI binary).

-- 1. Trailing-12-month vendor summary — the input to the weighted score.
DROP VIEW IF EXISTS v_vendor_trailing12mo;
CREATE VIEW v_vendor_trailing12mo AS
SELECT
    v.vendor_id,
    v.vendor_name,
    v.category,
    v.annual_budget,
    v.relationship_owner,
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

-- 2. Weighted scorecard scoring logic (documented here as the source of
--    truth; computed in Python in scripts/build_scorecard.py because the
--    MAX(0, ...) floor pattern used per sub-score isn't portable across
--    all SQLite builds as a single scalar expression):
--      sla_score      = avg_sla_compliance_pct                              (already 0-100)
--      delivery_score = avg_on_time_delivery_pct                            (already 0-100)
--      incident_score = MAX(0, 100 - total_incidents*8 - total_critical_incidents*20)
--      cost_score     = MAX(0, 100 - ABS(cost_variance_pct)*4)
--      composite_score = 0.30*sla_score + 0.25*delivery_score + 0.25*incident_score + 0.20*cost_score
--      tier = 'Strategic' if composite_score >= 80
--           = 'Monitor'   if composite_score >= 60
--           = 'Replace'   otherwise
--      override: tier = 'Replace' if total_critical_incidents >= 3, regardless of composite_score

-- 3. Vendors with 3+ critical incidents in the trailing 12 months —
--    the automatic "Replace" tier override described above.
SELECT vendor_name, category, total_critical_incidents, total_incidents
FROM v_vendor_trailing12mo
WHERE total_critical_incidents >= 3
ORDER BY total_critical_incidents DESC;

-- 4. Spend concentration by category — useful context for the QBR: which
--    categories carry the most budget exposure.
SELECT
    category,
    COUNT(*) AS n_vendors,
    ROUND(SUM(total_actual_cost), 0) AS total_spend,
    ROUND(AVG(avg_sla_compliance_pct), 1) AS avg_sla_compliance_pct
FROM v_vendor_trailing12mo
GROUP BY category
ORDER BY total_spend DESC;

-- 5. Cost variance outliers — vendors more than 10% over budget, a common
--    QBR talking point independent of the blended score.
SELECT vendor_name, category, total_actual_cost, total_budgeted_cost, cost_variance_pct
FROM v_vendor_trailing12mo
WHERE cost_variance_pct > 10
ORDER BY cost_variance_pct DESC;
