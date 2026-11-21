# Revenue Diligence Evidence & Professional Judgment Matrix
**Document Reference:** `QOE-EVID-MATRIX-06`  
**Workstream:** `06 — Revenue and Margin Quality`  
**Classification:** Quality of Earnings Evidentiary Standard & Audit Governance Matrix  

---

## 1. Evidentiary Hierarchy & Standard of Commercial Proof

In revenue quality and commercial due diligence, oral representations regarding customer relationships, pipeline strength, or pricing power are **inadmissible as primary audit evidence**.

```
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    EVIDENTIARY HIERARCHY                                           |
|                                                                                                    |
|   [TIER 1] EXECUTED EXTERNAL COMMERCIAL CONTRACTS & BANK CASH PROOF (Highest Reliability)          |
|   • Executed Master Service Agreements (MSAs), signed purchase orders, binding rate cards.         |
|   • Bank statements and lockbox remittance advices confirming third-party cash settlement.         |
|                                                                                                    |
|   [TIER 2] THIRD-PARTY LOGISTICS & FULFILLMENT DOCUMENTATION (High Reliability)                    |
|   • Carrier Bills of Lading (BOL), signed Proof of Delivery (POD), freight tracking logs.          |
|   • Electronic Data Interchange (EDI) 850/856 order acknowledgment and advance ship notices.       |
|                                                                                                    |
|   [TIER 3] INTERNAL ERP SALES SUBLEDGERS & BILLING SCHEDULES (Moderate Reliability)                |
|   • Itemized sales registers, credit memo journals, deferred revenue waterfall subledgers.         |
|   • Standard costing routings, SKU bill of materials (BOM), inventory relief reports.              |
|                                                                                                    |
|   [TIER 4] CRM PIPELINES & INTERNAL MANAGEMENT MEMOS (Conditional / Unverified)                    |
|   • Salesforce / HubSpot pipeline stages, soft sales forecasts, unvetted quote logs.               |
|   • Unsigned contract drafts, internal volume rebate accrual calculation spreadsheets.             |
|                                                                                                    |
|   [TIER 5] UNSUBSTANTIATED ORAL REPRESENTATIONS (Inadmissible for Quality of Earnings)             |
|   • Founder/management claims: "That customer loves us", "The price increase is 100% locked in".  |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Professional Judgment & Verification Matrix

The following matrix governs the evidentiary testing, red flags, and review requirements for revenue diligence:

| Diligence Focus Area | Primary Documentary Evidence | Secondary / Corroborating Evidence | Forensic Red Flags & Disallowance Triggers | Mandatory Audit Verification Procedure | Requisite Sign-Off Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sales Ledger-to-GL Tie-Out** | Line-item ERP sales register, Credit memo journal | General Ledger trial balance, Audited financial statements | Unreconciled variances between subledger and GL >0.5%; manual topside JEs posted to revenue. | Reconcile invoice sums to GL control accounts; verify debits to AR and credits to sales; test journal voucher approvals. | Senior Analyst + Manager |
| **Customer Concentration** | Customer master database, Tax ID roll-up tables | Parent-subsidiary corporate filings, Billing address records | Multiple child billing accounts masking >20% concentration in a single corporate parent. | Group accounts by ultimate corporate parent; calculate Top 5/10/20 shares; compute Herfindahl-Hirschman Index (HHI). | Senior Analyst + Manager |
| **Customer Cohort Retention** | Multi-year invoice histories with customer acquisition dates | CRM account creation logs, Contract start dates | Mature cohort revenue decay >15% annually; growth masked entirely by high new-logo churn. | Assemble vintage cohort matrix; compute annual Logo Retention, Gross Revenue Retention (GRR), and Net Retention (NRR). | Manager + Partner |
| **Price-Volume-Mix (PVM)** | Sales master file with SKU volumes, unit prices, and revenue | Item master catalogs, Published price lists, Freight cards | Volume contraction masked by emergency inflation surcharges; gross margin compression despite price hikes. | Execute Paasche/Laspeyres PVM decomposition; verify that Price + Volume + Mix foot exactly to total revenue variance. | Manager + Partner |
| **ASC 606 Cut-Off & Bill-and-Hold** | Sales invoices dated in final 15 days of fiscal period | Bills of Lading (BOL), Signed carrier delivery receipts (POD) | Invoices dated Dec 31 with carrier pickup in January; FOB Destination shipments recognized prior to delivery. | Sample 15 days before/after year-end; match invoice date to physical carrier delivery date; reverse premature margins. | Manager + Partner |
| **Post-Period Credit Memos** | Credit memo register for first 90 days of subsequent year | Customer dispute correspondence, Warehouse scrap logs | Spike in credit memos issued in Jan/Feb reversing December sales; concessions granted to induce year-end orders. | Inspect post-period credit memos; match to original invoice dates; reverse unrecorded prior-year dilution from EBITDA. | Senior Analyst + Manager |
| **Customer Profitability (Whale Curve)** | Customer-level revenue, direct SKU COGS, freight-out logs | Dedicated customer engineering hours, Return logs | Bottom 20% of accounts generate negative contribution margin; subsidized freight and non-standard packaging. | Allocate direct freight and variable cost-to-serve; rank accounts by net contribution; construct cumulative whale curve. | Senior Analyst + Manager |
| **Commercial Contract Audit** | Executed Master Service Agreements (MSAs), Statements of Work | Customer purchase orders, Rate cards, Surcharge amendments | Contracts lack minimum volume commitments; termination for convenience on 30-day notice; pending RFP rebids. | Sample top customer agreements; extract termination notice, volume tiers, MFN clauses, and price re-opener mechanisms. | Manager + Partner |
| **SaaS ARR Waterfall** | Monthly subscription billing logs (Stripe/Chargebee), SOWs | Bank cash receipts, Deferred revenue subledger | Marketing ARR disconnected from recognized GAAP subscription revenue; churned accounts retained in ARR. | Tie Beginning ARR + New + Expansion - Churn to ending ARR; reconcile cash billings to balance sheet deferred revenue. | Manager + Partner |
| **Lost Customer Run-Rate Haircut** | Customer termination notices, Chapter 11 bankruptcy dockets | Post-period monthly sales logs, Accounts receivable write-offs | Major customer exited mid-period or post-close, but historical LTM still includes unrepeatable earnings. | Calculate customer trailing 12-month revenue and contribution margin; model full-year pro-forma run-rate deduction. | Quality Partner |

---

## 3. Workpaper Cross-Referencing & Audit Trail Standards

To maintain numerical traceability throughout the simulator, every revenue workpaper must maintain strict alphanumeric cross-referencing:

```
[SRC-SL-INV] Raw ERP Sales Invoice Register
   │
   ▼
