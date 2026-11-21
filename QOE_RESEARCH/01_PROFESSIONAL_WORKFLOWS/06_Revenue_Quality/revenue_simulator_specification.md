# QoE Simulator Functional Specification — Revenue Quality Engine
**Document Reference:** `QOE-SPEC-SIM-06`  
**Workstream:** `06 — Revenue and Margin Quality`  
**Classification:** Technical Software Architecture & Simulation Blueprint  

---

## 1. System Architecture Overview

The Revenue Quality Engine models the dynamic interaction between a client selling products/services and a buy-side financial due diligence team auditing commercial sustainability:

```
+────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                  QOE REVENUE SIMULATOR ARCHITECTURE                                |
|                                                                                                    |
|   [CLIENT GENERATION ENGINE]                                                                       |
|   • Generates multi-year line-item sales subledgers, invoices, SKU pricing, and customer masters.  |
|   • Injects configurable commercial anomalies:                                                     |
|     - Period-end sales clustering ("hockey stick" billing pull-forwards).                          |
|     - ASC 606 cut-off timing errors (FOB Destination shipments billed prior to delivery).          |
|     - Disguised customer churn (silent attrition masked by aggressive new logo acquisition).       |
|     - Post-period credit memos reversing prior-year volume.                                        |
|     - Customer margin dispersion (loss-making accounts destroying value).                          |
|                                      │                                                             |
|                                      ▼ (Synthetic Sales Registers, Contracts, Carrier Logs)       |
|                                                                                                    |
|   [QOE EVALUATION & ADJUDICATION SUITE]                                                            |
|   • Module 1: Subledger-to-GL Tie-Out & Reconciliation Engine.                                     |
|   • Module 2: Automated Price-Volume-Mix (PVM) Decomposition Engine.                               |
|   • Module 3: Multi-Year Vintage Cohort & Retention Generator (GRR/NRR).                           |
|   • Module 4: Concentration & Herfindahl-Hirschman Index (HHI) Analyzer.                           |
|   • Module 5: Customer Profitability Whale Curve & Cost-to-Serve Allocator.                        |
|   • Module 6: Contract Audit & Backlog Verification Module.                                        |
|   • Module 7: Master Revenue & Margin Bridge Generator.                                            |
+────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Client Generation Engine: Anomaly Injection Parameters

The generator simulates realistic corporate behavior by parameterizing commercial stress and revenue manipulation:

| Anomaly Code | Commercial Phenomenon | Generation Mechanism & Injection Rules | Detection Trigger & Audit Test |
| :--- | :--- | :--- | :--- |
| **`ANOM-REV-01`** | **Quarter-End Hockey Stick** | Concentrates $35\% - 45\%$ of quarterly sales into the final 5 calendar days; shifts payment terms from Net 30 to Net 90. | Daily billing distribution analysis; DSO divergence. |
| **`ANOM-REV-02`** | **ASC 606 Cut-Off Acceleration** | Issues sales invoices on Dec 30/31 with FOB Destination terms, while scheduling carrier dispatch for Jan 4–8. | Cut-off testing matching invoice date to carrier Bill of Lading (BOL). |
| **`ANOM-REV-03`** | **Concealed Customer Churn** | Generates high top-line growth through 50+ small new accounts while 3 anchor accounts quietly reduce volume by 60%. | Vintage cohort analysis; Gross Revenue Retention (GRR) degradation. |
| **`ANOM-REV-04`** | **Post-Period Credit Memos** | Issues large credit memos in Jan/Feb of subsequent year citing "billing pricing corrections" for December shipments. | 90-day post-period credit memo audit. |
| **`ANOM-REV-05`** | **Value-Destroying Whale Curve** | Introduces 20% of customer accounts that require heavy subsidized freight and high return scrap, resulting in negative margins. | Cost-to-serve allocation and cumulative margin curve ranking. |
| **`ANOM-REV-06`** | **Unearned Rebate Accruals** | Credits gross revenue with top-tier vendor volume rebates despite actual annual purchase volumes missing required contractual tiers. | Vendor contract tier audit and tier threshold matching. |

---

## 3. Relational Database Schema Specification

The simulator data layer is structured using relational tables implemented in SQL:

```sql
-- Table 1: Customer Master
CREATE TABLE CustomerMaster (
    customer_id VARCHAR(20) PRIMARY KEY,
    parent_customer_id VARCHAR(20),
    customer_name VARCHAR(100) NOT NULL,
    business_division VARCHAR(50) NOT NULL,
    industry_sector VARCHAR(50),
    acquisition_year INT NOT NULL,
    standard_payment_terms VARCHAR(20) DEFAULT 'Net 30',
    credit_limit DECIMAL(15,2),
    account_status VARCHAR(20) CHECK (account_status IN ('Active', 'At-Risk', 'Churned', 'Expanding'))
);

