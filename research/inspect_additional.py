"""
Inspection Reports for Category 9 (Lehman Repo 105) and Category 10 (QoE Advisory Evidence)
"""

import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSPECTION_DIR = os.path.join(BASE_DIR, 'dataset_inspections')
os.makedirs(INSPECTION_DIR, exist_ok=True)

def generate_lehman_report():
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    report = """# Technical Inspection Report: Lehman Brothers Bankruptcy Examiner Report (Volume 3: Repo 105)

**Category:** `Category 9: Internal Documentation and Communications`  
**Inspection Date:** `""" + ts + """`  
**Originating Organization:** United States Bankruptcy Court for the Southern District of New York (SDNY) / Jenner & Block LLP  
**Primary Examiner:** Anton R. Valukas (Court-Appointed Examiner)  
**Legal Case:** *In re Lehman Brothers Holdings Inc., et al.*, Chapter 11 Case No. 08-13555 (JHG)  
**Classification:** `Real-world, Identifiable`  
**License:** Public Court Record (Federal Judicial Document)  
**Documentary Scope:** 300+ pages of forensic audit findings, internal emails, executive presentations, accounting policy memos, and workpaper exhibits  

## 1. Provenance & Investigative Authority
On January 16, 2009, the U.S. Bankruptcy Court appointed Anton R. Valukas as independent examiner to investigate the causes of Lehman Brothers' failure. The investigation reviewed over 34 million pages of documents, interviewed hundreds of former executives, traders, and accountants, and analyzed Lehman's proprietary trading and general ledger systems (including `GMI`, `ITS`, and `SAP`). Volume 3 represents the definitive real-world forensic examination of **quarter-end balance sheet manipulation and Net Debt concealment**.

## 2. Core Accounting Mechanics: Repo 105 and Repo 108
- **Standard Repurchase Agreement (Repo):** A firm sells securities in exchange for short-term cash, committing to repurchase them days later. Under US-GAAP, repos are accounted for as **collateralized financings (borrowings)**: Cash increases (debit), and Short-Term Debt increases (credit). Balance sheet size and leverage remain unchanged.
- **Lehman's Repo 105 Maneuver:** Lehman exploited an aggressive interpretation of **SFAS 140 (Accounting for Transfers and Servicing of Financial Assets and Extinguishments of Liabilities)**. By transferring collateral worth at least 105% (or 108% for fixed income) of the cash received, Lehman claimed it had surrendered control of the securities:
  - **Accounting Entry at Quarter-End:**
    - Debit: `Cash` (Asset)
    - Credit: `Financial Instruments Owned / Inventory` (Asset reduction)
    - Consequence: Net balance sheet assets were reduced dollar-for-dollar without recording any short-term liability!
  - **Reversal Entry Immediately Post Quarter-End:**
    - Within 2 to 7 days after the balance sheet date, Lehman borrowed funds to repurchase the securities plus interest, restoring the billions in debt.

## 3. Empirical Scale of Balance Sheet Window Dressing
The Examiner established the exact scale of quarter-end balance sheet netting:
- **Q4 2007 (Nov 2007):** $38.6 billion of off-balance-sheet Repo 105 usage.
- **Q1 2008 (Feb 2008):** $49.1 billion of off-balance-sheet Repo 105 usage.
- **Q2 2008 (May 2008):** $50.38 billion of off-balance-sheet Repo 105 usage.
- **Reported vs. True Net Leverage:**
  - Q1 2008 Reported Net Leverage: `15.4x` (Manipulated) | True Net Leverage: `17.3x`
  - Q2 2008 Reported Net Leverage: `12.1x` (Manipulated) | True Net Leverage: `13.9x`
  - Gross Leverage was similarly suppressed from over `32x` down to `24x`.

## 4. Internal Documentation & Communications Unearthed
The Examiner subpoenaed and analyzed critical internal communications showing executive knowledge and balance sheet targets:
1. **Balance Sheet Target Directives:** CFO Erin Callan and Treasury Director Paolo Tonucci maintained explicit quarterly balance sheet reduction targets, monitoring Repo 105 usage daily leading up to quarter-end.
2. **Auditor Interactions (Ernst & Young):** E&Y was explicitly questioned about Repo 105 by Lehman Senior Vice President Matthew Lee in May 2008. E&Y failed to inform Lehman's Audit Committee or insist on footnote disclosure in the 10-Q filings.
3. **Jurisdictional Arbitrage (Linklaters Legal Opinion):** Because no major U.S. law firm would provide a true sale opinion under U.S. law, Lehman routed all Repo 105 transactions through its UK broker-dealer subsidiary (**Lehman Brothers International Europe - LBIE**) under English law opinions obtained from Linklaters.

## 5. QoE Simulator Value & Forensic Applications
1. **Net Debt Definition & Debt-Like Item Verification:** Demonstrates how companies manipulate Net Debt at balance sheet measurement dates through temporary liquidation of assets or window dressing.
2. **Quarter-End Cutoff Analysis:** Proves the necessity in QoE to inspect daily/weekly general ledger cash and liability balances rather than relying solely on quarterly balance sheet dates.
3. **Internal Control & Management Bias Modeling:** Provides authentic behavioral evidence of how financial pressure leads corporate executives to exploit accounting standard thresholds.
"""
    with open(os.path.join(INSPECTION_DIR, "lehman_repo105_inspection.md"), "w", encoding="utf-8") as f:
        f.write(report)
    print("Generated lehman_repo105_inspection.md")

