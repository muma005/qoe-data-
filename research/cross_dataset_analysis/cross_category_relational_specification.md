# Cross-Category Relational Specification: Connecting Operational Events to Accounting Records and Financial Outcomes

**Document Purpose:** Define the end-to-end data relationships, foreign key linkages, double-entry accounting triggers, and error propagation mechanics that transform raw operational events into General Ledger records, bank movements, and financial statements.  
**Evidentiary Foundation:** AkzoNobel SAP ERP Event Log (1.59M events across 251k cases), UCI Commercial Retail Subledger (541k lines), Brazilian Olist Logistics (99k orders), Czech Bank Berka Cashbook (1.05M transactions), and SEC EDGAR FSDS (5,961 public corporate filings).

---

## 1. The Five Interconnected Subledgers

In an enterprise environment, financial reality is not created in the General Ledger; it is born in frontline operational subledgers and flows through five distinct transactional tiers:

```mermaid
flowchart TD
    subgraph Operational_Tier ["1. Operational Frontline Subledgers"]
        PO["Purchase Orders (PO)<br/>Procurement Commitments"]
        SO["Sales Orders (SO)<br/>Customer Commercial Contracts"]
    end

    subgraph Physical_Fulfillment_Tier ["2. Physical Logistics & Inventory Subledgers"]
        GR["Goods Received (GR)<br/>Warehouse Receiving Slips"]
        Ship["Carrier Shipments<br/>Freight Waybills & Delivery Proof"]
    end

    subgraph Commercial_Billing_Tier ["3. Invoicing & Subledger Verification"]
        IR["Supplier Invoices (AP)<br/>Vendor Bills & 3-Way Match"]
        INV["Customer Invoices (AR)<br/>Commercial Billing & Credit Notes"]
    end

    subgraph Treasury_Banking_Tier ["4. Treasury & Cashbook Subledger"]
        Disb["Bank Cash Disbursements<br/>AP Payment Runs & Cleared Wires"]
        Receipts["Bank Cash Receipts<br/>Customer Inflows & Lockbox"]
    end

    subgraph General_Ledger_Tier ["5. Double-Entry General Ledger"]
        GL_BS["Balance Sheet Accounts<br/>Cash, AR, Inv, AP, Debt, Equity"]
        GL_PL["Income Statement Accounts<br/>Revenue, COGS, Opex, Interest"]
    end

    PO -->|Contractual Delivery| GR
    SO -->|Warehouse Fulfillment| Ship
    GR -->|Match PO + GR + IR| IR
    Ship -->|Title Transfer Proof| INV
    IR -->|Approved for Payment| Disb
    INV -->|Collections Queue| Receipts
    GR -->|Debit Inv / Credit GR-IR| GL_BS
    IR -->|Debit GR-IR / Credit AP| GL_BS
    Disb -->|Debit AP / Credit Cash| GL_BS
    INV -->|Debit AR / Credit Revenue| GL_PL
    Receipts -->|Debit Cash / Credit AR| GL_BS
```

---

## 2. Line-Item Relational Data Schemas & Foreign Key Topography

To simulate authentic corporate operations, every transaction must carry immutable relational keys that connect operational documents to their financial descendants:

```mermaid
erDiagram
    PURCHASE_ORDERS ||--o{ GOODS_RECEIPTS : "fulfilled_by (1:N)"
    GOODS_RECEIPTS ||--o{ SUPPLIER_INVOICES : "billed_by (1:N)"
    SUPPLIER_INVOICES ||--o{ PAYMENT_BLOCKS : "held_by (0:N)"
    SUPPLIER_INVOICES ||--o{ BANK_DISBURSEMENTS : "cleared_by (1:1)"
    BANK_DISBURSEMENTS ||--o{ GL_JOURNAL_ENTRIES : "posts_to (1:1)"
    GL_JOURNAL_ENTRIES ||--o{ GL_JOURNAL_LINES : "contains (1:N)"
```

### Table 1: Purchase Order Header & Lines (`p2p_purchase_orders`)
* **Primary Key:** `po_id`, `po_item_id`
* **Operational Fields:** `vendor_id`, `pr_id` (nullable, 81.49% null due to PR bypass), `created_timestamp`, `purchasing_group`, `item_category`, `material_id`, `ordered_quantity`, `net_unit_price`, `currency`.
* **Financial Commitment:** `total_committed_amount = ordered_quantity * net_unit_price`.

