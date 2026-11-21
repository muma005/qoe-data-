# EBITDA Evidence & Professional Judgment Matrix
**Document Reference:** `QOE-EVID-MATRIX-05`  
**Workstream:** `05 — EBITDA Normalization and Adjustments`  
**Classification:** Quality of Earnings Evidentiary Standard & Audit Governance Matrix  

---

## 1. Evidentiary Hierarchy & Legal Standard of Proof

In transactional due diligence, evidentiary standards mirror those of forensic accounting and AICPA consulting standards. Oral representations made by company founders, investment bankers, or management are **not admissible as primary evidence**.

```
+----------------------------------------------------------------------------------------------------+
|                                    EVIDENTIARY HIERARCHY                                           |
|                                                                                                    |
|   [TIER 1] EXECUTED INDEPENDENT EXTERNAL DOCUMENTATION (Highest Reliability)                       |
|   • Executed legal settlement agreements, court bankruptcy dockets, certified MAI appraisals.      |
|   • Third-party bank statements, canceled checks, electronic wire debit/credit confirmations.      |
|                                                                                                    |
|   [TIER 2] ITEMISED VENDOR INVOICES & STATUTORY TAX RETURNS (High Reliability)                     |
|   • Itemized legal, consulting, and contractor invoices with detailed billing rates and dates.     |
|   • IRS Form W-2 / 1099 filings, state unemployment registers, signed commercial lease contracts.  |
|                                                                                                    |
|   [TIER 3] INDEPENDENT MARKET BENCHMARKS & COMPENSATION SURVEYS (Moderate-High Reliability)        |
|   • Published Mercer, ERI, Robert Half executive compensation surveys for NAICS code and region.   |
|   • CoStar / Cushman & Wakefield commercial industrial real estate lease rate benchmarks.          |
|                                                                                                    |
|   [TIER 4] INTERNAL MANAGEMENT SCHEDULES & SYSTEM WORKPAPERS (Conditional / Needs Verification)    |
|   • General Ledger journal voucher logs, monthly management accounting packages, budget decks.     |
|   • Unsigned contracts, forward-looking spreadsheet projections, internal cost allocation models.  |
|                                                                                                    |
|   [TIER 5] UNSUBSTANTIATED ORAL REPRESENTATIONS (Inadmissible for Add-Backs)                       |
|   • Executive assertions: "We won't spend that post-close", "That was a one-time vendor dispute."  |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Professional Judgment & Verification Matrix

The following matrix governs the evidentiary testing, red flags, and review requirements for each category of EBITDA adjustment:

| Category Code | Adjustment Category | Primary Documentary Evidence | Secondary / Corroborating Evidence | Forensic Red Flags & Disallowance Triggers | Mandatory Audit Verification Procedure | Requisite Sign-Off Level |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ADJ-CAT-01`** | **Transaction-Related Advisory & Legal** | Executed M&A engagement letters, itemized attorney fee invoices | Bank wire settlement slips, Board of Directors transaction resolutions | Invoices include general corporate governance or ongoing litigation; retainers paid for routine tax filing. | Reconcile invoice dates to transaction timeline; confirm scope excludes general corporate matters; check balance sheet capitalization. | Manager + Partner |
| **`ADJ-CAT-02`** | **Facility Restructuring & Severance** | Signed separation agreements, landlord lease termination releases | State WARN notices, payroll register showing final payouts | Terminated employees re-hired or replaced at other locations; severance is routine annual turnover. | Perform monthly headcount roll-forward by department; verify site physical closure via third-party freight logs. | Senior Analyst + Manager |
| **`ADJ-CAT-03`** | **Owner / Shareholder Compensation** | IRS Form W-2 (Boxes 1 & 5), 1099-NEC, corporate payroll summaries | Mercer / Robert Half executive compensation survey benchmarks | Claiming 100% add-back without deducting replacement GM salary; omitting personal auto/travel perks. | Compute total loaded owner cost; apply median benchmark compensation for comparable NAICS/revenue tier; verify net add-back math. | Manager + Partner |
| **`ADJ-CAT-04`** | **Related-Party Facility Leases** | Executed commercial lease agreements, certified MAI appraisal | County tax records, local commercial broker comps (Cushman/CBRE) | Lease is gross but appraisal is NNN without adjustment; company claims warehouse can be exited without cost. | Compare square footage and NNN expense terms; verify that lease rate variance is adjusted to independent appraised FMV. | Senior Analyst + Manager |
| **`ADJ-CAT-05`** | **Extraordinary Casualty & Repairs** | Third-party contractor repair invoices, disaster weather reports | Insurance claim proof-of-loss filings, adjustor damage assessments | Adding back gross repair without deducting insurance recoveries; claiming routine deferred maintenance as disaster. | Trace repair debits in GL; trace insurance recovery credits in Other Income; calculate net out-of-pocket loss; check Fixed Asset CapEx. | Senior Analyst + Manager |
| **`ADJ-CAT-06`** | **Non-Operating Insurance Recoveries** | Insurance settlement remittance advices, bank cash receipts | Policy release agreements, correspondence with claims adjustor | Crediting non-trading casualty or life insurance proceeds into operating revenue or gross margin. | Isolate all Other Income entries; reclassify non-operational insurance recoveries as mandatory QoE deductions. | Senior Analyst + Manager |
| **`ADJ-CAT-07`** | **Discretionary Consulting Fees** | Signed Statements of Work (SOWs), itemized billing timesheets | Completed deliverable reports, system cutover sign-off records | Retainers lack deliverable descriptions; advisory services represent recurring sales coaching or recurring tax. | Review SOW deliverables; interview management; test whether capability was absorbed internally; verify no CapEx overlap. | Senior Analyst + Manager |
| **`ADJ-CAT-08`** | **Customer Bad Debt Normalization** | U.S. Bankruptcy Court filings, historical AR aging ledgers | Default notices, customer collection correspondence, credit reports | Treating normal credit losses as non-recurring; historical bad debt averages >0.25% of sales across review period. | Calculate 3-year bad debt expense as % of revenue; reject add-back if within historical volatility range; verify NWC reserve tie-out. | Manager + Partner |
| **`ADJ-CAT-09`** | **Prospective Cost Savings & Synergies** | Newly executed vendor contracts, 3PL master service agreements | Board presentations, engineering synergy models, pricing schedules | Adding unearned future savings to historical actuals; savings require significant future CapEx or risk. | Exclude 100% of future savings from Historical Normalized EBITDA; model separately in buyer pro-forma synergy sensitivity deck. | Quality Partner |
| **`ADJ-CAT-10`** | **Capitalized Software / Costs** | Vendor invoices, Fixed Asset Register (FAR), software sub-ledger | Audit workpapers verifying ASC 350-40 internal-use software criteria | Proposing add-backs for expenditures that were capitalized on the balance sheet and never entered operating P&L. | Trace debit entry in general ledger; confirm invoice was debited to Asset (`GL 1-xxxx`) rather than OpEx (`GL 6-xxxx`); reject add-back. | Senior Analyst + Manager |
| **`ADJ-CAT-11`** | **Revenue Cut-Off Adjustments** | Sales invoices, Bills of Lading (BOL), proof of delivery receipts | Master customer contract shipping terms (FOB Destination vs Origin) | Booking revenue prior to delivery; bill-and-hold sales without meeting strict ASC 606 criteria; margin acceleration. | Perform cut-off testing 15 days before/after year-end; reverse unearned gross margin via mandatory QoE deduction; adjust AR and Inventory. | Manager + Partner |
| **`ADJ-CAT-12`** | **Unsupported Topside Plugs** | General Ledger manual journal entry audit logs, journal vouchers | CFO workpapers, vendor volume rebate contracts (if any) | Manual period-end journal entries debiting AR and crediting Other Income without external transaction backing. | Query all manual journal entries posted in final 5 days of period above materiality; require external invoices; reverse unsupported entries. | Manager + Partner |

