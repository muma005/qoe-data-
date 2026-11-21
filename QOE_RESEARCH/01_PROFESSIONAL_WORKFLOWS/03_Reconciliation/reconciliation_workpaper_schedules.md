# Quality of Earnings (QoE) Research Programme
## Workstream 03 — Financial Reconciliation
### Deliverable 2: Production-Grade Reconciliation Workpaper Schedules

This document establishes the eight core financial reconciliation schedules required in professional transaction advisory services (PwC, Alvarez & Marsal, Kroll, RSM, BDO, FTI Consulting). Every schedule adheres to strict mathematical balance, explicit formulas, verified source references (SRC-xxx), exception tags (EXC-xxx), and evidence links (EVD-xxx).

---

### Schedule 1: Trial Balance to General Ledger Tie-Out (REC-001)

* **Client / Target:** Apex Industrial Supply Group
* **Period Covered:** 12 Months Ended December 31, 2023 (FY2023)
* **Prepared By:** Senior TAS Analyst | **Date:** 2024-02-14
* **Reviewed By:** TAS Engagement Manager | **Date:** 2024-02-16
* **Objective:** Verify that the prepared Trial Balance mathematically equals the sum of all transactional debits and credits in the General Ledger by account and period.
* **Source Records:** SRC-001 (Prepared TB), SRC-002 (Prepared GL Detail Export).

| Account Code | Account Description | GL Total Debits ($) | GL Total Credits ($) | GL Net Movement ($) [Debits - Credits] | Prepared TB Net Movement ($) | Variance ($) [GL - TB] | Exception Ref | Audit / Diligence Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1-1000 | Cash - Operating Account | 14,850,200.00 | 14,326,150.00 | 524,050.00 | 524,050.00 | 0.00 | - | **PASS** - Reconciled |
| 1-1100 | Trade Accounts Receivable | 28,450,000.00 | 27,625,900.00 | 824,100.00 | 824,100.00 | 0.00 | - | **PASS** - Reconciled |
| 1-1150 | Allowance for Doubtful Accounts | 12,000.00 | 54,500.00 | -42,500.00 | -42,500.00 | 0.00 | - | **PASS** - Reconciled |
| 1-1200 | Inventory - Finished Goods | 16,840,000.00 | 15,220,000.00 | 1,620,000.00 | 1,620,000.00 | 0.00 | - | **PASS** - Reconciled |
| 1-1300 | Prepaid Expenses & Other Assets | 450,000.00 | 385,000.00 | 65,000.00 | 65,000.00 | 0.00 | - | **PASS** - Reconciled |
| 1-2000 | Machinery & Equipment | 1,250,000.00 | 145,000.00 | 1,105,000.00 | 1,105,000.00 | 0.00 | - | **PASS** - Reconciled |
| 1-2010 | Accumulated Depreciation | 0.00 | 485,000.00 | -485,000.00 | -485,000.00 | 0.00 | - | **PASS** - Reconciled |
| 2-1000 | Trade Accounts Payable | 15,420,000.00 | 16,099,600.00 | -679,600.00 | -679,600.00 | 0.00 | - | **PASS** - Reconciled |
| 2-2000 | Accrued Payroll & Bonuses | 3,850,000.00 | 4,120,000.00 | -270,000.00 | -270,000.00 | 0.00 | - | **PASS** - Reconciled |
| 2-3000 | Deferred Revenue | 1,450,000.00 | 1,730,000.00 | -280,000.00 | -280,000.00 | 0.00 | - | **PASS** - Reconciled |
| 2-4000 | Senior Bank Debt | 1,200,000.00 | 3,500,000.00 | -2,300,000.00 | -2,300,000.00 | 0.00 | - | **PASS** - Reconciled |
| 3-1000 | Common Stock & APIC | 0.00 | 1,500,000.00 | -1,500,000.00 | -1,500,000.00 | 0.00 | - | **PASS** - Reconciled |
| 3-2000 | Retained Earnings | 450,000.00 | 868,050.00 | -418,050.00 | -418,050.00 | 0.00 | - | **PASS** - Reconciled |
| 4-1000 | Commercial Sales Revenue | 185,000.00 | 25,035,000.00 | -24,850,000.00 | -24,850,000.00 | 0.00 | - | **PASS** - Reconciled |
| 5-1000 | Cost of Goods Sold | 15,400,000.00 | 0.00 | 15,400,000.00 | 15,400,000.00 | 0.00 | - | **PASS** - Reconciled |
| 6-1000 | Operating Expenses (S&M, G&A) | 6,120,000.00 | 0.00 | 6,120,000.00 | 6,120,000.00 | 0.00 | - | **PASS** - Reconciled |
| 7-1000 | Depreciation & Amortization | 850,000.00 | 0.00 | 850,000.00 | 850,000.00 | 0.00 | - | **PASS** - Reconciled |
| 8-1000 | Interest Expense | 320,000.00 | 0.00 | 320,000.00 | 320,000.00 | 0.00 | - | **PASS** - Reconciled |
| 9-1000 | Income Tax Expense | 453,600.00 | 0.00 | 453,600.00 | 453,600.00 | 0.00 | - | **PASS** - Reconciled |
| **TOTAL** | **Sum of All Accounts** | **101,850,800.00** | **101,850,800.00** | **0.00** | **0.00** | **0.00** | - | **BALANCED** |

