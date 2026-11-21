"""
Fast & Vectorized P2P Signal Extraction & Mathematical Modeling
===============================================================
Extracts empirical signals, transition matrices, latency hazard distributions,
and anomaly rates from:
1. AkzoNobel BPI Challenge 2019 SAP ERP event log (1.59M events, 251K cases)
2. Kenyan PPIP Public Procurement Dataset (Active tenders & procurement controls)
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
from collections import defaultdict, Counter

bpi_path = r"research\original_datasets\procurement_expenses\bpi_2019\BPI_Challenge_2019.csv"
kenya_csv = r"research\original_datasets\procurement_expenses\kenya_procurement\kenya_tenders_flattened.csv"
output_dir = r"research\p2p_signals"
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("PURCHASE-TO-PAY (P2P) EMPIRICAL SIGNAL EXTRACTION (VECTORIZED)")
print("=" * 80)
sys.stdout.flush()

# ==============================================================================
# PART 1: KENYAN PUBLIC PROCUREMENT SIGNAL EXTRACTION
# ==============================================================================
print("\n[PART 1] Analyzing Kenyan PPIP Public Procurement Signals...")
sys.stdout.flush()
kdf = pd.read_csv(kenya_csv)

# Parse timestamps
kdf['published_dt'] = pd.to_datetime(kdf['published_at'], errors='coerce')
kdf['close_dt'] = pd.to_datetime(kdf['close_at'], errors='coerce')
kdf['created_dt'] = pd.to_datetime(kdf['created_at'], errors='coerce')

# Calculate tender notice window (advertising latency) in days
kdf['notice_days'] = (kdf['close_dt'] - kdf['published_dt']).dt.total_seconds() / 86400.0

# Kenya Statutory Rules: Under Public Procurement and Asset Disposal Act (PPADA 2015) Sec 102,
# National open tenders require min 14 days, International open tenders min 21 or 30 days.
statutory_violation_count = int((kdf['notice_days'] < 14).sum())
statutory_violation_pct = float((statutory_violation_count / len(kdf)) * 100.0)

method_dist = kdf['procurement_method_title'].value_counts(dropna=False).to_dict()
cat_dist = kdf['procurement_category_title'].value_counts(dropna=False).to_dict()

# AGPO preference reservation
agpo_count = int(kdf['agpo_groups'].dropna().apply(lambda x: len(str(x).strip()) > 0).sum())
agpo_pct = float((agpo_count / len(kdf)) * 100.0)

# Addenda volatility
has_addenda = int((kdf['addenda_count'] > 0).sum())
has_addenda_pct = float((has_addenda / len(kdf)) * 100.0)

# Tender fees
free_tenders_pct = float((kdf['tender_fee'] == 0).sum() / len(kdf) * 100.0)

kenya_metrics = {
    'total_tenders': len(kdf),
    'procurement_methods': method_dist,
    'procurement_categories': cat_dist,
    'advertising_notice_days': {
        'mean': float(kdf['notice_days'].mean()),
        'median': float(kdf['notice_days'].median()),
        'min': float(kdf['notice_days'].min()),
        'max': float(kdf['notice_days'].max()),
        'std': float(kdf['notice_days'].std()),
        'p25': float(kdf['notice_days'].quantile(0.25)),
        'p75': float(kdf['notice_days'].quantile(0.75)),
        'statutory_short_notice_less_14d_pct': statutory_violation_pct
    },
    'validity_in_days': {
        'mean': float(kdf['validity_in_days'].mean()),
        'median': float(kdf['validity_in_days'].median()),
        'min': float(kdf['validity_in_days'].min()),
        'max': float(kdf['validity_in_days'].max()),
        'distribution': {str(k): int(v) for k, v in kdf['validity_in_days'].value_counts().items()}
    },
    'preference_reservation_pct': agpo_pct,
    'spec_volatility_addenda_pct': has_addenda_pct,
    'free_access_tender_fee_0_pct': free_tenders_pct,
    'top_procuring_entities': {str(k): int(v) for k, v in kdf['procuring_entity_name'].value_counts().head(10).items()}
}

print(f"  Tenders Analyzed: {kenya_metrics['total_tenders']}")
print(f"  Notice Days (Advertising): Median={kenya_metrics['advertising_notice_days']['median']:.1f}d, Mean={kenya_metrics['advertising_notice_days']['mean']:.1f}d")
print(f"  Short Notice (<14d violation rate): {kenya_metrics['advertising_notice_days']['statutory_short_notice_less_14d_pct']:.2f}%")
print(f"  AGPO Preference Reservation Rate: {kenya_metrics['preference_reservation_pct']:.2f}%")
print(f"  Addenda Modification Rate: {kenya_metrics['spec_volatility_addenda_pct']:.2f}%")
sys.stdout.flush()

with open(os.path.join(output_dir, "kenya_procurement_metrics.json"), "w") as f:
    json.dump(kenya_metrics, f, indent=2)


# ==============================================================================
# PART 2: BPI CHALLENGE 2019 SAP ERP SIGNAL EXTRACTION (VECTORIZED)
# ==============================================================================
print("\n[PART 2] Loading BPI 2019 SAP Event Log in full vectorized memory...")
sys.stdout.flush()
t0 = time.time()

# Columns to load
cols = [
    'case concept:name', 'case Item Category', 'case Spend area text',
    'case Vendor', 'event concept:name', 'event time:timestamp',
    'event Cumulative net worth (EUR)', 'event User'
]

# Read CSV fast
df = pd.read_csv(bpi_path, usecols=cols, encoding='latin1', low_memory=False)
df.columns = [c.strip() for c in df.columns]
print(f"Loaded {len(df):,} events in {time.time()-t0:.1f}s. Parsing timestamps vectorially...")
sys.stdout.flush()

# Vectorized datetime parse
t1 = time.time()
df['dt'] = pd.to_datetime(df['event time:timestamp'], format='%d-%m-%Y %H:%M:%S.%f', errors='coerce')
print(f"Parsed timestamps in {time.time()-t1:.1f}s ({df['dt'].notnull().sum():,} valid timestamps).")
sys.stdout.flush()

# Filter out rows with invalid timestamps or missing case names
df = df.dropna(subset=['case concept:name', 'dt']).copy()

# Sort strictly by case and datetime
t2 = time.time()
df = df.sort_values(by=['case concept:name', 'dt']).reset_index(drop=True)
print(f"Sorted dataset by case and timestamp in {time.time()-t2:.1f}s.")
sys.stdout.flush()

total_events = len(df)
unique_cases = df['case concept:name'].nunique()
unique_vendors = df['case Vendor'].nunique()
print(f"Total valid events: {total_events:,} across {unique_cases:,} cases and {unique_vendors:,} vendors.")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 1. Global Activity & Item Category Distributions
# ------------------------------------------------------------------------------
all_activities = df['event concept:name'].value_counts().to_dict()
item_categories = df['case Item Category'].value_counts().to_dict()

# ------------------------------------------------------------------------------
# 2. Vendor Spend & Concentration (HHI & Pareto)
# ------------------------------------------------------------------------------
# PO spend per vendor (using 'Create Purchase Order Item' cumulative net worth)
po_events = df[df['event concept:name'] == 'Create Purchase Order Item']
vendor_spends = po_events.groupby('case Vendor')['event Cumulative net worth (EUR)'].sum().to_dict()
total_spend = sum(vendor_spends.values())

sorted_spends = sorted(vendor_spends.values(), reverse=True)
top_1_spend = sum(sorted_spends[:int(len(sorted_spends)*0.01)]) / total_spend * 100.0 if total_spend > 0 else 0
top_5_spend = sum(sorted_spends[:int(len(sorted_spends)*0.05)]) / total_spend * 100.0 if total_spend > 0 else 0
top_20_spend = sum(sorted_spends[:int(len(sorted_spends)*0.20)]) / total_spend * 100.0 if total_spend > 0 else 0
hhi = sum([((s / total_spend) * 100)**2 for s in sorted_spends]) if total_spend > 0 else 0

print(f"Vendor Concentration: Total Spend = EUR {total_spend:,.2f}, HHI = {hhi:.2f}, Top 20% Spend Share = {top_20_spend:.2f}%")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 3. Vectorized Lifecycle Milestone Timestamps per Case
# ------------------------------------------------------------------------------
print("\nExtracting lifecycle milestones per case...")
sys.stdout.flush()
t3 = time.time()

# Extract first timestamp for critical events
def get_first_timestamps(activity_name):
    sub = df[df['event concept:name'] == activity_name]
    return sub.groupby('case concept:name')['dt'].first()

ts_po = get_first_timestamps('Create Purchase Order Item')
ts_gr = get_first_timestamps('Record Goods Receipt')
ts_ir = get_first_timestamps('Record Invoice Receipt')
ts_clear = get_first_timestamps('Clear Invoice')

# Collect activity flags per case
case_acts = df.groupby('case concept:name')['event concept:name'].agg(set)

# Build milestone dataframe
m_df = pd.DataFrame(index=df['case concept:name'].unique())
m_df['has_block'] = case_acts.apply(lambda s: 'Remove Payment Block' in s)
m_df['has_price_change'] = case_acts.apply(lambda s: 'Change Price' in s)
m_df['has_qty_change'] = case_acts.apply(lambda s: 'Change Quantity' in s)

m_df['t_po'] = ts_po
m_df['t_gr'] = ts_gr
m_df['t_ir'] = ts_ir
m_df['t_clear'] = ts_clear

print(f"Milestones extracted in {time.time()-t3:.1f}s.")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 4. Control-Flow Deviations & Sequencing Anomalies
# ------------------------------------------------------------------------------
total_cases = len(m_df)

# Maverick Buying: Invoice Receipt occurs BEFORE PO Creation
both_po_ir = m_df.dropna(subset=['t_po', 't_ir'])
maverick_mask = both_po_ir['t_ir'] < both_po_ir['t_po']
maverick_count = int(maverick_mask.sum())
maverick_pct = float((maverick_count / total_cases) * 100.0)
maverick_lead_days = (both_po_ir.loc[maverick_mask, 't_po'] - both_po_ir.loc[maverick_mask, 't_ir']).dt.total_seconds() / 86400.0
# filter extreme historical legacy dates (> 365d)
maverick_lead_filtered = maverick_lead_days[(maverick_lead_days >= 0) & (maverick_lead_days <= 365)]

# Invoicing before Goods Receipt
both_gr_ir = m_df.dropna(subset=['t_gr', 't_ir'])
ir_before_gr_mask = both_gr_ir['t_ir'] < both_gr_ir['t_gr']
ir_before_gr_count = int(ir_before_gr_mask.sum())
ir_before_gr_pct = float((ir_before_gr_count / total_cases) * 100.0)

# Payment block rate
payment_block_cases = int(m_df['has_block'].sum())
payment_block_pct = float((payment_block_cases / total_cases) * 100.0)

# Retroactive changes
price_change_cases = int(m_df['has_price_change'].sum())
price_change_pct = float((price_change_cases / total_cases) * 100.0)

qty_change_cases = int(m_df['has_qty_change'].sum())
qty_change_pct = float((qty_change_cases / total_cases) * 100.0)

# ------------------------------------------------------------------------------
# 5. Cycle Time & Latency Distributions (Hazard Functions)
# ------------------------------------------------------------------------------
# Delivery Lead Time: PO -> GR
both_po_gr = m_df.dropna(subset=['t_po', 't_gr'])
po_to_gr_days = (both_po_gr['t_gr'] - both_po_gr['t_po']).dt.total_seconds() / 86400.0
po_to_gr_clean = po_to_gr_days[(po_to_gr_days >= 0) & (po_to_gr_days <= 365)]

# Invoicing Latency: GR -> IR
gr_to_ir_days = (both_gr_ir.loc[~ir_before_gr_mask, 't_ir'] - both_gr_ir.loc[~ir_before_gr_mask, 't_gr']).dt.total_seconds() / 86400.0
gr_to_ir_clean = gr_to_ir_days[(gr_to_ir_days >= 0) & (gr_to_ir_days <= 365)]

# Payment Clearing Latency: IR -> Clear
both_ir_clear = m_df.dropna(subset=['t_ir', 't_clear'])
ir_to_clear_days = (both_ir_clear['t_clear'] - both_ir_clear['t_ir']).dt.total_seconds() / 86400.0
ir_to_clear_clean = ir_to_clear_days[(ir_to_clear_days >= 0) & (ir_to_clear_days <= 365)]

def calc_stats(series):
    if len(series) == 0:
        return None
    return {
        'count': int(len(series)),
        'mean': round(float(series.mean()), 2),
        'median': round(float(series.median()), 2),
        'std': round(float(series.std()), 2),
        'p25': round(float(series.quantile(0.25)), 2),
        'p75': round(float(series.quantile(0.75)), 2),
        'p95': round(float(series.quantile(0.95)), 2)
    }

# ------------------------------------------------------------------------------
# 6. Price Creep & Delta Distribution
# ------------------------------------------------------------------------------
price_chg_sub = df[df['case concept:name'].isin(m_df[m_df['has_price_change']].index)]
price_first = price_chg_sub.groupby('case concept:name')['event Cumulative net worth (EUR)'].first()
price_last = price_chg_sub.groupby('case concept:name')['event Cumulative net worth (EUR)'].last()
valid_p = (price_first > 0) & (price_last > 0)
price_delta_pct = ((price_last[valid_p] - price_first[valid_p]) / price_first[valid_p]) * 100.0
price_delta_clean = price_delta_pct[(price_delta_pct >= -100) & (price_delta_pct <= 500)]

# ------------------------------------------------------------------------------
# 7. Markov Transition Matrix across Top Activities
# ------------------------------------------------------------------------------
print("Computing Markov Transition Matrix across 1.59M events...")
sys.stdout.flush()
t4 = time.time()

# Shift activity within case
df['next_case'] = df['case concept:name'].shift(-1)
df['next_activity'] = df['event concept:name'].shift(-1)

# Valid transitions are where next_case == curr_case
valid_trans = df[df['case concept:name'] == df['next_case']]
trans_matrix_raw = pd.crosstab(valid_trans['event concept:name'], valid_trans['next_activity'], normalize='index')
markov_dict = {k: {dst: round(float(v), 4) for dst, v in row.items() if v > 0.005} for k, row in trans_matrix_raw.iterrows()}
print(f"Markov matrix generated in {time.time()-t4:.1f}s.")
sys.stdout.flush()

# Assemble Full BPI 2019 Metrics Dictionary
bpi_metrics = {
    'total_events_in_dataset': total_events,
    'total_cases_analyzed': total_cases,
    'unique_vendors_total': unique_vendors,
    'vendor_concentration': {
        'total_spend_eur': round(total_spend, 2),
        'herfindahl_hirschman_index_hhi': round(hhi, 2),
        'top_1_pct_vendors_spend_share': round(top_1_spend, 2),
        'top_5_pct_vendors_spend_share': round(top_5_spend, 2),
        'top_20_pct_vendors_spend_share': round(top_20_spend, 2),
    },
    'control_flow_deviation_rates': {
        'maverick_buying_ir_before_po_rate_pct': round(maverick_pct, 2),
        'maverick_cases_count': maverick_count,
        'ir_before_gr_rate_pct': round(ir_before_gr_pct, 2),
        'ir_before_gr_cases_count': ir_before_gr_count,
        'payment_block_unblocking_rate_pct': round(payment_block_pct, 2),
        'payment_block_cases_count': payment_block_cases,
        'retroactive_price_change_rate_pct': round(price_change_pct, 2),
        'retroactive_price_change_cases_count': price_change_cases,
        'retroactive_quantity_change_rate_pct': round(qty_change_pct, 2),
        'retroactive_quantity_change_cases_count': qty_change_cases,
    },
    'latency_distributions_days': {
        'po_to_gr_delivery_lead_time': calc_stats(po_to_gr_clean),
        'gr_to_ir_invoicing_latency': calc_stats(gr_to_ir_clean),
        'ir_to_clear_payment_latency': calc_stats(ir_to_clear_clean),
        'maverick_invoice_precedence_lead_days': calc_stats(maverick_lead_filtered)
    },
    'price_drift_impact': {
        'mean_price_delta_pct': round(float(price_delta_clean.mean()), 2) if len(price_delta_clean) > 0 else None,
        'median_price_delta_pct': round(float(price_delta_clean.median()), 2) if len(price_delta_clean) > 0 else None,
        'positive_creep_share_pct': round(float((price_delta_clean > 0).mean() * 100.0), 2) if len(price_delta_clean) > 0 else None
    },
    'activity_distribution': {str(k): int(v) for k, v in all_activities.items()},
    'item_category_distribution': {str(k): int(v) for k, v in item_categories.items()},
    'markov_transition_probabilities': markov_dict
}

with open(os.path.join(output_dir, "bpi_2019_p2p_metrics.json"), "w") as f:
    json.dump(bpi_metrics, f, indent=2)

print("\n" + "=" * 80)
print("P2P EMPIRICAL SIGNAL RESULTS (EXHAUSTIVE 251,734 CASES)")
print("=" * 80)
print(f"Total Cases: {total_cases:,}")
print(f"Vendor HHI Concentration: {bpi_metrics['vendor_concentration']['herfindahl_hirschman_index_hhi']} (Top 20% Vendors Hold: {bpi_metrics['vendor_concentration']['top_20_pct_vendors_spend_share']}%)")
print(f"Maverick Buying Rate (Invoice Receipt < PO Creation): {bpi_metrics['control_flow_deviation_rates']['maverick_buying_ir_before_po_rate_pct']}% ({maverick_count:,} cases)")
print(f"Premature Invoicing (Invoice Receipt < Goods Receipt): {bpi_metrics['control_flow_deviation_rates']['ir_before_gr_rate_pct']}% ({ir_before_gr_count:,} cases)")
print(f"Payment Block Rate (Set/Remove Payment Block): {bpi_metrics['control_flow_deviation_rates']['payment_block_unblocking_rate_pct']}% ({payment_block_cases:,} cases)")
print(f"Retroactive Price Change Rate: {bpi_metrics['control_flow_deviation_rates']['retroactive_price_change_rate_pct']}% ({price_change_cases:,} cases)")
print(f"Retroactive Quantity Change Rate: {bpi_metrics['control_flow_deviation_rates']['retroactive_quantity_change_rate_pct']}% ({qty_change_cases:,} cases)")
print(f"Fulfillment Delivery Lead Time (PO -> GR): Median={bpi_metrics['latency_distributions_days']['po_to_gr_delivery_lead_time']['median']}d, Mean={bpi_metrics['latency_distributions_days']['po_to_gr_delivery_lead_time']['mean']}d")
print(f"Invoicing Latency (GR -> IR): Median={bpi_metrics['latency_distributions_days']['gr_to_ir_invoicing_latency']['median']}d, Mean={bpi_metrics['latency_distributions_days']['gr_to_ir_invoicing_latency']['mean']}d")
print(f"Payment Clearing Latency (IR -> Clear): Median={bpi_metrics['latency_distributions_days']['ir_to_clear_payment_latency']['median']}d, Mean={bpi_metrics['latency_distributions_days']['ir_to_clear_payment_latency']['mean']}d")
print("=" * 80)
sys.stdout.flush()
