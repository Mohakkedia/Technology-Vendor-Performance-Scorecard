// build_qbr_deck.js
// --------------------
// Generates the Quarterly Business Review deck for Rackspace Managed
// Cloud (composite score 59.2, tier Replace) — the kind of deck a
// vendor manager would present TO the vendor to walk through the
// scorecard data and set expectations for the next quarter.
// Run: node scripts/build_qbr_deck.js
// Output: outputs/QBR_Rackspace_Managed_Cloud.pptx

const pptxgen = require("pptxgenjs");

const NAVY = "1F4E78";
const GOLD = "C9A227";
const GREY = "595959";
const WHITE = "FFFFFF";
const GREEN = "2E7D32";
const AMBER = "B7791F";
const RED = "C0392B";
const LIGHT = "EAF1F8";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Vendor Management";
pres.title = "QBR - Rackspace Managed Cloud";

function addFooter(slide, pageNum) {
  slide.addText("Quarterly Business Review — Rackspace Managed Cloud", {
    x: 0.4, y: 7.05, w: 9, h: 0.3, fontSize: 9, color: GREY, isTextBox: true,
  });
  slide.addText(String(pageNum), {
    x: 12.6, y: 7.05, w: 0.5, h: 0.3, fontSize: 9, color: GREY, align: "right", isTextBox: true,
  });
}

// ---- Slide 1: Title ----
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape("rect", { x: 0, y: 4.55, w: 13.33, h: 0.06, fill: { color: GOLD } });
  s.addText("Quarterly Business Review", {
    x: 0.7, y: 2.5, w: 12, h: 1.0, fontSize: 40, bold: true, color: WHITE, isTextBox: true,
  });
  s.addText("Rackspace Managed Cloud — Cloud Infrastructure Services", {
    x: 0.7, y: 3.5, w: 11.5, h: 0.6, fontSize: 20, color: "CFE0F0", italic: true, isTextBox: true,
  });
  s.addText("Q4 2025 Review Period: January – December 2025  |  Prepared by Vendor Management", {
    x: 0.7, y: 6.5, w: 11, h: 0.4, fontSize: 13, color: "9FB8D6", isTextBox: true,
  });
}

// ---- Slide 2: Executive Summary ----
{
  const s = pres.addSlide();
  s.addText("Executive Summary", { x: 0.5, y: 0.35, w: 12, h: 0.6, fontSize: 28, bold: true, color: NAVY, isTextBox: true });
  s.addShape("line", { x: 0.5, y: 1.0, w: 12.3, h: 0, line: { color: GOLD, width: 2 } });

  // KPI cards
  const kpis = [
    ["59.2", "Composite Score  /  100", RED],
    ["Replace", "Current Tier", RED],
    ["77.8%", "Avg SLA Compliance", AMBER],
    ["$434,198", "Actual Spend (Budget: $420,000)", AMBER],
  ];
  let x = 0.6;
  for (const [big, label, color] of kpis) {
    s.addShape("rect", { x, y: 1.3, w: 2.9, h: 1.6, fill: { color } });
    s.addText(big, { x, y: 1.45, w: 2.9, h: 0.8, fontSize: 26, bold: true, color: WHITE, align: "center", isTextBox: true });
    s.addText(label, { x: x + 0.1, y: 2.25, w: 2.7, h: 0.55, fontSize: 10.5, color: "F0F0F0", align: "center", isTextBox: true });
    x += 3.05;
  }

  s.addText("Key Points", { x: 0.6, y: 3.3, w: 12, h: 0.4, fontSize: 16, bold: true, color: NAVY, isTextBox: true });
  const points = [
    "Composite score of 59.2 places Rackspace in the Replace tier — driven primarily by inconsistent SLA compliance (range: 71.4% – 87.2% month to month) and two months with critical incidents.",
    "3 critical incidents recorded in 2025 (Feb, Jun, Sep) triggers an automatic Replace-tier override under our scoring policy, independent of the blended composite score.",
    "Spend is running 3.4% over the $420,000 annual budget ($434,198 actual) — a secondary but contributing factor.",
    "This review is intended to set clear, measurable improvement expectations before the January contract renewal decision.",
  ];
  let y = 3.75;
  for (const p of points) {
    s.addShape("rect", { x: 0.6, y, w: 0.08, h: 0.55, fill: { color: GOLD } });
    s.addText(p, { x: 0.85, y: y - 0.05, w: 11.7, h: 0.65, fontSize: 13, color: "333333", isTextBox: true });
    y += 0.72;
  }
  addFooter(s, 2);
}