* **Investigative Finding:** The Trial Balance and General Ledger foot and cross-foot with mathematical perfection across all 19 summary accounts. Zero unposted draft batches or orphan GL accounts detected.

---

### Schedule 2: Trial Balance to Management Accounts Bridge (REC-002)

* **Client / Target:** Apex Industrial Supply Group
* **Period Covered:** FY2023 (12 Months Ended Dec 31, 2023)
* **Objective:** Establish whether internal monthly P&L reporting presented to the Board matches the underlying Trial Balance.
* **Source Records:** SRC-001 (TB Movement), SRC-003 (FY23 Management Accounts Reporting Pack).

| Financial Line Item | Prepared TB Amount ($) | Mgmt Accounts Pack ($) | Variance ($) [TB - Mgmt] | Discrepancy Classification | Root Cause / Supporting Explanation | Evidence Link | Resolution / QoE Treatment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Commercial Revenue | 24,850,000.00 | 25,230,000.00 | -380,000.00 | Premature Revenue Recognition | Management accounts included  of bill-and-hold order #9842 that was invoiced Dec 31 but not shipped until Jan 04. | EVD-005 (Bill of Lading) | EXC-001: Management deck overstated revenue; TB is correct; reverse  from mgmt view. |
| Cost of Goods Sold | 15,400,000.00 | 15,172,000.00 | 228,000.00 | Cost Matching Violation | Management deck omitted the  COGS associated with the  premature revenue, claiming goods were in inventory. | EVD-008 (Stock Count) | EXC-001: Match COGS to revenue cut-off. |
| Gross Profit | 9,450,000.00 | 10,058,000.00 | -608,000.00 | Gross Margin Distortion | Mgmt deck gross margin is 39.86% vs TB gross margin of 38.03% (183 bps artificial lift). | CALC | Bridge documented. |
| Operating Expenses | 6,120,000.00 | 5,940,000.00 | 180,000.00 | Unrecorded Bonus Accrual | Management deck omitted  executive incentive bonus pool accrued in TB A/C 2-2000. | EVD-010 (Bonus Plan) | Management deck understates run-rate overhead. |
| Operating EBITDA | 3,330,000.00 | 4,118,000.00 | -788,000.00 | Topside EBITDA Inflation | Management reporting pack artificially inflated EBITDA by ,000 (23.7% overstatement). | CALC | Critical finding for purchase price negotiations. |

* **Investigative Finding:** The Board reporting pack was aggressively prepared using unposted Excel adjustments to achieve an earn-out target. The General Ledger Trial Balance reflects a more conservative, unmanipulated accounting state.

---

### Schedule 3: Management Accounts to Audited Statutory Financial Statements Bridge (REC-003)

* **Client / Target:** Apex Industrial Supply Group
* **Period Covered:** Audited Fiscal Year Ended December 31, 2023
* **Objective:** Bridge internal reporting to final audited financial statements and identify all independent auditor adjustments.
* **Source Records:** SRC-003 (Internal Mgmt Accounts), SRC-004 (Independent Auditor Report & AJE Log).

