# EBITDA Adjustment Calculation Library & Normalization Mechanics
**Document Reference:** `QOE-CALC-LIB-05`  
**Workstream:** `05 — EBITDA Normalization and Adjustments`  
**Classification:** Professional Financial Due Diligence Technical Specification  

---

## 1. Architectural Taxonomy of EBITDA Variants

In professional Financial Due Diligence (FDD) and Quality of Earnings (QoE) engagements, the term "EBITDA" is never used without precise qualification. Diligence teams distinguish between six discrete layers of operating profitability:

```
+-------------------------------------------------------------------------------+
| 1. Reported Accounting EBITDA (Management Accounts / Trial Balance P&L)       |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼ [Workstream 03 Tie-Out & Error Corrections]
+-------------------------------------------------------------------------------+
| 2. Reconciled Historical EBITDA (Audited FS & Clean General Ledger Baseline)   |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼ [Management Proposed Pitch Book Add-Backs]
+-------------------------------------------------------------------------------+
| 3. Management Adjusted EBITDA (Unvetted Seller Presentation)                  |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼ [QoE Due Diligence Scrutiny & Normalization]
+-------------------------------------------------------------------------------+
| 4. QoE Normalized / Adjusted EBITDA (Defensible Sustainable Baseline)         |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼ [In-Period Operational Run-Rate Changes]
+-------------------------------------------------------------------------------+
| 5. Run-Rate EBITDA (Annualized Mid-Year Price, Volume, Headcount Shifts)      |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼ [Structural Scope Shifts: M&A, Divestitures]
+-------------------------------------------------------------------------------+
| 6. Pro Forma EBITDA (Full-Year Restated Enterprise Scope)                    |
+-------------------------------------------------------------------------------+
```

### Definitions & Structural Distinctions

$$\begin{aligned}
\text{Reported EBITDA} &= \text{Operating Income (EBIT)} + \text{Depreciation} + \text{Amortization} \\
\text{Reconciled Historical EBITDA} &= \text{Reported EBITDA} \pm \Delta_{\text{Reconciliation Errors}} \pm \Delta_{\text{Cut-Off Adjustments}} \\
\text{QoE Normalized EBITDA} &= \text{Reconciled Historical EBITDA} + \sum \text{Accepted Add-backs} - \sum \text{Mandatory QoE Deductions} \\
\text{Run-Rate EBITDA} &= \text{QoE Normalized EBITDA} + \sum \Delta_{\text{Annualized Mid-Period Changes}} \\
\text{Pro Forma EBITDA} &= \text{Run-Rate EBITDA} + \sum \Delta_{\text{Full-Year Acquired Operations}} - \sum \Delta_{\text{Divested Operations}}
\end{aligned}$$

* **Reported EBITDA:** The raw figure derived from client monthly management accounts or unadjusted trial balances.
* **Reconciled Historical EBITDA:** The mathematically verified baseline resulting from Workstream 03 (Reconciliation) and Workstream 04 (Historical Analysis). It incorporates technical GAAP/IFRS corrections, inventory valuation adjustments, revenue cut-off corrections, and elimination of topside plug entries.
* **Adjusted EBITDA:** A general market term referring to EBITDA after add-backs. Management teams typically maximize this number by adding back every conceivable non-operational, non-recurring, or discretionary expense.
* **Normalized EBITDA:** The professional QoE standard. Represents the recurring, sustainable earning power of the target business under current operating scope, eliminating non-arm's-length arrangements, non-operating revenues/gains, and adjusting executive compensation to market replacement levels.
* **Run-Rate EBITDA:** Normalizes for operational changes that occurred *during* the measurement period (e.g., a contractual price hike enacted on October 1 annualized across the full 12 months, or a permanent plant shutdown occurring in Q3).
* **Pro Forma EBITDA:** Restates historical performance to reflect structural changes in corporate perimeter (e.g., incorporating 12 full months of an entity acquired on November 15, or carving out a discontinued subsidiary).

---

## 2. Mathematical Formulas & Calculation Logic

### 2.1 General Ledger Tracing & Invoice Verification
Prior to accepting any proposed adjustment, the QoE practitioner must verify the expense debit in the General Ledger (GL) and substantiate it with third-party source documentation:

$$\text{Coverage Ratio} = \frac{\sum_{i=1}^{k} \text{Sampled Invoice Amount}_i}{\text{Total Claimed Adjustment Amount}} \ge 0.85 \quad (85.0\% \text{ Mandatory Threshold})$$