// ---- Slide 3: SLA & Delivery Trend ----
{
  const s = pres.addSlide();
  s.addText("SLA Compliance & On-Time Delivery Trend", { x: 0.5, y: 0.35, w: 12.3, h: 0.6, fontSize: 24, bold: true, color: NAVY, isTextBox: true });
  s.addShape("line", { x: 0.5, y: 1.0, w: 12.3, h: 0, line: { color: GOLD, width: 2 } });

  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const sla = [74.7,71.6,83.5,77.1,76.0,81.2,71.4,80.7,72.6,84.0,73.6,87.2];
  const delivery = [76.7,75.0,76.6,71.7,74.0,61.7,74.2,82.0,74.5,69.6,73.4,91.4];

  s.addChart(pres.ChartType.line, [
    { name: "SLA Compliance %", labels: months, values: sla },
    { name: "On-Time Delivery %", labels: months, values: delivery },
  ], {
    x: 0.6, y: 1.3, w: 12.1, h: 5.0,
    showTitle: false, showLegend: true, legendPos: "b",
    lineDataSymbol: "circle", lineDataSymbolSize: 5,
    chartColors: [NAVY, GOLD],
    valAxisTitle: "%", showValAxisTitle: true,
    valAxisMinVal: 50, valAxisMaxVal: 100,
    catAxisLabelColor: "333333", valAxisLabelColor: "333333",
    valGridLine: { color: "E0E0E0", size: 1 },
  });
  s.addText("Target: 90% SLA compliance, 90% on-time delivery. Neither threshold was met in any month of 2025.", {
    x: 0.6, y: 6.35, w: 12, h: 0.4, fontSize: 12, italic: true, color: RED, isTextBox: true,
  });
  addFooter(s, 3);
}

// ---- Slide 4: Incident Summary ----
{
  const s = pres.addSlide();
  s.addText("Service Incident Summary", { x: 0.5, y: 0.35, w: 12.3, h: 0.6, fontSize: 24, bold: true, color: NAVY, isTextBox: true });
  s.addShape("line", { x: 0.5, y: 1.0, w: 12.3, h: 0, line: { color: GOLD, width: 2 } });

  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const incidents = [0,4,3,2,1,3,2,2,5,2,2,0];
  const critical = [0,1,0,0,0,1,0,0,2,0,0,0];

  s.addChart(pres.ChartType.bar, [
    { name: "Total Incidents", labels: months, values: incidents },
    { name: "Critical Incidents", labels: months, values: critical },
  ], {
    x: 0.6, y: 1.3, w: 8.2, h: 5.0,
    barDir: "col", barGrouping: "stacked",
    showTitle: false, showLegend: true, legendPos: "b",
    chartColors: [AMBER, RED],
    valAxisTitle: "Incident count", showValAxisTitle: true,
    catAxisLabelColor: "333333", valAxisLabelColor: "333333",
    valGridLine: { color: "E0E0E0", size: 1 },
  });

  s.addShape("rect", { x: 9.0, y: 1.3, w: 3.8, h: 5.0, fill: { color: LIGHT } });
  s.addText("2025 Totals", { x: 9.2, y: 1.5, w: 3.4, h: 0.4, fontSize: 15, bold: true, color: NAVY, isTextBox: true });
  const totals = [["28", "Total incidents"], ["4", "Critical incidents"], ["3", "Months with a critical incident"]];
  let ky = 2.0;
  for (const [big, label] of totals) {
    s.addText(big, { x: 9.2, y: ky, w: 3.4, h: 0.55, fontSize: 26, bold: true, color: RED, isTextBox: true });
    s.addText(label, { x: 9.2, y: ky + 0.55, w: 3.4, h: 0.4, fontSize: 11, color: "333333", isTextBox: true });
    ky += 1.15;
  }
  s.addText("Policy: 3+ critical incidents in a trailing 12-month period triggers an automatic Replace-tier flag.", {
    x: 9.2, y: 5.5, w: 3.4, h: 0.7, fontSize: 10.5, italic: true, color: GREY, isTextBox: true,
  });
  addFooter(s, 4);
}

