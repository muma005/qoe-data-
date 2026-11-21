# Technical Dataset Inspection: Brazilian E-Commerce (Olist) Logistics & Fulfillment

## 1. Metadata and Provenance
- **Dataset Title:** Brazilian E-Commerce Public Dataset by Olist (Orders & Logistics Subledger)
- **Originating Organization:** Olist Marketplace Platform (Curitiba, Brazil)
- **Primary Source / Host:** Kaggle / Olist Public Release (`https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce`)
- **Authenticity Category:** Real-World, Anonymized (Authentic marketplace orders and carrier tracking records across Brazil).
- **Physical File on Disk:** [olist_orders_dataset.csv](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/original_datasets/operational_performance/olist_orders_dataset.csv) (17,654,914 bytes / 17.6 MB)

---

## 2. Structural Dimensions & Field Inventory
- **Total Order Records:** 99,441 commercial orders
- **Temporal Span:** Operational transactions from `2016-09-04 21:15:19` to `2018-10-17 17:30:18` (2+ years)
- **Order Status Distribution:**
  - `delivered`: 96,478 orders (**97.02%**)
  - `shipped`: 1,107 orders (**1.11%**)
  - `canceled`: 625 orders (**0.63%**)
  - `unavailable`: 609 orders (**0.61%**)
  - `invoiced`: 314 orders (**0.32%**)
  - `processing`: 301 orders (**0.30%**)
  - `created`: 5 orders (**0.01%**)
  - `approved`: 2 orders (**0.00%**)

### Core Lifecycle Milestone Attributes:
| Attribute | Semantic Role | Quality / Coverage |
| :--- | :--- | :--- |
| `order_id` | Unique Order Primary Key | 99,441 non-null |
| `customer_id` | Transactional Customer Identifier | 99,441 non-null |
| `order_status` | Current Operational State | 99,441 non-null |
| `order_purchase_timestamp` | Customer Checkout Timestamp ($t_{\text{order}}$) | 99,441 non-null |
| `order_approved_at` | Payment Gateway Approval Timestamp ($t_{\text{approval}}$) | 99,281 non-null (160 null) |
| `order_delivered_carrier_date` | Carrier Handover / Dispatch Timestamp ($t_{\text{carrier}}$) | 97,658 non-null (1,783 null) |
| `order_delivered_customer_date` | Actual Customer Delivery Timestamp ($t_{\text{delivered}}$) | 96,476 non-null (2,965 null) |
| `order_estimated_delivery_date` | Contractual Estimated Delivery SLA ($t_{\text{SLA}}$) | 99,441 non-null |

---

## 3. Empirical Operational Lead Times & Fulfillment Latencies
Across 96,476 fulfilled orders, the empirical operational durations (in calendar days or hours) are:

| Operational Lead Time Stage | Metric Definition | Median | Mean | Std Dev | P25 | P75 | P95 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Payment Authorization** | $t_{\text{approval}} - t_{\text{order}}$ (Hours) | **0.34h** | 10.32h | 20.60h | 0.21h | 14.57h | 48.42h |
| **Warehouse Fulfillment** | $t_{\text{carrier}} - t_{\text{approval}}$ (Days) | **1.85d** | 2.86d | 3.45d | 0.90d | 3.62d | 8.16d |
| **Carrier Transit** | $t_{\text{delivered}} - t_{\text{carrier}}$ (Days) | **7.10d** | 9.24d | 8.01d | 4.10d | 12.02d | 24.12d |
| **Total Order-to-Delivery** | $t_{\text{delivered}} - t_{\text{order}}$ (Days) | **10.21d** | 12.49d | 8.99d | 6.76d | 15.71d | 29.21d |

---

## 4. Contractual SLA Performance & Delivery Delay Hazards
In Quality of Earnings and operational due diligence, fulfillment performance directly governs customer retention, warranty reserves, and dispute chargeback rates:
- **Total Delivered Orders Evaluated:** 96,476
- **On-Time Deliveries:** 88,649 (**91.89%**)
- **Contractual SLA Breaches (Late Deliveries):** 7,827 (**8.11%**)
- **Late Delivery Delay Severity ($\Delta t_{\text{late}} = t_{\text{delivered}} - t_{\text{SLA}}$):**
  - $\text{Median} = \mathbf{5.81\text{ days late}}$
  - $\text{Mean} = 9.55\text{ days late}$
  - $\text{P25} = 1.87\text{ days late}$
  - $\text{P75} = 11.82\text{ days late}$
  - $\text{P95} = \mathbf{29.64\text{ days late}}$ (nearly 1 full month past SLA!)
- **Early Delivery Buffer ($\Delta t_{\text{early}} = t_{\text{SLA}} - t_{\text{delivered}}$):**
  - On-time orders are delivered a median of **12.32 days early** relative to the stated estimated delivery date, indicating a highly conservative SLA buffering strategy to manage customer expectations.

---

## 5. Order Attrition & Cancellation Rate
- **Total Non-Delivered Attrition:** 1,234 orders (**1.24%** of all placed orders).
  - Explicit Order Cancellations: 625 orders (0.63%)
  - Inventory Stockouts / Unfulfillable (`unavailable`): 609 orders (0.61%)
- In financial due diligence, this 1.24% operational breakage rate represents unfulfilled gross demand and inventory management failure that prevents top-line realization.
