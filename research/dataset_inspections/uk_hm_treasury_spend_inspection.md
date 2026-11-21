# Technical Inspection Report: UK HM Treasury Spend Over £25,000

**Category:** `Category 1: Financial Accounting & General Ledger` & `Category 3: Procurement & Expenses`  
**Inspection Date:** `2026-11-12 10:51:24`  
**Originating Organization:** UK HM Treasury / Cabinet Office  
**Classification:** `Real-world, Identifiable`  
**License:** Open Government Licence v3.0  
**Total Records Inspected:** 132 accounts payable vouchers  
**Total Value of Monitored Disbursed Spend:** £30,223,630.53  

## 1. Schema & Field Architecture
- `Department Family` (object): Parent government ministry (`HM Treasury`).
- `Entity` (object): Operational accounting reporting unit (`HM Treasury`, `DMO` - Debt Management Office).
- `Date` (object): Accounting / voucher payment release date.
- `Expense Type` (object): General Ledger account classification code (e.g. IT services, professional consultancy, facilities, legal).
- `Expense Area` (object): Internal cost center or budget responsibility center.
- `Supplier` (object): Verified corporate vendor / payee legal name.
- `Transaction Number` (object/int): Unique accounting voucher identifier / check reference.
- `Amount` (float64): Net invoice line amount in GBP (£).
- `Narrative` (object): Business justification / voucher description text.

## 2. Expenditure Distribution & Threshold Profile
- **Total Monitored Spend:** £30,223,630.53
- **Voucher Size Distribution (GBP):**
  - Minimum: £352.50 (Strict lower threshold truncation at £25,000)
  - 25th Percentile: £26,772.01
  - Median: £52,342.78
  - Mean: £228,966.90
  - 75th Percentile: £202,500.00
  - Maximum: £4,850,000.00

## 3. Vendor Concentration & Expense Category Drivers
- **Unique Suppliers Monitored:** 51 vendors
- **Top 5 Suppliers by Disbursed Value:**
```
Supplier
DEUTSCHE BANK AG LONDON      4850000.00
CITY OF WESTMINSTER          4242399.53
ROYAL MINT                   4084045.57
FUJITSU SERVICES LIMITED     4047232.05
EXCHEQUER PARTNERSHIP PLC    3172233.66
```
- **Top 5 Expense Classifications:**
```
Expense Type
Consultants - Financial - Advisory only    8242041.76
Rates                                      4443222.53
IT profssnl svcs contractd out             3658459.71
AME Mint Stock Metal Costs                 2206345.12
DEL Mint Stock Manufacturing Costs         1713200.45
```

## 4. QoE Forensic & Simulator Applications
1. **Accounts Payable Distribution Validation:** Provides genuine empirical parameters for high-value invoice amounts, payment frequencies, and vendor concentration in enterprise general ledgers.
2. **Transaction Narrative Analysis:** Replicates real-world internal documentation where narrative descriptions vary widely from detailed contract references to vague service fee labels.
3. **P2P Matching Test Bed:** Establishes real-world voucher identifiers for cross-checking against procurement contracts and bank disbursements.
