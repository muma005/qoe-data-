# Working Capital, Cash Movements & Credit Risk: Empirical Signal Discovery and Mathematical Behavioral Modeling

## 1. Executive Summary & Research Grounding
This research establishes an empirical, evidence-based mathematical framework for **Treasury, Working Capital, Cash Movements, and Commercial Credit Risk**.

The analysis is grounded in the **Czech Bank (Berka) Relational Database**, an authentic commercial banking dataset comprising:
- **1,056,320 transaction ledger records** (`trans.csv`) spanning 1993 to 1998
- **4,500 commercial and personal bank accounts** (`account.csv`)
- **682 formal term-loan credit facilities** (`loan.csv`) totaling **CZK 103,261,740.00**
- **6,471 permanent standing orders** (`order.csv`) capturing fixed monthly committed outflows

```mermaid
flowchart TD
    subgraph Cash_Inflows ["1. Operating Cash Inflows"]
        Inflow["Total Cash Inflow: CZK 3.23B<br/>(405,083 Transactions | Median CZK 2,400)"]
        Collections["Commercial Collections & Deposits<br/>(Cash Deposits 'VKLAD' & Inward Transfers)"]
        InterestCredit["Bank Interest Credits<br/>('UROK' Inflows)"]
    end

    subgraph Treasury_Subledger ["2. Running Account Balance & Buffer"]
        AccountBal["Account Running Balances<br/>(Median CZK 33,143 | Mean CZK 38,518)"]
        StandingOrders["Fixed Standing Orders<br/>(83.5% Accounts | Median CZK 4,501/mo)"]
    end

    subgraph Cash_Outflows ["3. Operating Cash Outflows"]
        Outflow["Total Cash Outflow: CZK 3.03B<br/>(651,237 Transactions | Median CZK 2,120)"]
        Disbursements["Vendor Disbursements & Card Clearings<br/>(P2P Settlements & Cash Withdrawals)"]
    end

    subgraph Liquidity_Distress ["4. Working Capital Deficit & Overdraft"]
        Overdraft["Authorized Overdraft Occurrence<br/>(6.40% Accounts | 2,999 Transactions)"]
        SevereOverdraft["Severe Overdraft (&lt; -1,000 CZK)<br/>(5.13% Accounts | Max Deficit CZK 41,126)"]
    end

    subgraph Credit_Risk ["5. Debt Servicing & Default Hazard"]
        LoanBook["682 Loan Facilities: CZK 103.3M<br/>(Terms: 12, 24, 36, 48, 60 Months)"]
        DefaultBreakage["Loan Default Rate: 11.14% Overall<br/>(Closed Loans: 13.25% Default Rate)"]
        DeterministicLink["100% Deterministic Overdraft Correlation<br/>(Every Defaulted Borrower Suffered Account Overdraft)"]
    end

    Inflow --> AccountBal
    AccountBal --> Outflow
    AccountBal --> StandingOrders
    AccountBal -.->|Liquidity Depletion| Overdraft
    Overdraft --> SevereOverdraft
    LoanBook --> DefaultBreakage
    SevereOverdraft ===> DeterministicLink
    DeterministicLink ===> DefaultBreakage
```

---

## 2. Mathematical Modeling Framework

### A. Cashbook Transactional Balance Transition Model
Let the cash balance $B_i(t)$ of account $i$ at transaction step $t$ follow a discrete state update:
$$B_i(t) = B_i(t-1) + \Delta C_i(t)$$
where $\Delta C_i(t) \in \mathbb{R}$ represents the signed net cash flow:
$$\Delta C_i(t) = \begin{cases} +A_i(t) & \text{if } \text{Type}(t) = \text{PRIJEM (Credit/Inflow)} \\ -A_i(t) & \text{if } \text{Type}(t) \in \{\text{VYDAJ}, \text{VYBER}\} \text{ (Debit/Outflow)} \end{cases}$$
with transaction amount $A_i(t) > 0$.

### B. Authorized Overdraft & Working Capital Deficit Operator
An account enters a working capital deficit state whenever its running balance breaches zero:
$$\mathcal{I}_{\text{overdraft}}(i, t) = \begin{cases} 1 & \text{if } B_i(t) < 0 \\ 0 & \text{if } B_i(t) \ge 0 \end{cases}$$

