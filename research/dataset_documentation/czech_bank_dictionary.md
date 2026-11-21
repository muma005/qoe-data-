# Data Dictionary: Czech Bank Berka Relational Database

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
