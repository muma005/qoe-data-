# Master Revenue Quality Analytical Workpapers & Schedules
**Document Reference:** `QOE-WP-REV-06`  
**Engagement:** Apex Global Industrial Holding Inc. (Project Titanium)  
**Period Under Review:** FY2021 – FY2023 & LTM Ended December 31, 2023  
**Review Standard:** AICPA Quality of Earnings / Buy-Side Financial Due Diligence  

---

## Index of Analytical Schedules

* [Schedule 1: Sales Ledger-to-General Ledger Revenue Tie-Out](#schedule-1-sales-ledger-to-general-ledger-revenue-tie-out)
* [Schedule 2: Top 20 Customer Concentration & Relationship Tenure](#schedule-2-top-20-customer-concentration--relationship-tenure)
* [Schedule 3: Multi-Year Vintage Customer Cohort Matrix](#schedule-3-multi-year-vintage-customer-cohort-matrix)
* [Schedule 4: Price-Volume-Mix (PVM) Decomposition Model](#schedule-4-price-volume-mix-pvm-decomposition-model)
* [Schedule 5: Customer Profitability Whale Curve Analysis](#schedule-5-customer-profitability-whale-curve-analysis)
* [Schedule 6: Revenue Cut-Off & Post-Close Credit Memo Audit](#schedule-6-revenue-cut-off--post-close-credit-memo-audit)

---

### Schedule 1: Sales Ledger-to-General Ledger Revenue Tie-Out
* **Audit Objective:** Reconcile line-item ERP sales invoicing registers to the general ledger and audited income statements to verify starting revenue completeness.
* **Source Records:** Sales Invoice Subledger (`SRC-SL-INV`), Credit Memo Register (`SRC-SL-CM`), Trial Balance (`SRC-TB-FY23`).

$$\begin{array}{lrrrr}
\hline
\textbf{Reconciliation Component} & \textbf{FY2021 (\$)} & \textbf{FY2022 (\$)} & \textbf{FY2023 (\$)} & \textbf{LTM 2023 (\$)} \\
\hline
\text{Gross Invoiced Sales (ERP Subledger)} & 22,150,000.00 & 25,280,000.00 & 25,685,000.00 & 25,800,000.00 \\
\text{Less: Credit Memos \& Returned Goods} & -220,000.00 & -280,000.00 & -345,000.00 & -350,000.00 \\
\text{Less: Prompt Payment Cash Discounts (2/10 Net 30)} & -85,000.00 & -95,000.00 & -115,000.00 & -118,000.00 \\
\text{Less: Customer Volume Rebate Accruals} & -145,000.00 & -185,000.00 & -235,000.00 & -240,000.00 \\
\hline
\textbf{Net Commercial Revenue per General Ledger} & \mathbf{21,700,000.00} & \mathbf{24,720,000.00} & \mathbf{24,990,000.00} & \mathbf{25,092,000.00} \\
\text{Net Revenue per Audited Financial Statements} & 21,700,000.00 & 24,720,000.00 & 24,990,000.00 & 25,092,000.00 \\
\hline
\textbf{Tie-Out Variance} & \mathbf{0.00} & \mathbf{0.00} & \mathbf{0.00} & \mathbf{0.00} \\
\text{Audit Status} & \text{Tied Out } \checkmark & \text{Tied Out } \checkmark & \text{Tied Out } \checkmark & \text{Tied Out } \checkmark \\
\hline
\end{array}$$

* **Analytical Finding:** Zero unexplained tie-out variance between subledger invoices and general ledger control accounts. The baseline is mathematically verified.

---

### Schedule 2: Top 20 Customer Concentration & Relationship Tenure
* **Audit Objective:** Measure portfolio concentration, customer dependency, contractual termination notice, and gross profit dispersion.
* **Source Records:** Customer Master File (`CUST-MST-2023`), Master Service Agreements, General Ledger by Customer.

| Rank | Customer ID | Parent Account Name | Division | FY23 Revenue ($) | Share % | Cum. % | Gross Margin % | Tenure (Yrs) | Contract Expiry | Notice (Days) | Pricing Power |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `CUST-001` | Boeing Defense & Space | Manufacturing | 4,200,000 | 16.90% | 16.90% | 36.5% | 11 | 2026-12-31 | 180 | Strong |
| 2 | `CUST-002` | Lockheed Martin Aero | Manufacturing | 2,850,000 | 11.47% | 28.37% | 38.2% | 8 | 2025-06-30 | 120 | Strong |
| 3 | `CUST-003` | Grainger Industrial | Distribution | 2,400,000 | 9.66% | 38.03% | 21.4% | 14 | 2024-12-31 | 60 | Inflation-Only |
| 4 | `CUST-004` | Fastenal Company | Distribution | 2,100,000 | 8.45% | 46.48% | 20.8% | 12 | 2025-03-31 | 90 | Inflation-Only |
| 5 | `CUST-005` | Raytheon Technologies | Manufacturing | 1,950,000 | 7.84% | 54.32% | 35.4% | 7 | 2025-11-30 | 90 | Strong |
| 6 | `CUST-006` | Ferguson Enterprises | Distribution | 1,600,000 | 6.44% | 60.76% | 19.5% | 9 | 2024-09-30 | 60 | Inflation-Only |
| 7 | `CUST-007` | General Dynamics Land | Manufacturing | 1,450,000 | 5.84% | 66.60% | 34.0% | 6 | 2026-04-30 | 120 | Strong |
| 8 | `CUST-008` | Northrop Grumman | Manufacturing | 1,300,000 | 5.23% | 71.83% | 37.0% | 5 | 2025-08-31 | 90 | Strong |
| 9 | `CUST-009` | MSC Industrial Direct | Distribution | 1,150,000 | 4.63% | 76.46% | 22.0% | 10 | 2024-10-31 | 60 | Inflation-Only |
| 10 | `CUST-010` | Apex Cloud Enterprise | SaaS | 1,100,000 | 4.42% | 80.88% | 78.5% | 3 | 2026-01-31 | 30 | Strong |
| 11 | `CUST-011` | Applied Industrial Tech | Distribution | 950,000 | 3.82% | 84.70% | 21.0% | 8 | 2024-11-30 | 60 | Inflation-Only |
| 12 | `CUST-012` | L3Harris Technologies | Manufacturing | 880,000 | 3.54% | 88.24% | 36.0% | 4 | 2025-12-31 | 90 | Strong |
| 13 | `CUST-013` | Motion Industries | Distribution | 800,000 | 3.22% | 91.46% | 20.5% | 7 | 2025-02-28 | 60 | Inflation-Only |
| 14 | `CUST-014` | BAE Systems Inc | Manufacturing | 720,000 | 2.90% | 94.36% | 35.8% | 5 | 2026-06-30 | 90 | Strong |
| 15 | `CUST-015` | Wesco International | Distribution | 650,000 | 2.61% | 96.97% | 19.8% | 6 | 2024-12-31 | 60 | Inflation-Only |
| 16 | `CUST-016` | Vanguard Aerospace (Cut-off) | Distribution | 620,000 | 2.49% | 99.47% | 26.0% | 4 | 2025-05-31 | 30 | Negative |
| 17 | `CUST-017` | Great Plains Logistics (Bankrupt)| Distribution | 320,000 | 1.29% | 100.75% | 18.0% | 3 | Expired | 0 | Negative |
| 18 | `CUST-018` | OmniTech Cloud (SaaS) | SaaS | 450,000 | 1.81% | 102.56% | 76.0% | 2 | 2025-09-30 | 30 | Strong |
| 19 | `CUST-019` | Midwest Precision Tool | Manufacturing | 420,000 | 1.69% | 104.25% | 33.5% | 5 | 2024-08-31 | 30 | Inflation-Only |
| 20 | `CUST-020` | Apex Logistics (Related Party) | Distribution | 350,000 | 1.41% | 105.66% | 24.0% | 4 | None | 0 | Negative |
| — | — | **Top 5 Concentration** | — | **$13,500,000** | **54.32%** | — | **30.1%** | — | — | — | — |
| — | — | **Top 10 Concentration** | — | **$20,100,000** | **80.88%** | — | **31.2%** | — | — | — | — |
| — | — | **Total Group Revenue** | — | **$24,850,000** | **100.00%** | — | **30.5%** | — | — | — | — |

* **Concentration Assessment:**
  * **Top 1 Customer Share:** 16.90% (Boeing Defense).
  * **Top 5 Customer Share:** 54.32%.
  * **Top 10 Customer Share:** 80.88%.
  * **Herfindahl-Hirschman Index (HHI):** **864.2** (Moderately concentrated at group level, but highly concentrated in Aerospace Manufacturing division where Top 3 represent 78.4% of divisional revenue).

---

### Schedule 3: Multi-Year Vintage Customer Cohort Matrix
* **Audit Objective:** Reconstruct historical customer retention, logo churn, and expansion across annual vintages to evaluate organic top-line sustainability.
* **Source Records:** Sales Invoice Register 2020–2023, Customer Master (`SRC-COHORT-2023`).

$$\begin{array}{|l|l|r|r|r|r|r|}
\hline
\textbf{Cohort Vintage} & \textbf{Cohort Metric} & \textbf{FY2020} & \textbf{FY2021} & \textbf{FY2022} & \textbf{FY2023} & \textbf{LTM 2023} \\
\hline
\textbf{2020 Vintage} & \text{Active Logos} & 145 & 138 & 129 & 121 & 118 \\
& \text{Revenue (\$)} & \$8,500,000 & \$8,925,000 & \$9,192,750 & \$9,468,533 & \$9,500,000 \\
& \text{Cumulative Logo Retention \%} & 100.0\% & 95.2\% & 89.0\% & 83.4\% & 81.4\% \\
& \text{Net Revenue Retention (NRR)} & 100.0\% & 105.0\% & 103.0\% & 103.0\% & 102.5\% \\
\hline
\textbf{2021 Vintage} & \text{Active Logos} & — & 52 & 47 & 42 & 40 \\
& \text{Revenue (\$)} & — & \$3,200,000 & \$3,136,000 & \$3,073,280 & \$3,050,000 \\
& \text{Cumulative Logo Retention \%} & — & 100.0\% & 90.4\% & 80.8\% & 76.9\% \\
& \text{Net Revenue Retention (NRR)} & — & 100.0\% & 98.0\% & 98.0\% & 97.5\% \\
\hline
\textbf{2022 Vintage} & \text{Active Logos} & — & — & 68 & 59 & 56 \\
& \text{Revenue (\$)} & — & — & \$4,100,000 & \$4,305,000 & \$4,350,000 \\
& \text{Cumulative Logo Retention \%} & — & — & 100.0\% & 86.8\% & 82.4\% \\
& \text{Net Revenue Retention (NRR)} & — & — & 100.0\% & 105.0\% & 104.5\% \\
\hline
\textbf{2023 Vintage} & \text{Active Logos} & — & — & — & 48 & 48 \\
& \text{Revenue (\$)} & — & — & — & \$3,150,000 & \$3,200,000 \\
& \text{Cumulative Logo Retention \%} & — & — & — & 100.0\% & 100.0\% \\
& \text{Net Revenue Retention (NRR)} & — & — & — & 100.0\% & 100.0\% \\
\hline
\textbf{Total Enterprise} & \textbf{Total Active Logos} & \mathbf{145} & \mathbf{190} & \mathbf{244} & \mathbf{270} & \mathbf{262} \\
& \textbf{Total Revenue (\$)} & \mathbf{\$8,500,000} & \mathbf{\$12,125,000} & \mathbf{\$16,428,750} & \mathbf{\$19,996,813} & \mathbf{\$20,100,000} \\
& \textbf{Weighted Average GRR} & \mathbf{100.0\%} & \mathbf{96.5\%} & \mathbf{94.5\%} & \mathbf{94.6\%} & \mathbf{94.4\%} \\
& \textbf{Weighted Average NRR} & \mathbf{100.0\%} & \mathbf{103.7\%} & \mathbf{102.4\%} & \mathbf{102.1\%} & \mathbf{101.8\%} \\
\hline
\end{array}$$

* **Analytical Finding:**
  * Core 2020 vintage demonstrates strong net expansion (NRR 102.5%–105.0%), proving high switching costs for foundational aerospace and industrial accounts.
  * 2021 vintage exhibits slight net contraction (NRR 97.5%), driven by regional distributor churn in commodity fastener lines.
  * Enterprise logo retention averages **81.4% to 83.4%** over 4 years, representing a healthy, defensible commercial retention profile.

---

### Schedule 4: Price-Volume-Mix (PVM) Decomposition Model
* **Audit Objective:** Deconstruct total group revenue growth between FY2022 and FY2023 ($3,050,000 total variance) into pure price realization, unit volume changes, and product mix shift.
* **Source Records:** Sales Master File by SKU (`SRC-SKU-PVM`), Inventory Shipping Registers.

$$\begin{array}{|l|rrr|rrr|r|rrr|r|}
\hline
\textbf{Product Category} & \textbf{FY22 Vol} & \textbf{FY22 Prc} & \textbf{FY22 Rev} & \textbf{FY23 Vol} & \textbf{FY23 Prc} & \textbf{FY23 Rev} & \mathbf{\Delta \text{Rev}} & \textbf{Price Eff} & \textbf{Vol Eff} & \textbf{Mix Eff} & \textbf{Tied Out} \\
\hline
\text{Fasteners \& Hardware} & 1,420,000 & \$10.00 & \$14,200,000 & 1,510,000 & \$10.50 & \$15,850,000 & \$1,650,000 & \$750,000 & \$900,000 & \$0 & \$1,650,000 \ \checkmark \\
\text{Precision Machined} & 70,000 & \$80.00 & \$5,600,000 & 81,000 & \$83.95 & \$6,800,000 & \$1,200,000 & \$320,000 & \$880,000 & \$0 & \$1,200,000 \ \checkmark \\
\text{Assembly \& Tooling} & 40,000 & \$50.00 & \$2,000,000 & 42,000 & \$52.38 & \$2,200,000 & \$200,000 & \$100,000 & \$100,000 & \$0 & \$200,000 \ \checkmark \\
\text{Portfolio Mix Shift} & — & — & — & — & — & — & \$0 & \$0 & \$0 & \$0 & \$0 \ \checkmark \\
\hline
\textbf{Total Enterprise} & \mathbf{1,530,000} & \mathbf{\$14.25} & \mathbf{\$21,800,000} & \mathbf{1,633,000} & \mathbf{\$15.22} & \mathbf{\$24,850,000} & \mathbf{\$3,050,000} & \mathbf{\$1,170,000} & \mathbf{\$1,880,000} & \mathbf{\$0} & \mathbf{\$3,050,000} \ \checkmark \\
\hline
\end{array}$$

* **Analytical Finding:**
  * **Volume Growth Contribution:** **$1,880,000 (61.6% of growth)**. Driven by organic aerospace unit demand expansion.
  * **Price Realization Contribution:** **$1,170,000 (38.4% of growth)**. Reflected contractual raw material surcharge pass-through (+4.9% to +5.0% price increase).
  * **Mathematical Footing:** $\text{Price (\$1.17M)} + \text{Volume (\$1.88M)} \equiv \mathbf{\$3,050,000.00}$ (100.0% reconciled).

---

### Schedule 5: Customer Profitability Whale Curve Analysis
* **Audit Objective:** Quantify operating margin cross-subsidization across the customer portfolio by allocating direct cost-to-serve (freight-out, prompt discounts, return scrap).
* **Source Records:** Sales Subledger, Freight-Out GL `5-2000`, Credit Memo Register.

$$\begin{array}{|l|rrrrr|r|}
\hline
\textbf{Customer Decile} & \textbf{Accounts} & \textbf{Net Sales (\$)} & \textbf{Direct COGS (\$)} & \textbf{Cost-to-Serve (\$)} & \textbf{Net Contribution (\$)} & \textbf{Cumulative Margin \%} \\
\hline
\text{Decile 1 (Top 10\%)} & 27 & \$14,500,000 & \$9,570,000 & \$580,000 & \$4,350,000 & 58.0\% \\
\text{Decile 2 (11-20\%)} & 27 & \$4,800,000 & \$3,312,000 & \$240,000 & \$1,248,000 & 74.6\% \\
\text{Decile 3 (21-30\%)} & 27 & \$2,200,000 & \$1,562,000 & \$132,000 & \$506,000 & 81.4\% \\
\text{Decile 4 (31-40\%)} & 27 & \$1,400,000 & \$1,022,000 & \$98,000 & \$280,000 & 85.1\% \\
\text{Decile 5 (41-50\%)} & 27 & \$950,000 & \$712,500 & \$76,000 & \$161,500 & 87.3\% \\
\text{Decile 6 (51-60\%)} & 27 & \$650,000 & \$494,000 & \$58,500 & \$97,500 & 88.6\% \\
\text{Decile 7 (61-70\%)} & 27 & \$420,000 & \$323,400 & \$46,200 & \$50,400 & 89.2\% \\
\text{Decile 8 (71-80\%)} & 27 & \$250,000 & \$195,000 & \$35,000 & \$20,000 & 89.5\% \\
\text{Decile 9 (81-90\%)} & 27 & \$180,000 & \$145,800 & \$41,400 & -\$7,200 & 89.4\% \\
\text{Decile 10 (Bottom 10\%)} & 27 & \$150,000 & \$135,000 & \$72,000 & -\$57,000 & \mathbf{88.6\%} \\
\hline
\textbf{Total Customer Base} & \mathbf{270} & \mathbf{\$25,500,000} & \mathbf{\$17,471,700} & \mathbf{\$1,379,100} & \mathbf{\$6,649,200} & \mathbf{100.0\%} \\
\hline
\end{array}$$

* **Whale Curve Diligence Finding:**
  * **Top 20% of Accounts (Deciles 1 & 2):** Generate **74.6%** of total net contribution margin.
  * **Bottom 20% of Accounts (Deciles 9 & 10):** Generate negative contribution margin (**-$64,200 loss**), destroying enterprise value due to high freight-out costs and small, customized order handling.

---

### Schedule 6: Revenue Cut-Off & Post-Close Credit Memo Audit
* **Audit Objective:** Identify premature revenue recognition around fiscal year-end and post-closing credit memos reversing prior-period sales.
* **Source Records:** Sales Invoices Dec 15 – Jan 15, Bills of Lading, Credit Memos issued Jan 1 – Mar 31, 2024.

| Transaction ID | Customer Name | Invoice Date | Carrier Pickup | Physical Delivery | FOB Shipping Terms | Invoice Amount ($) | Margin Impact ($) | Diligence Finding |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `INV-9842` | Vanguard Aerospace | 2023-12-31 | 2024-01-06 | 2024-01-09 | FOB Destination | $240,000.00 | -$152,000.00 | **Cut-Off Violation:** Invoiced Dec 31; goods shipped Jan 6. Reversal mandated (`ADJ-009`). |
| `INV-9811` | Boeing Defense | 2023-12-28 | 2023-12-28 | 2023-12-30 | FOB Destination | $185,000.00 | $0.00 | Valid delivery prior to year-end; supported by signed POD. |
| `INV-9830` | Grainger Industrial | 2023-12-30 | 2023-12-30 | 2024-01-03 | FOB Shipping Pt | $92,000.00 | $0.00 | Valid recognition under FOB Shipping Point; title passed at dock. |
| `CM-2024-012`| Fastenal Company | 2024-01-14 | — | — | Credit Memo | -$38,000.00 | -$12,000.00 | **Unrecorded Return:** Pricing correction for Dec 2023 shipments; adjusted against 2023. |
| `CM-2024-022`| Motion Industries | 2024-01-28 | — | — | Credit Memo | -$24,500.00 | -$8,500.00 | **Defective Part Scrap:** Return of defective titanium pins shipped Dec 22; adjusted. |

* **Total Revenue Cut-Off & Credit Memo Haircut:** **-$302,500.00 Revenue** / **-$172,500.00 Gross Profit**.