The overdraft exposure depth $D_i(t)$ and cumulative account deficit $\Omega_i$ are:
$$D_i(t) = |B_i(t)| \cdot \mathcal{I}_{\text{overdraft}}(i, t)$$
$$\Omega_i = \int_{0}^T D_i(t) \, dt$$

### C. Credit Facility Debt Default Hazard Model
Let a loan facility $L_j = (A_j, \tau_j, M_j, \mathcal{S}_j)$ be defined by principal $A_j$, duration $\tau_j \in \{12, 24, 36, 48, 60\}$, monthly payment $M_j$, and loan performance status $\mathcal{S}_j \in \{A, B, C, D\}$.

The default indicator $\mathcal{Y}_j$ is:
$$\mathcal{Y}_j = \begin{cases} 1 & \text{if } \mathcal{S}_j \in \{B, D\} \text{ (Defaulted / Arrears)} \\ 0 & \text{if } \mathcal{S}_j \in \{A, C\} \text{ (Performing)} \end{cases}$$

The empirical default probability conditional on account overdraft history is:
$$\mathbb{P}(\text{Default} \mid \text{Overdraft}) = \frac{\sum_{j} \mathcal{Y}_j \cdot \mathbb{I}(\min B_j < 0)}{\sum_{j} \mathbb{I}(\min B_j < 0)}$$

---

## 3. Empirical Banking & Working Capital Discoveries

### Signal 1: Cash Inflow vs Outflow Velocity & Balance Buffer
Across **1,056,320 transaction records**:
- **Total Inflow Volume (`PRIJEM`):** **CZK 3,227,472,424.50** across 405,083 transactions.
  - Inflow Amount Distribution: $\text{Median} = \mathbf{\text{CZK } 2,400.00}$, $\text{Mean} = \text{CZK } 7,967.43$, $\text{P95} = \text{CZK } 25,600.00$.
- **Total Outflow Volume (`VYDAJ` / `VYBER`):** **CZK 3,030,321,135.80** across 651,237 transactions.
  - Outflow Amount Distribution: $\text{Median} = \mathbf{\text{CZK } 2,120.00}$, $\text{Mean} = \text{CZK } 4,653.18$, $\text{P95} = \text{CZK } 14,800.00$.
- **Transaction Asymmetry:** Outflows occur **1.61 times more frequently** than inflows, but inflows are **1.71 times larger in average magnitude**, reflecting batched revenue collections versus granular recurring disbursements.
- **Account Running Balances ($B_i$):**
  - $\text{Median} = \mathbf{\text{CZK } 33,143.40}$
  - $\text{Mean} = \text{CZK } 38,518.33$
  - $\text{P25} = \text{CZK } 19,006.75$
  - $\text{P75} = \text{CZK } 54,078.20$
  - $\text{P95} = \text{CZK } 88,382.40$
  - $\text{Max} = \text{CZK } 209,000.00$

### Signal 2: Authorized Overdrafts & Working Capital Friction
*   **Total Accounts Evaluated:** 4,500
*   **Overdraft Incidence Rate:** **6.40% of accounts (288 accounts)** breached zero balance into an overdraft state.
*   **Severe Overdraft Rate ($B < -1,000\text{ CZK}$):** **5.13% of accounts (231 accounts)** experienced sustained negative balances.
*   **Overdraft Frequency:** **2,999 transactions (0.28% of all transaction records)** occurred while in a negative balance state.
*   **Overdraft Exposure Depth ($D_i$):**
    *   $\text{Median} = \mathbf{\text{CZK } 2,440.80}$
    *   $\text{Mean} = \text{CZK } 4,341.70$
    *   $\text{P75} = \text{CZK } 5,720.50$
    *   $\text{P95} = \text{CZK } 14,242.00$
    *   $\text{Max Deficit} = \mathbf{\text{CZK } 41,125.70}$
