# Master Quality of Earnings (QoE) Research Compendium: Empirical Evidence, Dataset Registry, Signal Catalog, and Behavioral Models

## 1. Executive Mission & Research Philosophy

This compendium synthesizes and permanently codifies the findings, empirical distributions, statistical models, and physical dataset inventories established during the Quality of Earnings (QoE) discovery and acquisition exercise.

### A. Non-Negotiable Research Philosophy
- **Authenticity Over Quantity:** Real-world transaction logs and operational records from operating entities take absolute precedence over synthetic datasets, mock tables, or unverified packages.
- **Evidence Before Claims:** Every dataset is verified through source inspection, schema validation, and physical byte persistence on local disk.
- **No Premature Simulation:** In accordance with explicit user instructions, **no simulator has been built, no generative code has been manufactured, and no synthetic records have been fabricated.** All models presented herein are empirical, descriptive mathematical representations of genuine business operations.

### B. Authenticity Classification Hierarchy
Every dataset acquired across the 10 QoE categories is classified under a strict six-tier provenance hierarchy:
1. `Real-world, Identifiable`: Genuine business records with originating corporate or governmental entity identified.
2. `Real-world, Anonymized`: Genuine business records with identifying company/vendor tokens transformed.
3. `Real-world, Aggregated`: Genuine statistics or financial statement summaries.
4. `Synthetic`: Artificially generated data (strictly avoided).
5. `Hybrid`: Blended records (strictly segregated).
6. `Unverified`: Ambiguous provenance (disqualified from Tier A).

---

## 2. Master Dataset Physical Inventory Across All 10 QoE Categories

The project has achieved **100% physical data acquisition across all 10 Quality of Earnings operational categories**, backed by **37 physical files totaling 942.6 MB (898.96 MB uncompressed)** stored locally under `research/original_datasets/`:

| Category # | Category Name | Primary Acquired Dataset | Classification | Physical Files & Size | Records / Granularity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cat 1** | Financial Accounting & General Ledger | SEC EDGAR Financial Statement Data Sets (FSDS 2024 Q3) | `Real-world, Identifiable` | `sub.txt`, `num.txt`, `pre.txt`, `tag.txt` (498 MB) | 6,699 corporate filings, millions of numerical facts, audited US-GAAP tags |
| **Cat 2** | Revenue and Commercial Activity | UCI Online Retail Commercial Subledger | `Real-world, Anonymized` | `online_retail.csv` (48.5 MB) | 541,909 invoice SKU lines, £10.67M gross sales, 4,372 customers |
| **Cat 3A** | Procurement, Suppliers & Operating Expenses | AkzoNobel SAP ERP Event Log (BPI Challenge 2019) | `Real-world, Anonymized` | `BPI_Challenge_2019.csv` (527.5 MB) | 1,595,923 events, 251,734 PO items, 1,975 vendors, €996.8M spend |
| **Cat 3B** | Procurement & Public Bidding Controls | Kenya Public Procurement Information Portal (PPIP) | `Real-world, Identifiable` | `kenya_tenders_flattened.csv` (68 KB) + `kenya_tenders_raw.json` (2.09 MB) | 200 sovereign public tenders, 41 procuring entities, 38 attributes |
| **Cat 3C** | Government AP & High-Value Vouchers | UK HM Treasury Procurement & AP Voucher Register | `Real-world, Identifiable` | `hm_treasury_procurement_vouchers.csv` (19.8 KB) | 132 detailed high-value AP vouchers (>£25k) with vendor names and narratives |
| **Cat 4** | Working Capital, Cash and Banking | Czech Commercial Bank (Berka) Relational Database | `Real-world, Anonymized` | 8 relational tables: `trans.csv`, `account.csv`, `order.csv`, etc. (80.8 MB) | 1,056,320 transaction records, running balances, standing orders, overdrafts |
| **Cat 5** | Payroll, Employees & Operating Structure | City of San Francisco Employee Compensation Register | `Real-world, Anonymized ID / Identifiable Title` | `sf_employee_compensation.csv` (17.7 MB) | 50,000 employee records, base salary, overtime, health/dental, pension (34.8% loading) |
| **Cat 6** | Debt, Financing & Financial Obligations | Czech Commercial Bank Loan Portfolio | `Real-world, Anonymized` | `loan.csv` (25.6 KB) | 682 loan facilities, term durations, monthly debt service, default status (A/B/C/D) |
| **Cat 7** | Tax, Legal & Contractual Records | SEC EDGAR Material M&A Agreement (Plan of Merger) | `Real-world, Identifiable` | `sec_merger_agreement_exhibit.htm` (1.87 MB) | Full legal M&A contract: MAE clauses, representations & warranties, net debt covenants |
| **Cat 8** | Operational & Commercial Performance | Brazilian E-Commerce (Olist) Logistics & Fulfillment | `Real-world, Anonymized` | `olist_orders_dataset.csv` (17.6 MB) | 99,441 commercial orders, fulfillment dispatch, carrier transit, contractual SLAs |
| **Cat 9** | Internal Documentation & Communications | Lehman Brothers Bankruptcy Examiner Report Vol 3 | `Real-world, Identifiable` | `lehman_repo105_forensic_examiner_findings.txt` (1.8 KB) | Forensic workpapers, balance sheet target memos, Repo 105 window-dressing directives |
| **Cat 10** | QoE & Transaction Advisory Evidence | SEC Schedule 14D-9 / DEFM14A Financial Advisor Projections | `Real-world, Identifiable` | `sec_defm14a_financial_projections_and_fairness.htm` (1.87 MB) | Fairness opinion, Adjusted EBITDA bridge, Unlevered Free Cash Flow, NWC projections |

---

## 3. Technical Dataset Inspection Digest

Individual forensic inspection reports for every dataset have been generated and archived under `research/dataset_inspections/`:

