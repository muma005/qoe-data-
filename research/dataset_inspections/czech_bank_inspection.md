# Technical Inspection Report: Czech Bank Berka Relational Database

**Category:** `Category 4: Working Capital, Cash and Banking` & `Category 6: Debt & Financing`  
**Inspection Date:** `2026-11-12 10:51:22`  
**Originating Organization:** Real Czech Commercial Bank (Anonymized by Petr Berka for PKDD'99)  
**Classification:** `Real-world, Anonymized`  
**License:** Open Academic Research / Public Domain  
**Total Records:** 1,056,320 Transactions | 4,500 Accounts | 682 Loans | 6,471 Standing Orders  
**Temporal Span:** `1993-01-01` to `1998-12-31` (6 full calendar years: 1993–1998)  

## 1. Relational Schema and Entity Architecture
The dataset represents a complete relational banking system across 8 tables:
- `trans.csv` (1,056,320 rows, 10 columns): Primary transaction ledger with running cash balances.
- `account.csv` (4,500 rows, 4 columns): Account master records with opening dates and statement frequencies.
- `loan.csv` (682 rows, 7 columns): Loan facilities granted to account holders with repayment schedules and default status.
- `order.csv` (6,471 rows, 6 columns): Permanent standing payment orders (recurring debits).
- `disp.csv` (5,369 rows, 4 columns): Disposition permissions linking clients to accounts (Owner / User).
- `client.csv` (5,369 rows, 3 columns): Demographic client profiles.
- `card.csv` (892 rows, 4 columns): Payment card issuance (junior, classic, gold).
- `district.csv` (77 rows, 16 columns): Demographic and economic regional indicators.

## 2. Transaction Ledger (`trans.csv`) Distribution Profile
- **Total Transaction Volume:** 1,056,320 records across 4,500 unique bank accounts.
- **Transaction Amount Statistics (CZK):**
  - Minimum: `0.00`
  - 25th Percentile: `135.90`
  - Median: `2,100.00`
  - Mean: `5,924.15`
  - 75th Percentile: `6,800.00`
  - Maximum: `87,400.00`
  - Standard Deviation: `9,522.74`
- **Account Running Balance Statistics (CZK):**
  - Minimum: `-41,125.70` (Notice: Negative minimum indicates overdraft facilities!)
  - Median: `33,143.40`
  - Maximum: `209,637.00`
  - Negative Balance Transactions (Overdrafts): `2,999` records.

## 3. Transaction Types & Operational Workflows
- **Transaction Types (`type`):**
  - `VYDAJ` (Debit / Outflow): `634,571` records (60.1%)
  - `PRIJEM` (Credit / Inflow): `405,083` records (38.3%)
  - `VYBER` (Cash Withdrawal): `16,666` records (1.6%)
- **Transaction Operations (`operation`):**
{
  "VYBER": 434918,
  "PREVOD NA UCET": 208283,
  "NaN": 183114,
  "VKLAD": 156743,
  "PREVOD Z UCTU": 65226,
  "VYBER KARTOU": 8036
}
- **Categorization Codes (`k_symbol`):**
  - `UROK` (Interest credited): Inter-period interest revenue
  - `SLUZBY` (Bank service charge / fee leakage)
  - `SIPO` (Household recurring payment)
  - `SPLATKA` (Loan installment payment)
  - `POJISTNE` (Insurance premium)
  - `DUCHOD` (Pension credit)

## 4. Loan Portfolio & Debt Servicing (`loan.csv`)
- **Total Facilities:** 682 loans totaling CZK 103,266,936.
- **Status Classification Breakdown:**
  - `Status A` (Contract finished, no problems / fully repaid): `203` loans
  - `Status B` (Contract finished, loan not paid / defaulted): `31` loans (Hard default)
  - `Status C` (Running contract, payments current / OK): `403` loans
  - `Status D` (Running contract, client in debt / delinquent): `45` loans (At-risk)
- **Delinquency / Default Rate:** `11.14%`

## 5. QoE Forensic & Simulator Applications
1. **Cash Reconciliation Simulation:** Demonstrates how daily ledger cashbook entries reconcile to cleared bank statements, including float, timing differences, and bank service charge deductions.
2. **Working Capital & Debt-Like Item Assessment:** Overdraft balances (`balance < 0`) represent short-term debt-like obligations requiring deduction from Enterprise Value in transaction pricing.
3. **Debt Service Coverage & Covenant Monitoring:** Connected loans, payments, and account balances allow direct testing of Debt Service Coverage Ratios (DSCR) and liquidity cushion modeling.
