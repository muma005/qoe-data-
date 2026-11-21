# Master Revenue & Gross Margin Bridge Workpapers
**Document Reference:** `QOE-WP-REVBRIDGE-06`  
**Engagement:** Apex Global Industrial Holding Inc. (Project Titanium)  
**Valuation Date:** LTM Ended December 31, 2023  
**Review Standard:** AICPA Quality of Earnings / Buy-Side Financial Due Diligence  

---

## 1. Executive Summary & Revenue Bridge Architecture

In financial due diligence, top-line revenue diligence operates in tandem with EBITDA normalization. While Workstream 05 adjusted historical operating expenses, Workstream 06 audits the integrity, durability, and run-rate capacity of the revenue engine.

During diligence on Apex Global Industrial Holding Inc. ("Apex"), the team audited reported historical revenues of **$24,990,000.00 in FY2023** and **$25,092,000.00 in LTM 2023**.

Diligence procedures identified:
* **Premature Revenue Cut-Off (Bill-and-Hold #9842):** **-$240,000.00**
* **Unsupported Topside Manual Journal Entry (JE #2023-12-88):** **-$42,500.00**
* **Post-Period Customer Return & Scrap Credit Memos:** **-$62,500.00**
* **QoE Normalized Historical Revenue:** **$24,645,000.00** (-$345,000 / -1.38% historical haircut)
* **Lost Customer Run-Rate Deduction (Great Plains Bankruptcy):** **-$320,000.00** (Full-year trailing revenue elimination)
* **QoE Pro-Forma Run-Rate Sustainable Revenue:** **$24,325,000.00** (-$665,000 / -2.66% run-rate haircut)

```
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                  MASTER REVENUE RECONCILIATION BRIDGE                              |
|                                                                                                    |
|   Reported Baseline Net Revenue (Audited P&L):                                      $24,990,000.00 |
|   - Reversal of Premature Bill-and-Hold Shipment #9842 (ASC 606 Cut-off):            -$  240,000.00 |
|   - Reversal of Unsupported Topside Journal Entry Plug (JE #2023-12-88):             -$   42,500.00 |
|   - Post-Period Unrecorded Return Credit Memos (Fastenal & Motion):                  -$   62,500.00 |
|   ------------------------------------------------------------------------------------------------ |
|   = QoE Normalized Historical Sustainable Revenue:                                  $24,645,000.00 |
|                                                                                                    |
|   - Full-Year Run-Rate Elimination of Bankrupt Customer (Great Plains CUST-017):     -$  320,000.00 |
|   + Annualized Q4 Product Price Increase (5.0% on Fasteners & Precision):            +$  245,000.00 |
|   ------------------------------------------------------------------------------------------------ |
|   = QoE Pro-Forma Underwritten Run-Rate Revenue:                                    $24,570,000.00 |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Multi-Period Revenue Reconciliation Bridge (FY21 – FY23 & LTM)

All figures in USD ($). Every line item reconciles mathematically to source workpapers.

| Revenue Bridge Component | Ref ID | FY2021 ($) | FY2022 ($) | FY2023 ($) | LTM 2023 ($) | Analytical Rationale |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Reported Net Revenue (Audited Baseline)** | **REP-REV** | **21,700,000** | **24,720,000** | **24,990,000** | **25,092,000** | Reconciled sales per audited P&L & trial balance. |
| *QoE Diligence Revenue Adjustments:* | | | | | | |
| - Premature Cut-Off Reversal (Bill-and-Hold) | `REV-001` | 0 | 0 | (240,000) | (240,000) | FOB Destination goods invoiced Dec 31 shipped Jan 6 (`ADJ-009`). |
| - Unsupported Topside Plug Reversal | `REV-002` | 0 | 0 | (42,500) | (42,500) | Manual entry #2023-12-88 to AR/Other Income reversed (`ADJ-010`). |
| - Post-Period Unrecorded Returns & Scrap | `REV-003` | 0 | 0 | (62,500) | (62,500) | Credit memos CM-012 & CM-022 issued in Jan 2024 for 2023 sales. |
| **QoE Normalized Historical Revenue** | **NORM-REV** | **21,700,000** | **24,720,000** | **24,645,000** | **24,747,000** | **True historical commercial revenue earned in period.** |
| *Pro-Forma Run-Rate Adjustments:* | | | | | | |
| - Lost Customer Full-Year Elimination | `RUN-001` | 0 | 0 | (320,000) | (320,000) | Chapter 11 bankruptcy of Great Plains Logistics (`CUST-017`). |
| + Annualized In-Period Q4 Price Increase | `RUN-002` | 0 | 0 | 245,000 | 245,000 | 5.0% price increase enacted Oct 1 annualized across 9 stub months. |
| **QoE Pro-Forma Run-Rate Revenue** | **RUN-REV** | **21,700,000** | **24,720,000** | **24,570,000** | **24,672,000** | **Defensible top-line baseline for ongoing underwriting.** |

---

## 3. Gross Margin Decomposition Bridge (FY2022 to FY2023)

Between FY2022 and FY2023, reported Gross Margin expanded by **+$270,000 in dollars**, but compressed from **30.50% to 30.01% in margin percentage** (-49 basis points). The bridge below decomposes the economic drivers of this margin shift:

$$\begin{array}{lrr}
\hline
\textbf{Gross Margin Movement Component} & \textbf{Dollar Impact (\$)} & \textbf{Margin Percentage Impact (bps)} \\
\hline
\textbf{FY2022 Gross Profit Baseline (30.50\% on \$24,720,000)} & \mathbf{\$7,539,600.00} & \mathbf{30.50\%} \\
\text{+ Pure Price Increase Realization (Contractual Surcharges)} & +\$1,170,000.00 & +468 \text{ bps} \\
\text{- Raw Material \& Component Input Cost Inflation} & -\$1,145,000.00 & -458 \text{ bps} \\
\text{+ Volume Growth Impact (at FY22 Margin)} & +\$573,400.00 & 0 \text{ bps} \\
\text{- Freight-Out Cost-to-Serve Expansion (Carrier Surcharges)} & -\$185,000.00 & -74 \text{ bps} \\
\text{- Customer Mix Dilution (Higher Share of Low-Margin Accounts)} & -\$83,000.00 & -33 \text{ bps} \\
\text{+ High-Margin Enterprise SaaS Expansion Contribution} & +\$130,000.00 & +52 \text{ bps} \\
\text{- Reversal of Premature Bill-and-Hold Margin (INV-9842)} & -\$152,000.00 & -4 \text{ bps} \\
\hline
\textbf{FY2023 Normalized Gross Profit Baseline (30.01\% on \$24,645,000)} & \mathbf{\$7,848,000.00} & \mathbf{30.01\%} \\
\hline
\textbf{Net Variance (FY2022 to FY2023)} & \mathbf{+\$308,400.00} & \mathbf{-49\text{ bps}} \\
\hline
\end{array}$$

* **Analytical Finding:**
  * While Apex successfully passed through $1.17M in price increases, raw material cost inflation ($1.15M) and carrier freight-out expansion ($185k) completely absorbed the price benefit, driving a net **49 bps gross margin compression**.
  * The business is not exhibiting pricing expansion power; it is merely executing a defensive inflation pass-through.

---

## 4. Valuation Impact & Transaction Pricing Sensitivity

In transaction pricing, top-line quality findings directly impact Enterprise Value (EV). The table below demonstrates the compounding valuation haircut resulting from the combined **$345,000 revenue reduction** and **$172,500 gross margin reduction**:

$$\text{EBITDA Impact of Revenue Haircuts} = -\$152,000\ (\text{Cut-off}) - \$42,500\ (\text{Plug}) - \$18,500\ (\text{Scrap}) = -\$213,000.00$$

| Enterprise Value Multiple | Implied EV on Reported Top-Line | Defensible EV on Normalized Top-Line | Direct Buyer Valuation Savings |
| :---: | :---: | :---: | :---: |
| **6.0x EV / EBITDA** | $19,980,000 | $18,702,000 | **-$1,278,000** |
| **8.0x EV / EBITDA (Base Case)** | **$26,640,000** | **$24,936,000** | **-$1,704,000** |
| **10.0x EV / EBITDA** | $33,300,000 | $31,170,000 | **-$2,130,000** |

> [!IMPORTANT]
> **Strategic Diligence Takeaway:**  
> The revenue quality investigation revealed that the seller's claimed top-line expansion was artificially bolstered by premature billing ($240k), manual plugs ($42.5k), and unrecorded credit memos ($62.5k). Uncovering these commercial issues protects the buyer from **$1.704 million in overpayment** at an 8.0x valuation multiple.