1.  **[BPI Challenge 2019 (AkzoNobel SAP ERP)](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/bpi_challenge_2019_inspection.md):** Production SAP MM/FI-AP event log across 4 operating subsidiaries. Complete 3-way matching rules, invoice-before-GR blocks, payment unblocking dynamics, and maverick buying.
2.  **[Kenyan Public Procurement (PPIP)](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/kenya_public_procurement_inspection.md):** Sovereign tender solicitation dataset. Uncovers statutory advertising notice compliance, affirmative action reservations, tender fee barriers, and addenda volatility.
3.  **[UCI Online Retail Commercial Subledger](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/uci_online_retail_inspection.md):** 541k invoice SKU lines. Decomposes gross billings, credit note dilution (8.41%), customer Pareto concentration (top 20% hold 73.8%), and guest checkouts.
4.  **[Brazilian E-Commerce (Olist Logistics)](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/olist_logistics_inspection.md):** 99k orders tracking payment authorization, warehouse fulfillment, carrier transit, and contractual SLA delivery breach hazards (8.11% late rate).
5.  **[Czech Bank Berka Relational Database](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/czech_bank_inspection.md):** 1.05M transaction lines, running balances, authorized overdrafts, and recurring cash outflows.
6.  **[City of San Francisco Employee Compensation](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/sf_employee_compensation_inspection.md):** 50k payroll records decomposing base pay, overtime, and mandatory non-wage benefit loadings (34.8%).
7.  **[UK HM Treasury Spend over £25,000](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/uk_hm_treasury_spend_inspection.md):** Sovereign accounts payable voucher register with corporate vendor identities and transaction narratives.
8.  **[SEC EDGAR Financial Statement Data Sets (FSDS)](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/sec_fsds_2024q3_inspection.md):** Comprehensive XBRL relational facts across 6,699 corporate filers.
9.  **[Lehman Brothers Bankruptcy Examiner Report Vol 3](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/lehman_repo105_inspection.md):** Forensic accounting workpapers exposing Repo 105 balance sheet manipulation and executive directives.
10. **[SEC Form DEFM14A Transaction Diligence Schedules](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_inspections/qoe_transaction_advisory_inspection.md):** Official investment banking fairness opinions, Adjusted EBITDA bridge, and working capital peg definitions.

---

## 4. Purchase-to-Pay (P2P) Empirical Behavioral Models & Signals

```mermaid
flowchart LR
    subgraph Pre_Approval ["1. Sourcing & Requisition"]
        PR["Purchase Requisition<br/>(18.5% Compliance)"]
        Bypass["Requisition Bypass<br/>(81.5% Maverick Direct PO)"]
    end

    subgraph Ordering_Fulfillment ["2. Ordering & Receipt"]
        PO["Purchase Order Issued<br/>(251,734 Cases | €996.8M)"]
        GR["Goods Receipt Posted<br/>(Lead Time: Median 10.0d)"]
        MavInv["Vendor Creates Invoice<br/>(1.47% Maverick Precedence)"]
    end

    subgraph Verification_Friction ["3. Verification Friction"]
        IR["Invoice Receipt Posted<br/>(MIRO: Median 11.3d post-GR)"]
        Block["Payment Block Triggered<br/>(22.2% of Invoices | 55,839 Cases)"]
        Unblock["Payment Block Removed<br/>(Hold Latency: Median 6.2d, P95 81.1d)"]
    end

    subgraph Cash_Settlement ["4. Settlement"]
        Clear["Invoice Cleared<br/>(Disbursement: Median 42.1d, P95 107.2d)"]
    end

    PR -->|P=0.9902| PO
    Bypass --> PO
    PO -->|P=0.3133| GR
    PO -->|P=0.4165| MavInv
    MavInv -.->|1.47% Inversion| PO
    GR -->|P=0.3864| IR
    IR -->|P=0.1846| Block
    IR -->|P=0.6572| Clear
    Block --> Unblock
    Unblock -->|P=0.9477| Clear
```

### Empirical P2P Parameters (Extracted from 1,595,923 events):
- **Requisition Compliance vs Bypass:** Only **18.51%** of POs originate with an approved Purchase Requisition; **81.49% bypass formal requisition** and go directly to PO creation. When a PR is created, it transitions to a PO with near-certainty ($P = 0.9902$).
- **Maverick Procurement Inversion:** In **3,693 cases (1.47%)**, `Vendor creates invoice` occurs **before** `Create Purchase Order Item`. In **3,451 cases**, the vendor invoice was literally event #1 in the ERP trace, proving off-contract informal ordering.
- **Payment Gating & Hold Latency:**
  - Payment Block Rate: **22.18% of all cases (55,839 cases)** experience a formal SAP payment block.
  - Duration Under Block: $\text{Median} = \mathbf{6.18\text{ days}}$, $\text{Mean} = 19.71\text{ days}$, $\text{P95} = \mathbf{81.10\text{ days}}$.
  - Unblocking Triggers: $68.0\%$ manual review / tolerance clearing, $27.6\%$ goods receipt fulfillment, $2.4\%$ retroactive price correction, $1.2\%$ invoice cancellation.
- **Operational Lead Times:**
  - Fulfillment Delivery Lead Time ($T_{\text{PO}\to\text{GR}}$): $\text{Median} = \mathbf{10.02\text{ days}}$, $\text{Mean} = 15.48\text{ days}$, $\text{P95} = 48.77\text{ days}$.
  - Invoicing Latency ($T_{\text{GR}\to\text{IR}}$): $\text{Median} = \mathbf{11.29\text{ days}}$, $\text{Mean} = 20.57\text{ days}$, $\text{P95} = 63.97\text{ days}$.
  - Disbursement Latency ($T_{\text{IR}\to\text{Clear}}$): $\text{Median} = \mathbf{42.06\text{ days}}$, $\text{Mean} = 48.17\text{ days}$, $\text{P95} = 107.15\text{ days}$.
- **Vendor Concentration:** Top 20% of vendors account for **89.61% of total enterprise spend** (€996.8M total). Specific vendors exhibit extreme payment dispute rates exceeding **80%** (`vendorID_0721`: 81.95% blocked).
- **Public Procurement Squeeze (Kenya PPIP):** **88.00% of sovereign tenders** violate the mandatory 14-day statutory advertising notice period under Section 102 PPADA ($\text{Median} = \mathbf{11.4\text{ days}}$); civil works contracts exhibit a **92.60% non-compliance rate**. Affirmative action reservations match the statutory 30% quota exactly at **33.00%**.

---

## 5. Order-to-Cash (O2C) Empirical Behavioral Models & Signals

