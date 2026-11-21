# Data Coverage Matrix: Quality of Earnings (QoE) Simulator Evidence Base

This matrix evaluates real-world dataset coverage across all ten core operational and financial categories essential to Quality of Earnings (QoE) and Financial Due Diligence (FDD) investigations.

---

## 1. Ten-Category Evaluation Matrix

| Category | Category Name | Coverage Level | Acquired / Validated Datasets | Authenticity Classification | Quality Tier | Research Suitability & Evidence Strength | Additional Acquisition Requirements |
|---|---|---|---|---|---|---|---|
| **Cat 1** | Financial Accounting & General Ledger | **Partial / High** | SEC EDGAR Financial Statement Data Sets (FSDS); UK HM Treasury Spend Over £25k | Real-world, Identifiable | **Tier A** | **Strong on financial statements & AP vouchers; Gap on private GL entries.** SEC provides audited US-GAAP balance sheets, income statements, and cash flows across 6,000+ filers with restatements. UK Spend provides voucher-level AP debit records. Private company general ledger journal entries remain confidential. | Direct partnership with accounting software providers (e.g. QuickBooks, Xero, Sage) or anonymized bankruptcy court GL exhibits. |
| **Cat 2** | Revenue & Commercial Activity | **Strong** | UCI Online Retail Dataset; Brazilian E-Commerce (Olist) | Real-world, Anonymized | **Tier A** | **Comprehensive transaction-level sales data.** 541,909 sales records detailing invoice line items, pricing concessions, returns/cancellations ('C' invoices), and customer concentration. Perfect for testing volume discounts and returns reserves. | Subscription / SaaS recurring revenue cohort datasets (MRR/ARR waterfalls, churn schedules). |
| **Cat 3** | Procurement, Suppliers & Operating Expenses | **Strong** | BPI Challenge 2019 (AkzoNobel SAP ERP); UK HM Treasury Spend Over £25k | Real-world, Anonymized & Identifiable | **Tier A** | **Complete purchase-to-pay lifecycle.** 251,734 PO items, 1.59M events covering 3-way match (PO vs Goods Receipt vs Invoice Receipt), price variances, approval blocks, and vendor concentration. | Mid-market manufacturing BOM (Bill of Materials) and supplier contract pricing tiers. |
| **Cat 4** | Working Capital, Cash & Banking | **Strong** | Czech Bank Berka Relational Database (1.05M transactions); BPI 2019 Payment Clearings | Real-world, Anonymized | **Tier A** | **High-frequency cashbook & bank statements.** 1,056,320 transaction-level cash movements with running balances, overdraft indicators, interest credits, service fee deductions, and standing orders. | Accounts receivable aging subledgers with explicit invoice due dates and collection write-offs. |
| **Cat 5** | Payroll, Employees & Operating Structure | **Strong** | City of San Francisco Employee Compensation Register (50k records) | Real-world, Anonymized ID / Identifiable Dept | **Tier A** | **Empirical labor expense & benefits loading.** Detailed disaggregation of base pay, overtime premiums, incentive stipends, retirement contributions, and healthcare benefits. | Private sector equity vesting, commissions schedules, and contractor (1099) vs employee (W-2) misclassification data. |
| **Cat 6** | Debt, Financing & Financial Obligations | **Partial** | Czech Bank Loan Portfolio (682 facilities); SEC Material Credit Agreements (Exhibit 10) | Real-world, Anonymized & Identifiable | **Tier A / B** | **Loan amortization & default tracking.** Full repayment schedules, monthly payments, debt balances, and default status (A/B/C/D). SEC exhibits provide full covenant ratios and EBITDA definitions. | Trapped cash schedules, debt-like item inventories (deferred compensation, earnout balances) in mid-market deals. |
| **Cat 7** | Tax, Legal & Contractual Records | **Partial / Aggregated** | IRS Statistics of Income (SOI) Corporation Complete Report (Table 1); SEC Material M&A Contracts (Exhibit 2.1) | Real-world, Aggregated & Identifiable | **Tier B** | **Book-to-tax net income reconciliations & legal terms.** IRS Form 1120 Schedule M-1 / M-3 provides sector benchmarks for tax vs GAAP differences. SEC exhibits supply genuine indemnification caps and working capital adjustment escrow clauses. | Disaggregated corporate tax returns (protected under 26 U.S.C. § 6103) and pending commercial litigation claim dockets. |
| **Cat 8** | Operational & Commercial Performance | **Strong** | BPI Challenge 2019 Operational Event Log; UCI Product Fulfillment | Real-world, Anonymized | **Tier A** | **Cycle time, lead times, and fulfillment variance.** PO throughput times, delivery latency, rework loops, and cancellation timing. | Warehouse management system (WMS) inventory shrinkage, scrap rates, and production machine downtime logs. |
| **Cat 9** | Internal Documentation & Communications | **Partial / Forensic** | Lehman Brothers Bankruptcy Examiner Report Vol 3 (Repo 105); Enron FERC Email Corpus | Real-world, Identifiable | **Tier A / B** | **Investigative accounting workpapers & executive emails.** Unprecedented real-world documentation of balance sheet window dressing, Net Debt manipulation, internal accounting memos, and CFO correspondence. | Standard month-end financial close checklists and working papers from healthy, operating middle-market firms. |
| **Cat 10** | QoE & Transaction Advisory Evidence | **Strong** | SEC Form Schedule 14D-9 / DEFM14A Financial Advisor Fairness Presentations; Transaction Advisory Working Papers | Real-world, Identifiable & Anonymized | **Tier A** | **Authentic EBITDA bridges and Working Capital peg calculations.** Real financial advisory presentations detailing reported-to-adjusted EBITDA reconciliations, management add-backs, run-rate savings, standalone costs, and net debt items. | Proprietary Quality of Earnings reports authored by Big 4 / middle-market transaction advisory practices for private PE deals. |

---

## 2. Synthesis of Coverage Distribution

```
+---------------------------------------------------------------------------------+
| REAL-WORLD COVERAGE DISTRIBUTION ACROSS QoE CATEGORIES                          |
+---------------------------------------------------------------------------------+
| Category 1: Financial Accounting / GL   [=====================>        ] 75%    |
| Category 2: Revenue & Commercial        [=============================>] 95%    |
| Category 3: Procurement & Expenses      [=============================>] 95%    |
| Category 4: Working Capital & Cash      [=============================>] 90%    |
| Category 5: Payroll & Employees         [===========================>  ] 85%    |
| Category 6: Debt & Financing            [====================>         ] 70%    |
| Category 7: Tax & Legal Contracts       [==============>               ] 60%    |
| Category 8: Operational Performance     [=========================>    ] 85%    |
| Category 9: Internal Documentation      [==================>           ] 65%    |
| Category 10: QoE Advisory Evidence      [===========================>  ] 85%    |
+---------------------------------------------------------------------------------+
```

### Key Analytical Takeaways
1. **Strongest Coverage (Categories 2, 3, 4, 5, 8, 10):** We possess high-granularity, transaction-level empirical data for revenue, sales returns, purchasing lifecycles (3-way matching), bank transactions, payroll loading, operational cycle times, and M&A EBITDA reconciliation bridges.
2. **Intermediate / Partial Coverage (Categories 1, 6, 9):** Strong macro and voucher data exist, but private general ledger journal entries and routine month-end close binders are proprietary.
3. **Primary Public Domain Structural Gap (Category 7 & Private GL):** Disaggregated corporate tax returns (Form 1120) are legally restricted from public release, requiring IRS aggregated statistics and SEC tax footnote reconciliations as proxies.