### Table 2: Goods Receipt Receiving Slips (`p2p_goods_receipts`)
* **Primary Key:** `gr_id`, `gr_item_id`
* **Foreign Keys:** `po_id`, `po_item_id`, `material_id`, `vendor_id`.
* **Operational Fields:** `gr_timestamp`, `warehouse_id`, `received_quantity`, `receiving_user`, `carrier_tracking_id`, `inspection_status` (Accepted / Rejected / Damaged).
* **Financial Impact:** Triggers physical title transfer under FOB Shipping Point or FOB Destination.

### Table 3: Supplier Invoices & Accounts Payable (`p2p_supplier_invoices`)
* **Primary Key:** `invoice_id`, `invoice_item_id`
* **Foreign Keys:** `po_id`, `po_item_id`, `gr_id` (nullable in premature invoicing), `vendor_id`.
* **Operational Fields:** `invoice_number`, `invoice_date`, `received_date`, `billed_quantity`, `billed_unit_price`, `tax_amount`, `payment_terms` (e.g. Net 30, 2/10 Net 60), `due_date`.
* **Verification Flags:** `is_maverick` (invoice before PO = 1.47%), `is_premature` (invoice before GR = 6.50%), `is_payment_blocked` (22.18%).

### Table 4: Bank Payments & Treasury Clearing (`banking_disbursements`)
* **Primary Key:** `payment_id`
* **Foreign Keys:** `invoice_id`, `vendor_id`, `bank_account_id`.
* **Transactional Fields:** `clearing_date`, `payment_method` (ACH, Wire, Check), `disbursed_amount`, `bank_reference`, `clearing_latency_days`.

### Table 5: General Ledger Journal Entries (`gl_journal_entries`)
* **Primary Key:** `journal_entry_id`
* **Foreign Keys:** `source_subledger_type` (`P2P`, `O2C`, `PAYROLL`, `BANKING`), `source_document_id` (`po_id`, `invoice_id`, `payment_id`).
* **Attributes:** `posting_date`, `fiscal_period`, `ledger_type` (Standard, Adjusting, Restatement), `total_debit`, `total_credit` ($\sum \text{Debit} \equiv \sum \text{Credit}$).

---

## 3. Step-by-Step Accounting Progression & T-Account Reconciliations

The table below traces the exact double-entry mechanics as a single procurement case transitions from an operational need to a cleared cash wire:

| Lifecycle Stage | Frontline Operational Event | Empirical Probability / Timing | Accounting Recognition Rule | Debit Account (Dr) | Credit Account (Cr) | Balance Sheet / P&L Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 0: Requisition** | Employee requests material | $P(\text{PR}) = 0.1851$ (Bypass = 81.49%) | No GAAP Recognition | None (Off-Balance Sheet) | None (Off-Balance Sheet) | No accounting footprint. |
| **Stage 1: PO Issuance** | Purchasing team issues PO to Vendor | Median lead time = 10.02 days | Executory Contract (ASC 440) | None (Commitment Note) | None (Commitment Note) | Unrecorded commitment. |
| **Stage 2: Goods Receipt** | Warehouse accepts 1,000 units at dock | $T_{\text{PO}\to\text{GR}} \sim \text{Lognormal}(2.305, 0.812)$ | Physical Title Transfer (ASC 330) | **Dr. Raw Materials Inventory** ($10,000) | **Cr. GR/IR Clearing Accrual** ($10,000) | Working Capital: Inventory expands; Current Liabilities expand. |
| **Stage 3: Invoice Arrival** | Vendor invoice arrives in mail/EDI | $T_{\text{GR}\to\text{IR}} \sim \text{Lognormal}(2.424, 0.875)$ | Legal Liability Established (ASC 405) | **Dr. GR/IR Clearing Accrual** ($10,000) | **Cr. Accounts Payable** ($10,000) | GR/IR cleared to zero; formal AP liability recorded. |
| **Stage 4: Tolerance Block** | SAP tolerance check flags price/qty variance | $P(\text{Block}) = \mathbf{0.2218}$ (Hold: Median 6.18d, P95 81.1d) | Liability Locked; Cash Disallowance | No entry (Status flag locked in subledger) | No entry (Status flag locked in subledger) | Working Capital: DPO artificially stretched; cash preserved. |
| **Stage 5: AP Release** | AP clerk clears discrepancy override | Unblock trigger: 68% manual override | Invoice released to payment run | No entry (Flag set to 'Approved') | No entry (Flag set to 'Approved') | Queue transferred to Treasury. |
| **Stage 6: Bank Clearing** | Treasury runs ACH payment batch | $T_{\text{IR}\to\text{Clear}} \sim \text{Lognormal}(3.739, 0.582)$ | Settlement & Extinguishment | **Dr. Accounts Payable** ($10,000) | **Cr. Cash & Cash Equivalents** ($10,000) | Cash drops; AP drops; Net Working Capital returns to baseline. |

