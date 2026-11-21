# QoE Simulator Functional Specification — Working Capital & Debt Engine
**Document Reference:** `QOE-SPEC-SIM-07`  
**Workstream:** `07 — Working Capital, Target Peg, and Net Debt`  
**Classification:** Technical Software Architecture & Simulation Blueprint  

---

## 1. System Architecture Overview

The Working Capital and Debt Engine models the high-stakes negotiation between seller representations and buy-side forensic balance sheet audits:

```
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                              QOE WORKING CAPITAL & DEBT SIMULATOR                                  |
|                                                                                                    |
|   [CLIENT GENERATION ENGINE]                                                                       |
|   • Generates 24 to 36 consecutive monthly balance sheets, trial balances, and aging subledgers.   |
|   • Injects configurable balance sheet distortions:                                                |
|     - Stretched trade payables (delaying vendor disbursements prior to sale).                      |
|     - Suppressed accounts receivable and inventory obsolescence reserves.                          |
|     - Month-end cash window dressing (gathering cash, delaying check runs).                        |
|     - Hidden debt-like liabilities (unaccrued transaction bonuses, sales tax nexus exposure).     |
|     - Aggressive target peg proposals (low historical trough pegs to trigger true-up windfalls).   |
|                                      │                                                             |
|                                      ▼ (Synthetic Monthly Balance Sheets, Subledgers, Loan Files)  |
|                                                                                                    |
|   [QOE EVALUATION & ADJUDICATION SUITE]                                                            |
|   • Module 1: Balance Sheet Tie-Out & Four-Bucket Transaction Classifier.                          |
|   • Module 2: Operational Days Cycle Engine (Count-Back DSO, DIO, DPO, CCC).                       |
|   • Module 3: Stretched Accounts Payable Reclassification Engine.                                  |
|   • Module 4: Inventory Obsolescence Reserve Deficiency Analyzer.                                  |
|   • Module 5: Multi-Methodology Target Peg Evaluator & Negotiation Simulator.                      |
|   • Module 6: Debt & Debt-Like Item Forensic Scraper & Cash Offset Validator.                     |
|   • Module 7: Tripartite Settlement Firewall Integrity Checker (Double-Counting Blocker).          |
|   • Module 8: Definitive Enterprise Value to Equity Value Purchase Price Bridge Generator.         |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Client Generation Engine: Balance Sheet Anomaly Injection

| Anomaly Code | Balance Sheet Phenomenon | Generation Mechanism & Injection Rules | Detection Trigger & Audit Test |
| :--- | :--- | :--- | :--- |
| **`ANOM-WC-01`** | **Stretched Accounts Payable** | Halts disbursements on invoices >$25k during final 90 days; expands DPO by >6 days; accumulates >$200k in 60+ day AP. | AP subledger aging stratification; DPO spike vs historical baseline. |
| **`ANOM-WC-02`** | **Suppressed AR Doubtful Allowance** | Reduces allowance balance by 20% while 90+ day overdue customer balances increase; ignores bankrupt accounts. | Bad debt loss roll-forward; aging bracket percentage test. |
| **`ANOM-WC-03`** | **Unreserved Dead Inventory** | Carries $150k+ of inventory with zero unit consumption in trailing 12 months; limits book reserve to <2%. | Months of Supply (MOS) by SKU; scrap log to GL reconciliation. |
| **`ANOM-WC-04`** | **Month-End Cash Window Dressing** | Concentrates customer collections on 28th-30th; delays vendor check release until 2nd of subsequent month. | Daily bank cash balance tracking; intra-month peak vs month-end gap. |
| **`ANOM-WC-05`** | **Off-Balance-Sheet Deal Bonuses** | Omits change-of-control transaction bonuses and employer payroll taxes from accrued operating liabilities. | Board minutes inspection; M&A engagement letter review. |
| **`ANOM-WC-06`** | **Seller Low-Peg Bias** | Proposes 12-month average or seasonal trough peg during growth phase to manufacture an unearned closing true-up. | Multi-methodology peg variance modeling (LTM vs 6M vs % Rev). |

---

## 3. Relational Database Schema Specification

The simulator data layer is structured using relational tables implemented in SQL:

```sql
-- Table 1: Balance Sheet Account Master & Transaction Bucket Mapping
CREATE TABLE BalanceSheetAccountMaster (
    account_code VARCHAR(20) PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    account_category VARCHAR(30) CHECK (account_category IN ('Asset', 'Liability', 'Equity')),
    financial_statement_line VARCHAR(100) NOT NULL,
    transaction_bucket VARCHAR(30) CHECK (transaction_bucket IN ('Operating NWC', 'Net Debt', 'Cash', 'Excluded')),
    is_active BOOLEAN DEFAULT TRUE
);

-- Table 2: Monthly Balance Sheet Ledger (24 to 36 Months)
CREATE TABLE MonthlyBalanceSheetLedger (
    ledger_id VARCHAR(30) PRIMARY KEY,
    engagement_id VARCHAR(20) NOT NULL,
    fiscal_period VARCHAR(10) NOT NULL,
    month_end_date DATE NOT NULL,
    account_code VARCHAR(20) NOT NULL REFERENCES BalanceSheetAccountMaster(account_code),
    book_balance DECIMAL(15,2) NOT NULL,
    qoe_adjustment_amount DECIMAL(15,2) DEFAULT 0.00,
    normalized_balance DECIMAL(15,2) NOT NULL
);

