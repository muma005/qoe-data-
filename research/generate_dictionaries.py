"""
Generate Individual Data Dictionaries in research/dataset_documentation/
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(BASE_DIR, 'dataset_documentation')
os.makedirs(DOC_DIR, exist_ok=True)

dicts = {
    "sec_edgar_dictionary.md": """# Data Dictionary: SEC EDGAR Financial Statement Data Sets (FSDS)

**Source:** U.S. Securities and Exchange Commission (DERA Data Library)  
**Classification:** `Real-world, Identifiable`  
**License:** Public Domain  

## Table: sub.txt (Submissions Master)
- `adsh` (VARCHAR(20), PK): Accession Submission Number assigned by EDGAR.
- `cik` (INT): Central Index Key identifying the corporate filer.
- `name` (VARCHAR): Legal entity name of the registrant.
- `sic` (INT): Standard Industrial Classification code.
- `countryba` / `stprba` / `cityba`: Business address location.
- `form` (VARCHAR(10)): Filing form type (`10-K`, `10-Q`, `8-K`, `20-F`).
- `period` (DATE): Balance sheet reporting period end date (YYYYMMDD).
- `fy` (INT): Fiscal year.
- `fp` (VARCHAR(2)): Fiscal period (`FY`, `Q1`, `Q2`, `Q3`, `Q4`).
- `filed` (DATE): Official SEC receipt timestamp.
- `prevrpt` (BOOLEAN): Restatement flag (1 if an amendment of an earlier report, 0 otherwise).

## Table: num.txt (Reported Numeric Facts)
- `adsh` (VARCHAR(20), FK): Submission identifier.
- `tag` (VARCHAR(256), FK): Taxonomy accounting tag (e.g. `Revenues`, `Assets`).
- `version` (VARCHAR(20), FK): Taxonomy release version (e.g. `us-gaap/2024`).
- `ddate` (DATE): Effective balance sheet date of the fact.
- `qtrs` (INT): Duration in quarters (0 for point-in-time balance sheet items; 1, 2, 4 for income statement flows).
- `uom` (VARCHAR(20)): Unit of measure (e.g. `USD`, `shares`).
- `value` (NUMERIC): Reported numerical amount.
- `segments` (VARCHAR): Segment dimensional qualifiers (e.g. business segment, geographic region).

## Table: tag.txt (Accounting Tag Definitions)
- `tag` (VARCHAR(256), PK): Name of the XBRL accounting tag.
- `version` (VARCHAR(20), PK): Taxonomy of origin.
- `custom` (BOOLEAN): 1 if company-specific custom tag; 0 if standard US-GAAP.
- `abstract` (BOOLEAN): 1 if structural header tag; 0 if monetary fact tag.
- `datatype` (VARCHAR(20)): Data type (e.g. `monetaryItemType`).
- `crdr` (CHAR(1)): Normal balance indicator (`C` for Credit, `D` for Debit).
- `doc` (TEXT): Official US-GAAP definition and accounting literature reference.

## Table: pre.txt (Statement Presentation Structure)
- `adsh` (VARCHAR(20), FK): Submission identifier.
- `report` (INT): Sequential statement index within the filing.
- `line` (INT): Presentation line number within that statement.
- `stmt` (CHAR(2)): Statement classification (`BS` = Balance Sheet, `IS` = Income Statement, `CF` = Cash Flows, `EQ` = Equity, `CP` = Comprehensive Income).
- `tag` (VARCHAR(256)): Tag mapped to this line.
- `version` (VARCHAR(20)): Taxonomy version.
- `prompt` (VARCHAR): Company-specific line label printed on face statements.
""",

    "czech_bank_dictionary.md": """# Data Dictionary: Czech Bank Berka Relational Database