---

## 3. Workpaper Cross-Referencing & Audit Trail Standards

To ensure complete reproducibility in simulation and audit contexts, every workpaper must maintain strict alphanumeric cross-referencing:

```
[SRC-xxx] Raw Source Record / Accounting Export
   │
   ▼
[PREP-xxx] Standardized & Cleansed Dataset (Workstream 02)
   │
   ▼
[REC-xxx] Financial Reconciliation Workpaper (Workstream 03)
   │
   ▼
[ANA-xxx] Historical Financial Analysis Schedule (Workstream 04)
   │
   ▼
[ADJ-xxx] EBITDA Adjustment Workpaper (Workstream 05)
   ├── [EVD-xxx] Third-Party Source Evidence (Invoices, Leases, Appraisals)
   ├── [DEC-xxx] Formal Adjudication Decision Record
   └── [EBR-xxx] Master Multi-Period EBITDA Bridge Line Item
```

### Standard Audit Tickmark Index

* $\checkmark$ : **Traced to General Ledger:** Confirmed amount agrees exactly with transaction journal debit/credit.
* $\Phi$ : **Vouched to Third-Party Invoice:** Inspected original invoice, verified dates, vendor name, and description.
* $\Lambda$ : **Mathematical Footing Checked:** Verified column, row, and formula calculations foot without rounding error.
* $\Omega$ : **Benchmarked to External Data:** Reconciled to independent salary survey (Mercer) or appraisal (Cushman).
* $\Psi$ : **Balance Sheet & NWC Checked:** Verified zero duplication with Net Working Capital peg or Net Debt items.
* $\Theta$ : **Mandatory QoE Deduction:** Technical correction or error reversal adjusting reported EBITDA downward.
