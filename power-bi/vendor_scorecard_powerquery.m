// vendor_scorecard_powerquery.m
// --------------------------------
// Power Query M for the Vendor Performance Scorecard Power BI report.
// Two queries: Vendors (dimension) and VendorMonthlyMetrics (fact) —
// load both, then build the relationship VendorMonthlyMetrics[vendor_id]
// -> Vendors[vendor_id] (many-to-one) in Model view.
//
// How to use in Power BI Desktop:
//   Home -> Get Data -> Text/CSV -> select data/vendors.csv
//   Home -> Get Data -> Text/CSV -> select data/vendor_monthly_metrics.csv
//   Home -> Advanced Editor -> paste the matching query below over the
//   auto-generated one, adjusting the file path to your local copy.

// ===== Query: Vendors =====
let
    Source = Csv.Document(File.Contents("data/vendors.csv"), [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, {
        {"vendor_id", type text}, {"vendor_name", type text}, {"category", type text},
        {"annual_budget", type number}, {"relationship_owner", type text}, {"contract_start", type date}
    })
in
    TypedColumns

// ===== Query: VendorMonthlyMetrics =====
let
    Source = Csv.Document(File.Contents("data/vendor_monthly_metrics.csv"), [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, {
        {"vendor_id", type text}, {"month", type text},
        {"sla_compliance_pct", type number}, {"on_time_delivery_pct", type number},
        {"incident_count", Int64.Type}, {"critical_incident_count", Int64.Type},
        {"actual_cost", type number}, {"budgeted_cost", type number}
    }),
    // Add a proper Date column from the "YYYY-MM" text month, for the
    // report's date-axis visuals and any time-intelligence DAX
    AddedMonthDate = Table.AddColumn(TypedColumns, "month_date", each Date.FromText([month] & "-01"), type date)
in
    AddedMonthDate

// ===== Query: DimDate (a minimal calendar table for time-intelligence DAX) =====
let
    StartDate = #date(2025, 1, 1),
    EndDate = #date(2025, 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    Dates = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    TableFromList = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}),
    TypedDate = Table.TransformColumnTypes(TableFromList, {{"Date", type date}}),
    AddedYear = Table.AddColumn(TypedDate, "Year", each Date.Year([Date]), Int64.Type),
    AddedMonth = Table.AddColumn(AddedYear, "Month", each Date.Month([Date]), Int64.Type),
    AddedMonthName = Table.AddColumn(AddedMonth, "MonthName", each Date.ToText([Date], "MMM yyyy"), type text),
    AddedQuarter = Table.AddColumn(AddedMonthName, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text)
in
    AddedQuarter