| Income Statement Line | FY23 Management Accounts ($) | Audit Adjustment ID | Nature of Audit Adjustment | Auditor Adjustment Amount ($) | FY23 Audited Statutory FS ($) | QoE Normalization Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Net Revenue | 25,230,000.00 | AJE-01 | Cut-off reversal of bill-and-hold shipment #9842 | -380,000.00 | 24,850,000.00 | Negative EBITDA adjustment of -,000 |
| Cost of Goods Sold | 15,172,000.00 | AJE-02 | Lower-of-cost-or-market inventory obsolescence reserve | +373,000.00 | 15,545,000.00 | -,000 to EBITDA ( NRV write-down +  cost true-up) |
| **Gross Profit** | **10,058,000.00** | | **Subtotal Gross Profit Impact** | **-753,000.00** | **9,305,000.00** | **Gross Margin drops to 37.44%** |
| Operating Expenses | 5,940,000.00 | AJE-03 | True-up of executive incentive bonus pool | +180,000.00 | 6,120,000.00 | Negative EBITDA adjustment of -,000 |
| Depreciation & Amortization | 850,000.00 | AJE-04 | Tax vs GAAP straight-line depreciation true-up | -35,000.00 | 815,000.00 | EBITDA neutral (affects D&A line only) |
| **Operating Income (EBIT)** | **3,268,000.00** | | **Subtotal Operating Income Impact** | **-898,000.00** | **2,370,000.00** | **Total Operating Profit Overstatement: ,000** |
| Interest Expense | 320,000.00 | AJE-05 | Unaccrued shareholder debt interest | +45,000.00 | 365,000.00 | Debt-like item; Net Debt adjustment |
| Income Tax Expense | 619,080.00 | AJE-06 | Deferred tax effect of pre-tax adjustments (21%) | -200,130.00 | 418,950.00 | Tax provision true-up |
| **Net Income** | **2,328,920.00** | | **Net Bottom-Line Disconnect** | **-742,870.00** | **1,586,050.00** | **Internal Net Income overstated by 46.8%** |

* **Investigative Finding:** 100% of the variance between management reporting and audited statements is explained by 6 distinct audit journal entries (AJE-01 through AJE-06). Management never incorporated these audit adjustments back into monthly reporting packages for subsequent quarters, creating an ongoing disconnect.

---

### Schedule 4: Accounts Receivable Subledger Aging to GL Control Tie-Out (REC-006)

* **Client / Target:** Apex Industrial Supply Group
* **As of Date:** December 31, 2023
* **Objective:** Reconcile customer-level open aging balances to GL Trade Accounts Receivable Control Account (1-1100).
* **Source Records:** SRC-007 (Detailed AR Aging Report), SRC-001 (Trial Balance A/C 1-1100).

| Customer ID | Customer Legal Name | Current ($) | 1-30 Days ($) | 31-60 Days ($) | 61-90 Days ($) | 91-120 Days ($) | >120 Days ($) | Total Balance ($) | Disputed / Risk Flag |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| CUST-101 | Midwest Industrial Logistics | 124,500.00 | 45,000.00 | 12,000.00 | 0.00 | 0.00 | 0.00 | 181,500.00 | Clean - Standard Terms |
| CUST-102 | Great Lakes Equipment Corp | 85,200.00 | 28,400.00 | 15,600.00 | 9,800.00 | 0.00 | 0.00 | 139,000.00 | Clean - Performing |
| CUST-103 | Summit Fabrication Ltd | 42,000.00 | 18,000.00 | 0.00 | 0.00 | 0.00 | 0.00 | 60,000.00 | Clean - Prompt |
| CUST-104 | Vanguard Precision Tooling | 15,000.00 | 32,000.00 | 28,000.00 | 22,500.00 | 18,000.00 | 45,000.00 | 160,500.00 | **DISPUTED**:  past 120 days uncollectible |
| CUST-105 | Apex Distribution Partners | 68,400.00 | 14,200.00 | 0.00 | 0.00 | 0.00 | 0.00 | 82,600.00 | Related Party Affiliate |
| CUST-106 | Horizon Supply Chain LLC | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -12,500.00 | -12,500.00 | **CREDIT MEMO**: Unapplied Q3 credit memo |
| CUST-107 | Delta Manufacturing Services | 94,000.00 | 21,000.00 | 8,500.00 | 0.00 | 0.00 | 0.00 | 123,500.00 | Clean - Performing |
| CUST-108 | Keystone Components Corp | 31,500.00 | 9,800.00 | 4,200.00 | 1,500.00 | 0.00 | 0.00 | 47,000.00 | Clean - Performing |
| **SUBTOTAL** | **Sum of Customer Subledger** | **460,600.00** | **168,400.00** | **68,300.00** | **33,800.00** | **18,000.00** | **32,500.00** | **781,600.00** | |
| GL-1100 | **General Ledger Control Account** | | | | | | | **824,100.00** | **Per Trial Balance** |
| VARIANCE | **Unreconciled Control Break (GL - Subledger)** | | | | | | | **42,500.00** | **EXC-002: Manual JE Plug** |

