"""
Order-to-Cash (O2C) Empirical Signal Extraction & Mathematical Modeling
========================================================================
Extracts empirical signals, customer concentration metrics, credit note dilution rates,
operational lead time distributions, and SLA breach hazards from:
1. UCI Online Retail Dataset (541,909 invoice SKU lines)
2. Brazilian E-Commerce (Olist) Logistics Dataset (99,441 orders)
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
from collections import Counter

uci_path = r"research\original_datasets\revenue_commercial\uci_online_retail\online_retail.csv"
olist_path = r"research\original_datasets\operational_performance\olist_orders_dataset.csv"
output_dir = r"research\o2c_signals"
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("ORDER-TO-CASH (O2C) EMPIRICAL SIGNAL EXTRACTION")
print("=" * 80)
sys.stdout.flush()

# ==============================================================================
# PART 1: UCI ONLINE RETAIL REVENUE & COMMERCIAL SIGNAL EXTRACTION
# ==============================================================================
print("\n[PART 1] Loading and Analyzing UCI Online Retail Dataset (541k records)...")
sys.stdout.flush()
t0 = time.time()

# Load UCI dataset
df_uci = pd.read_csv(uci_path, encoding='latin1', low_memory=False)
print(f"Loaded {len(df_uci):,} records in {time.time()-t0:.2f}s.")
sys.stdout.flush()

# Parse datetime
df_uci['dt'] = pd.to_datetime(df_uci['InvoiceDate'], errors='coerce')

# Convert numeric
df_uci['Quantity'] = pd.to_numeric(df_uci['Quantity'], errors='coerce')
df_uci['UnitPrice'] = pd.to_numeric(df_uci['UnitPrice'], errors='coerce')

# Calculate Line Total Revenue
df_uci['LineTotal'] = df_uci['Quantity'] * df_uci['UnitPrice']

# Identify Credit Notes / Cancellations ('C' prefix in InvoiceNo or Quantity < 0)
df_uci['InvoiceNo_str'] = df_uci['InvoiceNo'].astype(str).str.strip()
df_uci['is_credit_note'] = df_uci['InvoiceNo_str'].str.startswith('C') | (df_uci['Quantity'] < 0)

# Clean subsets
sales_df = df_uci[~df_uci['is_credit_note']].copy()
credit_df = df_uci[df_uci['is_credit_note']].copy()

# Total gross revenue and credit note dilution
gross_revenue = float(sales_df[sales_df['LineTotal'] > 0]['LineTotal'].sum())
# Note: credit note line totals are negative, so take abs for sum
credit_note_total = float(abs(credit_df['LineTotal'].sum()))
net_revenue = gross_revenue - credit_note_total
dilution_rate_pct = (credit_note_total / gross_revenue) * 100.0 if gross_revenue > 0 else 0.0

total_invoices = df_uci['InvoiceNo_str'].nunique()
sales_invoices = sales_df['InvoiceNo_str'].nunique()
credit_invoices = credit_df['InvoiceNo_str'].nunique()
credit_invoice_pct = (credit_invoices / total_invoices) * 100.0 if total_invoices > 0 else 0.0

print(f"  Gross Invoiced Revenue: £{gross_revenue:,.2f}")
print(f"  Credit Notes & Returns: £{credit_note_total:,.2f} ({dilution_rate_pct:.2f}% dilution)")
print(f"  Net Recognized Revenue: £{net_revenue:,.2f}")
print(f"  Total Invoices: {total_invoices:,} (Sales: {sales_invoices:,}, Credit Notes: {credit_invoices:,} = {credit_invoice_pct:.2f}%)")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# Customer Revenue & Concentration (Pareto & HHI)
# ------------------------------------------------------------------------------
print("Analyzing Customer Concentration & Repeat Behaviors...")
sys.stdout.flush()

# Customer Identification Analysis
records_with_cust = df_uci['CustomerID'].notnull().sum()
records_without_cust = df_uci['CustomerID'].isnull().sum()
rev_with_cust = float(sales_df[sales_df['CustomerID'].notnull()]['LineTotal'].sum())
rev_without_cust = float(sales_df[sales_df['CustomerID'].isnull()]['LineTotal'].sum())

# Net customer spend (Gross - Returns per customer)
cust_grouped = df_uci.dropna(subset=['CustomerID']).groupby('CustomerID').agg(
    gross_spend=('LineTotal', lambda x: x[x > 0].sum()),
    credit_spend=('LineTotal', lambda x: abs(x[x < 0].sum())),
    net_spend=('LineTotal', 'sum'),
    invoice_count=('InvoiceNo_str', 'nunique'),
    first_order=('dt', 'min'),
    last_order=('dt', 'max')
)

total_cust_net_rev = cust_grouped['net_spend'].sum()
sorted_cust_spends = cust_grouped['net_spend'].sort_values(ascending=False).values
num_custs = len(sorted_cust_spends)

top_1_cust_spend = sum(sorted_cust_spends[:int(max(1, num_custs * 0.01))]) / total_cust_net_rev * 100.0
top_5_cust_spend = sum(sorted_cust_spends[:int(max(1, num_custs * 0.05))]) / total_cust_net_rev * 100.0
top_10_cust_spend = sum(sorted_cust_spends[:int(max(1, num_custs * 0.10))]) / total_cust_net_rev * 100.0
top_20_cust_spend = sum(sorted_cust_spends[:int(max(1, num_custs * 0.20))]) / total_cust_net_rev * 100.0

# Herfindahl-Hirschman Index (HHI) for customers
# s_i is percentage share (0 to 100)
cust_hhi = sum([((s / total_cust_net_rev) * 100)**2 for s in sorted_cust_spends if s > 0]) if total_cust_net_rev > 0 else 0

# Repeat vs One-time customers
one_time_custs = (cust_grouped['invoice_count'] == 1).sum()
repeat_custs = (cust_grouped['invoice_count'] > 1).sum()
repeat_cust_pct = (repeat_custs / num_custs) * 100.0

# Inter-purchase interval (repeat purchase latency) for repeat customers
repeat_cust_ids = cust_grouped[cust_grouped['invoice_count'] > 1].index
invoice_dates = sales_df.dropna(subset=['CustomerID']).groupby(['CustomerID', 'InvoiceNo_str'])['dt'].first().reset_index()
invoice_dates = invoice_dates.sort_values(by=['CustomerID', 'dt'])
invoice_dates['prev_dt'] = invoice_dates.groupby('CustomerID')['dt'].shift(1)
invoice_dates['inter_purchase_days'] = (invoice_dates['dt'] - invoice_dates['prev_dt']).dt.total_seconds() / 86400.0
inter_purchase_clean = invoice_dates['inter_purchase_days'].dropna()
inter_purchase_clean = inter_purchase_clean[(inter_purchase_clean >= 0) & (inter_purchase_clean <= 365)]

# Invoice basket size (SKUs per invoice) and Invoice value distribution
invoice_stats = sales_df.groupby('InvoiceNo_str').agg(
    skus_count=('StockCode', 'count'),
    invoice_value=('LineTotal', 'sum')
)
inv_val_clean = invoice_stats['invoice_value'][invoice_stats['invoice_value'] > 0]
skus_clean = invoice_stats['skus_count']

# Country distribution
country_dist = sales_df.groupby('Country')['LineTotal'].sum().sort_values(ascending=False)
top_countries = {str(k): round(float(v), 2) for k, v in country_dist.head(10).items()}
uk_revenue_share_pct = (country_dist.get('United Kingdom', 0) / gross_revenue) * 100.0

def calc_stats_series(series):
    if len(series) == 0:
        return None
    return {
        'count': int(len(series)),
        'mean': round(float(series.mean()), 2),
        'median': round(float(series.median()), 2),
        'std': round(float(series.std()), 2),
        'min': round(float(series.min()), 2),
        'p25': round(float(series.quantile(0.25)), 2),
        'p75': round(float(series.quantile(0.75)), 2),
        'p95': round(float(series.quantile(0.95)), 2),
        'max': round(float(series.max()), 2)
    }

uci_metrics = {
    'total_records': len(df_uci),
    'revenue_summary_gbp': {
        'gross_invoiced_revenue': round(gross_revenue, 2),
        'credit_notes_and_returns': round(credit_note_total, 2),
        'net_recognized_revenue': round(net_revenue, 2),
        'credit_dilution_rate_pct': round(dilution_rate_pct, 2)
    },
    'invoice_counts': {
        'total_invoices': total_invoices,
        'sales_invoices': sales_invoices,
        'credit_invoices': credit_invoices,
        'credit_invoice_share_pct': round(credit_invoice_pct, 2)
    },
    'customer_identification': {
        'records_with_customer_id': int(records_with_cust),
        'records_without_customer_id': int(records_without_cust),
        'revenue_with_customer_id': round(rev_with_cust, 2),
        'revenue_without_customer_id': round(rev_without_cust, 2),
        'unidentified_revenue_share_pct': round((rev_without_cust / gross_revenue) * 100.0, 2)
    },
    'customer_concentration': {
        'unique_identified_customers': num_custs,
        'herfindahl_hirschman_index_hhi': round(cust_hhi, 2),
        'top_1_pct_customers_share': round(top_1_cust_spend, 2),
        'top_5_pct_customers_share': round(top_5_cust_spend, 2),
        'top_10_pct_customers_share': round(top_10_cust_spend, 2),
        'top_20_pct_customers_share': round(top_20_cust_spend, 2),
        'one_time_buyers_count': int(one_time_custs),
        'repeat_buyers_count': int(repeat_custs),
        'repeat_buyer_rate_pct': round(repeat_cust_pct, 2)
    },
    'invoice_size_distributions': {
        'skus_per_invoice': calc_stats_series(skus_clean),
        'monetary_value_per_invoice_gbp': calc_stats_series(inv_val_clean),
        'repeat_order_inter_purchase_latency_days': calc_stats_series(inter_purchase_clean)
    },
    'geographic_distribution': {
        'uk_domestic_share_pct': round(uk_revenue_share_pct, 2),
        'top_10_countries': top_countries
    }
}

print(f"  Customer Concentration: HHI = {cust_hhi:.2f}, Top 20% Customers Hold: {top_20_cust_spend:.2f}%")
print(f"  Repeat Customer Rate: {repeat_cust_pct:.2f}% ({repeat_custs:,} repeat vs {one_time_custs:,} one-time)")
print(f"  Repeat Purchase Latency: Median={uci_metrics['invoice_size_distributions']['repeat_order_inter_purchase_latency_days']['median']}d, Mean={uci_metrics['invoice_size_distributions']['repeat_order_inter_purchase_latency_days']['mean']}d")
print(f"  Unidentified / Guest Revenue: {uci_metrics['customer_identification']['unidentified_revenue_share_pct']}% of Gross Revenue")
sys.stdout.flush()

with open(os.path.join(output_dir, "uci_retail_o2c_metrics.json"), "w") as f:
    json.dump(uci_metrics, f, indent=2)


# ==============================================================================
# PART 2: OLIST LOGISTICS ORDER-TO-CASH SIGNAL EXTRACTION
# ==============================================================================
print("\n[PART 2] Loading and Analyzing Brazilian E-Commerce (Olist) Logistics (99k orders)...")
sys.stdout.flush()
t1 = time.time()

df_olist = pd.read_csv(olist_path)
print(f"Loaded {len(df_olist):,} orders in {time.time()-t1:.2f}s.")
sys.stdout.flush()

# Parse timestamps
ts_cols = [
    'order_purchase_timestamp', 'order_approved_at',
    'order_delivered_carrier_date', 'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in ts_cols:
    df_olist[col + '_dt'] = pd.to_datetime(df_olist[col], errors='coerce')

# Status distribution
status_dist = df_olist['order_status'].value_counts().to_dict()
status_dist_pct = {k: round(v / len(df_olist) * 100.0, 2) for k, v in status_dist.items()}

# Attrition / Cancellation Rate
canceled_count = status_dist.get('canceled', 0)
unavailable_count = status_dist.get('unavailable', 0)
attrition_count = canceled_count + unavailable_count
attrition_rate_pct = (attrition_count / len(df_olist)) * 100.0

# ------------------------------------------------------------------------------
# Order-to-Cash Fulfillment Latencies (Hazard Distributions)
# ------------------------------------------------------------------------------
print("Computing Order Fulfillment Latency Hazards & SLA Breaches...")
sys.stdout.flush()

# 1. Payment Authorization Latency: purchase -> approved (in hours)
auth_latency_hrs = (df_olist['order_approved_at_dt'] - df_olist['order_purchase_timestamp_dt']).dt.total_seconds() / 3600.0
auth_clean_hrs = auth_latency_hrs[(auth_latency_hrs >= 0) & (auth_latency_hrs <= 24 * 30)]

# 2. Warehouse Fulfillment Latency: approved -> carrier handover (in days)
fulfill_latency_days = (df_olist['order_delivered_carrier_date_dt'] - df_olist['order_approved_at_dt']).dt.total_seconds() / 86400.0
fulfill_clean_days = fulfill_latency_days[(fulfill_latency_days >= 0) & (fulfill_latency_days <= 90)]

# 3. Carrier Transit Latency: carrier handover -> customer delivery (in days)
transit_latency_days = (df_olist['order_delivered_customer_date_dt'] - df_olist['order_delivered_carrier_date_dt']).dt.total_seconds() / 86400.0
transit_clean_days = transit_latency_days[(transit_latency_days >= 0) & (transit_latency_days <= 90)]

# 4. Total Order-to-Delivery Lead Time: purchase -> customer delivery (in days)
total_o2c_days = (df_olist['order_delivered_customer_date_dt'] - df_olist['order_purchase_timestamp_dt']).dt.total_seconds() / 86400.0
total_o2c_clean = total_o2c_days[(total_o2c_days >= 0) & (total_o2c_days <= 120)]

# 5. SLA Contractual Breach: delivered vs estimated delivery date (in days)
# Positive means LATE (delivered after SLA date), Negative means EARLY
delivered_orders = df_olist.dropna(subset=['order_delivered_customer_date_dt', 'order_estimated_delivery_date_dt']).copy()
sla_diff_days = (delivered_orders['order_delivered_customer_date_dt'] - delivered_orders['order_estimated_delivery_date_dt']).dt.total_seconds() / 86400.0

sla_breach_count = (sla_diff_days > 0).sum()
on_time_count = (sla_diff_days <= 0).sum()
sla_breach_rate_pct = (sla_breach_count / len(delivered_orders)) * 100.0

# Late delivery delay severity (only for late orders)
late_delay_clean = sla_diff_days[sla_diff_days > 0]
early_lead_clean = abs(sla_diff_days[sla_diff_days <= 0])

olist_metrics = {
    'total_orders': len(df_olist),
    'order_status_distribution': status_dist,
    'order_status_percentage': status_dist_pct,
    'attrition_cancellation_rate_pct': round(attrition_rate_pct, 2),
    'fulfillment_latencies': {
        'payment_authorization_latency_hours': calc_stats_series(auth_clean_hrs),
        'warehouse_fulfillment_latency_days': calc_stats_series(fulfill_clean_days),
        'carrier_transit_latency_days': calc_stats_series(transit_clean_days),
        'end_to_end_order_to_delivery_days': calc_stats_series(total_o2c_clean)
    },
    'sla_performance': {
        'total_delivered_evaluated': int(len(delivered_orders)),
        'on_time_deliveries_count': int(on_time_count),
        'sla_breach_late_count': int(sla_breach_count),
        'sla_breach_rate_pct': round(sla_breach_rate_pct, 2),
        'on_time_rate_pct': round(100.0 - sla_breach_rate_pct, 2),
        'late_delivery_delay_days': calc_stats_series(late_delay_clean),
        'early_delivery_lead_days': calc_stats_series(early_lead_clean)
    }
}

print(f"  Delivered Orders: {len(delivered_orders):,} / {len(df_olist):,} ({status_dist_pct.get('delivered', 0)}%)")
print(f"  Order Attrition Rate (Canceled/Unavailable): {attrition_rate_pct:.2f}%")
print(f"  SLA Breach (Late Delivery) Rate: {sla_breach_rate_pct:.2f}% ({sla_breach_count:,} late orders)")
print(f"  Late Delivery Severity: Median={olist_metrics['sla_performance']['late_delivery_delay_days']['median']}d, Mean={olist_metrics['sla_performance']['late_delivery_delay_days']['mean']}d late")
print(f"  End-to-End Delivery Time: Median={olist_metrics['fulfillment_latencies']['end_to_end_order_to_delivery_days']['median']}d, Mean={olist_metrics['fulfillment_latencies']['end_to_end_order_to_delivery_days']['mean']}d")
sys.stdout.flush()

with open(os.path.join(output_dir, "olist_logistics_o2c_metrics.json"), "w") as f:
    json.dump(olist_metrics, f, indent=2)

print("\n" + "=" * 80)
print("ORDER-TO-CASH SIGNAL EXTRACTION COMPLETED SUCCESSFULLY")
print("=" * 80)
sys.stdout.flush()
