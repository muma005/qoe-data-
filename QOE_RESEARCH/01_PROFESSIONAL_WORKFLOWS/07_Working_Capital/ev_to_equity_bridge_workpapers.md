# Master Enterprise Value to Equity Value Bridge Workpapers
**Document Reference:** `QOE-WP-EVBRIDGE-07`  
**Engagement:** Apex Global Industrial Holding Inc. (Project Titanium)  
**Valuation Date:** Closing as of December 31, 2023  
**Review Standard:** AICPA Quality of Earnings / Buy-Side Financial Due Diligence  

---

## 1. Executive Summary & Purchase Price Bridge Architecture

In M&A transactions, the headline enterprise valuation agreed in the Letter of Intent (LOI) does not represent the cash paid to the seller at closing. The **Enterprise Value to Equity Value Bridge** converts theoretical enterprise value into the definitive cash purchase price.

During due diligence on Apex Global Industrial Holding Inc. ("Apex"), the buy-side QoE team audited management's proposed transaction bridge. 

Management claimed an Equity Value of **$29,354,000.00**, based on an inflated EBITDA ($4.118M at 8.0x = $32.944M EV), minimal debt deductions ($3.5M bank debt only), ignoring $768,000 in debt-like liabilities, and claiming an unearned $239,000 working capital windfall by proposing an artificially low target peg.

Forensic balance sheet diligence established:
* **Defensible QoE Enterprise Value:** **$28,884,000.00** ($3.6105M Normalized EBITDA $\times$ 8.0x)
* **Less: Funded Debt Payoff:** **-$4,024,500.00** (Bank debt + shareholder note & interest)
* **Less: Debt-Like Item Deductions:** **-$768,000.00** (Stretched AP, deal bonuses, sales tax, PTO, deferred rev, CapEx)
* **Plus: Unrestricted Cash at Close:** **+$174,050.00** ($524k cash less $100k restricted less $250k min operating cash)
* **Plus: Cash-Like Tax Refund:** **+$42,000.00** (Verified IRS Form 941-X ERC refund)
* **Working Capital Adjustment:** **+$75,000.00** ($4.375M Delivered NWC less $4.300M Agreed Peg)
* **QoE Defensible Equity Purchase Price (Cash at Close):** **$24,382,550.00**
* **Total Transaction Value Haircut (Buyer Cash Savings):** **-$4,971,450.00** (16.9% reduction against seller claim)