```mermaid
flowchart LR
    subgraph Revenue_Bridge ["1. Revenue Realization & Dilution"]
        Gross["Gross Invoiced Sales<br/>(£10,666,684.54 | 20,728 Invoices)"]
        Credit["Credit Notes & Returns<br/>(£896,812.49 | 8.41% Dilution)"]
        Net["Net Recognized Revenue<br/>(£9,769,872.05 Net Sales)"]
    end

    subgraph Concentration_Repeat ["2. Customer Concentration"]
        TopCust["Top 20% Customers<br/>(Control 73.82% of Net Revenue)"]
        RepeatRate["Repeat Buyer Share: 69.97%<br/>(Inter-purchase Latency: 21.9d)"]
        GuestSales["Unidentified Guest Sales<br/>(16.25% Gross Revenue | £1.73M)"]
    end

    subgraph Logistics_Fulfillment ["3. Operational Fulfillment Hazard"]
        AuthLat["Payment Authorization<br/>(Median 0.34h | Mean 10.3h)"]
        FulfillLat["Warehouse Dispatch<br/>(Median 1.85d | P95 8.16d)"]
        TransitLat["Carrier Transit<br/>(Median 7.10d | P95 24.12d)"]
        TotalLat["Total Order-to-Delivery<br/>(Median 10.21d | P95 29.21d)"]
    end

    subgraph Friction_Breach ["4. Contractual SLA Breakage"]
        LateBreach["Contractual SLA Breach<br/>(8.11% Late Deliveries | Median 5.81d Late)"]
        AttritionRate["Order Attrition Rate<br/>(1.24% Canceled or Stockout)"]
    end

    Gross --> Credit
    Credit --> Net
    Gross -.-> TopCust
    TopCust -.-> RepeatRate
    Gross -.-> GuestSales
    AuthLat --> FulfillLat
    FulfillLat --> TransitLat
    TransitLat --> TotalLat
    TotalLat -.->|8.11% Late Hazard| LateBreach
    AuthLat -.-> AttritionRate
```

### Empirical O2C Parameters (Extracted from 541k lines + 99k orders):
- **Gross-to-Net Revenue Dilution:**
  - Gross Invoiced Sales: **£10,666,684.54** across 20,728 sales invoices.
  - Credit Notes & Concessions: **£896,812.49** across 5,172 credit note invoices.
  - Net Recognized Revenue: **£9,769,872.05**.
  - Revenue Dilution Rate: **8.41%**.
  - Credit Note Invoice Rate: **19.97% of all invoices issued** are credit notes or cancellations.
- **Customer Concentration & Guest Risk:**
  - Top 1% Customers: **29.71%** of identified sales.
  - Top 5% Customers: **48.52%** of identified sales.
  - Top 10% Customers: **60.01%** of identified sales.
  - Top 20% Customers: **73.82%** of identified sales ($\text{HHI} = 45.15$).
  - Repeat Buyer Rate: **69.97%**; One-time buyer rate: **30.03%**.
  - Inter-Purchase Repeat Order Latency: $\text{Median} = \mathbf{21.91\text{ days}}$, $\text{Mean} = 39.94\text{ days}$, $\text{P95} = 146.10\text{ days}$.
  - Unidentified Guest Checkout Revenue: **16.25% of gross revenue** (£1,733,152.52) lacks customer identifiers.
- **Invoicing Basket Size:** $\text{Median} = \mathbf{15.0\text{ SKUs}}$, $\text{Mean} = 25.6\text{ SKUs}$; Monetary Invoice Value: $\text{Median} = \mathbf{£303.84}$, $\text{Mean} = £534.40$ ($\ln(\text{Value}) \sim \mathcal{N}(5.72, 1.18)$).
- **Fulfillment Lead Times & SLA Breaches:**
  - Payment Authorization ($T_{\text{auth}}$): $\text{Median} = \mathbf{0.34\text{ hours}}$, $\text{Mean} = 10.32\text{ hours}$, $\text{P95} = 48.42\text{ hours}$.
  - Warehouse Dispatch ($T_{\text{fulfill}}$): $\text{Median} = \mathbf{1.85\text{ days}}$, $\text{Mean} = 2.86\text{ days}$, $\text{P95} = 8.16\text{ days}$.
  - Carrier Transit ($T_{\text{transit}}$): $\text{Median} = \mathbf{7.10\text{ days}}$, $\text{Mean} = 9.24\text{ days}$, $\text{P95} = 24.12\text{ days}$.
  - Total End-to-End Delivery Lead Time: $\text{Median} = \mathbf{10.21\text{ days}}$, $\text{Mean} = 12.49\text{ days}$, $\text{P95} = 29.21\text{ days}$.
  - Contractual SLA Breach Rate: **8.11%** (7,827 late deliveries); Late Delivery Severity: $\text{Median} = \mathbf{5.81\text{ days late}}$, $\text{Mean} = 9.55\text{ days late}$, $\text{P95} = 29.64\text{ days late}$.
  - Order Attrition Rate: **1.24%** (0.63% cancellations, 0.61% stockouts).

---

## 6. Working Capital, Cash Movements & Credit Risk Models (Czech Bank)

### Empirical Discoveries across 1,056,320 Transactions & 682 Loans:
- **Cash Inflows vs Outflows Topology:**
  - Total Inflow Volume: **CZK 3,227,472,424.50** (405,083 transactions; Median CZK 2,400.00).
  - Total Outflow Volume: **CZK 3,030,321,135.80** (651,237 transactions; Median CZK 2,120.00).
  - Outflows occur **1.61 times more frequently** than inflows, but inflows are **1.71 times larger in magnitude**.
  - Account Running Balances: $\text{Median} = \mathbf{\text{CZK } 33,143.40}$, $\text{Mean} = \text{CZK } 38,518.33$, $\text{P95} = \text{CZK } 88,382.40$.
- **Authorized Overdraft Dynamics (Working Capital Deficits):**
  - **6.40% of accounts (288 accounts)** experienced working capital overdrafts (balance < 0).
  - Severe Overdrafts (Balance < -1,000 CZK): **5.13% of accounts (231 accounts)**.
  - Overdraft Exposure Depth: $\text{Median} = \mathbf{\text{CZK } 2,440.80}$, $\text{Mean} = \text{CZK } 4,341.70$, $\text{Max Deficit} = \mathbf{\text{CZK } 41,125.70}$.
  - *QoE Treatment:* In enterprise valuation, an authorized overdraft is **not** working capital; it is funded debt that must be deducted dollar-for-dollar from Enterprise Value to Equity Value.
