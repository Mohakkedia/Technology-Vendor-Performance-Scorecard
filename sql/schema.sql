-- schema.sql
-- ------------
-- Schema for the Technology Vendor Performance Scorecard. Two tables:
-- one row per vendor (contract/category metadata), one row per
-- vendor-month (the operational metrics the scorecard is built from).

DROP TABLE IF EXISTS vendors;
CREATE TABLE vendors (
    vendor_id       TEXT PRIMARY KEY,
    vendor_name     TEXT NOT NULL,
    category        TEXT NOT NULL,      -- e.g. Cloud Infrastructure, Security, Network, SaaS-HR, SaaS-Finance
    annual_budget    REAL NOT NULL,
    relationship_owner TEXT NOT NULL,
    contract_start   TEXT NOT NULL
);

DROP TABLE IF EXISTS vendor_monthly_metrics;
CREATE TABLE vendor_monthly_metrics (
    metric_id            INTEGER PRIMARY KEY,
    vendor_id            TEXT NOT NULL REFERENCES vendors(vendor_id),
    month                TEXT NOT NULL,          -- 'YYYY-MM'
    sla_compliance_pct    REAL NOT NULL,          -- % of SLA targets met that month
    on_time_delivery_pct   REAL NOT NULL,         -- % of deliverables/tickets closed on time
    incident_count          INTEGER NOT NULL,      -- # of service incidents attributed to vendor
    critical_incident_count  INTEGER NOT NULL,     -- subset of incident_count rated critical/P1
    actual_cost              REAL NOT NULL,         -- actual spend that month
    budgeted_cost              REAL NOT NULL         -- budgeted spend that month
);

CREATE INDEX idx_metrics_vendor ON vendor_monthly_metrics(vendor_id);
CREATE INDEX idx_metrics_month ON vendor_monthly_metrics(month);
