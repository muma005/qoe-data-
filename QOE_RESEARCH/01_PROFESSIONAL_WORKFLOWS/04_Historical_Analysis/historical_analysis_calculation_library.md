# Quality of Earnings (QoE) Research Programme
## Workstream 04 — Historical Financial Analysis
### Deliverable 2: Historical Financial Analysis Methodology & Calculation Library

This technical library defines the core financial metrics, mathematical formulas, data requirements, worked examples, and transaction interpretation guidelines used by tier-one financial due diligence (FDD) and Quality of Earnings (QoE) practitioners.

---

### Master Calculation Index

1. **Compound Annual Growth Rate (CAGR)**
2. **Year-over-Year (YoY) & Month-over-Month (MoM) Percentage Growth**
3. **Latest Twelve Months (LTM / TTM) & Run-Rate Calculation**
4. **Year-to-Date (YTD) Comparative Run-Rate**
5. **Vertical Common-Sizing (% of Revenue)**
6. **Gross Profit & Basis Point (bps) Margin Bridge**
7. **Price-Volume-Mix (PVM) Mathematical Decomposition**
8. **Degree of Operating Leverage (DOL) & Fixed/Variable Cost Decomposition**
9. **Operating Expense Ratios (S&M %, G&A %, R&D %)**
10. **Operating EBITDA & EBITDA Margin**
11. **EBITDA Growth Contribution & Margin Bridge**
12. **Operating Cash Flow (OCF) & EBITDA-to-OCF Cash Conversion Ratio**
13. **Free Cash Flow (FCF) & EBITDA-to-FCF Cash Conversion Ratio**
14. **Days Sales Outstanding (DSO) — Standard vs. Countback Method**
15. **Days Inventory Outstanding (DIO) & Inventory Turnover**
16. **Days Payable Outstanding (DPO)**
17. **Cash Conversion Cycle (CCC)**
18. **SaaS Metrics: ARR Bridge, Gross Retention (GRR), Net Retention (NRR), and CAC Payback**

---

### 1. Compound Annual Growth Rate (CAGR)

* **Definition:** The smoothed annualized rate of growth across a multi-year historical period, eliminating interim year-to-year volatility.
* **Mathematical Formula:**
  $$\text{CAGR}_{t_0 \to t_n} = \left( \frac{\text{Metric}_{t_n}}{\text{Metric}_{t_0}} \right)^{\frac{1}{n}} - 1$$
* **Required Input Fields:** Baseline period value ($\text{Metric}_{t_0}$), Ending period value ($\text{Metric}_{t_n}$), Number of elapsed annual periods ($n$).
* **Appropriate Period:** Multi-year comparisons (typically 2-year or 3-year historical horizons, e.g., FY21 to FY23, where $n = 2$).
* **Worked Calculation Example:**
  * FY21 Gross Revenue = \$19,000,000.00
  * FY23 Gross Revenue = \$24,850,000.00
  * Elapsed years $n = 2$
  $$\text{CAGR} = \left( \frac{24,850,000}{19,000,000} \right)^{\frac{1}{2}} - 1 = (1.30789)^{0.5} - 1 = 14.36\%$$
* **Transaction Interpretation:** Demonstrates the underlying compound expansion velocity of the business across economic cycles.
* **Diligence Limitations:** Masks mid-period volatility. For example, a company that grew 40% in Year 1 and declined 10% in Year 2 can have the same CAGR as a steady 14% grower, yet presents a deteriorating trajectory at the transaction date.
* **Common Traps:** Incorrectly setting $n = 3$ when examining three financial statements (e.g. FY21, FY22, FY23). There are only two elapsed periods of growth between FY21 and FY23.
* **Condition Prohibiting Use:** Should NOT be used if the baseline period is negative (e.g., negative EBITDA) or zero, or if an intervening acquisition fundamentally transformed the corporate perimeter without pro-forma restatement.

---

### 2. Year-over-Year (YoY) & Month-over-Month (MoM) Growth

