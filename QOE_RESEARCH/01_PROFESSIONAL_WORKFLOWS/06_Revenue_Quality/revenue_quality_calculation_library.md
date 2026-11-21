# Revenue Quality Calculation Library & Mathematical Formulas
**Document Reference:** `QOE-CALC-LIB-06`  
**Workstream:** `06 — Revenue and Margin Quality`  
**Classification:** Professional Financial Due Diligence Technical Specification  

---

## 1. Architectural Taxonomy of Revenue Quality Metrics

In transaction advisory and financial due diligence, reported statutory revenue is subjected to multi-layered decomposition. Diligence teams distinguish between eight dimensions of revenue quality:

```
+───────────────────────────────────────────────────────────────────────────────+
| 1. Gross Invoiced Revenue (Sales Register / Subledger Total)                 |
+───────────────────────────────────────────────────────────────────────────────+
                                      │
                                      ▼ [Credit Memos, Returns, Discounts, Rebates]
+───────────────────────────────────────────────────────────────────────────────+
| 2. Reconciled Net GAAP Revenue (Audited P&L Baseline)                         |
+───────────────────────────────────────────────────────────────────────────────+
                                      │
                                      ▼ [ASC 606 Cut-Off, Bill-and-Hold, Plugs]
+───────────────────────────────────────────────────────────────────────────────+
| 3. QoE Normalized Sustainable Revenue (Clean Historical Commercial Baseline)  |
+───────────────────────────────────────────────────────────────────────────────+
                                      │
                                      ▼ [Lost Customer Annualization, Contract Exits]
+───────────────────────────────────────────────────────────────────────────────+
| 4. Pro-Forma Run-Rate Revenue (Underwritten Ongoing Top-Line Capacity)       |
+───────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Mathematical Formulations & Calculation Algorithms

### 2.1 Sales Ledger to General Ledger Tie-Out & Coverage Ratio
Prior to conducting detailed customer or SKU diligence, the practitioner must verify that the transaction-level sales ledger reconciles to the general ledger revenue accounts:

$$\text{Reconciled Net Sales} = \sum_{i=1}^{N} \text{Gross Invoice Amount}_i - \sum_{j=1}^{M} \text{Credit Memo Amount}_j - \sum \text{Prompt Pay Discounts} - \sum \text{Rebate Accruals}$$

$$\text{Sales Ledger Tie-Out Variance} = |\text{Net Sales per Subledger} - \text{Net Revenue per Trial Balance}|$$

$$\text{Testing Coverage Ratio} = \frac{\sum_{k \in \text{Tested Accounts}} \text{Revenue}_k}{\text{Total Reconciled Net Revenue}} \ge 0.80 \quad (80.0\% \text{ Institutional Scoping Threshold})$$

* If $\text{Sales Ledger Tie-Out Variance} > 0.005 \times \text{Reported Revenue}$ (0.5%), diligence is halted until management provides an invoice-level reconciliation.

---

### 2.2 Price-Volume-Mix (PVM) Decomposition Model
When revenue expands or contracts across fiscal periods, FDD teams isolate the exact contribution of price increases, unit shipment changes, and shifts in product composition.

For a business with $K$ product categories between Base Period ($t-1$) and Current Period ($t$):

$$\Delta \text{Revenue} = \text{Revenue}_t - \text{Revenue}_{t-1} = \text{Price Effect} + \text{Volume Effect} + \text{Mix Effect}$$

#### The Formulations:

1. **Price Effect (Pure Pricing Power / Surcharges):**
   The portion of revenue change caused solely by changes in unit selling prices, holding volumes and product mix constant at current period levels:
   $$\text{Price Effect} = \sum_{k=1}^{K} Q_{k, t} \times \left( P_{k, t} - P_{k, t-1} \right)$$

2. **Volume Effect (Organic Demand / Market Growth):**
   The portion of revenue change driven by total unit volume growth across the business, evaluated at base period weighted average selling prices:
   $$\text{Volume Effect} = \left( \sum_{k=1}^{K} Q_{k, t} - \sum_{k=1}^{K} Q_{k, t-1} \right) \times \bar{P}_{t-1}$$
   Where:
   $$\bar{P}_{t-1} = \frac{\sum_{k=1}^{K} \text{Revenue}_{k, t-1}}{\sum_{k=1}^{K} Q_{k, t-1}}$$

3. **Mix Effect (Portfolio Composition Shift):**
   The portion of revenue change resulting from customers buying a different proportion of higher-priced versus lower-priced products:
   $$\text{Mix Effect} = \sum_{k=1}^{K} \left( \frac{Q_{k, t}}{\sum Q_{t}} - \frac{Q_{k, t-1}}{\sum Q_{t-1}} \right) \times \left( P_{k, t-1} - \bar{P}_{t-1} \right) \times \sum_{k=1}^{K} Q_{k, t}$$

#### Mathematical Footing Identity:
$$\text{Price Effect} + \text{Volume Effect} + \text{Mix Effect} \equiv \Delta \text{Revenue} \quad (\text{Exact to the Cent})$$

---

### 2.3 Customer Cohort Analysis & Vintage Decay
Customer cohort modeling tracks the behavior of customer groups acquired in specific fiscal years (vintages) across subsequent years:

For Cohort $V$ in Fiscal Year $t \ge V$:

$$\text{Cohort Decay Rate}_{V, t} = 1 - \frac{\text{Active Logos}_{V, t}}{\text{Active Logos}_{V, t-1}}$$

$$\text{Cumulative Vintage Logo Retention}_{V, t} = \frac{\text{Active Logos}_{V, t}}{\text{Initial Acquired Logos}_{V, V}}$$

$$\text{Vintage Revenue Retention Factor}_{V, t} = \frac{\text{Revenue}_{V, t}}{\text{Initial Vintage Revenue}_{V, V}}$$

* **Commercial Red Flag:** If cumulative revenue for mature cohorts ($t \ge V+2$) decays at $>10\%$ annually, top-line growth is entirely dependent on continuous, high-cost customer acquisition (treadmill effect).

---

### 2.4 Retention & Churn Mechanics (SaaS & Contractual Models)
For subscription and recurring contract models, revenue quality is defined by retention metrics:

$$\text{Logo Retention Rate} = \frac{N_{\text{active, end}} - N_{\text{new acquired}}}{N_{\text{active, start}}}$$

$$\text{Gross Revenue Retention (GRR)} = \frac{\text{ARR}_{\text{start}} - \text{Contraction ARR} - \text{Churned ARR}}{\text{ARR}_{\text{start}}} \quad (\le 100.0\%)$$

$$\text{Net Revenue Retention (NRR)} = \frac{\text{ARR}_{\text{start}} + \text{Expansion ARR} - \text{Contraction ARR} - \text{Churned ARR}}{\text{ARR}_{\text{start}}}$$

$$\text{Customer Acquisition Cost (CAC) Payback Months} = \frac{\text{Sales \& Marketing Expense}_{t-1}}{\text{New Net ARR Acquired}_t \times \text{Subscription Gross Margin \%}} \times 12$$

$$\text{Customer Lifetime Value (LTV)} = \frac{\text{Average Annual Revenue per User (ARPU)} \times \text{Gross Margin \%}}{\text{Annual Logo Churn Rate \%}}$$

---

### 2.5 Customer Concentration & Herfindahl-Hirschman Index (HHI)
To evaluate revenue vulnerability to customer loss:

$$\text{Top } N \text{ Concentration Share} = \frac{\sum_{i=1}^{N} \text{Revenue}_i}{\text{Total Reconciled Net Revenue}}$$

$$\text{Herfindahl-Hirschman Index (HHI)} = \sum_{i=1}^{C} \left( s_i \times 100 \right)^2$$
Where $s_i$ is the revenue market share of customer $i$ expressed as a decimal ($s_i = \text{Revenue}_i / \text{Total Revenue}$).

* **Concentration Risk Brackets:**
  * $\text{HHI} < 1,000$: Unconcentrated / Diversified customer portfolio.
  * $1,000 \le \text{HHI} \le 1,800$: Moderately Concentrated.
  * $\text{HHI} > 1,800$: Highly Concentrated (Severe structural transaction risk).
  * If $\text{Top 1 Customer Share} > 15\%$ or $\text{Top 10 Share} > 50\%$, lenders typically require special customer retention escrows.

---

### 2.6 Customer Profitability & Whale Curve Allocation
Diligence calculates true contribution margins by allocating cost-to-serve:

$$\text{Customer Gross Profit}_i = \text{Billed Revenue}_i - \text{Direct Product COGS}_i$$

$$\text{Customer Net Contribution}_i = \text{Customer Gross Profit}_i - \text{Direct Freight-Out}_i - \text{Customer Sales Commissions}_i - \text{Dedicated Account Support}_i$$

$$\text{Cumulative Margin Percentage}_m = \frac{\sum_{i=1}^{m} \text{Customer Net Contribution}_i}{\sum_{i=1}^{C} \text{Customer Net Contribution}_i} \times 100\%$$

* **Whale Curve Phenomemon:** In distribution businesses, the top 20% of accounts routinely generate $120\% - 150\%$ of cumulative operating profits, while the bottom 20% destroy $20\% - 50\%$ of profits through high return rates, non-standard order sizes, and subsidized freight.

---

### 2.7 ASC 606 Revenue Timing & Cut-Off Errors
When goods are shipped FOB Destination on December 31 but delivered in January:

$$\Delta \text{Revenue}_{\text{Cut-Off}} = -\text{Invoiced Value of Unfulfilled Orders}$$

$$\Delta \text{COGS}_{\text{Cut-Off}} = -\text{Cost Value of Goods in Transit (Restored to Inventory)}$$

$$\text{Mandatory EBITDA Haircut} = \Delta \text{Revenue}_{\text{Cut-Off}} - \Delta \text{COGS}_{\text{Cut-Off}} = -(\text{Gross Profit Recognized Prematurely})$$

---

### 2.8 Lost Customer Run-Rate EBITDA Haircut
When a material customer churns mid-period or post-closing, historical Normalized EBITDA overstates forward maintainable earnings. The run-rate haircut strips out the unrepeatable gross contribution:

$$\text{Lost Customer Run-Rate Haircut} = - \left( \text{Customer Trailing 12-Month Revenue} \times \text{Customer Contribution Margin \%} \right) \times (1 - \text{Period Weight Already Excluded})$$

If Customer $X$ generated $\$1,000,000$ in trailing revenue at a $25\%$ gross margin and terminated on September 30, the historical LTM already lost 3 months of revenue, but still contains 9 months ($\$750,000$ revenue / $\$187,500$ margin) that will never recur:
$$\text{Run-Rate EBITDA Haircut} = -\$187,500.00$$