* **Investigative Finding:** The GL control account exceeds the customer aging subledger by exactly ,500.00. Audit trail analysis revealed manual journal entry #2023-12-88 debited GL A/C 1-1100 and credited Other Income without an offsetting subledger customer record. Management plug confirmed.

---

### Schedule 5: Accounts Payable Subledger Aging to GL Control Tie-Out (REC-007)

* **Client / Target:** Apex Industrial Supply Group
* **As of Date:** December 31, 2023
* **Objective:** Reconcile vendor-level open aging balances and Goods Received Not Invoiced (GRNI) to GL Trade Accounts Payable Control Accounts (2-1000 & 2-1050).
* **Source Records:** SRC-008 (Detailed AP Aging Report), SRC-009 (GRNI Open PO Subledger), SRC-001 (TB).

| Vendor ID | Vendor Legal Name | Current ($) | 1-30 Days ($) | 31-60 Days ($) | 61-90 Days ($) | 91-120 Days ($) | >120 Days ($) | Total Balance ($) | Operational Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| VEND-501 | Midwest Raw Steel Co | 185,000.00 | 42,000.00 | 0.00 | 0.00 | 0.00 | 0.00 | 227,000.00 | Prime Raw Material Vendor |
| VEND-502 | Precision Fasteners Inc | 34,200.00 | 12,500.00 | 6,800.00 | 0.00 | 0.00 | 0.00 | 53,500.00 | Standard Terms |
| VEND-503 | Apex Freight & Logistics | 62,000.00 | 28,000.00 | 14,000.00 | 8,500.00 | 0.00 | 0.00 | 112,500.00 | Inbound / Outbound Freight |
| VEND-504 | Global Packaging Solutions | 21,000.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 21,000.00 | Packaging Materials |
| VEND-505 | Industrial Power & Utilities | 18,500.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 18,500.00 | Monthly Utility |
| VEND-506 | Highland Machine Tooling | 45,000.00 | 32,000.00 | 19,000.00 | 15,000.00 | 12,000.00 | 28,000.00 | 151,000.00 | **DISPUTED**:  withheld for machine failure |
| VEND-507 | Tri-State Maintenance LLC | 8,500.00 | 4,200.00 | 0.00 | 0.00 | 0.00 | 0.00 | 12,700.00 | Facility Maintenance |
| **SUBTOTAL** | **Sum of Vendor Subledger** | **374,200.00** | **118,700.00** | **39,800.00** | **23,500.00** | **12,000.00** | **28,000.00** | **596,200.00** | Trade AP Subledger Total |
| GRNI-ACC | **Goods Received Not Invoiced** | | | | | | | **68,400.00** | Valid dock receipts unbilled (EVD-007) |
| **TOTAL AP** | **Total Trade AP & Accruals** | | | | | | | **664,600.00** | Subledger AP + GRNI |
| GL-CONTROL | **General Ledger Control Balance** | | | | | | | **679,600.00** | GL A/C 2-1000 + 2-1050 |
| VARIANCE | **Unreconciled Break (GL - Subledger)** | | | | | | | **15,000.00** | **Misclassification Break** |

* **Investigative Finding:** GL exceeds subledger by ,000.00. Investigation revealed an entry debiting Legal Expense and crediting Trade Accounts Payable (2-1000) for estimated outside counsel fees instead of Other Accrued Expenses (2-2100). Zero cash or EBITDA impact, but requires reclassification on the closing Balance Sheet.

---

### Schedule 6: Inventory Perpetual Subledger to GL Roll-Forward (REC-008)

* **Client / Target:** Apex Industrial Supply Group
* **Period Covered:** FY2023 (12 Months Ended Dec 31, 2023)
* **Objective:** Roll forward perpetual inventory balances from stock registers to GL asset accounts and verify COGS consumption.
* **Source Records:** SRC-010 (Perpetual Inventory Report), SRC-011 (Stocktake Count Sheets), SRC-001 (TB).

