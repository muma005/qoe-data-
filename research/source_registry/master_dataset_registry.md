# Master Dataset Registry: 100% Physical Acquisition Across All 10 Categories

This registry documents all acquired and verified real-world datasets across the ten Quality of Earnings operational and financial categories. **Every single category is backed by physical files residing in `research/original_datasets/`.**

## Summary Table
| Category | Dataset Name | Classification | Records / Footprint | Tier | Status |
|---|---|---|---|---|---|
| **Cat 1** | SEC EDGAR Financial Statement Data Sets (2024 Q3) | `Real-world, Identifiable` | 6,699 filings | Millions of numerical facts (498 MB) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 2** | UCI Online Retail Dataset | `Real-world, Anonymized` | 541,909 sales records (48.5 MB CSV) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 3** | BPI Challenge 2019 (AkzoNobel SAP ERP Event Log) | `Real-world, Anonymized` | 1,595,923 events | 251,734 PO cases | €996.8M spend (527.5 MB CSV) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 3 (Add)** | Kenyan Public Procurement Information Portal (PPIP) | `Real-world, Identifiable` | 200 sovereign tenders | 41 procuring entities | 38 attributes (2.16 MB) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 3 (Gov)** | UK HM Treasury Procurement & AP Voucher Register | `Real-world, Identifiable` | 132 detailed high-value vouchers (>£25k) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 4** | Czech Bank Berka Relational Database | `Real-world, Anonymized` | 1,056,320 transaction records (62.9 MB CSV) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 5** | City of San Francisco Employee Compensation Register | `Real-world, Anonymized ID / Identifiable Title` | 50,000 employee compensation records (17.7 MB) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 6** | Czech Bank Commercial & Personal Loan Portfolio | `Real-world, Anonymized` | 682 loan facilities | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 7** | SEC EDGAR Material M&A Agreement (Annex A: Plan of Merger) | `Real-world, Identifiable` | Full legal transaction agreement (1.87 MB) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 8** | Brazilian E-Commerce (Olist) Order Fulfillment & Logistics | `Real-world, Anonymized` | 99,441 commercial orders (17.6 MB CSV) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 9** | Lehman Brothers Bankruptcy Examiner Report Vol 3 (Repo 105) | `Real-world, Identifiable` | Forensic findings & executive memos | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |
| **Cat 10** | SEC Form DEFM14A Financial Advisor Diligence & Projections | `Real-world, Identifiable` | Official M&A proxy & fairness presentation (1.87 MB) | **Tier A — Priority** | `Acquired & Inspected (On Disk)` |

## Detailed Inventory Profiles Across All 10 Categories

### Cat 1: SEC EDGAR Financial Statement Data Sets (2024 Q3)
- **Category:** Category 1: Financial Accounting & General Ledger
- **Physical Path:** `research/original_datasets/financial_accounting/sec_fsds_2024q3/`
- **Classification:** `Real-world, Identifiable`
- **Quality Tier:** `Tier A — Priority` (Score: 39/40)
- **Originating Source:** U.S. Securities and Exchange Commission (DERA)
- **Record Count & Format:** 6,699 filings | Millions of numerical facts (498 MB) (TSV (sub.txt, num.txt, tag.txt, pre.txt))
- **Granularity:** Financial statement line item & footnote fact level
- **Operational Substance:** Audited US-GAAP balance sheets, income statements, cash flows, tag taxonomy, and restatement flags (prevrpt = 1).
---

### Cat 2: UCI Online Retail Dataset
- **Category:** Category 2: Revenue and Commercial Activity
- **Physical Path:** `research/original_datasets/revenue_commercial/uci_online_retail/`
- **Classification:** `Real-world, Anonymized`
- **Quality Tier:** `Tier A — Priority` (Score: 36/40)
- **Originating Source:** UCI Machine Learning Repository / UK Wholesaler
- **Record Count & Format:** 541,909 sales records (48.5 MB CSV) (XLSX / CSV)
- **Granularity:** Invoice SKU line item level
- **Operational Substance:** Customer concentration, bulk volume discounting, unit prices, product descriptions, and 8,905 credit note cancellations ('C' invoices).
---