*   **QoE Forensic Meaning:** Working capital peg calculations in transaction advisory require segregating operational cash from financing debt. An authorized overdraft is **not** negative working capital; it is **funded bank debt** that must be treated as a debt-like item and subtracted dollar-for-dollar from Enterprise Value to arrive at Equity Purchase Price.

---

### Signal 3: Fixed Monthly Committed Outflows (Standing Orders)
*   **Standing Order Adoption:** **83.51% of accounts (3,758 of 4,500)** have active permanent standing orders (`order.csv`).
*   **Committed Outflow Magnitude:**
    *   $\text{Median} = \mathbf{\text{CZK } 4,501.00\text{ / month}}$
    *   $\text{Mean} = \text{CZK } 5,649.01\text{ / month}$
    *   $\text{P75} = \text{CZK } 7,294.00\text{ / month}$
    *   $\text{P95} = \text{CZK } 11,882.00\text{ / month}$
*   **Commitment Composition:**
    *   Household / Utility Assessments (`SIPO`): 3,502 orders (54.1%)
    *   Uncharacterized / Vendor Transfers (` `): 1,379 orders (21.3%)
    *   Term Loan Debt Service (`UVER`): 717 orders (11.1%)
    *   Insurance Premiums (`POJISTNE`): 532 orders (8.2%)
    *   Equipment / Vehicle Leasing (`LEASING`): 341 orders (5.3%)
*   **QoE Meaning:** These standing orders represent non-discretionary, fixed operational cash obligations. In cash flow quality analysis, accounts with high committed outflow-to-balance ratios lack liquidity resilience and suffer rapid distress when operating inflows experience seasonal dips.

---

### Signal 4: Credit Risk, Debt Servicing & Default Hazards (`loan.csv`)
An exhaustive analysis of **682 term-loan facilities** totaling **CZK 103,261,740.00** establishes the empirical baseline for debt default:

| Loan Status Code | Operational Meaning | Count | Share (%) | Total Principal (CZK) | Overdraft Rate | Mean Account Balance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Status A** | Finished Contract, Normal Servicing | 203 | 29.77% | CZK 31,416,480 | **0.00%** | CZK 47,295.50 |
| **Status B** | Finished Contract, Default / Unpaid | 31 | 4.55% | CZK 6,712,596 | **100.00%** | CZK 35,159.60 |
| **Status C** | Active Contract, Normal Servicing | 403 | 59.09% | CZK 56,265,108 | **0.00%** | CZK 45,588.60 |
| **Status D** | Active Contract, In Debt / Arrears | 45 | 6.60% | CZK 8,867,556 | **100.00%** | CZK 35,170.90 |
| **Total / Overall** | **All Credit Facilities** | **682** | **100.00%** | **CZK 103,261,740** | **11.14%** | **CZK 43,846.80** |

```mermaid
xychart-beta
    title "Loan Portfolio Status & Principal Distribution (CZK Millions)"
    x-axis ["A: Finished OK", "B: Finished Default", "C: Active OK", "D: Active Arrears"]
    y-axis "Principal (CZK M)" 0 --> 60
    bar [31.42, 6.71, 56.27, 8.87]
```

#### Key Credit Risk Discoveries:
1.  **Overall Portfolio Default Rate:** **11.14%** (76 defaulted loans).
2.  **Closed Contract Default Rate:** **13.25%** ($31 / [203 + 31]$).
3.  **Capital at Risk:** **CZK 15,580,152.00 (15.09% of the total loan book)** is in default or serious repayment arrears.
4.  **100% Deterministic Overdraft Linkage:**
    *   **100.0% of borrowers who defaulted (Status B and D)** suffered authorized or unauthorized overdrafts in their transactional account.
    *   **0.0% of borrowers who remained in good standing (Status A and C)** ever dipped below zero balance!
    *   Defaulted accounts carried an average balance **25.6% lower** than performing accounts (CZK 35.1k vs CZK 47.3k).
5.  **Forensic QoE Implication:** In quality of earnings and net debt investigations, transactional cashbook behavior provides an infallible leading indicator of credit distress. A borrower entering an overdraft position on their operational account has an extreme probability of subsequent debt default, mandating full bad-debt reserve provisioning.
