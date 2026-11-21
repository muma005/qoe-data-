# Dataset Documentation & Data Dictionaries Archive

This directory contains formal schema definitions, data dictionaries, provenance declarations, and licensing documentation for all real-world datasets acquired in the Quality of Earnings (QoE) research initiative.

---

## Document Index

1. [SEC EDGAR Financial Statement Data Sets Dictionary](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_documentation/sec_edgar_dictionary.md)
   - Schema mapping for `sub.txt`, `num.txt`, `tag.txt`, `pre.txt`.
   - Taxonomy definitions (US-GAAP / IFRS).
   - Core primary keys (`adsh`, `tag`, `version`, `ddate`, `qtrs`).

2. [Czech Bank Berka Relational Database Dictionary](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_documentation/czech_bank_dictionary.md)
   - Entity-relationship descriptions for all 8 tables (`trans`, `account`, `loan`, `order`, `disp`, `client`, `card`, `district`).
   - Transaction operation codes (`VYBER`, `PREVOD NA UCET`, `VKLAD`) and k-symbols (`UROK`, `SLUZBY`, `SPLATKA`, `SIPO`).

3. [UCI Online Retail Data Dictionary](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_documentation/uci_online_retail_dictionary.md)
   - Invoice line item attribute definitions (`InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`).
   - Credit note coding conventions (`'C'` prefix).

4. [City of San Francisco Employee Compensation Dictionary](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_documentation/sf_employee_compensation_dictionary.md)
   - Wage and benefit component definitions (Base Salaries, Overtime, Other Pay, Retirement, Health/Dental, Total Compensation).
   - Municipal department codes and job family classifications.

5. [BPI Challenge 2019 AkzoNobel SAP ERP Event Log Dictionary](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_documentation/bpi_challenge_2019_dictionary.md)
   - Purchase-to-pay event attributes (`concept:name`, `org:resource`, `time:timestamp`).
   - 2-way vs 3-way matching lifecycles, goods receipt events, and invoice clearance events.

6. [UK HM Treasury Spend Over £25,000 Dictionary](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/dataset_documentation/uk_spend_dictionary.md)
   - Accounts payable voucher fields (Department, Entity, Date, Expense Type, Expense Area, Supplier, Transaction Number, Amount, Narrative).