* **Definition:** The percentage change in a financial metric between equivalent calendar or fiscal periods.
* **Mathematical Formula:**
  $$\text{Growth Rate} = \frac{\text{Value}_{\text{Current}} - \text{Value}_{\text{Prior}}}{\text{Value}_{\text{Prior}}}$$
* **Required Input Fields:** Current period value, Prior comparative period value.
* **Appropriate Period:** YoY is evaluated on annual or equivalent monthly periods (e.g., June 2023 vs. June 2022); MoM is evaluated sequentially across consecutive months.
* **Worked Calculation Example:**
  * FY22 Revenue = \$21,800,000.00; FY23 Revenue = \$24,850,000.00
  $$\text{YoY Growth} = \frac{24,850,000 - 21,800,000}{21,800,000} = \frac{3,050,000}{21,800,000} = +13.99\%$$
* **Transaction Interpretation:** Highlights immediate acceleration or deceleration in top-line demand and expense creep.
* **Diligence Limitations:** MoM growth is highly vulnerable to seasonal calendar shifts, holiday timing, and billing day counts (e.g., February has 20 business days vs. 23 in March).
* **Common Traps:** Comparing months sequentially without seasonally adjusting. Always prioritize YoY monthly comparisons (June 2023 vs June 2022) over sequential MoM (June 2023 vs May 2023) in seasonal businesses.

---

### 3. Latest Twelve Months (LTM / TTM) & Run-Rate Calculation

* **Definition:** The continuous twelve-month financial performance ending on the most recent available historical balance sheet date.
* **Mathematical Formula:**
  $$\text{LTM} = \text{Full Prior Fiscal Year} - \text{Prior Year Equivalent Interim Period} + \text{Current Year Interim Period}$$
* **Required Input Fields:** Full prior audited year, prior year YTD interim, current year YTD interim.
* **Appropriate Period:** Any transaction date falling midway through a fiscal year (e.g., LTM September 2023).
* **Worked Calculation Example (for a deal closing September 30, 2023):**
  * Full Year FY22 Revenue = \$21,800,000.00
  * Less: 9-Month YTD Ended September 30, 2022 = -\$16,100,000.00
  * Plus: 9-Month YTD Ended September 30, 2023 = +\$18,450,000.00
  $$\text{LTM Revenue} = 21,800,000 - 16,100,000 + 18,450,000 = \$24,150,000.00$$
* **Transaction Interpretation:** The single most critical valuation benchmark in M&A. Acquisition purchase prices are almost universally negotiated as a multiple of LTM Adjusted EBITDA.
* **Diligence Limitations:** If the interim periods contain seasonal distortion or unadjusted year-end audit adjustments, the LTM calculation will inherit those errors.
* **Common Traps:** Adding the last 12 individual months without confirming that the monthly trial balances foot to the audited year-end.

---

### 4. Year-to-Date (YTD) Comparative Run-Rate

* **Definition:** Cumulative financial performance from the first day of the current fiscal year up to the latest interim reporting month, compared directly to the identical calendar span in the prior fiscal year.
* **Mathematical Formula:**
  $$\text{YTD Growth} = \frac{\text{YTD}_{\text{Current Year, Month } m} - \text{YTD}_{\text{Prior Year, Month } m}}{\text{YTD}_{\text{Prior Year, Month } m}}$$
* **Required Input Fields:** Cumulative revenue/costs for Month 1 through Month $m$ in Year $t$; Cumulative revenue/costs for Month 1 through Month $m$ in Year $t-1$.
* **Appropriate Period:** Interim trading periods (e.g., 6-Month YTD June, 9-Month YTD September).
* **Worked Calculation Example:**
  * 6-Month YTD June 2022 Revenue = \$10,400,000.00
  * 6-Month YTD June 2023 Revenue = \$11,990,000.00
  $$\text{YTD Growth} = \frac{11,990,000 - 10,400,000}{10,400,000} = +15.29\%$$
* **Transaction Interpretation:** Establishes whether current-year trading momentum is outpacing, matching, or trailing historical annual trends.
* **Diligence Limitations:** YTD figures cannot be annualized by multiplying by $12/m$ in a seasonal business without adjusting for historical seasonality weights.

