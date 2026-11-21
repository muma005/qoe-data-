# Virtual Data Room (VDR) Taxonomy & Permissions Specification
**Repository Path:** `QOE_RESEARCH/01_PROFESSIONAL_WORKFLOWS/01_Data_Intake/vdr_folder_taxonomy.md`  
**Standard Reference:** Datasite Diligence Architecture / ICAEW Guideline 71  

---

## 1. Directory Tree & Indexing Schema

The standard FDD Virtual Data Room repository enforces strict numerical indexing and functional segregation:

```
CLIENT_ROOT_VDR/
├── 00_Admin_and_Diligence_Control/
│   ├── 00.01_Master_Information_Request_List.xlsx
│   ├── 00.02_VDR_Index_and_Document_Register.xlsx
│   └── 00.03_Diligence_QA_Tracker.xlsx
├── 01_Corporate_Governance_and_Legal/
│   ├── 01.01_Articles_of_Incorporation_and_Bylaws/
│   └── 01.02_Shareholder_and_Cap_Table_Agreements/
├── 02_Financial_Statements/
│   ├── 02.01_Audited_Annual_Reports_FY22_FY24/
│   └── 02.02_Monthly_Management_Reporting_Packs/
├── 03_Accounting_Records_and_General_Ledger/
│   ├── 03.01_Monthly_Trial_Balances_36_Months/
│   ├── 03.02_Transaction_Level_General_Ledger/
│   └── 03.03_Chart_of_Accounts_and_Policy_Manual/
├── 04_Revenue_Customers_and_Contracts/
│   ├── 04.01_Monthly_Customer_Sales_Ledgers/
│   ├── 04.02_Top_20_Customer_Master_Agreements/
│   └── 04.03_Customer_Churn_and_Retention_Logs/
├── 05_Procurement_and_Operating_Expenses/
│   ├── 05.01_Vendor_AP_Invoicing_Subledgers/
│   ├── 05.02_Top_Supplier_Master_Agreements/
│   └── 05.03_Operating_Expense_Contracts_and_Leases/
├── 06_Workforce_Payroll_and_Compensation/
│   ├── 06.01_Employee_Census_and_Compensation/
│   ├── 06.02_Executive_and_Officer_Agreements/
│   └── 06.03_Benefit_Plans_and_Payroll_Tax_Filings/
├── 07_EBITDA_Normalizations_and_Workpapers/
│   ├── 07.01_Management_EBITDA_Bridge_Schedule/
│   └── 07.02_Add_Back_Primary_Invoices_and_Proof/
├── 08_Working_Capital_and_Inventory/
│   ├── 08.01_Aged_Accounts_Receivable_Subledgers/
│   ├── 08.02_Aged_Accounts_Payable_Subledgers/
│   ├── 08.03_Perpetual_Inventory_Valuation_and_Aging/
│   └── 08.04_Physical_Inventory_Count_Workpapers/
├── 09_Treasury_Cash_and_Debt_Facilities/
│   ├── 09.01_Bank_Statements_and_Reconciliations/
│   ├── 09.02_Credit_Agreements_and_Covenant_Reports/
│   └── 09.03_Debt_Payoff_Letters_and_Debt_Like_Items/
├── 10_Tax_Filings_and_Nexus_Studies/
│   ├── 10.01_Federal_Form_1120_Returns_3_Years/
│   ├── 10.02_State_Income_and_Franchise_Tax_Returns/
│   └── 10.03_Sales_and_Use_Tax_Wayfair_Nexus_Studies/
└── 99_Clean_Team_Restricted_Access/
    ├── 99.01_Unmasked_Customer_Identities/
    └── 99.02_Detailed_Employee_PII_and_Salaries/
```

---

## 2. Granular Access Control & Security Matrix

Security permissions in professional data rooms are assigned by participant role to protect sensitive commercial and personal data:

| User Group | Default Permission Tier | Watermarking | Download Enabled? | Restricted Clean Team Access? |
| :--- | :--- | :---: | :---: | :---: |
| **QoE Engagement Lead / Partner** | Administrator / Full Access | Off | Yes | Yes (Authorized Signatory) |
| **QoE Diligence Analysts** | Contributor / Extract Access | Custom User Watermark | Yes | Yes (Clean Team Members) |
| **Buyer Investment Team** | Reviewer / Limited Download | Dynamic Email Watermark | Selective (No Raw PII) | **NO ACCESS** |
| **Target Company CFO / Controller** | Contributor (Upload & Q&A) | Off | Yes | No |
| **Target Advisory / Intermediary** | Administrator / Overseer | Off | Yes | No |
| **Lender / Financing Sources** | Viewer / Highly Restricted | Dynamic Watermark + Print Block | No (View Only) | **NO ACCESS** |

---

## 3. Mandatory Document Ingestion Validation Rules

Every document ingested into the VDR must satisfy the following technical checks before acceptance into the diligence archive:

1. **SHA-256 Checksum Calculation:** Upon upload, an SHA-256 hash is computed and recorded in the document register to establish a cryptographically verifiable chain of custody.
2. **Virus & Malware Scanning:** Zero-day quarantine scan executed automatically upon upload.
3. **OCR Text Layer Verification:** Scanned PDF documents must undergo automated Optical Character Recognition (OCR) to enable keyword and account code searchability.
4. **Immutability Enforcement:** Version control prevents accidental overwrites; replacement files are saved as `_v02` with an audit log tracking the replacement author and timestamp.
