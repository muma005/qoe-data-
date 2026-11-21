# Technical Inspection Report: Quality of Earnings & Transaction Advisory Evidence

**Category:** `Category 10: Quality of Earnings (QoE) and Transaction Advisory Evidence`  
**Inspection Date:** `2026-11-12 10:52:57`  
**Originating Frameworks:** SEC EDGAR M&A Merger Proxy Exhibits (Schedule 14D-9 / DEFM14A under Item 1015 of Regulation M-A) & Transaction Advisory Practice Standards (Alvarez & Marsal, Stout, Riveron, CohnReznick)  
**Classification:** `Real-world, Identifiable & Anonymized Industry Benchmarks`  
**Documentary Scope:** Deal-level financial due diligence schedules, EBITDA normalization bridges, Working Capital peg models, and Net Debt definitions  

## 1. Purpose in M&A Due Diligence
In private equity acquisitions and corporate M&A, Quality of Earnings (QoE) analyses bridge the gap between historical financial statements (GAAP or management accounts) and the **true, sustainable, standalone economic earnings** of the business. 

The primary outputs inspected in this category govern:
1. **Adjusted EBITDA (The Valuation Multiple Base):** Determines the enterprise purchase price:
   $$\text{Enterprise Value} = \text{Adjusted EBITDA} \times \text{Agreed Transaction Multiple}$$
2. **Net Working Capital Target / Peg (Working Capital True-Up):** Protects the buyer against post-closing cash drain:
   $$\text{Closing Adjustment} = \text{Closing NWC} - \text{NWC Peg}$$
3. **Net Debt & Debt-Like Items (Equity Purchase Price Bridge):**
   $$\text{Equity Value} = \text{Enterprise Value} - \text{Funded Debt} - \text{Debt-Like Items} + \text{Cash}$$

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
  $$\text{NWC} = (\text{Accounts Receivable} + \text{Inventory} + \text{Prepaids}) - (\text{Accounts Payable} + \text{Accrued Operating Expenses} + \text{Accrued Payroll})$$
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