---

### 5. Vertical Common-Sizing (% of Revenue)

* **Definition:** Expressing every financial line item on the income statement as an exact percentage of gross or net revenue.
* **Mathematical Formula:**
  $$\text{Common-Size } \% = \frac{\text{Financial Line Item Value}}{\text{Total Revenue}} \times 100$$
* **Required Input Fields:** Line item amount, Total revenue.
* **Appropriate Period:** Applied across all annual, LTM, and monthly income statements.
* **Worked Calculation Example:**
  * FY23 Total Revenue = \$24,850,000.00
  * FY23 Direct Raw Materials = \$9,850,000.00
  $$\text{Raw Materials } \% = \frac{9,850,000}{24,850,000} \times 100 = 39.64\%$$
* **Transaction Interpretation:** Immediately reveals shifts in cost structure, cost creep, and operating leverage. If revenue grows 14% but Raw Materials expand from 37.89% to 39.64% of revenue, the analyst detects input margin compression.
* **Common Traps:** Using different revenue denominators (e.g. gross billed revenue vs net recognized revenue) across different periods, which distorts percentages.

---

### 6. Gross Profit & Basis Point (bps) Margin Bridge

* **Definition:** Measuring the absolute profitability of products sold after direct costs, and quantifying margin shifts in basis points ($1\% = 100 \text{ bps}$).
* **Mathematical Formula:**
  $$\text{Gross Profit} = \text{Revenue} - \text{Cost of Goods Sold (COGS)}$$
  $$\text{Gross Margin } \% = \frac{\text{Gross Profit}}{\text{Revenue}} \times 100$$
  $$\text{Margin Change (bps)} = (\text{Gross Margin}_{t} - \text{Gross Margin}_{t-1}) \times 10,000$$
* **Worked Calculation Example:**
  * FY21: Revenue \$19.00M, COGS \$11.45M, Gross Profit \$7.55M, Gross Margin = $39.7368\%$
  * FY23: Revenue \$24.85M, COGS \$15.40M, Gross Profit \$9.45M, Gross Margin = $38.0282\%$
  $$\text{Margin Change} = (0.380282 - 0.397368) \times 10,000 = -171 \text{ bps}$$
* **Transaction Interpretation:** A 171 bps margin contraction represents \$425,000 of lost gross profit in FY23 relative to FY21 efficiency.

---

### 7. Price-Volume-Mix (PVM) Mathematical Decomposition

* **Definition:** An econometric variance bridge that isolates whether revenue growth was driven by price increases, unit sales volume, or shifts in product composition.
* **Mathematical Formulation (Standard FDD 3-Bucket Model):**
  $$\Delta \text{Revenue} = \text{Revenue}_1 - \text{Revenue}_0 = \text{Price Effect} + \text{Volume Effect} + \text{Mix Effect}$$
  $$\text{Price Effect} = \sum_{i} \left( P_{i,1} - P_{i,0} \right) \times V_{i,1}$$
  $$\text{Volume Effect} = \left( V_{\text{total},1} - V_{\text{total},0} \right) \times \bar{P}_0$$
  $$\text{Mix Effect} = \sum_{i} \left[ V_{\text{total},1} \times \left( \frac{V_{i,1}}{V_{\text{total},1}} - \frac{V_{i,0}}{V_{\text{total},0}} \right) \times \left( P_{i,0} - \bar{P}_0 \right) \right]$$
  *(Where $P_{i}$ is unit price of SKU $i$, $V_{i}$ is volume of SKU $i$, and $\bar{P}_0$ is baseline portfolio weighted average price).*
* **Worked Calculation Example (Commercial Fasteners Category):**
  * FY22 ($t_0$): $V_0 = 1,420,000$ units, $P_0 = \$10.00$, $\text{Revenue}_0 = \$14,200,000.00$
  * FY23 ($t_1$): $V_1 = 1,510,000$ units, $P_1 = \$10.4967$, $\text{Revenue}_1 = \$15,850,000.00$
  * Total Change = $+\$1,650,000.00$
  $$\text{Price Effect} = (10.4967 - 10.00) \times 1,510,000 = +\$750,000.00$$
  $$\text{Volume Effect} = (1,510,000 - 1,420,000) \times 10.00 = +\$900,000.00$$
  $$\text{Sum} = 750,000 + 900,000 = \$1,650,000.00 \quad (\text{Balanced})$$