### Cat 3A: BPI Challenge 2019 (AkzoNobel SAP ERP Event Log)
- **Category:** Category 3: Procurement, Suppliers & Operating Expenses
- **Physical Path:** `research/original_datasets/procurement_expenses/bpi_2019/BPI_Challenge_2019.csv`
- **Classification:** `Real-world, Anonymized`
- **Quality Tier:** `Tier A — Priority` (Score: 40/40)
- **Originating Source:** AkzoNobel / 4TU.ResearchData / Eindhoven University of Technology
- **Record Count & Format:** 1,595,923 events | 251,734 PO items | 76,349 POs | 1,975 vendors | €996.8M spend (527.5 MB CSV)
- **Granularity:** Line-item transaction event level with millisecond timestamps
- **Operational Substance:** Production SAP MM / FI-AP event log across 4 operating subsidiaries. Complete 3-way matching, payment block dynamics (22.18% block rate), retroactive price/quantity revisions, requisition bypasses (81.49%), and maverick buying (1.47%).
---

### Cat 3B: Kenyan Public Procurement Information Portal (PPIP) Active Tenders
- **Category:** Category 3: Procurement, Suppliers & Operating Expenses
- **Physical Path:** `research/original_datasets/procurement_expenses/kenya_procurement/`
- **Classification:** `Real-world, Identifiable`
- **Quality Tier:** `Tier A — Priority` (Score: 38/40)
- **Originating Source:** Public Procurement Regulatory Authority (PPRA), Republic of Kenya (`https://tenders.go.ke/api/active-tenders`)
- **Record Count & Format:** 200 sovereign tenders | 41 procuring entities | 38 attributes (2.16 MB JSON + CSV)
- **Granularity:** Sovereign tender notice, specification, and evaluation milestone level
- **Operational Substance:** Statutory advertising notice compliance (88.0% <14d notice squeeze), AGPO affirmative action reservations (33.0%), pay-to-bid barrier fees (7.0%), specification addenda volatility (5.0%), and county procuring entity concentration.
---

### Cat 3C: UK HM Treasury Procurement & AP Voucher Register
- **Category:** Category 3: Procurement, Suppliers & Operating Expenses
- **Physical Path:** `research/original_datasets/procurement_expenses/hm_treasury_procurement_vouchers.csv`
- **Classification:** `Real-world, Identifiable`
- **Quality Tier:** `Tier A — Priority` (Score: 35/40)
- **Originating Source:** UK HM Treasury / Cabinet Office
- **Record Count & Format:** 132 detailed high-value vouchers (>£25k) (CSV)
- **Granularity:** Accounts payable voucher transaction level
- **Operational Substance:** Specific corporate vendor names (Atos, E&Y), unique transaction numbers, expense types, and narrative descriptions.
---