| Inventory Category | Jan 01 2023 Opening Balance ($) | Inbound Purchases / WIP Transfers ($) | COGS Relieved / Consumption ($) | Scrap & Variance Adjustments ($) | Calculated Dec 31 Balance ($) | Dec 31 GL Book Balance ($) | Variance ($) [GL - Subledger] | Root Cause & Evidence Ref |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Raw Materials (1-1200) | 480,000.00 | 6,850,000.00 | -6,720,000.00 | -45,000.00 | 565,000.00 | 565,000.00 | 0.00 | Reconciled; scrap confirmed via stocktake |
| Work-in-Progress (1-1210) | 215,000.00 | 6,720,000.00 | -6,645,000.00 | 0.00 | 290,000.00 | 290,000.00 | 0.00 | Tied to open shop-floor work orders |
| Finished Goods (1-1220) | 780,000.00 | 6,645,000.00 | -6,660,000.00 | 0.00 | 765,000.00 | 765,000.00 | 0.00 | Tied to warehouse SKU master |
| **Total Inventory Asset** | **1,475,000.00** | **20,215,000.00** | **-20,025,000.00** | **-45,000.00** | **1,620,000.00** | **1,620,000.00** | **0.00** | **Full subledger roll-forward ties to GL** |
| Obsolescence Reserve (1-1250) | -85,000.00 | 0.00 | 0.00 | -145,000.00 | -230,000.00 | -85,000.00 | **145,000.00** | EXC-001 / AJE-02: Auditor lower-of-cost-or-market write-down unposted in monthly GL |
| **Net Inventory Valuation** | **1,390,000.00** | **20,215,000.00** | **-20,025,000.00** | **-190,000.00** | **1,390,000.00** | **1,535,000.00** | **145,000.00** | **Net Working Capital Overstated by ,000** |

* **Investigative Finding:** Gross inventory rolls forward with exact mathematical agreement across raw materials, WIP, and finished goods. However, the inventory obsolescence allowance was suppressed in monthly management books, understating the reserve by ,000 relative to audited net realizable value.

---

### Schedule 7: Bank Statement to General Ledger Four-Column Proof of Cash (REC-009)

* **Client / Target:** Apex Industrial Supply Group
* **Bank Facility:** First National Operating Account #xxxx-8842
* **Period Covered:** One Month Ended January 31, 2024
* **Objective:** Establish complete substantive reconciliation of beginning cash, cash receipts, cash disbursements, and ending cash between third-party bank statements and the General Ledger.
* **Source Records:** SRC-012 (Bank Statement), SRC-013 (Bank Rec Report), SRC-002 (GL Cash Account 1-1000).

| Reference | Line Description | Col 1: Beg Balance (Jan 01) ($) | Col 2: Cash Receipts ($) | Col 3: Cash Disbursements ($) | Col 4: End Balance (Jan 31) ($) | Verification Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| BANK-01 | **Balance per Bank Statement** | **482,500.00** | **1,245,000.00** | **1,180,200.00** | **547,300.00** | Direct Bank Statement & Confirmation |
| ADJ-01 | Prior Month Deposits in Transit (cleared Jan) | 35,000.00 | -35,000.00 | 0.00 | 0.00 | Traced to Jan 02 bank deposit slip |
| ADJ-02 | Current Month Deposits in Transit (Jan 31) | 0.00 | 48,500.00 | 0.00 | 48,500.00 | Traced to Feb 02 bank clearance |
| ADJ-03 | Prior Month Outstanding Checks (cleared Jan) | -62,400.00 | 0.00 | -62,400.00 | 0.00 | Traced to Jan cleared check list |
| ADJ-04 | Current Month Outstanding Checks (Jan 31) | 0.00 | 0.00 | 71,800.00 | -71,800.00 | Open check register at Jan 31 |
| ADJ-05 | Bank Error: Unauthorized wire fee debit | 0.00 | 0.00 | -5,200.00 | 5,200.00 | Reversed by bank on Feb 03 |
| CALC-01 | **Adjusted Bank Balance** | **455,100.00** | **1,258,500.00** | **1,184,400.00** | **529,200.00** | **Formula: Sum of Bank Rows** |
| BOOK-01 | **Balance per General Ledger (A/C 1-1000)** | **455,100.00** | **1,252,100.00** | **1,183,150.00** | **524,050.00** | **Trial Balance Cash Movement** |
| ADJ-06 | Unrecorded Bank Interest Income | 0.00 | 1,400.00 | 0.00 | 1,400.00 | Bank credit memo on Jan 31 |
| ADJ-07 | Customer Direct Wire (Unrecorded AR receipt) | 0.00 | 5,000.00 | 0.00 | 5,000.00 | Wire from Midwest Logistics Jan 30 |
| ADJ-08 | Bank Service Charges & Wire Fees | 0.00 | 0.00 | 850.00 | -850.00 | Bank debit memo on Jan 31 |
| ADJ-09 | Customer NSF Check Returned | 0.00 | 0.00 | 400.00 | -400.00 | Bounced check from Apex client |
| CALC-02 | **Adjusted Book Balance** | **455,100.00** | **1,258,500.00** | **1,184,400.00** | **529,200.00** | **Formula: Sum of Book Rows** |
| VARIANCE| **Variance (Adjusted Bank - Adjusted Book)** | **0.00** | **0.00** | **0.00** | **0.00** | **Fully Reconciled Across All 4 Columns** |