* **Transaction Interpretation:** Proves that 54.5% of category growth was organic unit volume, while 45.5% was inflationary pricing.

---

### 8. Degree of Operating Leverage (DOL)

* **Definition:** A measure of how sensitive operating income or EBITDA is to percentage changes in revenue, reflecting the fixed versus variable cost structure.
* **Mathematical Formula:**
  $$\text{DOL} = \frac{\% \Delta \text{Operating Income}}{\% \Delta \text{Revenue}} = \frac{\text{Contribution Margin}}{\text{Operating Income}} = \frac{\text{Revenue} - \text{Variable Costs}}{\text{EBIT}}$$
* **Worked Calculation Example (FY22 to FY23):**
  * Revenue grew from \$21.80M to \$24.85M ($+13.99\%$)
  * EBIT changed from \$2.55M to \$2.48M ($-2.75\%$)
  $$\text{DOL} = \frac{-2.75\%}{+13.99\%} = -0.20$$
* **Transaction Interpretation:** Severe warning sign. Operating leverage turned negative in FY23; despite 14% top-line growth, operating profit contracted, indicating that fixed and step-fixed corporate overhead was added faster than revenue expansion.

---

### 9. Operating Expense Ratios (S&M %, G&A %, R&D %)

* **Definition:** The percentage of revenue dedicated to major functional operating expenditure categories.
* **Mathematical Formula:**
  $$\text{S\&M Ratio} = \frac{\text{Sales \& Marketing Expense}}{\text{Revenue}} \times 100$$
  $$\text{G\&A Ratio} = \frac{\text{General \& Administrative Expense}}{\text{Revenue}} \times 100$$
* **Worked Calculation Example (FY23 Apex Industrial):**
  * S&M = \$2,850,000 / \$24,850,000 = $11.47\%$
  * G&A = \$3,270,000 / \$24,850,000 = $13.16\%$
  * Total SG&A Ratio = $24.63\%$ (Expanded from $23.95\%$ in FY21)
* **Transaction Interpretation:** Highlights whether back-office and marketing costs are scaling efficiently or consuming gross margin gains.

---

### 10. Operating EBITDA & EBITDA Margin

* **Definition:** Earnings Before Interest, Taxes, Depreciation, and Amortization, representing core operational cash profitability prior to capital structure, asset intensity, and tax jurisdictions.
* **Mathematical Formula:**
  $$\text{EBITDA} = \text{Operating Profit (EBIT)} + \text{Depreciation} + \text{Amortization}$$
  $$\text{EBITDA Margin } \% = \frac{\text{EBITDA}}{\text{Revenue}} \times 100$$
* **Worked Calculation Example (FY23):**
  * Operating Profit = \$2,480,000.00
  * Plus D&A = \$850,000.00
  * EBITDA = \$3,330,000.00
  $$\text{EBITDA Margin} = \frac{3,330,000}{24,850,000} \times 100 = 13.40\%$$
* **Transaction Interpretation:** Baseline profitability for private equity valuation. In FY21, EBITDA margin was 15.79%; the 239 bps margin drop indicates structural profit erosion.

---

### 11. EBITDA Growth Contribution & Margin Bridge

* **Definition:** Decomposing the dollar variance in EBITDA from Period 0 to Period 1 into Volume Contribution, Gross Margin Drag, and SG&A Overhead Expansion.
* **Mathematical Formula:**
  $$\Delta \text{EBITDA} = \left( \Delta \text{Revenue} \times \text{GM}_0 \right) + \left( \text{Revenue}_1 \times \Delta \text{GM} \right) - \Delta \text{SG\&A}$$