---

## 4. How Operational Friction Propagates into Financial Statement Distortions

When operations experience friction, the errors do not remain contained in the warehouse or procurement desk; they propagate directly into distorted financial statements:

```mermaid
sequenceDiagram
    autonumber
    actor Supplier as Supplier / Freight
    actor Warehouse as Warehouse (GR)
    actor AP as Accounts Payable
    actor Treasury as Treasury (Bank)
    actor GL as General Ledger
    actor Auditor as QoE Diligence Auditor

    Supplier->>Warehouse: Ships goods with 5.81-day carrier SLA delay
    Warehouse->>AP: Records Goods Receipt at dock
    Supplier->>AP: Invoices with 5% price variance ($10,500 vs $10,000 PO)
    Note over AP: SAP 3-Way Match Fails!<br/>Payment Block Set (p = 0.2218)
    AP--xTreasury: Invoice blocked from payment run (Hold: 81.1 days)
    Note over Treasury: Cash remains in Bank account!<br/>DPO artificially stretches from 42d to 81d
    Treasury->>GL: Period-End Close: High AP + High Cash reported
    GL->>Auditor: Financials show strong Operating Cash Flow
    Auditor->>Auditor: Forensic Normalization:<br/>Unwinds DPO stretch (-$500k cash adjustment)<br/>Re-establishes normalized working capital peg!
```

### Disconnect A: The Maverick Buying Unrecorded Liability Trap
* **Operational Failure:** Employee orders $250,000 in software consulting without a Purchase Order.
* **Accounting Propagation:** Because no PO exists, the warehouse cannot record a Goods Receipt, and the accounting software has no GR/IR accrual.
* **Period-End Distortion:** At quarter-end, the company closes its books. Reported operating expenses are understated by $250k, and accounts payable is understated by $250k.
* **QoE Red Flag:** When the vendor invoice eventually arrives post-close (the 1.47% maverick inversion), it must be booked retroactively, wiping out the prior quarter's reported profit.

### Disconnect B: The Premature Invoicing Cut-off Error
* **Operational Failure:** Vendor issues an invoice on December 28th for goods that will not physically arrive until January 8th (the 6.50% premature invoicing rate).
* **Accounting Propagation:** AP enters the invoice into the system before Goods Receipt. If the ERP system defaults to booking the expense immediately, the company records cost of sales before title transfer has occurred.
* **Period-End Distortion:** Violates the matching principle and ASC 606 revenue/expense cut-off rules.

### Disconnect C: The Logistics Delay $\to$ Cash Deficit $\to$ Loan Default Chain
* **Operational Trigger:** Freight carrier misses SLA by 29.6 days (P95 logistics delay).
* **Commercial Consequence:** Customer refuses shipment and demands an 8.41% credit note adjustment.
* **Treasury Shock:** Anticipated $500,000 cash collection does not arrive in the bank account.
* **Banking Default Propagation:** Bank cashbook balance breaches zero into an authorized overdraft (6.40% hazard). Under the empirical **100% deterministic overdraft-to-default rule**, the company fails its quarterly debt service covenant, triggering credit default reclassification on the balance sheet.

---

## 5. Summary Specification for Cross-Subledger Simulation Validation

When building the simulator, the cross-subledger reconciliation engine must enforce the following five mathematical invariance checks on every simulation tick:

1. **The Three-Way Match Balance Check:**
   $$\text{Quantity}_{\text{PO}} \ge \text{Quantity}_{\text{GR}} \ge \text{Quantity}_{\text{IR}}$$
   *(Violations must trigger the empirical 22.18% Payment Block state machine).*
2. **The GR/IR Clearing Account Invariant:**
   $$\text{Balance}(\text{GR/IR Clearing}) = \sum \text{Goods Receipts} - \sum \text{Invoice Receipts}$$
   *(Must resolve to exactly zero upon matching).*
3. **The Cash-to-Disbursement Invariant:**
   $$\text{Ending Cash} = \text{Beginning Cash} + \sum \text{Customer Receipts} - \sum \text{Vendor Clearings} - \sum \text{Payroll}$$
4. **The Working Capital Peg Formula:**
   $$\text{NWC} = (\text{AR} + \text{Inventory} + \text{Contract Assets}) - (\text{AP} + \text{Accrued Liabilities})$$
5. **The Benford Procurement Audit Check:**
   $$\text{MAD}(\text{PO Spend First Digits}) \le 0.012 \quad (\text{Nigrini Acceptable Conformity})$$

---
*Specification permanently archived for cross-subledger simulation implementation.*