$$\text{Variance Error Rate} = \frac{|\sum \text{GL Debits} - \sum \text{Invoiced Amounts}|}{\sum \text{GL Debits}}$$

* If $\text{Variance Error Rate} > 0.05$ (5%), the untested balance is rejected in full, and management must provide a reconciled sub-ledger.
* Any item lacking third-party invoice backing is reclassified as `Rejected-Addback`.

---

### 2.2 Owner / Executive Compensation Replacement Benchmarking
Owner-operators of closely held enterprises frequently draw discretionary compensation, distribute profits via W-2 payroll, or employ family members at non-market rates. The normalization formula replaces total historical owner-related costs with fair market value (FMV) executive compensation:

$$\text{Net Owner Compensation Add-Back} = \text{Total Historical Owner Cost} - \text{FMV Replacement Cost}$$

Where:
$$\text{Total Historical Owner Cost} = \sum (\text{Base W-2 Salary} + \text{Discretionary Bonuses} + \text{Employer Payroll Taxes} + \text{Employer 401(k) / Pension Match} + \text{Corporate Medical/Dental Premiums} + \text{Personal Perks \& Auto Allowances})$$

$$\text{FMV Replacement Cost} = (\text{Benchmark Replacement Base Salary} \times (1 + \tau_{\text{payroll}})) + \text{Benchmark Target Bonus} + \text{Standard Corporate Benefit Load}$$

* $\tau_{\text{payroll}}$: Standard employer statutory payroll taxes (FICA/Medicare/Unemployment, typically $7.65\% - 9.0\%$).
* Benchmark sources: Mercer Executive Compensation Survey, Robert Half Management Resources, Economic Research Institute (ERI), or specialized executive search retained quotes.
* **Double-Counting Firewall:** If an owner's personal auto lease or personal travel is already captured under SG&A Travel/Vehicle add-backs, it *must* be deducted from `Total Historical Owner Cost` to prevent duplicate add-backs.

---

### 2.3 Related-Party Facility Rent & Lease Normalization
When a target company leases operational facilities (warehouses, plants, headquarters) from an entity owned by the company's founders or shareholders, rental rates frequently deviate from open-market commercial rates:

$$\text{Net Rent Normalization Adjustment} = \text{Actual Contractual Rent Expensed} - \text{Certified Fair Market Rent (FMV)}$$

Where:
$$\text{Certified Fair Market Rent (FMV)} = \text{Certified Square Footage} \times \text{Independent Appraised Market Rate per Sq Ft} \pm \text{NNN Expense Adjustments}$$

* **Triple-Net (NNN) Adjustment:** If the historical lease was Gross (landlord paid property tax and insurance) but the post-transaction commercial lease will be NNN (tenant pays property tax and insurance), the FMV base rent must be adjusted:
$$\text{Adjusted FMV Rent} = \text{Market NNN Base Rent} + \text{Historical Property Taxes} + \text{Historical Building Insurance}$$
* A positive result represents an **Add-Back** (historical rent was above market, inflating historical expense).
* A negative result represents an **EBITDA Deduction** (historical rent was below market, artificially depressing historical expense and overstating reported EBITDA).

---

### 2.4 Extraordinary Casualty Losses Net of Insurance Recovery
Management frequently adds back the gross repair costs of a casualty event (storm, fire, flood) while allowing the insurance reimbursement to remain in Operating Income or Other Income, effectively double-counting the earnings benefit:

$$\text{Net Casualty Loss Add-Back} = \max\left(0, \; \text{Gross Casualty Repair Costs} - \text{Insurance Reimbursements Received/Accrued}\right)$$

Concurrently, if the insurance reimbursement was booked to Operating Income:
$$\text{Mandatory QoE Deduction} = -\text{Insurance Proceeds Credited to Operating P&L}$$

$$\text{Combined Net Diligence Impact} = \text{Gross Repair Costs} - \text{Insurance Reimbursements} - \text{Insurance Income Credit} \equiv 0$$

* If insurance fully covered the damage, the net impact on maintainable EBITDA is **Zero**.
* If repair costs were debited to Property, Plant & Equipment (Capital Expenditure) rather than P&L, **Zero Add-Back is Permitted**, and any insurance recovery credited to P&L must be deducted in full.

---

### 2.5 Severance & Facility Closure Restructuring
To qualify as an acceptable add-back, severance and exit costs must be tied to a permanent, non-reversible operational change:

$$\text{Normalized Severance Add-Back} = \sum_{j \in \text{Closed Site}} \text{Contractual Separation Pay}_j - \text{Historical Normal Employee Turnover Expense}$$