**Source:** Real Commercial Bank in Czech Republic (PKDD'99)  
**Classification:** `Real-world, Anonymized`  
**License:** Open Academic Research  

## Table: trans.csv (Transaction Ledger)
- `trans_id` (INT, PK): Unique transaction identifier.
- `account_id` (INT, FK): Bank account number.
- `date` (DATE): Transaction date (YYMMDD format).
- `type` (VARCHAR):
  - `PRIJEM`: Credit / Deposit / Cash Inflow (+).
  - `VYDAJ`: Debit / Withdrawal / Cash Outflow (-).
  - `VYBER`: Cash withdrawal.
- `operation` (VARCHAR):
  - `VYBER KARTOU`: Credit card cash withdrawal.
  - `VKLAD`: Cash deposit at teller.
  - `PREVOD Z UCTU`: Electronic transfer collection from another bank.
  - `VYBER`: Cash withdrawal at branch.
  - `PREVOD NA UCET`: Electronic remittance to another bank.
- `amount` (FLOAT): Transaction amount in Czech Koruna (CZK).
- `balance` (FLOAT): Account running balance immediately after transaction.
- `k_symbol` (VARCHAR): Character code explaining purpose:
  - `POJISTNE`: Insurance premium.
  - `SLUZBY`: Bank service fee / charge.
  - `UROK`: Credit interest earned.
  - `SANKC. UROK`: Sanction / penalty interest for overdraft.
  - `SIPO`: Household recurring payment.
  - `DUCHOD`: Pension credit.
  - `SPLATKA`: Loan installment repayment.

## Table: loan.csv (Credit Facilities)
- `loan_id` (INT, PK): Unique loan facility identifier.
- `account_id` (INT, FK): Borrower account.
- `date` (DATE): Loan issuance date.
- `amount` (FLOAT): Total principal borrowed.
- `duration` (INT): Term length in months (12, 24, 36, 48, 60).
- `payments` (FLOAT): Monthly debt service payment amount.
- `status` (CHAR(1)):
  - `A`: Contract finished, fully repaid without issues.
  - `B`: Contract finished, loan defaulted / unpaid.
  - `C`: Running contract, payments currently on-track.
  - `D`: Running contract, client in debt / delinquent.

## Table: order.csv (Standing Payment Orders)
- `order_id` (INT, PK): Standing order key.
- `account_id` (INT, FK): Source account.
- `bank_to` (CHAR(2)): Recipient commercial bank code.
- `account_to` (INT): Recipient account number.
- `amount` (FLOAT): Scheduled transfer amount.
- `k_symbol` (VARCHAR): Purpose categorization (`SIPO`, `LEASING`, `POJISTNE`, `UVER`).
""",

    "uci_online_retail_dictionary.md": """# Data Dictionary: UCI Online Retail Dataset

**Source:** Great Britain Online Giftware Wholesaler / Retailer  
**Classification:** `Real-world, Anonymized`  
**License:** CC BY 4.0  

## Fields
- `InvoiceNo` (VARCHAR(10), PK part): 6-digit integer assigned to each transaction. If prepended with letter `'C'`, it indicates a cancellation / credit note.
- `StockCode` (VARCHAR(20)): Product / SKU identifier code. Contains 3,684 distinct SKU items, plus administrative charge codes (e.g. `POST`, `D`, `CRUK`, `BANK CHARGES`, `AMAZONFEE`).
- `Description` (VARCHAR(256)): Descriptive product trade name.
- `Quantity` (INT): Number of units sold (positive) or returned/cancelled (negative).
- `InvoiceDate` (DATETIME): Invoice creation timestamp.
- `UnitPrice` (FLOAT): Selling price per unit in British Pounds (£).
- `CustomerID` (INT/FLOAT): Unique 5-digit customer identification number. Null/NaN for guest walk-in transactions (135,080 rows).
- `Country` (VARCHAR(50)): Name of country where customer resides (38 distinct countries, 90%+ United Kingdom).
""",

    "sf_employee_compensation_dictionary.md": """# Data Dictionary: City of San Francisco Employee Compensation Register

**Source:** City and County of San Francisco Controller's Office  
**Classification:** `Real-world, Anonymized ID / Identifiable Department`  
**License:** Public Domain  

## Fields
- `organization_group_code` (INT): High-level organizational cluster code (1 to 7).
- `organization_group` (VARCHAR): Name of organizational group (e.g. `Public Protection`, `Community Health`, `Human Welfare & Neighborhood Development`).
- `department_code` (VARCHAR(3)): Department abbreviation (e.g. `POL`, `FIR`, `DPH`).
- `department` (VARCHAR): Full municipal operating department name.
- `job_family_code` (VARCHAR(4)): Labor classification code.
- `job_family` (VARCHAR): Professional labor grouping (e.g. `Information Systems`, `Nursing`, `Protection & Apprehension`).
- `job_code` (VARCHAR(6)): Official job classification code.
- `job` (VARCHAR): Specific job title.
- `employee_identifier` (INT): Unique anonymized employee tracking number.
- `salaries` (FLOAT): Base regular cash wages earned during calendar/fiscal year.
- `overtime` (FLOAT): Overtime premium compensation.
- `other_salaries` (FLOAT): Shift differentials, bonuses, longevity pay, settlement stipends.
- `total_salary` (FLOAT): Gross cash compensation (`salaries + overtime + other_salaries`).
- `retirement` (FLOAT): City employer pension contribution paid on behalf of employee.
- `health_and_dental` (FLOAT): City employer health, medical, and dental premium payments.
- `other_benefits` (FLOAT): Employer life insurance, disability, workers' compensation allocations.
- `total_benefits` (FLOAT): Sum of non-cash employment benefits (`retirement + health_and_dental + other_benefits`).
- `total_compensation` (FLOAT): Total cost of employment to the city (`total_salary + total_benefits`).
"""
}

for filename, content in dicts.items():
    p = os.path.join(DOC_DIR, filename)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated data dictionary: {p}")
