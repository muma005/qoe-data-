# Data Cleansing & Integrity Control Matrix (Workstream 02)
**Document Path:** `QOE_RESEARCH/01_PROFESSIONAL_WORKFLOWS/02_Data_Preparation/data_cleansing_and_integrity_control_matrix.md`  
**Purpose:** Technical specification of the 16 mandatory data preparation integrity controls governing financial due diligence databooks.

---

## The Sixteen Core Integrity Controls

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DATA PREPARATION INTEGRITY CONTROL MATRIX                       │
├────┬─────────────────────────────┬─────────────────────────────────────────────────────┤
│ 01 │ Record & Row Count Parity   │ Ingestion completeness verification                 │
│ 02 │ Debit/Credit Parity (GL)    │ Transactional double-entry balancing                │
│ 03 │ Trial Balance Zero-Sum      │ Period-level trial balance zero-sum assertion       │
│ 04 │ Account Code Completeness   │ Primary key integrity and null code detection       │
│ 05 │ Leading Zero Preservation   │ String data type enforcement on account numbers     │
│ 06 │ Date Range Boundary Check   │ Temporal scope compliance                           │
│ 07 │ Missing Period Detection    │ Continuity verification across 36 monthly closes    │
│ 08 │ Duplicate Line Detection    │ Uniqueness check on primary keys and transaction IDs│
│ 09 │ 100% COA Mapping Coverage   │ Unmapped accounts trap and null category isolation  │
│ 10 │ Formula vs. Hardcode Audit  │ Cell-level integrity audit on spreadsheet models    │
│ 11 │ Opening-to-Closing Rollfwd  │ Inter-period balance continuity verification        │
│ 12 │ Retained Earnings Bridge    │ Net income to balance sheet equity reconciliation   │
│ 13 │ Suspense Account Balance    │ Dumping-ground and clearing account audit           │
│ 14 │ Subledger-to-GL Control     │ Subledger control account tie-out                   │
│ 15 │ Version Collision Delta     │ Programmatic detection of unannounced restatements │
│ 16 │ Intercompany Zero-Sum Parity│ Elimination verification across operating perimeter │
└────┴─────────────────────────────┴─────────────────────────────────────────────────────┘
```

---

### Control 01: Record & Row Count Parity
1. **What it Tests:** Compares the physical line count of the raw source file against the total ingested rows in the standardized database table.
2. **Why it Matters:** Guarantees that no rows were dropped during CSV parsing, character encoding conversions, or text delimiter splitting.
3. **How it is Performed:** 
   $$\text{Raw Line Count} - \text{Header Lines} \equiv \text{Ingested Database Row Count}$$
4. **What a Failed Result Indicates:** Silent truncation due to buffer overflow, unescaped line breaks inside memo fields, or text delimiter collisions.
5. **What the Analyst Does Next:** Inspects the raw file at the line where truncation occurred; configures parser to escape multiline strings and re-runs ingestion.
6. **Evidence Retained:** Automated ingestion log containing source byte size, raw line count, and database inserted row count.

---

### Control 02: Transactional Debit/Credit Parity (General Ledger)
1. **What it Tests:** Verifies that total debits equal total credits across the entire transaction-level general ledger extract.
2. **Why it Matters:** Asserts that double-entry bookkeeping rules were maintained in the exported population.
3. **How it is Performed:**
   $$\sum_{j=1}^{N} \text{Debit Amount}_j - \sum_{j=1}^{N} \text{Credit Amount}_j \equiv 0.00$$
4. **What a Failed Result Indicates:** Corrupt ERP database, selective extraction filtering (e.g. exporting only P&L accounts while omitting Balance Sheet lines), or interrupted export jobs.
5. **What the Analyst Does Next:** Rejects the GL extract; instructs client IT to re-export the entire balanced ledger across all posting accounts.
6. **Evidence Retained:** GL control schedule showing sum of debits, sum of credits, and zero variance.

---

### Control 03: Monthly Trial Balance Zero-Sum Parity
1. **What it Tests:** Verifies that every single monthly trial balance balances to net zero.
2. **Why it Matters:** A trial balance that does not balance cannot produce reliable financial statements or databook schedules.
3. **How it is Performed:**
   $$\text{For each month } t \in \{1 \dots 36\}: \quad \sum_{i=1}^{K} \text{Net Account Balance}_{i,t} \equiv 0.00$$
4. **What a Failed Result Indicates:** Unposted journal batches, out-of-balance software modules, or manual spreadsheet deletions.
5. **What the Analyst Does Next:** Flags the specific month(s) out of balance; issues formal VDR deficiency notice to Financial Controller.
6. **Evidence Retained:** Monthly trial balance tie-out register with month-by-month balancing assertions.

---

### Control 04: Account Code Completeness
1. **What it Tests:** Asserts that zero rows have null, empty, or whitespace-only account code identifiers.
2. **Why it Matters:** Account codes are the primary relational foreign keys used to map accounts into financial statement categories.
3. **How it is Performed:**
   $$\text{Count}(\text{Rows where } \text{Account\_Code} \text{ IS NULL OR TRIM}(\text{Account\_Code}) = '') \equiv 0$$
4. **What a Failed Result Indicates:** Orphaned transaction lines, summary subtotal rows improperly included in raw data, or corrupted ERP export formatting.
5. **What the Analyst Does Next:** Filters and isolates blank account rows. If they represent subtotal headers, they are purged; if they are true orphaned transactions, they are escalated to the client.
6. **Evidence Retained:** Exception log confirming zero null account identifiers.

---

### Control 05: Leading Zero Preservation
1. **What it Tests:** Verifies that account codes containing leading zeros (e.g., `001050`, `04-2010`) were not converted to numeric integers (`1050`, `4-2010`).
2. **Why it Matters:** Converting string account codes to numbers permanently corrupts relational joins against the Chart of Accounts.
3. **How it is Performed:** RegEx pattern validation confirming that ingested account codes match the character length and structure of the master COA.
4. **What a Failed Result Indicates:** An analyst opened the raw CSV in Excel and re-saved it, allowing Excel's default type auto-detection to strip leading zeros.
5. **What the Analyst Does Next:** Discards the modified file; re-ingests the raw unedited source file via Power Query or Python with explicit text typing.
6. **Evidence Retained:** Type validation log confirming text string casting.

---

### Control 06: Date Range Boundary Check
1. **What it Tests:** Asserts that every transaction posting date falls strictly between the approved diligence start date and end date.
2. **Why it Matters:** Prevents future-dated entries or historical out-of-scope entries from distorting financial metrics.
3. **How it is Performed:**
   $$\min(\text{Posting Date}) \ge \text{Diligence Start Date} \quad \text{AND} \quad \max(\text{Posting Date}) \le \text{Diligence End Date}$$
4. **What a Failed Result Indicates:** Inclusion of memorized/future transactions or incorrect filter criteria applied during ERP extraction.
5. **What the Analyst Does Next:** Segregates out-of-scope transactions; requests confirmation from client accounting.
6. **Evidence Retained:** Date boundary audit log showing minimum and maximum timestamp bounds.

---

### Control 07: Missing Period Detection
1. **What it Tests:** Verifies that exactly 36 consecutive monthly accounting periods exist without temporal gaps.
2. **Why it Matters:** A missing month conceals seasonal fluctuations, revenue declines, or delayed expense postings.
3. **How it is Performed:**
   $$\text{Count}(\text{Distinct Monthly Period Dates}) \equiv 36$$
4. **What a Failed Result Indicates:** Client omitted a month from the export or skipped an interim accounting close.
5. **What the Analyst Does Next:** Halts data preparation; issues immediate request for missing monthly trial balances.
6. **Evidence Retained:** Monthly timeline schedule with confirmed coverage for all 36 periods.

---

### Control 08: Duplicate Line Detection
1. **What it Tests:** Asserts that every transactional row has a unique primary key or composite identifier.
2. **Why it Matters:** Duplicate transactions artificially double revenues or expenses, distorting EBITDA.
3. **How it is Performed:**
   $$\text{Count}(\text{Distinct Primary Keys}) \equiv \text{Total Ingested Rows}$$
4. **What a Failed Result Indicates:** Client ran overlapping export queries (e.g., exporting YTD and Q4 files that overlap) and appended them.
5. **What the Analyst Does Next:** Deduplicates identical rows based on composite keys (`Document_ID` + `Account` + `Date` + `Amount`); logs deduplication count.
6. **Evidence Retained:** Deduplication log recording removed rows and retained unique population.

---

### Control 09: 100% Chart of Accounts Mapping Coverage
1. **What it Tests:** Asserts that every active account code in the trial balance is mapped to a valid Level 1, Level 2, and Level 3 category in the master taxonomy.
2. **Why it Matters:** Unmapped accounts cause revenues or expenses to vanish from financial statement summaries, creating erroneous EBITDA numbers.
3. **How it is Performed:**
   $$\text{Count}(\text{Trial Balance Rows where } \text{L1\_Statement\_Tier IS NULL AND Balance} \ne 0.00) \equiv 0$$
4. **What a Failed Result Indicates:** The target introduced new accounts mid-period that are missing from the initial mapping dictionary.
5. **What the Analyst Does Next:** Traps unmapped accounts into the `UNMAPPED_ACCOUNTS_EXCEPTION_LOG`; assigns a senior reviewer to classify the account.
6. **Evidence Retained:** Master Chart of Accounts mapping sign-off showing 100% mapping coverage.

---

### Control 10: Formula vs. Hardcode Integrity Audit
1. **What it Tests:** Inspects client-provided summary spreadsheets to identify cells where formulas were overwritten with static numbers.
2. **Why it Matters:** Sellers frequently overwrite subtotal formulas to hide plug numbers, balance sheet imbalances, or poor performance.
3. **How it is Performed:** Automated audit script checking `.HasFormula` property across all total and subtotal rows.
4. **What a Failed Result Indicates:** Intentional or accidental tampering with summary calculations.
5. **What the Analyst Does Next:** Rejects the client’s summary spreadsheet; rebuilds the entire P&L and Balance Sheet natively from the raw trial balance.
6. **Evidence Retained:** Redline audit schedule highlighting hardcoded cells and calculated discrepancies.

---

### Control 11: Opening-to-Closing Balance Sheet Continuity Roll-Forward
1. **What it Tests:** Verifies that the ending balance of each balance sheet account in period $t-1$ exactly matches the opening balance in period $t$.
2. **Why it Matters:** Detects unannounced retroactive journal entries posted into closed prior periods.
3. **How it is Performed:**
   $$\mathbf{\text{Ending Balance}}_{i,t-1} + \mathbf{\text{Period Net Activity}}_{i,t} \equiv \mathbf{\text{Ending Balance}}_{i,t}$$
4. **What a Failed Result Indicates:** The client reopened a closed prior period and posted retroactive changes without notifying the diligence team.
5. **What the Analyst Does Next:** Executes a Version Delta Audit to isolate the exact retroactive entries; demands a formal client explanation.
6. **Evidence Retained:** Balance sheet continuity schedule showing zero unexplained roll-forward breaks.

---

### Control 12: Retained Earnings Continuity Bridge
1. **What it Tests:** Bridges opening retained earnings to ending retained earnings via reported GAAP net income and distributions.
2. **Why it Matters:** Confirms that the Income Statement ties mathematically to the Balance Sheet equity section.
3. **How it is Performed:**
   $$\mathbf{\text{Ending Retained Earnings}}_t \equiv \mathbf{\text{Beg Retained Earnings}}_{t-1} + \mathbf{\text{Net Income}}_t - \mathbf{\text{Dividends / Distributions}}_t$$
4. **What a Failed Result Indicates:** Direct-to-equity adjustments (bypassing the P&L) or unrecorded owner dividend draws.
5. **What the Analyst Does Next:** Analyzes general ledger activity in equity accounts to identify non-operating charges routed directly to equity.
6. **Evidence Retained:** Retained earnings roll-forward workpaper reconciling net income to balance sheet equity.

---

### Control 13: Suspense & Clearing Account Scrubbing
1. **What it Tests:** Verifies that suspense, payroll clearing, and "Ask My Accountant" accounts have a net zero balance at each period end.
2. **Why it Matters:** Clearing accounts are commonly used to park unresolved cash disbursements, unrecorded payroll taxes, or unallocated expenses.
3. **How it is Performed:**
   $$\text{Ending Balance in Account } 9990 \text{ (Suspense)} \equiv \$0.00$$
4. **What a Failed Result Indicates:** Incomplete monthly closes, cash leakage, or unrecorded operating expenses.
5. **What the Analyst Does Next:** Requests general ledger detail for all activity passing through suspense; flags non-zero balances for EBITDA adjustment in Workstream 05.
6. **Evidence Retained:** Suspense account analysis schedule with transactional itemization.

---

### Control 14: Subledger-to-General-Ledger Control Account Tie-Out
1. **What it Tests:** Reconciles the detailed Accounts Receivable (AR) and Accounts Payable (AP) subledger agings to the trial balance control accounts.
2. **Why it Matters:** Proves that the aging schedules represent the real assets and liabilities on the balance sheet.
3. **How it is Performed:**
   $$\sum \text{Aged AR Subledger Invoices} \equiv \text{GL Account } 1100 \text{ (Trade Receivables)}$$
   $$\sum \text{Aged AP Subledger Invoices} \equiv \text{GL Account } 2010 \text{ (Trade Payables)}$$
4. **What a Failed Result Indicates:** Manual top-side journal entries posted directly to the general ledger control account bypassing the subledger, or unapplied customer cash.
5. **What the Analyst Does Next:** Quantifies the variance; investigates whether the difference represents uncollectible receivables or unrecorded liabilities.
6. **Evidence Retained:** Subledger tie-out schedule documenting variances between aging reports and the general ledger.

---

### Control 15: Version Collision Delta Audit
1. **What it Tests:** Compares re-submitted client files against prior submissions for identical historical periods.
2. **Why it Matters:** Clients often upload revised files that quietly alter historical earnings without explanation.
3. **How it is Performed:**
   $$\Delta_{i,t} = \text{AccountBalance}_{i,t}^{(\text{Revised})} - \text{AccountBalance}_{i,t}^{(\text{Prior})}$$
4. **What a Failed Result Indicates:** Unannounced retroactive restatements or earnings management.
5. **What the Analyst Does Next:** Generates a delta variance report; demands written client reconciliation explaining every non-zero delta.
6. **Evidence Retained:** Delta comparison workpaper with highlighted historical variances.

---

### Control 16: Intercompany Zero-Sum Parity Assertion
1. **What it Tests:** Confirms that intercompany receivables and payables net to absolute zero across the consolidated perimeter.
2. **Why it Matters:** An intercompany imbalance indicates cash leakage, uneliminated intercompany profit, or out-of-perimeter entity involvement.
3. **How it is Performed:**
   $$\sum_{k=1}^{M} \text{Intercompany AR}_k - \sum_{k=1}^{M} \text{Intercompany AP}_k \equiv 0.00$$
4. **What a Failed Result Indicates:** Mismatched transfer pricing, unrecorded intercompany management fees, or timing differences between entity closes.
5. **What the Analyst Does Next:** Isolates the entity pair causing the imbalance; reviews intercompany journal entries to identify the unrecorded offset.
6. **Evidence Retained:** Intercompany elimination matrix showing entity-by-entity cross-reconciliations.

---

## 2. The Strict Boundary Rule: Integrity Verification vs. Substantive Reconciliation

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE WORKSTREAM 02 OPERATIONAL BOUNDARY                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Data Preparation Controls (01 to 16) test INTERNAL TECHNICAL INTEGRITY ONLY.         │
│ 2. If a control fails (e.g. an unbalanced suspense balance of $42,500 in Control 13),   │
│    the data preparation team DOES NOT adjust, reclassify, or plug the balance.         │
│ 3. The anomaly is isolated into an Exception Log, and the pure raw data is retained.   │
│ 4. Substantive reconciliations against external tax returns (IRS Form 1120/1065) and   │
│    audited financial statements belong strictly to Workstream 03 (Reconciliation).    │
│ 5. Proposing adjusting journal entries (AJEs) to haircut EBITDA belongs to Workstream  │
│    05 (EBITDA Normalization).                                                          │
│ 6. In the simulator, any attempt to "solve" a failure by silently editing client data  │
│    triggers a fatal Evidentiary Tampering penalty.                                     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