Conditions for Acceptance:
1. The physical location must be permanently closed, or the business line discontinued.
2. Terminated positions must *not* be backfilled at other locations.
3. Leases must be legally terminated or subleased with verified liability settlement.
4. Normal recurring severance (annual executive churn, routine operational turnover) is treated as recurring SG&A and rejected.

---

### 2.6 Run-Rate Annualization Formula
When an operational change occurs mid-year, historical actuals only reflect a fraction of the full-year financial impact. The run-rate adjustment annualizes the structural shift:

$$\text{Run-Rate Adjustment} = (\text{Annualized Run-Rate Metric}) - (\text{Historical Actuals Incurred in Period})$$

For an in-period price increase enacted at month $m$ (where $m \in [1, 12]$):
$$\text{Run-Rate Price Adjustment} = \sum_{t=1}^{m-1} \left( \text{Volume}_t \times (\text{New Unit Price} - \text{Old Unit Price}) \right)$$

For a mid-year operational headcount addition hired at month $m$:
$$\text{Run-Rate Headcount Cost Adjustment} = -\sum_{t=1}^{m-1} \left( \text{Monthly Fully Loaded Compensation} \right)$$

---

### 2.7 Working Capital vs. EBITDA Double-Counting Firewall

A cardinal rule of transaction advisory is preserving the mathematical firewall between **EBITDA Normalization**, **Net Working Capital (NWC)**, and **Net Debt / Debt-Like Items**:

```
+----------------------------------------------------------------------------------------------------+
|                                    TRANSACTION VALUE EQUATION                                      |
|                                                                                                    |
|   Enterprise Value (EV) = QoE Normalized EBITDA  x  Agreed Valuation Multiple                     |
|   Equity Purchase Price = Enterprise Value  -  Net Debt  +  (Closing NWC  -  Target NWC Peg)      |
+----------------------------------------------------------------------------------------------------+
```

Any financial item can only be settled in **one** of these three mechanisms:

| Financial Item | Correct Transaction Treatment | Double-Counting Violation If Misplaced |
| :--- | :--- | :--- |
| **Accrued Transaction Bonuses** | Deducted dollar-for-dollar as **Debt-Like Item** in Enterprise-to-Equity Bridge. | Adding back to EBITDA *and* deducting from purchase price as Net Debt creates double recovery for buyer. |
| **Unpaid Customer Rebates / Returns Reserve** | Settled in **Net Working Capital** peg and true-up. | Adding back to EBITDA inflates EV, while adjusting NWC penalizes seller twice. |
| **Past Due Sales Tax / Payroll Tax Liabilities** | Deducted as **Debt-Like Item**. | Do not adjust in EBITDA unless ongoing compliance cost increases baseline OpEx. |
| **Capitalized Software / Development Fees** | Balance Sheet asset creation (CapEx). | Adding back to EBITDA an item that never entered P&L double-counts earnings. |

---

## 3. Screening & Materiality Decision Framework

### Materiality Thresholds
In professional FDD, adjustments are subjected to strict scoping thresholds:

$$\text{Individual Item De Minimis Threshold} = \min\left(\$25,000, \; 0.5\% \times \text{Reported EBITDA}\right)$$

$$\text{Aggregate Category Scoping Threshold} = \min\left(\$50,000, \; 1.0\% \times \text{Reported EBITDA}\right)$$

* Any proposed adjustment below the de minimis threshold is waived unless it relates to a systemic internal control failure or recurring compliance breach.

### Buy-Side vs. Sell-Side Posture Matrix

```
+------------------------------+----------------------------------+----------------------------------+
| Dimension                    | Buy-Side QoE Posture             | Sell-Side / Vendor Due Diligence |
+------------------------------+----------------------------------+----------------------------------+
| Primary Objective            | Protect buyer from overpaying;   | Maximize defensible valuation;   |
|                              | uncover earnings risks & haircuts| capture all supportable add-backs|
+------------------------------+----------------------------------+----------------------------------+
| Treatment of Ambiguous Items | Default to REJECT / DEDUCT       | Default to PRESENT WITH CAVEATS  |
+------------------------------+----------------------------------+----------------------------------+
| Future Cost Savings          | Exclude entirely from historical | Present as Pro Forma Run-Rate    |
+------------------------------+----------------------------------+----------------------------------+
| Replacement Costs            | Fully burden management costs    | Benchmark to lowest defensible   |
+------------------------------+----------------------------------+----------------------------------+
| Standard of Proof            | Executed contracts + bank proof  | Management representation + plan |
+------------------------------+----------------------------------+----------------------------------+
```