[PREP-REV] Cleansed & Deduplicated Sales Dataset (Workstream 02)
   │
   ▼
[REC-REV] General Ledger Revenue Tie-Out Schedule (Workstream 03)
   │
   ▼
[ANA-REV] Top-Level Historical Sales Trend Schedule (Workstream 04)
   │
   ▼
[REV-xxx] Revenue Quality Analytical Schedule (Workstream 06)
   ├── [CUST-xxx] Top Customer Account Dossier & Contract Review
   ├── [COH-xxx] Multi-Year Customer Vintage Cohort Matrix
   ├── [PVM-xxx] Price-Volume-Mix Decomposition Model
   └── [RBR-xxx] Master Revenue Reconciliation Bridge Line Item
```

### Standard Audit Tickmark Index

* $\checkmark$ : **Traced to General Ledger:** Confirmed amount agrees exactly with trial balance revenue accounts.
* $\Phi$ : **Vouched to Carrier Shipping Manifest:** Verified physical carrier pickup, tracking number, and proof of delivery.
* $\Lambda$ : **Mathematical Footing Checked:** Verified column, row, and formula calculations foot without rounding error.
* $\Omega$ : **Benchmarked to Customer Contract:** Reconciled to executed Master Service Agreement, rate card, or PO.
* $\Psi$ : **PVM Decomposition Checked:** Verified that Price, Volume, and Mix contributions sum to total revenue variance.
* $\Theta$ : **Mandatory Revenue Haircut:** Technical correction or commercial deduction adjusting reported revenue downward.