-- Table 3: Accounts Payable Subledger Aging
CREATE TABLE ApSubledgerAging (
    ap_record_id VARCHAR(30) PRIMARY KEY,
    engagement_id VARCHAR(20) NOT NULL,
    balance_date DATE NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    vendor_name VARCHAR(100) NOT NULL,
    agreed_payment_terms VARCHAR(20) NOT NULL,
    current_amount DECIMAL(15,2) NOT NULL,
    days_31_60_amount DECIMAL(15,2) NOT NULL,
    days_61_90_amount DECIMAL(15,2) NOT NULL,
    days_over_90_amount DECIMAL(15,2) NOT NULL,
    total_book_ap DECIMAL(15,2) NOT NULL,
    stretched_ap_amount DECIMAL(15,2) DEFAULT 0.00
);

-- Table 4: Debt and Debt-Like Items Register
CREATE TABLE DebtAndDebtLikeItem (
    item_id VARCHAR(20) PRIMARY KEY,
    engagement_id VARCHAR(20) NOT NULL,
    classification_type VARCHAR(30) CHECK (classification_type IN ('Funded Debt', 'Debt-Like Item', 'Cash Asset', 'Cash Deduction', 'Cash-Like Item')),
    account_code VARCHAR(20),
    description VARCHAR(150) NOT NULL,
    counterparty VARCHAR(100) NOT NULL,
    document_reference VARCHAR(100) NOT NULL,
    book_balance DECIMAL(15,2) NOT NULL,
    diligence_tested_amount DECIMAL(15,2) NOT NULL,
    final_deduction_amount DECIMAL(15,2) NOT NULL,
    signoff_status VARCHAR(20) NOT NULL
);

-- Table 5: Target Working Capital Peg Scenarios
CREATE TABLE TargetWorkingCapitalPegScenario (
    scenario_id VARCHAR(20) PRIMARY KEY,
    engagement_id VARCHAR(20) NOT NULL,
    peg_methodology VARCHAR(50) NOT NULL,
    formula_description VARCHAR(200) NOT NULL,
    target_peg_amount DECIMAL(15,2) NOT NULL,
    closing_delivered_nwc DECIMAL(15,2) NOT NULL,
    purchase_price_adjustment DECIMAL(15,2) NOT NULL,
    collar_amount DECIMAL(15,2) DEFAULT 0.00,
    sponsoring_party VARCHAR(20) CHECK (sponsoring_party IN ('Seller', 'Buyer', 'Compromise'))
);

-- Table 6: Enterprise Value to Equity Value Bridge Line Items
CREATE TABLE EvToEquityBridgeLineItem (
    bridge_line_id VARCHAR(20) PRIMARY KEY,
    engagement_id VARCHAR(20) NOT NULL,
    line_order INT NOT NULL,
    line_label VARCHAR(100) NOT NULL,
    seller_claimed_amount DECIMAL(15,2) NOT NULL,
    qoe_verified_amount DECIMAL(15,2) NOT NULL,
    variance_amount DECIMAL(15,2) NOT NULL,
    settlement_category VARCHAR(30) NOT NULL
);
```

---

## 4. QoE Evaluation Suite: Core Algorithms

### 4.1 Count-Back DSO Calculation Algorithm
```python
def calculate_countback_dso(ending_ar, monthly_revenues, days_in_months):
    """
    Computes count-back exhaustion DSO.
    monthly_revenues: list of monthly revenues ordered from most recent to oldest.
    days_in_months: list of calendar days in those corresponding months.
    """
    remaining_ar = ending_ar
    exhaustion_days = 0.0
    
    for rev, days in zip(monthly_revenues, days_in_months):
        if remaining_ar >= rev:
            remaining_ar -= rev
            exhaustion_days += days
        else:
            fraction = remaining_ar / rev
            exhaustion_days += (fraction * days)
            remaining_ar = 0.0
            break
            
    if remaining_ar > 0:
        # If AR exceeds trailing revenue lookback
        exhaustion_days += (remaining_ar / monthly_revenues[-1]) * days_in_months[-1]
        
    return round(exhaustion_days, 1)
```

### 4.2 Stretched AP Detection & Reclassification Engine
```python
def detect_stretched_ap(ap_aging_records):
    """
    Scans vendor aging records; reclassifies payables aged beyond agreed terms.
    """
    stretched_liabilities = []
    total_stretched_amount = 0.0
    
    for record in ap_aging_records:
        terms = record['agreed_payment_terms']
        over_60 = record['days_61_90_amount'] + record['days_over_90_amount']
        
        # If vendor terms are Net 30 or Net 60, any balance >60 days is classified as stretched
        if terms in ['Net 30', 'Net 45', 'Net 60'] and over_60 > 5000.00:
            stretched_amount = over_60
            total_stretched_amount += stretched_amount
            stretched_liabilities.append({
                'vendor_name': record['vendor_name'],
                'stretched_amount': stretched_amount,
                'action': 'Reclassify from Operating NWC to Debt-Like Item'
            })
            
    return {
        'total_stretched_ap': total_stretched_amount,
        'itemized_vendors': stretched_liabilities,
        'nwc_adjustment': +total_stretched_amount,  # Reduces liabilities, increasing NWC
        'debt_adjustment': -total_stretched_amount   # Deducted from Purchase Price
    }
```