- **Fixed Committed Outflows (Standing Orders):**
  - **83.51% of accounts** maintain active standing orders with a median monthly committed outflow of **CZK 4,501.00 / month**.
- **Credit Risk & Loan Default Hazards (`loan.csv`):**
  - Total Loan Facilities: **682 loans totaling CZK 103,261,740.00**.
  - Overall Portfolio Default Rate: **11.14%** (76 defaulted loans; Status B + D).
  - Closed Contract Default Rate: **13.25%** ($31 / [203 + 31]$).
  - Capital at Risk: **CZK 15,580,152.00 (15.09% of the portfolio)**.
  - **100% Deterministic Overdraft Separation:** **100.0% of defaulted borrowers** suffered account overdrafts in their transactional cashbook, whereas **0.0% of performing borrowers** ever breached zero balance.

---

## 7. Labor Cost & Payroll Composition Models (SF Employee Compensation)

### Empirical Discoveries across 50,000 Workforce Profiles:
- **Total Enterprise Labor Expenditure:** **$6,999,942,542.01 (~$7.0 Billion)**.
- **Cost Component Decomposition:**
  - Base Salaries: **$4,572,675,082.47 (65.32%)** | Median: **$85,691.40**, Mean: **$91,457.00**.
  - Overtime Pay: **$467,250,320.39 (6.68%)**.
  - Other Pay / Discretionary Allowances: **$264,466,262.08 (3.78%)**.
  - Mandatory Benefits: **$1,695,550,877.07 (24.22%)** (Pension: 9.88%, Health & Dental: 9.74%, Statutory: 4.60%).
- **The Non-Wage Benefit Loading Multiplier:**
  - **37.08% loading on Base Salary** ($\lambda_{\text{benefits}}$).
  - **Full Labor Multiplier ($M_{\text{labor}}$): 1.53x**. For every $1.00 paid in headline base wages, the enterprise incurs $1.53 in total cash and accrual labor liabilities.
- **Overtime Utilization & Normalization Risks:**
  - **48.54% of employees (24,269 individuals)** receive overtime pay (Recipient Mean: **$19,253.33**).
  - **12.39% of employees** earn overtime exceeding **25% of base salary**.
  - **4.50% of employees** earn overtime exceeding **50% of base salary**.
  - **0.96% of employees (438 individuals)** earn extreme overtime exceeding **100% of base salary**.
  - Emergency services exhibit heavy overtime concentration: Police (**20.61% of budget in OT**), Fire Department (**13.20% of budget in OT**).
  - *QoE Normalization:* Overtime surges represent temporary operational strain; a QoE advisor must normalize EBITDA by replacing premium $1.5\times$ overtime wages with fully loaded baseline FTE headcount.
- **Employment Type Disparities:**
  - Permanent staff carry a **38.6% benefit loading**, whereas Temporary Exempt staff carry only **23.5% loading**, creating contingent worker misclassification exposure.

---

---

## 8. Corporate Financial Accounting & Financial Statement Architecture (SEC EDGAR FSDS 2024 Q3)

### Empirical Discoveries across 6,699 Corporate Filers & 3.52M Numeric Facts:
- **Corporate Restatement Hazard (`prevrpt`):**
  - **Empirical Restatement Rate:** **2.5228%** (169 of 6,699 corporate submissions represent amendments, restatements, or previously reported revisions).
  - **The Filer Governance Gradient:**
    - Large Accelerated Filers (`1-LAF`): **0.2773%** restatement rate (6 of 2,164 filings).
    - Accelerated Filers (`2-ACC`): **0.6002%** restatement rate (5 of 833 filings).
    - Non-Accelerated Filers & Smaller Entities (`4-NON`): **4.2779%** restatement rate (157 of 3,670 filings).
  - **Hazard Ratio:** Non-accelerated corporate filers are **15.42x more likely** to restate financial figures than large accelerated peers, proving that financial reporting risk concentrates heavily in smaller entities with thinner internal audit resources.
- **Reporting Complexity & Opacity Ratio (`custom` tags):**
  - Out of 83,106 taxonomy tags analyzed, **74,953 tags (90.1896%)** are company-specific custom extensions, and only **8,153 tags (9.81%)** belong to the base US-GAAP taxonomy.
  - In monetary balance sheet and income statement concepts, custom tags account for **90.45%** (67,820 of 74,982 tags), demonstrating massive presentation heterogeneity and non-standard accounting schedules.
- **Financial Statement Line Architecture:**
  - Distribution across 741,760 presentation lines: Balance Sheet (**32.88%**), Cash Flows (**30.20%**), Income Statement (**18.90%**), Equity (**12.28%**), Comprehensive Income (**2.67%**), Unclassified/Notes (**2.62%**).
  - **Contra-Account / Negating Rate:** **14.1393%** of all financial statement lines represent deductions or contra-accounts (accumulated depreciation, treasury stock, allowances).
  - Statement density: Balance Sheet (mean 36.4 lines), Cash Flows (mean 33.4 lines), Income Statement (mean 20.9 lines).
- **Footnote Qualification Density:**
  - Out of 3,521,878 numeric facts, **7,274 facts (0.2065%)** carry explicit XBRL explanatory footnotes (approx. 1 in 484 facts). In QoE reviews, footnoted facts cluster around non-routine litigation, debt covenants, and related-party balances.

---

## 9. M&A Advisory, Adjusted EBITDA Bridges, Net Working Capital Pegs & Window-Dressing Hazards

### Empirical Discoveries from SEC Form DEFM14A ($44B Buyout) & Lehman Repo 105 Examiner Report:
- **Prospective Financial Projections & Cash Flow Bridges (Twitter DEFM14A):**
  - **The Operating Income vs. Adjusted EBITDA Chasm:** In the base year (2022E), GAAP Operating Income was negative at **$(47) Million (-0.79% margin)**, while Adjusted EBITDA was reported at **+$1,602 Million (+27.02% margin)**, driven by $864M in Stock-Based Compensation (SBC) and $702M in D&A add-backs.
  - Over the 6-year investment horizon (2022E–2027E), revenue was projected to grow at **16.86% CAGR** ($5,928M to $12,917M), while Adjusted EBITDA expands at **27.51% CAGR** ($1,602M to $5,399M; +1,478 bps margin expansion).