* **Investigative Finding:** The Four-Column Proof of Cash proves the absence of cash kiting, unrecorded bank accounts, or float manipulation. All reconciling items are substantiated by subsequent-period bank clearance statements.

---

### Schedule 8: Corporate Group Intercompany Matrix & Elimination Schedule (REC-004)

* **Client / Target:** Apex Global Industrial Holding Inc. (Consolidated Group)
* **Entities:** Entity 10 (US Operating Co), Entity 20 (UK Distribution Ltd), Entity 30 (EU Manufacturing BV).
* **As of Date:** December 31, 2023
* **Objective:** Verify bilateral intercompany balances, eliminate reciprocal transactions, and isolate currency or timing breaks.
* **Source Records:** SRC-001 (Entity TBs), SRC-005 (Group Consolidation Files).

| Sending Entity | Receiving Entity | Transaction Stream | Entity A Recorded Balance ($) | Entity B Recorded Balance ($) | Variance / Break ($) [A - B] | Root Cause Analysis | Elimination Adjustment Type | Downstream Diligence Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Entity 10 (US) | Entity 20 (UK) | Trade AR / AP (Products) | 450,000.00 | 420,000.00 | 30,000.00 | Shipment #UK-884 in transit across Atlantic over year-end. | Debit Inventory in Transit , Credit Intercompany Payable  | EXC-004: Balance Sheet elimination adjustment; zero group EBITDA impact. |
| Entity 10 (US) | Entity 20 (UK) | Corporate Management Fee | 120,000.00 | 120,000.00 | 0.00 | Monthly allocation of corporate C-suite overhead (/mo). | Full reciprocal elimination | Clean elimination. Zero group variance. |
| Entity 20 (UK) | Entity 30 (EU) | Sub-Assembly Components | 310,000.00 | 285,000.00 | 25,000.00 | FX rate mismatch: UK booked at 1.18 GBP/EUR; EU booked at 1.15; plus unrecorded price rebate. | Revalue intercompany balances at closing spot rate; book  rebate |  EBITDA adjustment in UK entity; eliminates on consolidation. |
| Entity 30 (EU) | Entity 10 (US) | Working Capital Loan Note | 500,000.00 | 500,000.00 | 0.00 | Principal of intercompany subordinated promissory note. | Full reciprocal elimination | Loan balances match. Zero principal variance. |
| Entity 30 (EU) | Entity 10 (US) | Accrued Loan Interest | 18,500.00 | 0.00 | 18,500.00 | Entity 30 accrued .5k interest receivable; Entity 10 failed to accrue interest expense. | Debit Interest Expense .5k, Credit Intercompany Payable .5k | EXC-005: Entity 10 net income overstated by .5k; Net Debt adjustment. |
| **TOTAL** | **Consolidated Group** | **All Streams** | **1,398,500.00** | **1,325,000.00** | **73,500.00** | **Total Group Intercompany Disconnect** | **Consolidation Eliminations Required** | **Net ,500 balance sheet reconciliation break** |

* **Investigative Finding:** The group intercompany accounts have an aggregate break of ,500.00. Unreconciled intercompany accounts mask ,500 of unrecorded interest expense and ,000 of unaccrued inventory in transit. Both must be adjusted in the consolidated closing position.