```
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                MASTER EV TO EQUITY PURCHASE PRICE BRIDGE                           |
|                                                                                                    |
|   Headline Enterprise Value (QoE Normalized EBITDA $3.6105M x 8.0x):                $28,884,000.00 |
|   - Senior Bank Debt (Term Loan $2.5M + Revolver $1.0M):                             -$ 3,500,000.00 |
|   - Subordinated Shareholder Promissory Note & Accrued Interest:                     -$   524,500.00 |
|   - Stretched Accounts Payable Over 60 Days:                                         -$   250,000.00 |
|   - Accrued Transaction Bonuses & Deal Advisory Fees:                                -$   145,000.00 |
|   - State Sales & Use Tax Audit Exposure:                                            -$    68,000.00 |
|   - Unfunded Employee Vacation & PTO Liability:                                      -$    45,000.00 |
|   - Customer Deferred Revenue Fulfillment Cost Haircut (ASC 805):                    -$   140,000.00 |
|   - Machinery Deferred Maintenance & CapEx Backlog:                                  -$   120,000.00 |
|   + Cash on Hand in Operating Bank Accounts:                                         +$   524,050.00 |
|   - Restricted Cash (Letter of Credit Cash Collateral):                             -$   100,000.00 |
|   - Minimum Operating Cash Buffer (Day-1 Operating Float):                           -$   250,000.00 |
|   + Verified Employee Retention Credit (ERC) Tax Refund:                             +$    42,000.00 |
|   + Working Capital Adjustment (Delivered NWC $4.375M less Peg $4.300M):             +$    75,000.00 |
|   ------------------------------------------------------------------------------------------------ |
|   = Final Equity Purchase Price (Cash Paid at Closing):                             $24,382,550.00 |
|                                                                                                    |
|   Management Claimed Equity Value (Seller Pitch Book):                               $29,354,000.00 |
|   Total Diligence Haircut (Direct Buyer Purchase Price Savings):                     -$ 4,971,450.00 |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Comparison: Management Proposed vs. QoE Verified Bridge

All figures in USD ($). Every row ties out mathematically to source workpapers.

| Transaction Bridge Line Item | Ref ID | Management Claim | QoE Verified | Diligence Variance | Analytical Rationale |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Operating EBITDA Baseline** | `EBITDA` | $4,118,000 | $3,610,500 | -$507,500 | Rejection of bad debt, unearned 3PL savings, and caps (`WS05`). |
| Agreed EV Multiple | `MULT` | 8.0x | 8.0x | — | Contractual baseline multiple agreed in LOI. |
| **Headline Enterprise Value** | **`EV`** | **$32,944,000** | **$28,884,000** | **-$4,060,000** | **Direct EV haircut resulting from EBITDA adjustments.** |
| - Senior Secured Bank Debt | `DBT-001/2` | ($3,500,000) | ($3,500,000) | $0 | Term loan ($2.5M) and revolver ($1.0M) verified via payoff letter. |
| - Subordinated Shareholder Note | `DBT-003` | ($500,000) | ($524,500) | -$24,500 | Unaccrued compound interest per loan agreement terms. |
| - Stretched Accounts Payable | `DBT-004` | $0 | ($250,000) | -$250,000 | AP over 60 days reclassified from NWC to prevent cash drag. |
| - Accrued Transaction Bonuses | `DBT-005` | $0 | ($145,000) | -$145,000 | Change-of-control success fees and M&A legal advisory costs. |
| - State Sales/Use Tax Exposure | `DBT-006` | $0 | ($68,000) | -$68,000 | Unremitted sales tax on out-of-state shipments (Wayfair). |
| - Unfunded Employee PTO Deficit | `DBT-007` | $0 | ($45,000) | -$45,000 | Unaccrued earned vacation liability per employee census. |
| - Deferred Revenue Haircut | `DBT-008` | $0 | ($140,000) | -$140,000 | Post-close obligation fulfillment cost (50% of unearned rev). |
| - CapEx Deferred Maintenance | `DBT-009` | $0 | ($120,000) | -$120,000 | Catch-up maintenance backlog on CNC machine spindles. |
| + Total Cash on Hand | `CSH-001` | $524,050 | $524,050 | $0 | Reconciled cash balance per closing bank statements. |
| - Restricted Cash Collateral | `CSH-002` | $0 | ($100,000) | -$100,000 | Cash pledged to collateralize workers comp letter of credit. |
| - Minimum Operating Cash Buffer | `CSH-003` | $0 | ($250,000) | -$250,000 | Necessary operating float to fund daily checks and payroll. |
| + Cash-Like Tax Refund | `CSH-004` | $0 | $42,000 | +$42,000 | Verified Employee Retention Credit (ERC) refund from IRS. |
| + Working Capital Adjustment | `PEG-ADJ` | $385,950 | $75,000 | -$310,950 | Seller proposed low peg ($4.136M); QoE defended $4.300M peg. |
| **Final Equity Purchase Price** | **`EQ-VAL`**| **$29,354,000** | **$24,382,550** | **-$4,971,450** | **Total cash savings achieved through due diligence.** |

---

## 3. Working Capital True-Up Sensitivity Schedule

In the definitive Sale and Purchase Agreement (SPA), the parties agree to a **Target Working Capital Peg of $4,300,000.00** with an agreed **$\pm \$75,000.00 Collar**. The schedule below illustrates post-closing cash true-up settlements across closing working capital outcomes:

$$\text{Post-Closing True-Up Cash Flow} = 
\begin{cases} 
\text{Closing NWC} - \$4,375,000 & \text{if Closing NWC} > \$4,375,000 \text{ (Buyer pays Seller)} \\
0.00 & \text{if } \$4,225,000 \le \text{Closing NWC} \le \$4,375,000 \text{ (Within Collar)} \\
\text{Closing NWC} - \$4,225,000 & \text{if Closing NWC} < \$4,225,000 \text{ (Seller pays Buyer)}
\end{cases}$$

| Delivered Closing NWC | Variance vs Target Peg ($4.300M) | Collar Status | Cash Flow Direction | Net True-Up Cash Amount |
| :---: | :---: | :---: | :---: | :---: |
| **$4,600,000** | +$300,000 | Above Upper Collar | Buyer pays Seller | **+$225,000.00** |
| **$4,500,000** | +$200,000 | Above Upper Collar | Buyer pays Seller | **+$125,000.00** |
| **$4,375,000 (Base Case)** | **+$75,000** | **Upper Collar Boundary** | **Zero True-Up** | **$0.00** |
| **$4,300,000 (Target Peg)** | $0 | Inside Collar | Zero True-Up | **$0.00** |
| **$4,225,000** | -$75,000 | Lower Collar Boundary | Zero True-Up | **$0.00** |
| **$4,100,000** | -$200,000 | Below Lower Collar | Seller pays Buyer | **-$125,000.00** |
| **$4,000,000** | -$300,000 | Below Lower Collar | Seller pays Buyer | **-$225,000.00** |

---

## 4. Valuation Multiple Sensitivity Schedule

The table below illustrates the sensitivity of the final Equity Purchase Price across enterprise valuation multiples, holding net debt and working capital adjustments constant:

$$\text{Equity Purchase Price} = (\text{Normalized EBITDA} \times \text{Multiple}) - \text{Net Debt (\$4,576,450)} + \text{WC Adjustment (\$75,000)}$$

| EV Multiple | Implied Enterprise Value | Net Debt Deduction | WC Adjustment | Defensible Equity Purchase Price | Buyer Savings vs Seller Claim |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **6.0x** | $21,663,000 | -$4,576,450 | +$75,000 | **$17,161,550** | **-$7,558,450** |
| **7.0x** | $25,273,500 | -$4,576,450 | +$75,000 | **$20,772,050** | **-$6,264,950** |
| **8.0x (Base Case)** | **$28,884,000** | **-$4,576,450** | **+$75,000** | **$24,382,550** | **-$4,971,450** |
| **9.0x** | $32,494,500 | -$4,576,450 | +$75,000 | **$27,993,050** | **-$3,677,950** |
| **10.0x** | $36,105,000 | -$4,576,450 | +$75,000 | **$31,603,550** | **-$2,384,450** |

> [!IMPORTANT]
> **Summary Transaction Consequence:**  
> The comprehensive financial due diligence across Workstreams 05, 06, and 07 successfully reduced the transaction purchase price from **$29,354,000.00 to $24,382,550.00**, delivering **$4,971,450.00 in direct, verified cash savings** for the buyer while ensuring the business is delivered with adequate liquidity and zero unrecorded supplier drag.