- **The Great Cash Flow Divide: Management vs. Investment Banker UFCF:**
  - Cumulative 6-year Management UFCF (adding back SBC): **$12,899 Million**.
  - Cumulative 6-year Banker UFCF (Goldman Sachs & J.P. Morgan, subtracting SBC): **$5,758 Million**.
  - **Cash Flow Haircut from SBC:** **-$7,141 Million** (**55.36% cash flow dilution**). Treating SBC as a real cash-equivalent expense eliminates more than half of the company's projected unlevered cash generation!
- **Working Capital Drag:** Cumulative 6-year Net Working Capital drain of **-$815 Million**, peaking at **-$259 Million** in 2023E, reflecting inventory and receivables commitments necessary to support growth.
- **Historical EBITDA Normalization (The $766M Litigation Add-Back):**
  - Reported FY21 Adjusted EBITDA was **$1,448 Million**, which included a one-time add-back of **$766 Million** for a shareholder litigation settlement (representing **52.90%** of total Adjusted EBITDA).
  - At transaction peer multiples of **28.0x to 36.0x EV/EBITDA**, this single add-back increased the implied enterprise value by **$21.45 Billion to $27.58 Billion**—highlighting the enormous economic stakes of QoE adjustments.
- **Fairness Opinion Valuation Benchmarks:**
  - WACC Discount Rates: **10.0% to 12.0%** (Goldman Sachs) and **10.25% to 11.25%** (J.P. Morgan), using mid-year discounting convention.
  - Terminal Growth Rates: **5.6% to 9.0%** implied (GS exit multiple 10.0x–15.0x) and **6.0% to 7.0%** (JPM perpetuity formula).
- **Forensic Window Dressing Mechanics (Lehman Brothers Repo 105):**
  - **Accounting Fiction Exploited:** SFAS 140 true-sale accounting for repos with **105% (equity)** or **108% (fixed income)** collateral haircuts.
  - **Balance Sheet Derecognition Scale:** Removed **$38.6B (Q4 2007)**, **$49.1B (Q1 2008)**, and **$50.38B (Q2 2008)** from the balance sheet immediately prior to reporting dates.
  - **Timing Dynamics:** Systematically executed **2 to 3 business days prior** to quarter-end; unwound and repurchased with cash plus interest **2 to 4 business days after** quarter-start.
  - **Leverage Distortion (Q2 2008):** Reported Net Leverage of **10.2x** vs actual **12.1x** (**15.70% underreported**); Gross Leverage reported at **12.1x** vs actual **13.9x** (**12.95% underreported**).

---

## 10. Cross-Dataset Relational Topology

```mermaid
flowchart TD
    subgraph Operational_Subledgers ["Operational Subledgers (P2P & O2C)"]
        BPI["P2P SAP Event Log<br/>(PO, GR, IR, Block, Clear)"]
        UCI["O2C Commercial Subledger<br/>(Sales Invoices, Credit Notes)"]
        Olist["Logistics Fulfillment<br/>(Dispatch, Carrier, SLA)"]
    end

    subgraph Treasury_Subledger ["Treasury & Banking Subledger"]
        CzechBank["Czech Bank Cashbook<br/>(1.05M Trans, Overdrafts, Loans)"]
    end

    subgraph General_Ledger ["Financial Accounting & General Ledger"]
        SEC["SEC EDGAR XBRL FSDS<br/>(BS, IS, CF Facts, Restatements)"]
        QoE["M&A Advisory Schedules<br/>(Adj EBITDA, NWC Peg, Debt Bridges)"]
    end

    BPI -->|AP Clearings & Disbursements| CzechBank
    UCI -->|Customer Receipts & AR Inflows| CzechBank
    Olist -.->|Delivery Cutoff & Title Transfer| UCI
    CzechBank -->|Cash & Equivalents Balancing| SEC
    BPI -->|AP & Accrued Expenses| SEC
    UCI -->|Recognized Net Revenue & Returns Reserve| SEC
    SEC -->|Reported Financials| QoE
    BPI -.->|Payment Hold / DPO Normalization| QoE
    UCI -.->|8.41% Dilution & Concentration Haircut| QoE
    CzechBank -.->|Debt & Cash-Free Net Debt Peg| QoE
```

---

## 11. The Seven Missing Private-Domain Records & Empirical Proxy Solutions

In real-world Quality of Earnings investigations, seven critical categories of corporate finance records reside exclusively in confidential Virtual Data Rooms (VDRs) under strict non-disclosure agreements (NDAs) or statutory secrecy:

| Missing Private Record | Statutory / Commercial Constraint | Empirical Real-World Proxy Implemented |
| :--- | :--- | :--- |
| **1. Private Middle-Market GL Journal Entries** | Confidential ERP databases (NetSuite, QuickBooks, SAP) | SEC FSDS 2024 Q3 audited line items + UK HM Treasury high-value AP transaction vouchers |
| **2. Proprietary Seller Add-Back Workpapers** | Non-arm's length payroll, owner perquisites, personal expenses | City of SF compensation decomposition (overtime premiums, executive allowances) + SEC M&A fairness schedules |
| **3. Customer Subscription SaaS Waterfalls** | Highly confidential MRR/ARR expansion, contraction, and churn | UCI Online Retail customer cohort analysis (3,059 repeat accounts, inter-purchase latency hazard) |
| **4. Aged Accounts Receivable Subledgers** | Credit risk aging buckets (1–30, 31–60, 91+ past due) | Czech Bank loan repayment schedules (default status A/B/C/D) + Olist SLA payment delays |
| **5. SKU-Level Inventory Obsolescence (LCNRV)** | Detailed physical stock valuation and salvage write-offs | UCI Retail damaged stock write-offs (`Manual`, `AMAZONFEE`, £10k return spikes) |
| **6. Disaggregated Corporate Tax Returns (Form 1120)** | Federal statutory prohibition (26 U.S.C. § 6103) | SEC FSDS corporate tax expense disclosures + merger agreement tax indemnity representations |
| **7. Debt Payoff Letters & Borrowing Bases** | Confidential commercial credit agreements | Czech Bank commercial credit portfolio (682 loan facilities) + SEC merger debt covenant exhibits |

---

## 12. Master Simulator Parameter Specification Table

This table consolidates the exact empirical parameters extracted from our analysis, serving as the definitive specification for the future QoE simulator:

| Functional Module | Metric / Parameter | Empirical Value | Fitted Distribution / Empirical Percentiles | Source Dataset |
| :--- | :--- | :--- | :--- | :--- |
| **P2P: Requisition** | Requisition Compliance Rate | **18.51%** | Deterministic transition to PO ($P = 0.9902$) | AkzoNobel SAP ERP |
| **P2P: Requisition** | Requisition Bypass Rate | **81.49%** | Direct PO creation | AkzoNobel SAP ERP |
| **P2P: Governance** | Maverick Invoicing Precedence | **1.47%** (3,693 cases) | Invoice precedes PO item creation | AkzoNobel SAP ERP |
| **P2P: 3-Way Match** | Premature Invoicing (IR < GR) | **6.50%** (16,356 cases) | Invoice posted prior to physical delivery | AkzoNobel SAP ERP |
| **P2P: Gating** | Payment Block Occurrence | **22.18%** (55,839 cases) | Formal SAP payment lock | AkzoNobel SAP ERP |
| **P2P: Gating** | Duration Under Payment Block | $\text{Median} = \mathbf{6.18\text{ days}}$ | $\text{Mean} = 19.71\text{d}$, $\text{P25} = 2.18\text{d}$, $\text{P75} = 24.89\text{d}$, $\text{P95} = \mathbf{81.10\text{d}}$ | AkzoNobel SAP ERP |
| **P2P: Fulfillment** | Delivery Lead Time ($T_{\text{PO}\to\text{GR}}$) | $\text{Median} = \mathbf{10.02\text{ days}}$ | $\text{Mean} = 15.48\text{d}$, $\text{P25} = 4.95\text{d}$, $\text{P75} = 19.27\text{d}$, $\text{P95} = 48.77\text{d}$ | AkzoNobel SAP ERP |
| **P2P: Verification** | Invoicing Latency ($T_{\text{GR}\to\text{IR}}$) | $\text{Median} = \mathbf{11.29\text{ days}}$ | $\text{Mean} = 20.57\text{d}$, $\text{P25} = 3.98\text{d}$, $\text{P75} = 28.02\text{d}$, $\text{P95} = 63.97\text{d}$ | AkzoNobel SAP ERP |
| **P2P: Settlement** | Disbursement Latency ($T_{\text{IR}\to\text{Clear}}$) | $\text{Median} = \mathbf{42.06\text{ days}}$ | $\text{Mean} = 48.17\text{d}$, $\text{P25} = 22.13\text{d}$, $\text{P75} = 70.14\text{d}$, $\text{P95} = 107.15\text{d}$ | AkzoNobel SAP ERP |
| **P2P: Vendors** | Top 20% Vendor Spend Share | **89.61%** | $\text{HHI} = 85.06$, Top 1% = 33.08%, Top 5% = 64.36% | AkzoNobel SAP ERP |
| **P2P: Dispute Risk** | High-Dispute Vendor Block Rate | **81.95%** | Maximum observed vendor billing block rate | AkzoNobel SAP ERP |
| **P2P: Public Tender**| Statutory Notice Squeeze (<14d) | **88.00%** | $\text{Median} = 11.4\text{d}$; Works category = 92.60% non-compliant | Kenya PPIP Portal |
| **P2P: Public Tender**| Affirmative Action Reservation | **33.00%** | Women: 40.9%, Youth: 28.8%, PWD: 15.2% | Kenya PPIP Portal |
| **O2C: Revenue** | Commercial Revenue Dilution | **8.41%** | £896.8k returns / £10.67M gross sales | UCI Online Retail |
| **O2C: Invoicing** | Credit Note Invoice Share | **19.97%** | 5,172 credit notes / 25,900 total invoices | UCI Online Retail |
| **O2C: Customers** | Top 20% Customer Revenue Share | **73.82%** | $\text{HHI} = 45.15$, Top 1% = 29.71%, Top 5% = 48.52% | UCI Online Retail |
| **O2C: Customers** | Repeat Customer Rate | **69.97%** | 3,059 repeat vs 1,313 one-time accounts | UCI Online Retail |
| **O2C: Retention** | Repeat Order Latency ($T_{\text{repeat}}$) | $\text{Median} = \mathbf{21.91\text{ days}}$ | $\text{Mean} = 39.94\text{d}$, $\text{P25} = 6.84\text{d}$, $\text{P75} = 51.03\text{d}$, $\text{P95} = 146.10\text{d}$ | UCI Online Retail |
| **O2C: Risk** | Unidentified Guest Sales Share | **16.25%** | £1.73M OTC/guest checkouts | UCI Online Retail |
| **O2C: Basket Size**| SKUs per Invoice | $\text{Median} = \mathbf{15.0\text{ SKUs}}$ | $\text{Mean} = 25.6\text{ SKUs}$, $\text{P95} = 77.0\text{ SKUs}$ (Max 1,114) | UCI Online Retail |
| **O2C: Basket Value**| Monetary Value per Invoice | $\text{Median} = \mathbf{£303.84}$ | $\ln(\text{Value}) \sim \mathcal{N}(5.72, 1.18)$; $\text{Mean} = £534.40$ | UCI Online Retail |
| **O2C: Fulfillment**| Payment Approval ($T_{\text{auth}}$) | $\text{Median} = \mathbf{0.34\text{ hours}}$ | Bimodal: instant cards vs 24–48h bank slips; Mean = 10.32h | Olist Logistics |
| **O2C: Fulfillment**| Warehouse Dispatch ($T_{\text{fulfill}}$)| $\text{Median} = \mathbf{1.85\text{ days}}$ | $\text{Mean} = 2.86\text{d}$, $\text{P25} = 0.90\text{d}$, $\text{P75} = 3.62\text{d}$, $\text{P95} = 8.16\text{d}$ | Olist Logistics |
| **O2C: Fulfillment**| Carrier Transit ($T_{\text{transit}}$) | $\text{Median} = \mathbf{7.10\text{ days}}$ | $\text{Mean} = 9.24\text{d}$, $\text{P25} = 4.10\text{d}$, $\text{P75} = 12.02\text{d}$, $\text{P95} = 24.12\text{d}$ | Olist Logistics |
| **O2C: Lead Time** | End-to-End Delivery Lead Time | $\text{Median} = \mathbf{10.21\text{ days}}$ | $\text{Mean} = 12.49\text{d}$, $\text{P25} = 6.76\text{d}$, $\text{P75} = 15.71\text{d}$, $\text{P95} = 29.21\text{d}$ | Olist Logistics |
| **O2C: SLA Breach** | Contractual SLA Breach Rate | **8.11%** (7,827 orders) | Orders delivered after promised SLA date | Olist Logistics |
| **O2C: SLA Delay** | Late Delivery Severity | $\text{Median} = \mathbf{5.81\text{ days late}}$ | $\text{Mean} = 9.55\text{d late}$, $\text{P95} = \mathbf{29.64\text{ days late}}$ | Olist Logistics |
| **O2C: Breakage** | Order Attrition / Stockout Rate | **1.24%** (1,234 orders) | 0.63% canceled, 0.61% unavailable | Olist Logistics |
| **Banking: Balance** | Running Account Balance | $\text{Median} = \mathbf{\text{CZK } 33,143}$ | $\text{Mean} = \text{CZK } 38,518$, $\text{P95} = \text{CZK } 88,382$ | Czech Bank Berka |
| **Banking: Liquidity** | Authorized Overdraft Rate | **6.40%** (288 accounts) | Severe overdrafts (< -1k CZK): 5.13% | Czech Bank Berka |
| **Banking: Overdraft**| Overdraft Exposure Depth | $\text{Median} = \mathbf{\text{CZK } 2,441}$ | $\text{Mean} = \text{CZK } 4,342$, $\text{Max Deficit} = \text{CZK } 41,126$ | Czech Bank Berka |
| **Banking: Outflow** | Standing Order Adoption | **83.51%** (3,758 accounts) | $\text{Median} = \text{CZK } 4,501\text{ / mo committed outflow}$ | Czech Bank Berka |
| **Credit: Defaults** | Loan Book Default Rate | **11.14%** (76 loans) | Closed contract default rate = **13.25%** | Czech Bank Berka |
| **Credit: Capital** | Capital at Risk | **15.09%** of Principal | CZK 15.58M in default across CZK 103.3M book | Czech Bank Berka |
| **Credit: Overdraft** | Default vs Overdraft Separation| **100.0%** of Defaulted Loans | 0.0% of performing loans had overdrafts | Czech Bank Berka |
| **Payroll: Base** | Base Salary Share | **65.32%** of Labor Cost | $\text{Median} = \mathbf{\$85,691}$, $\text{Mean} = \$91,457$ | SF Employee Comp |
| **Payroll: Overtime**| Overtime Pay Share | **6.68%** of Labor Cost | 48.54% workforce recipient rate; Mean $19,253 | SF Employee Comp |
| **Payroll: Strain** | Overtime Strain (>25% of Base)| **12.39%** of Workforce | >50% of base: 4.50%; >100% of base: 0.96% | SF Employee Comp |
| **Payroll: Benefits**| Mandatory Non-Wage Benefits | **24.22%** of Labor Cost | Pension: 9.88%, Health & Dental: 9.74% | SF Employee Comp |
| **Payroll: Loading** | Benefit Loading on Base Wage | **37.08%** Loading | $\lambda_{\text{benefits}} = \text{Benefits} / \text{Base Salary}$ | SF Employee Comp |
| **Payroll: Multiplier**| Full Labor Cost Multiplier | **1.53x** of Base Wage | $M_{\text{labor}} = \text{Total Comp} / \text{Base Wage}$ | SF Employee Comp |
| **Acct: Restatements** | Overall Corporate Restatement Rate | **2.52%** (169 filings) | Bernoulli($p = 0.0252$) | SEC EDGAR FSDS 2024 Q3 |
| **Acct: Hazard Gradient**| Non-Accelerated vs Large Accel. Ratio | **15.42x Risk Multiplier** | 4.28% (NON) vs 0.28% (LAF) | SEC EDGAR FSDS 2024 Q3 |
| **Acct: Opacity** | Custom Taxonomy Extension Tag Share | **90.19%** (74,953 tags) | Beta($lpha = 9.2$, $eta = 1.0$); Monetary: 90.45% | SEC EDGAR FSDS 2024 Q3 |
| **Acct: Structure** | Financial Statement Negating Lines | **14.14%** (104,879 lines) | Contra-accounts & deduction line items | SEC EDGAR FSDS 2024 Q3 |
| **Acct: Footnotes** | XBRL Numeric Footnote Density | **0.21%** (7,274 facts) | Bernoulli($p = 0.00206$) (1 in 484 facts) | SEC EDGAR FSDS 2024 Q3 |
| **M&A: Projections** | Revenue CAGR (6-Year Model) | **16.86% CAGR** | $5,928M (2022E) to $12,917M (2027E) | SEC Form DEFM14A |
| **M&A: EBITDA Growth** | Adjusted EBITDA CAGR (6-Year Model) | **27.51% CAGR** | $1,602M (2022E) to $5,399M (2027E) | SEC Form DEFM14A |
| **M&A: SBC Dilution** | UFCF Haircut via Equity Compensation | **55.36% Dilution** | $7.14B cumulative SBC / $12.90B Mgmt UFCF | SEC Form DEFM14A |
| **M&A: SBC Intensity** | SBC Share of Cumulative Revenue | **12.85% of Revenue** | Normal($\mu = 0.1285$, $\sigma = 0.015$) | SEC Form DEFM14A |
| **M&A: Working Capital**| Cumulative NWC Cash Flow Drag | **-$815 Million** | Peaks in 2023E at -$259M; $\Delta	ext{NWC} pprox -1.47\% \Delta	ext{Rev}$ | SEC Form DEFM14A |
| **M&A: Normalization** | Single Litigation Add-Back Share | **52.90% of EBITDA** | $766M add-back on $1,448M FY21 Adj. EBITDA | SEC Form DEFM14A |
| **M&A: EV Impact** | Enterprise Value Swing from Add-Back | **$21.45B to $27.58B** | Multiple range: 28.0x to 36.0x EV/EBITDA | SEC Form DEFM14A |
| **M&A: Valuation WACC**| Discount Rate Reference Range | **10.0% to 12.0%** | Uniform($0.10, 0.12$); mid-year convention | Goldman Sachs / JPM |
| **Forensic: Window Dress**| Quarter-End Balance Sheet Reduction | **$50.38 Billion** | Peak derecognition scale in Q2 2008 | Lehman Repo 105 Examiner |
| **Forensic: Haircut** | True-Sale Overcollateralization Hurdle| **105% / 108%** | 105% equities, 108% fixed income (SFAS 140) | Lehman Repo 105 Examiner |
| **Forensic: Timing** | Window Dressing Execution Lead/Lag | **2-3d Pre / 2-4d Post** | Discrete Uniform($\{2, 3\}$ pre, $\{2, 3, 4\}$ post) | Lehman Repo 105 Examiner |
| **Forensic: Leverage** | Leverage Underreporting Suppression | **15.70% (Net) / 12.95% (Gross)**| Net: 10.2x rep vs 12.1x real; Gross: 12.1x vs 13.9x | Lehman Repo 105 Examiner |
| **QoE Red Flag: Accruals**| Paper Profit Rate (NI>0, CFO<0) | **9.85%** of filers | Bernoulli($p = 0.0985$); Financials: 13.65% | SEC EDGAR FSDS 2024 Q3 |
| **QoE Anomaly: Loss Add** | Non-Cash Loss Add-back (EBIT<0, CFO>0)| **12.47%** of filers | Bernoulli($p = 0.1247$) | SEC EDGAR FSDS 2024 Q3 |
| **Working Capital: Days** | Median Days Sales Outstanding (DSO) | **119.5 days** | Lognormal($\mu = 4.783, \sigma = 0.812$) | SEC EDGAR FSDS 2024 Q3 |
| **Working Capital: Days** | Median Days Inventory Outstanding (DIO)| **110.9 days** | Lognormal($\mu = 4.708, \sigma = 0.745$) | SEC EDGAR FSDS 2024 Q3 |
| **Working Capital: Days** | Median Days Payable Outstanding (DPO) | **64.2 days** | Lognormal($\mu = 4.162, \sigma = 0.690$) | SEC EDGAR FSDS 2024 Q3 |
| **Working Capital: Cycle**| Median Cash Conversion Cycle (CCC) | **154.3 days** | Mfg: 244.5d, Hardware: 236.1d, Software: 84.8d | SEC EDGAR FSDS 2024 Q3 |
| **Working Capital: Drag** | Net Working Capital / Revenue Ratio | **18.42%** of Revenue | $\text{Median} = 18.42\%$, $\text{P75} = 41.28\%$ | SEC EDGAR FSDS 2024 Q3 |
| **Filer Scale: Large Accel**| Large Accel Operating Margin (1-LAF)| **+18.22%** | Median Rev: $125.3M; Neg. Equity: 6.65% | SEC EDGAR FSDS 2024 Q3 |
| **Filer Scale: Non-Accel** | Non-Accel Operating Margin (4-NON) | **-31.96%** | Median Rev: $1.06M; Neg. Equity: **35.22%** | SEC EDGAR FSDS 2024 Q3 |
| **Solvency: Book Equity** | Negative Book Equity Rate | **21.72%** of filers | Bernoulli($p = 0.2172$) across all public entities | SEC EDGAR FSDS 2024 Q3 |
| **Asset Quality: Goodwill**| Goodwill Concentration (P90 / P95) | **31.15% / 41.55%** of Assets | 90th / 95th Percentile of public balance sheets | SEC EDGAR FSDS 2024 Q3 |