-- Table 2: Product & SKU Master
CREATE TABLE ProductSkuMaster (
    sku_id VARCHAR(20) PRIMARY KEY,
    sku_code VARCHAR(50) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL,
    base_unit_price DECIMAL(15,4) NOT NULL,
    standard_unit_cost DECIMAL(15,4) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Table 3: Sales Invoice Line Items (Transactional Subledger)
CREATE TABLE SalesInvoiceLine (
    invoice_line_id VARCHAR(30) PRIMARY KEY,
    invoice_number VARCHAR(30) NOT NULL,
    invoice_date DATE NOT NULL,
    customer_id VARCHAR(20) NOT NULL REFERENCES CustomerMaster(customer_id),
    sku_id VARCHAR(20) NOT NULL REFERENCES ProductSkuMaster(sku_id),
    shipped_quantity DECIMAL(15,4) NOT NULL,
    unit_selling_price DECIMAL(15,4) NOT NULL,
    gross_line_amount DECIMAL(15,2) NOT NULL,
    line_discount_amount DECIMAL(15,2) DEFAULT 0.00,
    net_line_amount DECIMAL(15,2) NOT NULL,
    carrier_tracking_number VARCHAR(50),
    shipping_terms VARCHAR(30) CHECK (shipping_terms IN ('FOB Destination', 'FOB Shipping Point', 'Drop-Ship')),
    carrier_pickup_date DATE,
    carrier_delivery_date DATE,
    gl_account_code VARCHAR(20) NOT NULL
);

-- Table 4: Commercial Contracts & MSAs
CREATE TABLE CommercialContract (
    contract_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES CustomerMaster(customer_id),
    contract_start_date DATE NOT NULL,
    contract_expiration_date DATE NOT NULL,
    termination_notice_days INT NOT NULL,
    has_minimum_volume_commitment BOOLEAN DEFAULT FALSE,
    committed_annual_volume DECIMAL(15,2),
    has_price_escalator BOOLEAN DEFAULT FALSE,
    escalator_index_type VARCHAR(50),
    has_mfn_clause BOOLEAN DEFAULT FALSE,
    governing_law VARCHAR(50)
);

-- Table 5: Customer Cohort Vintage Matrix
CREATE TABLE CustomerCohortVintage (
    cohort_id VARCHAR(20) PRIMARY KEY,
    vintage_year INT NOT NULL,
    fiscal_period VARCHAR(10) NOT NULL,
    active_logo_count INT NOT NULL,
    period_revenue DECIMAL(15,2) NOT NULL,
    gross_revenue_retention_pct DECIMAL(6,3),
    net_revenue_retention_pct DECIMAL(6,3),
    annual_churn_rate_pct DECIMAL(6,3)
);

-- Table 6: Master Revenue Bridge Line Items
CREATE TABLE RevenueBridgeLineItem (
    bridge_line_id VARCHAR(20) PRIMARY KEY,
    engagement_id VARCHAR(20) NOT NULL,
    line_item_order INT NOT NULL,
    line_item_name VARCHAR(100) NOT NULL,
    fy21_amount DECIMAL(15,2) NOT NULL,
    fy22_amount DECIMAL(15,2) NOT NULL,
    fy23_amount DECIMAL(15,2) NOT NULL,
    ltm_amount DECIMAL(15,2) NOT NULL,
    bridge_category VARCHAR(30) CHECK (bridge_category IN ('Reported Baseline', 'QoE Cut', 'Normalized Baseline', 'Run-Rate Shift', 'Pro-Forma Underwritten'))
);
```

---

## 4. QoE Evaluation Suite: Algorithmic Specifications

### 4.1 Automated Price-Volume-Mix (PVM) Engine
```python
def calculate_pvm_decomposition(df_base, df_current):
    """
    Computes exact Paasche-Laspeyres Price, Volume, and Mix decomposition.
    df_base and df_current must contain columns: ['product_category', 'units', 'revenue']
    """
    # 1. Merge base and current periods on category
    merged = df_base.merge(df_current, on='product_category', suffixes=('_base', '_curr'))
    
    # 2. Compute category unit prices
    merged['price_base'] = merged['revenue_base'] / merged['units_base']
    merged['price_curr'] = merged['revenue_curr'] / merged['units_curr']
    
    # 3. Overall portfolio averages
    total_units_base = merged['units_base'].sum()
    total_units_curr = merged['units_curr'].sum()
    total_rev_base = merged['revenue_base'].sum()
    total_rev_curr = merged['revenue_curr'].sum()
    avg_price_base = total_rev_base / total_units_base
    
    # 4. Calculate PVM components
    price_effect = (merged['units_curr'] * (merged['price_curr'] - merged['price_base'])).sum()
    volume_effect = (total_units_curr - total_units_base) * avg_price_base
    
    # Mix effect = Remaining delta to ensure exact footing
    total_revenue_delta = total_rev_curr - total_rev_base
    mix_effect = total_revenue_delta - price_effect - volume_effect
    
    return {
        'total_revenue_delta': total_revenue_delta,
        'price_effect': price_effect,
        'volume_effect': volume_effect,
        'mix_effect': mix_effect,
        'is_reconciled': abs(total_revenue_delta - (price_effect + volume_effect + mix_effect)) < 0.01
    }
```

### 4.2 Cut-Off Anomaly Detection Algorithm
```python
def audit_revenue_cutoff(sales_lines_df, year_end_date):
    """
    Identifies FOB Destination shipments invoiced prior to year-end with delivery in subsequent year.
    """
    anomalies = sales_lines_df[
        (sales_lines_df['shipping_terms'] == 'FOB Destination') &
        (sales_lines_df['invoice_date'] <= year_end_date) &
        (sales_lines_df['carrier_delivery_date'] > year_end_date)
    ]
    
    haircut_revenue = anomalies['net_line_amount'].sum()
    return {
        'flagged_invoices': anomalies['invoice_number'].tolist(),
        'haircut_revenue': haircut_revenue,
        'recommendation': 'Reverse revenue and matching COGS via mandatory QoE deduction.'
    }
```