// ---- Slide 5: Cost vs Budget ----
{
  const s = pres.addSlide();
  s.addText("Actual Spend vs. Budget", { x: 0.5, y: 0.35, w: 12.3, h: 0.6, fontSize: 24, bold: true, color: NAVY, isTextBox: true });
  s.addShape("line", { x: 0.5, y: 1.0, w: 12.3, h: 0, line: { color: GOLD, width: 2 } });

  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const actual = [33476,35187,39670,37401,36240,37973,38156,36421,36713,34938,33747,35277];
  const budget = new Array(12).fill(35000);

  s.addChart(pres.ChartType.line, [
    { name: "Actual Cost ($)", labels: months, values: actual },
    { name: "Budgeted Cost ($)", labels: months, values: budget },
  ], {
    x: 0.6, y: 1.3, w: 12.1, h: 5.0,
    showTitle: false, showLegend: true, legendPos: "b",
    lineDataSymbol: "circle", lineDataSymbolSize: 5,
    chartColors: [RED, "808080"],
    valAxisTitle: "$", showValAxisTitle: true,
    catAxisLabelColor: "333333", valAxisLabelColor: "333333",
    valGridLine: { color: "E0E0E0", size: 1 },
  });
  s.addText("Annual actual: $434,198  |  Annual budget: $420,000  |  Variance: +3.4% over budget", {
    x: 0.6, y: 6.35, w: 12, h: 0.4, fontSize: 12, italic: true, color: "333333", isTextBox: true,
  });
  addFooter(s, 5);
}

// ---- Slide 6: Score Breakdown ----
{
  const s = pres.addSlide();
  s.addText("Composite Score Breakdown", { x: 0.5, y: 0.35, w: 12.3, h: 0.6, fontSize: 24, bold: true, color: NAVY, isTextBox: true });
  s.addShape("line", { x: 0.5, y: 1.0, w: 12.3, h: 0, line: { color: GOLD, width: 2 } });

  const labels = ["SLA Score (30%)", "Delivery Score (25%)", "Incident Score (25%)", "Cost Score (20%)"];
  const values = [77.8, 73.5, 8.0, 86.6];
  s.addChart(pres.ChartType.bar, [
    { name: "Score (0-100)", labels, values },
  ], {
    x: 0.8, y: 1.4, w: 8.2, h: 4.8,
    barDir: "bar",
    showTitle: false, showLegend: false,
    showValue: true, dataLabelPosition: "outEnd",
    chartColors: [NAVY],
    valAxisMinVal: 0, valAxisMaxVal: 100,
    catAxisLabelColor: "333333", valAxisLabelColor: "333333",
    valGridLine: { color: "E0E0E0", size: 1 },
  });
  s.addShape("rect", { x: 9.2, y: 1.4, w: 3.6, h: 4.8, fill: { color: LIGHT } });
  s.addText("Weighted Composite = 59.2", { x: 9.4, y: 1.6, w: 3.2, h: 0.5, fontSize: 15, bold: true, color: NAVY, isTextBox: true });
  s.addText(
    "The Incident Score (8.0/100) is the single biggest drag on the composite — 28 total incidents and 4 critical incidents " +
    "over 12 months score far below the other three components. Improving incident volume, even without a change in SLA " +
    "compliance, would move Rackspace out of the Replace tier.",
    { x: 9.4, y: 2.2, w: 3.2, h: 3.8, fontSize: 12, color: "333333", isTextBox: true }
  );
  addFooter(s, 6);
}

// ---- Slide 7: Action Plan ----
{
  const s = pres.addSlide();
  s.addText("Improvement Plan & Next Steps", { x: 0.5, y: 0.35, w: 12.3, h: 0.6, fontSize: 26, bold: true, color: NAVY, isTextBox: true });
  s.addShape("line", { x: 0.5, y: 1.0, w: 12.3, h: 0, line: { color: GOLD, width: 2 } });

  const items = [
    ["Root-cause the September incident spike", "5 incidents including 2 critical in a single month — request a formal RCA (root cause analysis) report within 15 business days."],
    ["Commit to a 90% SLA compliance floor", "Current trailing average is 77.8%; request a written improvement commitment with monthly checkpoints for Q1 2026."],
    ["Reduce critical incidents to zero for 2 consecutive quarters", "This is the specific condition that would lift the automatic Replace-tier override at the next review."],
    ["30-day follow-up checkpoint", "A shorter interim review (not a full QBR) to confirm the RCA and Q1 plan are on track before the annual renewal decision."],
  ];
  let y = 1.35;
  for (const [t, d] of items) {
    s.addShape("rect", { x: 0.5, y, w: 0.08, h: 1.05, fill: { color: GOLD } });
    s.addText(t, { x: 0.75, y, w: 11.8, h: 0.45, fontSize: 16, bold: true, color: NAVY, isTextBox: true });
    s.addText(d, { x: 0.75, y: y + 0.45, w: 11.8, h: 0.6, fontSize: 12.5, color: "333333", isTextBox: true });
    y += 1.3;
  }
  addFooter(s, 7);
}

pres.writeFile({ fileName: "outputs/QBR_Rackspace_Managed_Cloud.pptx" }).then(() => {
  console.log("Wrote outputs/QBR_Rackspace_Managed_Cloud.pptx");
});