### Cat 4: Czech Bank Berka Relational Database
- **Category:** Category 4: Working Capital, Cash and Banking
- **Physical Path:** `research/original_datasets/working_capital_banking/czech_bank/`
- **Classification:** `Real-world, Anonymized`
- **Quality Tier:** `Tier A — Priority` (Score: 40/40)
- **Originating Source:** Czech Commercial Bank (PKDD'99)
- **Record Count & Format:** 1,056,320 transaction records (62.9 MB CSV) (CSV across 8 relational tables)
- **Granularity:** Cashbook / bank account transaction level
- **Operational Substance:** Exact daily cash movements, running balances, authorized overdraft indicators, interest credits, service fees, and standing orders.
---

### Cat 5: City of San Francisco Employee Compensation Register
- **Category:** Category 5: Payroll, Employees & Operating Structure
- **Physical Path:** `research/original_datasets/payroll_employees/sf_employee_compensation/`
- **Classification:** `Real-world, Anonymized ID / Identifiable Title`
- **Quality Tier:** `Tier A — Priority` (Score: 35/40)
- **Originating Source:** City and County of San Francisco Controller
- **Record Count & Format:** 50,000 employee compensation records (17.7 MB) (CSV)
- **Granularity:** Employee annual compensation record
- **Operational Substance:** Decomposed labor cost: base salaries, overtime premiums, other pay, retirement contributions, and healthcare benefits (34.8% loading).
---

### Cat 6: Czech Bank Commercial & Personal Loan Portfolio
- **Category:** Category 6: Debt, Financing & Financial Obligations
- **Physical Path:** `research/original_datasets/debt_financing/czech_bank_loans/loan.csv`
- **Classification:** `Real-world, Anonymized`
- **Quality Tier:** `Tier A — Priority` (Score: 39/40)
- **Originating Source:** Czech Commercial Bank
- **Record Count & Format:** 682 loan facilities (CSV)
- **Granularity:** Credit facility & repayment schedule level
- **Operational Substance:** Principal amounts, term durations, monthly debt service payments, and loan default performance status (A/B/C/D).
---

### Cat 7: SEC EDGAR Material M&A Agreement (Annex A: Plan of Merger)
- **Category:** Category 7: Tax, Legal & Contractual Records
- **Physical Path:** `research/original_datasets/tax_legal_contracts/sec_merger_agreement_exhibit.htm`
- **Classification:** `Real-world, Identifiable`
- **Quality Tier:** `Tier A — Priority` (Score: 36/40)
- **Originating Source:** SEC EDGAR / Twitter, Inc. (CIK 0001418091)
- **Record Count & Format:** Full legal transaction agreement (1.87 MB) (HTML)
- **Granularity:** Contractual clause level
- **Operational Substance:** Authentic legal definitions: working capital adjustments, MAE clauses, representations & warranties, closing conditions, and debt covenants.
---

### Cat 8: Brazilian E-Commerce (Olist) Order Fulfillment & Logistics
- **Category:** Category 8: Operational & Commercial Performance
- **Physical Path:** `research/original_datasets/operational_performance/olist_orders_dataset.csv`
- **Classification:** `Real-world, Anonymized`
- **Quality Tier:** `Tier A — Priority` (Score: 38/40)
- **Originating Source:** Olist Marketplace Platform
- **Record Count & Format:** 99,441 commercial orders (17.6 MB CSV) (CSV)
- **Granularity:** Order milestone event level
- **Operational Substance:** Exact operational timestamps: purchase, payment approval, carrier handover, actual customer delivery, and estimated delivery dates.
---

### Cat 9: Lehman Brothers Bankruptcy Examiner Report Vol 3 (Repo 105)
- **Category:** Category 9: Internal Documentation & Communications
- **Physical Path:** `research/original_datasets/internal_documentation/lehman_repo105_forensic_examiner_findings.txt`
- **Classification:** `Real-world, Identifiable`
- **Quality Tier:** `Tier A — Priority` (Score: 34/40)
- **Originating Source:** U.S. Bankruptcy Court SDNY / Jenner & Block LLP
- **Record Count & Format:** Forensic findings & executive memos (Text / Workpaper Record)
- **Granularity:** Accounting policy & internal directive level
- **Operational Substance:** Unprecedented real-world documentation of balance sheet window-dressing, CFO balance sheet reduction targets, and Net Debt manipulation.
---

### Cat 10: SEC Form DEFM14A Financial Advisor Diligence & Projections
- **Category:** Category 10: QoE & Transaction Advisory Evidence
- **Physical Path:** `research/original_datasets/qoe_transaction_advisory/sec_defm14a_financial_projections_and_fairness.htm`
- **Classification:** `Real-world, Identifiable`
- **Quality Tier:** `Tier A — Priority` (Score: 36/40)
- **Originating Source:** SEC EDGAR (Goldman Sachs & J.P. Morgan Opinions)
- **Record Count & Format:** Official M&A proxy & fairness presentation (1.87 MB) (HTML)
- **Granularity:** Transaction advisory schedule level
- **Operational Substance:** Authentic M&A diligence schedules: Adjusted EBITDA projections, Unlevered Free Cash Flow bridges, and Net Working Capital changes.
---