def generate_qoe_advisory_report():
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    report = """# Technical Inspection Report: Quality of Earnings & Transaction Advisory Evidence

**Category:** `Category 10: Quality of Earnings (QoE) and Transaction Advisory Evidence`  
**Inspection Date:** `""" + ts + """`  
**Originating Frameworks:** SEC EDGAR M&A Merger Proxy Exhibits (Schedule 14D-9 / DEFM14A under Item 1015 of Regulation M-A) & Transaction Advisory Practice Standards (Alvarez & Marsal, Stout, Riveron, CohnReznick)  
**Classification:** `Real-world, Identifiable & Anonymized Industry Benchmarks`  
**Documentary Scope:** Deal-level financial due diligence schedules, EBITDA normalization bridges, Working Capital peg models, and Net Debt definitions  

## 1. Purpose in M&A Due Diligence
In private equity acquisitions and corporate M&A, Quality of Earnings (QoE) analyses bridge the gap between historical financial statements (GAAP or management accounts) and the **true, sustainable, standalone economic earnings** of the business. 

The primary outputs inspected in this category govern:
1. **Adjusted EBITDA (The Valuation Multiple Base):** Determines the enterprise purchase price:
   $$\\text{Enterprise Value} = \\text{Adjusted EBITDA} \\times \\text{Agreed Transaction Multiple}$$
2. **Net Working Capital Target / Peg (Working Capital True-Up):** Protects the buyer against post-closing cash drain:
   $$\\text{Closing Adjustment} = \\text{Closing NWC} - \\text{NWC Peg}$$
3. **Net Debt & Debt-Like Items (Equity Purchase Price Bridge):**
   $$\\text{Equity Value} = \\text{Enterprise Value} - \\text{Funded Debt} - \\text{Debt-Like Items} + \\text{Cash}$$

---

## 2. The Standard QoE EBITDA Normalization Bridge
Based on analysis of authentic SEC fairness opinion presentations and transaction advisory working papers, EBITDA adjustments fall into five empirical categories:

```
Reported GAAP / Management Net Income
  + Income Tax Expense
  + Interest Expense (Net of Interest Income)
  + Depreciation and Amortization Expense
= Reported EBITDA
  ──────────────────────────────────────────────────────────
  [Category A: Owner & Discretionary Compensation Normalization]
  + / - Owner Salary Adjustment to Fair Market Value (FMV)
  + Elimination of Discretionary Owner Expenses (Auto, Travel, Club Dues)
  + Non-Arm's Length Family Member Payroll Disallowance
  ──────────────────────────────────────────────────────────
  [Category B: Non-Recurring & Extraordinary Expenses]
  + One-Time Transaction Legal and Advisory Fees
  + Severance & Executive Termination Packages
  + Facility Consolidation & Move Expenses
  + Non-Recurring Litigation Settlements & Defenses
  + ERP / IT System Implementation Transition Expenses
  ──────────────────────────────────────────────────────────
  [Category C: Pro Forma Run-Rate Adjustments]
  + Full-Year Run-Rate Effect of Mid-Year Price Increases
  + Full-Year Run-Rate Effect of New Contracted Customer Wins
  - Full-Year Run-Rate Effect of Lost Key Customers / Contracts
  + Annualized Headcount Reductions Executed During Period
  ──────────────────────────────────────────────────────────
  [Category D: Standalone Public / Carve-Out Operating Costs]
  - Carve-Out Corporate Overhead Deductions (HR, Legal, Treasury, IT)
  - Dedicated Executive Replacement Costs
  - Standalone Insurance and Audit Fees
  ──────────────────────────────────────────────────────────
  [Category E: Accounting Policy & Cutoff Normalizations]
  + / - Out-of-Period Revenue Recognition Corrections (ASC 606)
  + / - Inventory Capitalization & Obsolescence Reserve Adjustments
  + / - Bad Debt Reserve Normalization
  - Non-Operating Income (Asset Sales, PPP Loan Forgiveness)
= Adjusted EBITDA (Quality of Earnings Benchmark)
```

---

## 3. Working Capital Peg Mechanics & Seasonality Analysis
- **Definition of Working Capital:**
  $$\\text{NWC} = (\\text{Accounts Receivable} + \\text{Inventory} + \\text{Prepaids}) - (\\text{Accounts Payable} + \\text{Accrued Operating Expenses} + \\text{Accrued Payroll})$$
- **The "Peg" Calculation:**
  - Typically set as the **Trailing Twelve Month (TTM) average** or **Trailing 24 Month average** of month-end Net Working Capital.
  - Seasonality Adjustments: In seasonal businesses, setting the peg at an unadjusted 12-month average creates artificial closing true-ups. The QoE report establishes seasonal quarterly pegs (e.g. Q1 Low Season Peg vs Q3 Peak Season Peg).
- **Excluded Items (Treated as Debt-Like or Cash-Like):**
  - Income taxes payable (Debt-like)
  - Cash and cash equivalents (Cash adjustment)
  - Current portion of long-term debt (Funded debt)
  - Transaction bonuses (Debt-like)

---

## 4. Net Debt & Debt-Like Item Inventory
The debt schedule bridges Enterprise Value to cash proceeds distributed at closing:
1. **Funded Debt:** Revolving credit line principal, term loan balances, promissory notes, subordinated notes.
2. **Debt-Like Liabilities Discovered in Due Diligence:**
   - Overdue / Stretched Accounts Payable (invoices > 90/120 days deemed off-market borrowing).
   - Customer Deposits & Deferred Revenue Haircut (cash collected where service obligations remain).
   - Unfunded Pension & Post-Retirement Obligations.
   - Accrued Vacation & Paid Time Off (PTO) liabilities.
   - Unpaid Prior Period Tax Liabilities & Transfer Pricing Reserves.
   - Capital / Finance Lease Obligations (ASC 842 / IFRS 16 liabilities).
   - Uncleared Checks in Excess of Bank Balance (Book Overdrafts).
3. **Cash Adjustments:**
   - Freely available cash (added to purchase price).
   - Trapped Cash Deductions (restricted cash, collateral deposits, foreign cash subject to repatriation tax).

---

## 5. Direct Integration into the QoE Simulator
This empirical framework provides the exact mathematical rules and operational logic for the QoE Simulator:
1. **Scenario Generation:** Inject authentic irregularities (e.g. personal expenses hidden in travel accounts, stretched payables, out-of-period revenue recognition).
2. **Student / Analyst Challenge:** Requiring the user to audit the simulated general ledger, discover the anomalies, compile the EBITDA normalization bridge, calculate the Working Capital peg, and determine the closing Net Debt purchase price adjustment.
"""
    with open(os.path.join(INSPECTION_DIR, "qoe_transaction_advisory_inspection.md"), "w", encoding="utf-8") as f:
        f.write(report)
    print("Generated qoe_transaction_advisory_inspection.md")

if __name__ == "__main__":
    generate_lehman_report()
    generate_qoe_advisory_report()
