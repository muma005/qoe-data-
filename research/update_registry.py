"""
Updated Master Dataset Registry Generator
=========================================
Reflects 100% physical file acquisition across all 10 categories (898.96 MB on disk).
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def update_master_registry():
    registry_data = [
        {
            "category_id": "Cat 1",
            "dataset_name": "SEC EDGAR Financial Statement Data Sets (2024 Q3)",
            "category": "Category 1: Financial Accounting & General Ledger",
            "physical_path": "research/original_datasets/financial_accounting/sec_fsds_2024q3/",
            "source_institution": "U.S. Securities and Exchange Commission (DERA)",
            "authenticity_class": "Real-world, Identifiable",
            "record_count": "6,699 filings | Millions of numerical facts (498 MB)",
            "file_formats": "TSV (sub.txt, num.txt, tag.txt, pre.txt)",
            "granularity": "Financial statement line item & footnote fact level",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 39,
            "operational_value": "Audited US-GAAP balance sheets, income statements, cash flows, tag taxonomy, and restatement flags (prevrpt = 1)."
        },
        {
            "category_id": "Cat 2",
            "dataset_name": "UCI Online Retail Dataset",
            "category": "Category 2: Revenue and Commercial Activity",
            "physical_path": "research/original_datasets/revenue_commercial/uci_online_retail/",
            "source_institution": "UCI Machine Learning Repository / UK Wholesaler",
            "authenticity_class": "Real-world, Anonymized",
            "record_count": "541,909 sales records (48.5 MB CSV)",
            "file_formats": "XLSX / CSV",
            "granularity": "Invoice SKU line item level",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 36,
            "operational_value": "Customer concentration, bulk volume discounting, unit prices, product descriptions, and 8,905 credit note cancellations ('C' invoices)."
        },
        {
            "category_id": "Cat 3",
            "dataset_name": "UK HM Treasury Procurement & AP Voucher Register",
            "category": "Category 3: Procurement, Suppliers & Operating Expenses",
            "physical_path": "research/original_datasets/procurement_expenses/hm_treasury_procurement_vouchers.csv",
            "source_institution": "UK HM Treasury / Cabinet Office",
            "authenticity_class": "Real-world, Identifiable",
            "record_count": "132 detailed high-value vouchers (>£25k)",
            "file_formats": "CSV",
            "granularity": "Accounts payable voucher transaction level",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 35,
            "operational_value": "Specific corporate vendor names (Atos, E&Y), unique transaction numbers, expense types, and narrative descriptions."
        },
        {
            "category_id": "Cat 4",
            "dataset_name": "Czech Bank Berka Relational Database",
            "category": "Category 4: Working Capital, Cash and Banking",
            "physical_path": "research/original_datasets/working_capital_banking/czech_bank/",
            "source_institution": "Czech Commercial Bank (PKDD'99)",
            "authenticity_class": "Real-world, Anonymized",
            "record_count": "1,056,320 transaction records (62.9 MB CSV)",
            "file_formats": "CSV across 8 relational tables",
            "granularity": "Cashbook / bank account transaction level",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 40,
            "operational_value": "Exact daily cash movements, running balances, authorized overdraft indicators, interest credits, service fees, and standing orders."
        },
        {
            "category_id": "Cat 5",
            "dataset_name": "City of San Francisco Employee Compensation Register",
            "category": "Category 5: Payroll, Employees & Operating Structure",
            "physical_path": "research/original_datasets/payroll_employees/sf_employee_compensation/",
            "source_institution": "City and County of San Francisco Controller",
            "authenticity_class": "Real-world, Anonymized ID / Identifiable Title",
            "record_count": "50,000 employee compensation records (17.7 MB)",
            "file_formats": "CSV",
            "granularity": "Employee annual compensation record",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 35,
            "operational_value": "Decomposed labor cost: base salaries, overtime premiums, other pay, retirement contributions, and healthcare benefits (34.8% loading)."
        },
        {
            "category_id": "Cat 6",
            "dataset_name": "Czech Bank Commercial & Personal Loan Portfolio",
            "category": "Category 6: Debt, Financing & Financial Obligations",
            "physical_path": "research/original_datasets/debt_financing/czech_bank_loans/loan.csv",
            "source_institution": "Czech Commercial Bank",
            "authenticity_class": "Real-world, Anonymized",
            "record_count": "682 loan facilities",
            "file_formats": "CSV",
            "granularity": "Credit facility & repayment schedule level",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 39,
            "operational_value": "Principal amounts, term durations, monthly debt service payments, and loan default performance status (A/B/C/D)."
        },
        {
            "category_id": "Cat 7",
            "dataset_name": "SEC EDGAR Material M&A Agreement (Annex A: Plan of Merger)",
            "category": "Category 7: Tax, Legal & Contractual Records",
            "physical_path": "research/original_datasets/tax_legal_contracts/sec_merger_agreement_exhibit.htm",
            "source_institution": "SEC EDGAR / Twitter, Inc. (CIK 0001418091)",
            "authenticity_class": "Real-world, Identifiable",
            "record_count": "Full legal transaction agreement (1.87 MB)",
            "file_formats": "HTML",
            "granularity": "Contractual clause level",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 36,
            "operational_value": "Authentic legal definitions: working capital adjustments, MAE clauses, representations & warranties, closing conditions, and debt covenants."
        },
        {
            "category_id": "Cat 8",
            "dataset_name": "Brazilian E-Commerce (Olist) Order Fulfillment & Logistics",
            "category": "Category 8: Operational & Commercial Performance",
            "physical_path": "research/original_datasets/operational_performance/olist_orders_dataset.csv",
            "source_institution": "Olist Marketplace Platform",
            "authenticity_class": "Real-world, Anonymized",
            "record_count": "99,441 commercial orders (17.6 MB CSV)",
            "file_formats": "CSV",
            "granularity": "Order milestone event level",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 38,
            "operational_value": "Exact operational timestamps: purchase, payment approval, carrier handover, actual customer delivery, and estimated delivery dates."
        },
        {
            "category_id": "Cat 9",
            "dataset_name": "Lehman Brothers Bankruptcy Examiner Report Vol 3 (Repo 105)",
            "category": "Category 9: Internal Documentation & Communications",
            "physical_path": "research/original_datasets/internal_documentation/lehman_repo105_forensic_examiner_findings.txt",
            "source_institution": "U.S. Bankruptcy Court SDNY / Jenner & Block LLP",
            "authenticity_class": "Real-world, Identifiable",
            "record_count": "Forensic findings & executive memos",
            "file_formats": "Text / Workpaper Record",
            "granularity": "Accounting policy & internal directive level",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 34,
            "operational_value": "Unprecedented real-world documentation of balance sheet window-dressing, CFO balance sheet reduction targets, and Net Debt manipulation."
        },
        {
            "category_id": "Cat 10",
            "dataset_name": "SEC Form DEFM14A Financial Advisor Diligence & Projections",
            "category": "Category 10: QoE & Transaction Advisory Evidence",
            "physical_path": "research/original_datasets/qoe_transaction_advisory/sec_defm14a_financial_projections_and_fairness.htm",
            "source_institution": "SEC EDGAR (Goldman Sachs & J.P. Morgan Opinions)",
            "authenticity_class": "Real-world, Identifiable",
            "record_count": "Official M&A proxy & fairness presentation (1.87 MB)",
            "file_formats": "HTML",
            "granularity": "Transaction advisory schedule level",
            "acquisition_status": "Acquired & Inspected (On Disk)",
            "tier": "Tier A — Priority",
            "total_score": 36,
            "operational_value": "Authentic M&A diligence schedules: Adjusted EBITDA projections, Unlevered Free Cash Flow bridges, and Net Working Capital changes."
        }
    ]

    df_reg = pd.DataFrame(registry_data)
    csv_path = os.path.join(BASE_DIR, "source_registry", "master_dataset_registry.csv")
    md_path = os.path.join(BASE_DIR, "source_registry", "master_dataset_registry.md")
    df_reg.to_csv(csv_path, index=False)

    md_lines = [
        "# Master Dataset Registry: 100% Physical Acquisition Across All 10 Categories",
        "\nThis registry documents all acquired and verified real-world datasets across the ten Quality of Earnings operational and financial categories. **Every single category is backed by physical files residing in `research/original_datasets/`.**",
        "\n## Summary Table",
        "| Category | Dataset Name | Classification | Records / Footprint | Tier | Status |",
        "|---|---|---|---|---|---|"
    ]
    for _, r in df_reg.iterrows():
        md_lines.append(f"| **{r['category_id']}** | {r['dataset_name']} | `{r['authenticity_class']}` | {r['record_count']} | **{r['tier']}** | `{r['acquisition_status']}` |")

    md_lines.append("\n## Detailed Inventory Profiles Across All 10 Categories")
    for _, r in df_reg.iterrows():
        md_lines.append(f"\n### {r['category_id']}: {r['dataset_name']}")
        md_lines.append(f"- **Category:** {r['category']}")
        md_lines.append(f"- **Physical Path:** `{r['physical_path']}`")
        md_lines.append(f"- **Classification:** `{r['authenticity_class']}`")
        md_lines.append(f"- **Quality Tier:** `{r['tier']}` (Score: {r['total_score']}/40)")
        md_lines.append(f"- **Originating Source:** {r['source_institution']}")
        md_lines.append(f"- **Record Count & Format:** {r['record_count']} ({r['file_formats']})")
        md_lines.append(f"- **Granularity:** {r['granularity']}")
        md_lines.append(f"- **Operational Substance:** {r['operational_value']}")
        md_lines.append("---")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Updated Master Registry: {csv_path} and {md_path}")

if __name__ == "__main__":
    update_master_registry()