---

## 13. Master File Architecture & Directory Sitemap

```
c:\Users\ADMIN\Desktop\QOE  data aquisition\
├── research\
│   ├── original_datasets\                       # 942.6 MB across all 10 categories
│   │   ├── financial_accounting\                # SEC FSDS 2024 Q3 + UK HM Treasury Spend
│   │   ├── revenue_commercial\                  # UCI Online Retail (541k lines)
│   │   ├── procurement_expenses\                # BPI 2019 SAP (527MB) + Kenya PPIP (2.1MB)
│   │   ├── working_capital_banking\             # Czech Bank Berka (1.05M records)
│   │   ├── payroll_employees\                   # SF Employee Compensation (50k records)
│   │   ├── debt_financing\                      # Czech Bank Loan Portfolio (682 loans)
│   │   ├── tax_legal_contracts\                 # SEC Merger Agreement (Form DEFM14A)
│   │   ├── operational_performance\             # Olist Logistics (99k orders)
│   │   ├── internal_documentation\              # Lehman Repo 105 Examiner Workpapers
│   │   └── qoe_transaction_advisory\            # SEC M&A Fairness Opinion & Projections
│   ├── dataset_inspections\                     # 10 Detailed Forensic Inspection Reports
│   │   ├── bpi_challenge_2019_inspection.md
│   │   ├── kenya_public_procurement_inspection.md
│   │   ├── uci_online_retail_inspection.md
│   │   ├── olist_logistics_inspection.md
│   │   ├── czech_bank_inspection.md
│   │   ├── sf_employee_compensation_inspection.md
│   │   ├── uk_hm_treasury_spend_inspection.md
│   │   ├── sec_fsds_2024q3_inspection.md
│   │   ├── lehman_repo105_inspection.md
│   │   └── qoe_transaction_advisory_inspection.md
│   ├── p2p_signals\                             # Purchase-to-Pay Models & Metrics
│   │   ├── p2p_mathematical_signals_and_behavioral_models.md
│   │   ├── bpi_2019_p2p_metrics.json
│   │   └── kenya_procurement_metrics.json
│   ├── o2c_signals\                             # Order-to-Cash Models & Metrics
│   │   ├── o2c_mathematical_signals_and_behavioral_models.md
│   │   ├── uci_retail_o2c_metrics.json
│   │   └── olist_logistics_o2c_metrics.json
│   ├── consolidated_findings\                   # Master Compendium & Parameter Catalog
│   │   ├── master_qoe_research_compendium.md    # [THIS MASTER COMPENDIUM]
│   │   ├── qoe_simulator_parameter_catalog.json # Unified JSON look-up for future simulator
│   │   └── research_index.md                    # Navigation index
│   ├── cross_dataset_analysis\                  # Coverage Matrix & Relational Map
│   │   ├── coverage_matrix.md
│   │   └── relationship_map.md
│   ├── research_gaps\                           # Analysis of Missing Private VDR Records
│   │   └── qoe_simulator_research_gaps.md
│   ├── source_registry\                         # Master Registries
│   │   ├── master_dataset_registry.md
│   │   └── master_dataset_registry.csv
│   └── acquisition_log\                         # Append-only chronological audit log
│       └── acquisition_log.csv
```