* **Worked Calculation Example (FY22 to FY23):**
  * Revenue Delta = $+\$3,050,000$; FY22 Gross Margin = $39.22\%$
  * Volume GP Contribution = $3,050,000 \times 0.3922 = +\$1,196,210.00$
  * Margin Rate Change = $38.03\% - 39.22\% = -1.19\%$
  * Margin Compression Drag = $24,850,000 \times (-0.0119) = -\$296,210.00$
  * Net Gross Profit Increase = $1,196,210 - 296,210 = +\$900,000.00$
  * Less: Incremental SG&A Overhead = \$6,120,000 - \$5,250,000 = -\$870,000.00
  $$\Delta \text{EBITDA} = 900,000 - 870,000 = +\$30,000.00 \quad (\text{Balanced})$$
* **Transaction Interpretation:** Proves that \$1.19M of profit generated by higher sales volume was almost entirely consumed by \$296k of margin compression and \$870k of SG&A expansion.

---

### 12. Operating Cash Flow (OCF) & Cash Conversion Ratio

* **Definition:** Measures the percentage of accounting EBITDA that actually translates into Operating Cash Flow after working capital changes, cash taxes, and cash interest.
* **Mathematical Formula:**
  $$\text{OCF} = \text{EBITDA} + \Delta \text{Working Capital} - \text{Cash Taxes} - \text{Cash Interest}$$
  $$\text{Operating Cash Conversion Ratio} = \frac{\text{OCF}}{\text{EBITDA}} \times 100$$
* **Worked Calculation Example (FY23):**
  * Reported EBITDA = \$3,330,000.00
  * Working Capital Investment = -\$760,000.00
  * Cash Taxes = -\$440,000.00
  * Cash Interest = -\$320,000.00
  * OCF = \$1,810,000.00
  $$\text{Cash Conversion} = \frac{1,810,000}{3,330,000} \times 100 = 54.35\%$$
* **Transaction Interpretation:** Cash conversion declined from 65.0% in FY21 to 54.35% in FY23. Over 45% of paper earnings were absorbed by working capital growth, debt interest, and taxes.

---

### 13. Free Cash Flow (FCF) & Free Cash Conversion Ratio

* **Definition:** Cash generated by operations after funding mandatory Maintenance Capital Expenditures.
* **Mathematical Formula:**
  $$\text{FCF} = \text{OCF} - \text{Maintenance CapEx}$$
  $$\text{Free Cash Conversion Ratio} = \frac{\text{FCF}}{\text{EBITDA}} \times 100$$
* **Worked Calculation Example (FY23):**
  * OCF = \$1,810,000.00
  * Less Maintenance CapEx = -\$580,000.00
  * Free Cash Flow = \$1,230,000.00
  $$\text{FCF Conversion} = \frac{1,230,000}{3,330,000} \times 100 = 36.94\%$$
* **Transaction Interpretation:** Only 36.94% of reported EBITDA is genuinely free cash available for debt repayment or shareholder dividends.

---

### 14. Days Sales Outstanding (DSO)

* **Definition:** The average number of days required to collect trade receivables from commercial sales.
* **Mathematical Formula (Standard Countback / Average Method):**
  $$\text{DSO} = \frac{\text{Ending Trade Accounts Receivable}}{\text{Gross Revenue}} \times 365$$
* **Worked Calculation Example (FY23):**
  * Ending AR = \$3,250,000.00; FY23 Revenue = \$24,850,000.00
  $$\text{DSO} = \frac{3,250,000}{24,850,000} \times 365 = 47.7 \text{ days (48 days)}$$
* **Transaction Interpretation:** DSO stretched from 41.9 days in FY21 to 47.7 days in FY23. A 6-day collection delay ties up \$408,000 of liquidity.

---

### 15. Days Inventory Outstanding (DIO) & Inventory Turns

* **Definition:** The average number of days inventory sits on warehouse shelves or plant floors before being consumed or sold.
* **Mathematical Formula:**
  $$\text{DIO} = \frac{\text{Ending Inventory}}{\text{COGS}} \times 365$$
  $$\text{Inventory Turnover} = \frac{\text{COGS}}{\text{Ending Inventory}} = \frac{365}{\text{DIO}}$$
