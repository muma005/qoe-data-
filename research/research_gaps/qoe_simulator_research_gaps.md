# Research Gap Report: Quality of Earnings (QoE) Public Evidence Deficits and Acquisition Strategy

This report identifies the critical aspects of real-world Quality of Earnings (QoE) and Financial Due Diligence (FDD) work that remain unsupported by publicly accessible datasets, establishes the root causes of these data voids, and outlines actionable acquisition strategies to obtain the missing records.

---

## 1. Executive Summary of Public Domain Gaps

While public open-data portals, academic repositories, and regulatory filings provide substantial empirical evidence for macro-financial statements, public sector vouchers, and retail transactions, **they do not contain the proprietary, highly sensitive accounting workpapers that form the core of private middle-market M&A due diligence**.

```
+─────────────────────────────────────────────────────────────────────────────────+
| QoE INFORMATION ACCESS SPECTRUM                                                 |
+─────────────────────────────────────────────────────────────────────────────────+
| ACCESSIBLE IN PUBLIC DOMAIN         │ RESTRICTED / PRIVATE M&A DOMAIN           |
| (Found & Acquired)                  │ (The Critical QoE Gaps)                   |
|─────────────────────────────────────┼───────────────────────────────────────────|
| • Audited Public 10-K / 10-Q (SEC)  │ • Private Company Monthly Trial Balances  |
| • Municipal Employee Pay (DataSF)   │ • Detailed General Ledger Journal Entries |
| • E-Commerce Sales Invoices (UCI)   │ • Seller Add-Back Workpaper Schedules     |
| • Public Spend Vouchers (GOV.UK)    │ • Customer-Level SaaS MRR/ARR Waterfalls  |
| • Bank Transactions (Czech Bank)    │ • Aged AR & AP Subledgers with Due Dates  |
| • Public Examiner Reports (Lehman)  │ • SKU-Level Inventory Obsolescence Binders|
| • Aggregated Tax Benchmarks (IRS)   │ • Actual Corporate Tax Returns (Form 1120)|
+─────────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Deep Dive: The Seven Critical QoE Data Gaps

### Gap 1: Transaction-Level General Ledger Journal Entries for Private Companies
- **What is Missing:** Unadjusted, monthly general ledger (GL) journal entries for private operating companies ($10M–$100M revenue), featuring account numbers, transaction dates, debit and credit values, journal entry descriptions, preparer/approver IDs, and journal source codes (e.g. general journal `GJ`, sales journal `SJ`, cash disbursements `CD`).
- **Root Cause:** Enterprise ERP databases (SAP, NetSuite, QuickBooks) are strictly proprietary and considered core business secrets. Furthermore, confidentiality agreements (NDAs) between targets and transaction advisory firms legally preclude publication.
- **Why Synthetic Data Fails Here:** As revealed in our qualification of the Marco Schreyer benchmark, synthetic journal entries lack authentic human behavioral anomalies—such as end-of-quarter manual plug entries, reversed accruals, round-dollar suspense postings, and narrative typos—that QoE auditors investigate.

### Gap 2: Disaggregated Seller Add-Back Schedules & Normalization Workpapers
- **What is Missing:** Detailed management add-back bridge schedules with supporting invoice documentation, specifically:
  - Personal / discretionary expenses of business owners (country club dues, personal vehicle leases, non-business travel, family health insurance).
  - Non-arm's length compensation for family members or related-party officers.
  - One-time litigation settlements, severance packages, and facility move expenses.
  - Pro forma run-rate adjustments for price increases, new customer wins, or facility closures.
- **Root Cause:** These schedules are compiled exclusively inside confidential M&A Virtual Data Rooms (VDRs) such as Intralinks, Datasite, or Firmex, accessible only to prospective buyers and diligence teams.

### Gap 3: Customer-Level Recurring Revenue Waterfalls & Churn Schedules
- **What is Missing:** Disaggregated customer-by-month billing and revenue recognition schedules for subscription, software, or recurring service businesses:
  - Monthly Recurring Revenue (MRR) and Annual Recurring Revenue (ARR) bridges: Beginning ARR + New Bookings + Expansion ARR - Contraction ARR - Churn = Ending ARR.
  - Cohort retention tables and Net Revenue Retention (NRR) curves.
  - Contract master records detailing billing terms, multi-year commitments, termination-for-convenience clauses, and service level agreement (SLA) penalties.
- **Root Cause:** Releasing customer lists, specific contract values, and churn history represents catastrophic competitive disclosure.

### Gap 4: Aged Accounts Receivable (AR) Subledgers with Explicit Due Dates & Collections
- **What is Missing:** Daily or monthly AR subledgers tracking each invoice from issuance through collection:
  - Invoice date, payment due date, agreed payment terms (Net 30, Net 60), actual payment receipt date, days past due, and disputed balance flags.
  - Specific bad debt write-offs and allowance for doubtful accounts roll-forwards.
- **Root Cause:** Available open-data sets provide order dates and payment values (e.g. Olist, UCI Retail), but do not track credit risk aging buckets (Current, 1–30, 31–60, 61–90, 91+ days past due) or formal collection dispute logs.

### Gap 5: Inventory Valuation, SKU-Level Aging & Obsolescence Reserve Reports
- **What is Missing:** Perpetual inventory subledgers containing SKU-level unit costs, standard cost variance roll-ups, historical movement turnover ratios, and excess/obsolescence (E&O) reserves calculated against lower-of-cost-or-net-realizable-value (LCNRV).
- **Root Cause:** Inventory details contain proprietary manufacturing bill of materials (BOM) and margin formulas that competitors could reverse-engineer.

### Gap 6: Disaggregated Corporate Income Tax Returns (Form 1120 / Schedule M-3)
- **What is Missing:** Entity-level federal, state, and local tax returns reconciling financial statement net income (book income) to taxable income:
  - Permanent differences (meals and entertainment disallowance, tax-exempt municipal interest).
  - Temporary differences (MACRS accelerated tax depreciation vs straight-line GAAP depreciation, deferred revenue timing, bad debt reserve deductions).
  - Sales and use tax filings across economic nexus jurisdictions (Wayfair audit risk).
- **Root Cause:** **Federal Statutory Prohibition:** Under 26 U.S.C. § 6103, federal corporate income tax returns are confidential government records protected under criminal penalty of law. Only anonymized industry aggregates (IRS SOI Publication 16) are lawful to publish.

### Gap 7: Debt Payoff Letters, Covenants & Borrowing Base Certificates
- **What is Missing:** Bank payoff letters specifying exact per diem interest, prepayment penalties, capital lease payoff balances, and monthly borrowing base certificates (AR and inventory collateral formulas) for revolving credit facilities.
- **Root Cause:** Credit facility agreements and collateral certificates are restricted to corporate borrowers and commercial lending syndicates.

---

## 3. Recommended Acquisition Pathways & Counterparty Engagement

To bridge these gaps without compromising ethics, legality, or authenticity, the QoE Simulator project should pursue four targeted acquisition channels:

```
┌────────────────────────────────────────────────────────────────────────┐
| STRATEGIC ACQUISITION PATHWAYS FOR PROPRIETARY QoE EVIDENCE             |
├────────────────────────────────────────────────────────────────────────┤
│ 1. Transaction Advisory Firm Partnerships (Anonymized Deal Archives)   │
│ 2. Public Insolvency & Bankruptcy Dockets (PACER / CourtListener)      │
│ 3. Small-Business ERP & Accounting SaaS Research Partnerships          │
│ 4. Private Equity Sponsor Historical Archive Access                    │
└────────────────────────────────────────────────────────────────────────┘
```

### Pathway 1: Transaction Advisory Practice Partnerships (The Gold Standard)
- **Target Counterparties:** National transaction advisory and financial due diligence practices (e.g. Alvarez & Marsal, FTI Consulting, Riveron, Stout, CohnReznick, BDO, RSM, PKF).
- **Proposed Mechanism:** Propose an academic or research partnership under a strict Data Transfer Agreement (DTA). The advisory firm anonymizes completed historical diligence files (3–5 years old):
  - Strip company names, brand names, and identifiable product tags.
  - Multiplicatively scale financial amounts by a random scalar ($S \in [0.7, 1.3]$) to preserve exact percentage ratios, margin structures, and distributional distributions while masking absolute dollar figures.
- **Deliverable Target:** 5–10 complete, closed QoE workpaper binders across manufacturing, healthcare, software, and consumer services.

### Pathway 2: Public Bankruptcy Dockets (PACER, RECAP & Claims Agents)
- **Target Counterparties:** U.S. Bankruptcy Courts (SDNY, District of Delaware, Southern District of Texas) and claims administration portals (Kroll Restructuring Administration, Epiq Corporate Restructuring, Omni Bridgeway, Stretto).
- **Proposed Mechanism:** In Chapter 11 bankruptcy filings, corporate debtors are legally required to file unsealed financial schedules under penalty of perjury:
  - **Statement of Financial Affairs (SOFA):** Details all payments to insiders, related-party distributions, owner compensation, and extraordinary payments in the 1–3 years preceding filing.
  - **Schedule E/F (Creditors Holding Unsecured Claims):** The complete accounts payable subledger listing every trade vendor, invoice claim, invoice date, and disputed status.
  - **Schedule G (Executory Contracts and Unexpired Leases):** Complete inventories of commercial lease liabilities, customer agreements, and licensing commitments.
  - **Fee Applications & Forensic Examiner Reports:** Advisory firms (such as A&M or FTI) file detailed narrative time sheets, forensic audit workpapers, and cash burn schedules as public court exhibits.
- **Feasibility:** High; all filings are public domain and accessible via CourtListener / PACER for minimal statutory download fees.

### Pathway 3: Accounting SaaS & ERP Platform Research Partnerships
- **Target Counterparties:** Cloud accounting platform research divisions (e.g. Intuit QuickBooks Research, Xero Small Business Insights, Sage Data, NetSuite).
- **Proposed Mechanism:** Apply for researcher API access to anonymized aggregate small-to-medium enterprise (SME) ledger data. Many accounting platforms publish macroeconomic indices but also grant academic access to anonymized journal entry transaction corpuses under privacy-preserving Differential Privacy (DP) frameworks.
- **Feasibility:** Moderate; requires formal institutional research credentials.

### Pathway 4: Private Equity Sponsor Historical Archives
- **Target Counterparties:** Lower middle-market private equity funds ($100M–$500M AUM) with exited portfolio companies.
- **Proposed Mechanism:** Request access to historical due diligence files of portfolio companies that have already been liquidated or fully exited (where competitive sensitivity is moot).
- **Feasibility:** High when framed as an educational or modeling initiative for financial talent development.
