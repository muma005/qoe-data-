# Working Capital & Net Debt Calculation Library
**Document Reference:** `QOE-CALC-LIB-07`  
**Workstream:** `07 — Working Capital, Target Peg, and Net Debt`  
**Classification:** Professional Financial Due Diligence Technical Specification  

---

## 1. Architectural Taxonomy of Working Capital & Debt Metrics

In transaction advisory and financial due diligence (FDD), balance sheet accounts are categorized into four mutually exclusive transactional buckets to govern the Enterprise Value to Equity Value purchase price settlement:

```
+───────────────────────────────────────────────────────────────────────────────+
| 1. Operating Net Working Capital (Settled via Target Peg & Post-Close True-Up)|
+───────────────────────────────────────────────────────────────────────────────+
                                      │
                                      ▼ [Deducted Dollar-for-Dollar at Closing]
+───────────────────────────────────────────────────────────────────────────────+
| 2. Funded Debt & Debt-Like Items (Direct Purchase Price Haircut)              |
+───────────────────────────────────────────────────────────────────────────────+
                                      │
                                      ▼ [Added Dollar-for-Dollar at Closing]
+───────────────────────────────────────────────────────────────────────────────+
| 3. Unrestricted Cash & Cash-Like Items (Added to Equity Purchase Price)       |
+───────────────────────────────────────────────────────────────────────────────+
                                      │
                                      ▼ [Zero Direct Impact on Cash Bridge]
+───────────────────────────────────────────────────────────────────────────────+
| 4. Excluded / Equity Accounts (Intercompany, Stock, Retained Earnings)       |
+───────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Mathematical Formulations & Calculation Algorithms

### 2.1 Trade Working Capital vs. Operating Net Working Capital

$$\text{Trade Working Capital (TWC)} = \text{Trade Accounts Receivable} + \text{Inventories} - \text{Trade Accounts Payable}$$

$$\text{Operating Net Working Capital (NWC)} = \text{Operating Current Assets} - \text{Operating Current Liabilities}$$

Where:
$$\text{Operating Current Assets} = \text{Trade AR (Net)} + \text{Inventories (Net)} + \text{Prepaid Expenses} + \text{Other Operating Current Assets}$$
$$\text{Operating Current Liabilities} = \text{Trade AP (Current)} + \text{Accrued Payroll/Opex} + \text{Operating Taxes Payable} + \text{Accrued Customer Rebates}$$

* **Excluded from Operating Assets:** Cash and cash equivalents, restricted cash, short-term investments, income tax refunds receivable, financing notes receivable.
* **Excluded from Operating Liabilities:** Bank borrowings, revolving credit lines, current portion of long-term debt, shareholder notes, accrued interest, stretched payables over terms, transaction bonuses, income taxes payable.

---

### 2.2 Operational Days Metrics: Standard vs. Count-Back (Exhaustion) Method

#### Standard 365-Day Formulas:
$$\text{DSO} = \frac{\text{Trade AR}}{\text{Gross Revenue}} \times 365, \quad \text{DIO} = \frac{\text{Inventory}}{\text{COGS}} \times 365, \quad \text{DPO} = \frac{\text{Trade AP}}{\text{COGS or Purchases}} \times 365$$
$$\text{Cash Conversion Cycle (CCC)} = \text{DSO} + \text{DIO} - \text{DPO}$$

#### Count-Back (Exhaustion) Method (Required for Seasonal Businesses):
The count-back method eliminates annual revenue distortions by exhausting ending balances against historical monthly/daily activity.

For Accounts Receivable at month $M$ with ending balance $B_{\text{AR}}$:
$$\text{DSO}_{\text{count-back}} = \sum_{k=0}^{n-1} D_{M-k} + \left( \frac{B_{\text{AR}} - \sum_{k=0}^{n-1} R_{M-k}}{R_{M-n}} \right) \times D_{M-n}$$
Where:
* $R_{M-k}$ is the revenue recognized in month $M-k$.
* $D_{M-k}$ is the number of calendar days in month $M-k$.
* $n$ is the number of full preceding months exhausted such that $\sum_{k=0}^{n-1} R_{M-k} \le B_{\text{AR}} < \sum_{k=0}^{n} R_{M-k}$.

---

### 2.3 Stretched Accounts Payable Quantification Formula
When a target company deliberately delays vendor disbursements prior to sale, aging accounts payable beyond commercial terms creates an artificial cash buildup.

$$\text{Stretched Accounts Payable} = \sum_{v \in \text{Vendors}} \max\left(0, \; \text{Aged AP Balance}_{v, >\text{Terms}} - \text{Historical Baseline Aged AP}_v\right)$$

In practice, diligence sets an objective contractual cutoff:
$$\text{Stretched AP} = \text{Total AP Aged Over 60 Days} - \text{Permissible Commercial Dispute Reserve}$$

* **Transaction Reclassification:**
  $$\Delta \text{Operating Current Liabilities} = -\text{Stretched AP} \implies \text{Increases Operating NWC}$$
  $$\text{Debt-Like Item Addition} = +\text{Stretched AP} \implies \text{Deducted Dollar-for-Dollar from Purchase Price}$$
* **Mathematical Proof of Neutrality for Seller on Honest Terms:**  
  If the seller pays the vendor before closing, cash decreases by $\$250\text{k}$ and AP decreases by $\$250\text{k}$. If the seller does not pay, cash is $\$250\text{k}$ higher, but the buyer deducts $\$250\text{k}$ as a Debt-Like Item. The cash paid at closing is identical.

---

### 2.4 Inventory Excess & Obsolescence Reserve Deficiency Model
Diligence calculates required inventory reserves based on SKU-level trailing 12-month (TTM) consumption:

$$\text{Months of Supply (MOS)}_i = \frac{\text{Ending Quantity on Hand}_i}{\text{TTM Units Consumed / Sold}_i} \times 12$$

$$\text{Required Reserve}_i = 
\begin{cases} 
0.00 & \text{if } \text{MOS}_i \le 12 \text{ months} \\
0.50 \times \text{Carrying Cost}_i & \text{if } 12 < \text{MOS}_i \le 24 \text{ months (Slow-Moving)} \\
1.00 \times \text{Carrying Cost}_i & \text{if } \text{MOS}_i > 24 \text{ months or Zero TTM Sales (Dead Stock)}
\end{cases}$$

$$\text{Reserve Deficiency Adjustment} = \sum_{i=1}^{S} \text{Required Reserve}_i - \text{Booked General Ledger Reserve}$$

* If $\text{Reserve Deficiency Adjustment} > 0$, operating inventory carrying value is reduced in Normalized NWC:
  $$\Delta \text{Normalized Inventory} = -\text{Reserve Deficiency Adjustment}$$

---

### 2.5 Working Capital Target Peg Methodologies

Diligence models five distinct peg methodologies to establish the baseline for the closing true-up:

1. **12-Month LTM Average Peg:**
   $$\text{Peg}_{\text{12M}} = \frac{1}{12} \sum_{m=1}^{12} \text{Normalized NWC}_m$$
2. **6-Month Recent Trend Peg:**
   $$\text{Peg}_{\text{6M}} = \frac{1}{6} \sum_{m=7}^{12} \text{Normalized NWC}_m$$
3. **Seasonal Point-in-Time Peg (Closing Month Historical Average):**
   $$\text{Peg}_{\text{Seasonal}} = \frac{1}{Y} \sum_{y=1}^{Y} \text{Normalized NWC}_{\text{Closing Month}, y}$$
4. **Percentage of Revenue Peg:**
   $$\text{Peg}_{\% \text{Rev}} = \left( \frac{\sum_{m=1}^{12} \text{Normalized NWC}_m}{\sum_{m=1}^{12} \text{Revenue}_m} \right) \times \text{QoE Run-Rate Revenue}$$

$$\text{Purchase Price Working Capital Adjustment} = \text{Closing Delivered NWC} - \text{Negotiated Target Peg}$$

* If $\text{Closing NWC} > \text{Target Peg} \implies \text{Purchase Price Increases}$ (Buyer pays Seller cash true-up).
* If $\text{Closing NWC} < \text{Target Peg} \implies \text{Purchase Price Decreases}$ (Seller pays Buyer cash true-up).

---

### 2.6 Intra-Month Peak Working Capital Volatility Formula
Working capital requirements oscillate during the month due to payroll cycles and collection timing:

$$\text{Intra-Month Peak Gap} = \max_{d \in [1, 31]} (\text{Daily Working Capital}_d) - \text{Month-End Reported NWC}$$

$$\text{Recommended Minimum Operating Cash Buffer} = \max\left( \text{Intra-Month Peak Gap}, \; \text{Semi-Monthly Gross Payroll} + \text{Outstanding Checks Float} \right)$$

* The minimum operating cash buffer is deducted from gross cash on hand, preventing the seller from sweeping cash required to fund Day-1 operations.

---

### 2.7 SaaS Deferred Revenue Haircut & Fulfillment Cost Model (ASC 805)
Under **ASC 805 (Business Combinations)** and fair value purchase accounting:

$$\text{Post-Closing Performance Obligation Cost} = \text{Cost to Fulfill Obligations (Direct Hosting, Support, Account Mgmt)}$$

$$\text{ASC 805 Fair Value of Deferred Revenue} = \text{Post-Closing Fulfillment Cost} + \text{Normal Commercial Profit Margin \%}$$

$$\text{Deferred Revenue Haircut} = \text{Book Value of Deferred Revenue} - \text{Fair Value of Deferred Revenue}$$

* **Transaction Debt-Like Treatment:**
  $$\text{Debt-Like Deduction} = \text{Post-Closing Performance Obligation Fulfillment Cost} \quad (\approx 40\% - 60\% \text{ of Deferred Revenue})$$

---

### 2.8 Definitive Enterprise Value to Equity Value Purchase Price Bridge Formula

$$\mathbf{Equity\ Purchase\ Price\ (Cash\ at\ Close) = Enterprise\ Value - Funded\ Debt - Debt\text{-}Like\ Items + Unrestricted\ Cash + Cash\text{-}Like\ Items + (Closing\ NWC - Target\ Peg)}$$

Where:
$$\begin{aligned}
\text{Enterprise Value (EV)} &= \text{QoE Normalized EBITDA} \times \text{Valuation Multiple} \\
\text{Funded Debt} &= \text{Senior Term Debt} + \text{Revolver} + \text{Shareholder Notes} + \text{Accrued Interest} \\
\text{Debt-Like Items} &= \text{Stretched AP} + \text{Transaction Bonuses} + \text{Severance Liabilities} + \text{Tax Audit Reserves} + \text{Deferred Rev Cost} + \text{CapEx Deficit} \\
\text{Unrestricted Cash} &= \text{Total Cash on Hand} - \text{Restricted / Trapped Cash} - \text{Minimum Operating Cash Buffer} \\
\text{Cash-Like Items} &= \text{Verified Tax Refunds Receivable} + \text{Refundable Cash Deposits} \\
\text{Working Capital Adjustment} &= \text{Closing Delivered Normalized NWC} - \text{Agreed Target Peg}
\end{aligned}$$