* **Worked Calculation Example (FY23):**
  * Ending Inventory = \$4,000,000.00; COGS = \$15,400,000.00
  $$\text{DIO} = \frac{4,000,000}{15,400,000} \times 365 = 94.8 \text{ days}$$
  $$\text{Turns} = \frac{15,400,000}{4,000,000} = 3.85\times$$
* **Transaction Interpretation:** Inventory turns slowed from 4.1x in FY21 to 3.85x in FY23, indicating buffer stock accumulation or slow-moving SKU buildup.

---

### 16. Days Payable Outstanding (DPO)

* **Definition:** The average number of days the company takes to pay trade suppliers and raw material vendors.
* **Mathematical Formula:**
  $$\text{DPO} = \frac{\text{Ending Trade Accounts Payable}}{\text{COGS}} \times 365$$
* **Worked Calculation Example (FY23):**
  * Ending AP = \$2,110,000.00; COGS = \$15,400,000.00
  $$\text{DPO} = \frac{2,110,000}{15,400,000} \times 365 = 50.0 \text{ days}$$
* **Transaction Interpretation:** DPO extended from 45.3 days in FY21 to 50.0 days in FY23. Management is stretching vendors to finance inventory and AR growth.

---

### 17. Cash Conversion Cycle (CCC)

* **Definition:** The net elapsed time in days between cash outlay for raw materials/inventory and cash recovery from customer collections.
* **Mathematical Formula:**
  $$\text{CCC} = \text{DSO} + \text{DIO} - \text{DPO}$$
* **Worked Calculation Example (FY23):**
  * DSO = 47.7 days, DIO = 94.8 days, DPO = 50.0 days
  $$\text{CCC} = 47.7 + 94.8 - 50.0 = 92.5 \text{ days}$$
* **Transaction Interpretation:** In FY21, the CCC was 82.2 days ($41.9 + 85.6 - 45.3$). The 10.3-day elongation in the cash conversion cycle indicates working capital inefficiency.

---

### 18. SaaS Metrics: ARR Bridge, GRR, NRR, and CAC Payback

* **Definitions & Formulas:**
  1. **ARR Waterfall Bridge:**
     $$\text{Ending ARR} = \text{Beg ARR} + \text{New ARR} + \text{Expansion ARR} - \text{Churned ARR} - \text{Contraction ARR}$$
  2. **Gross Revenue Retention (GRR):**
     $$\text{GRR} = \frac{\text{Beg ARR} - \text{Churned ARR} - \text{Contraction ARR}}{\text{Beg ARR}} \times 100 \quad (\text{Max } 100\%)$$
  3. **Net Revenue Retention (NRR):**
     $$\text{NRR} = \frac{\text{Beg ARR} - \text{Churned ARR} - \text{Contraction ARR} + \text{Expansion ARR}}{\text{Beg ARR}} \times 100$$
  4. **Customer Acquisition Cost (CAC) Payback Period (Months):**
     $$\text{CAC Payback} = \frac{\text{Prior Period S\&M Expense}}{\text{Net New ARR Added} \times \text{Subscription Gross Margin } \%} \times 12$$
* **Worked Calculation Example (CloudMatrix Analytics Inc. - FY23):**
  * Beginning ARR = \$15,000,000.00
  * New ARR = +\$2,400,000.00
  * Expansion ARR = +\$3,600,000.00
  * Churned ARR = -\$1,800,000.00
  * Contraction ARR = -\$1,000,000.00
  * Ending ARR = \$18,200,000.00
  $$\text{GRR} = \frac{15,000,000 - 1,800,000 - 1,000,000}{15,000,000} \times 100 = \frac{12,200,000}{15,000,000} = 81.33\%$$
  $$\text{NRR} = \frac{12,200,000 + 3,600,000}{15,000,000} \times 100 = \frac{15,800,000}{15,000,000} = 105.33\%$$
* **Transaction Interpretation:** While top-line NRR appears acceptable at 105.3%, a GRR of 81.3% reveals substantial customer leakage (18.7% gross dollar churn/contraction per year). Growth is dependent on heavy upsells into a few large accounts.
