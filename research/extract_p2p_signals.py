"""
Comprehensive P2P Signal Extraction & Mathematical Modeling
===========================================================
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
print("PURCHASE-TO-PAY (P2P) EMPIRICAL SIGNAL EXTRACTION")
print("=" * 80)

# ==============================================================================
# PART 1: KENYAN PUBLIC PROCUREMENT SIGNAL EXTRACTION
# ==============================================================================
print("\n[PART 1] Analyzing Kenyan PPIP Public Procurement Signals...")
kdf = pd.read_csv(kenya_csv)

# Parse timestamps
kdf['published_dt'] = pd.to_datetime(kdf['published_at'], errors='coerce')
kdf['close_dt'] = pd.to_datetime(kdf['close_at'], errors='coerce')
kdf['created_dt'] = pd.to_datetime(kdf['created_at'], errors='coerce')

# Calculate tender notice window (advertising latency) in days
kdf['notice_days'] = (kdf['close_dt'] - kdf['published_dt']).dt.total_seconds() / 86400.0

# Kenya Statutory Rules: Under Public Procurement and Asset Disposal Act (PPADA 2015) Sec 102,
# National open tenders require min 14 days, International open tenders min 21 or 30 days.
statutory_violation_count = (kdf['notice_days'] < 14).sum()
statutory_violation_pct = (statutory_violation_count / len(kdf)) * 100.0

# Method breakdown
method_dist = kdf['procurement_method_title'].value_counts(dropna=False).to_dict()
cat_dist = kdf['procurement_category_title'].value_counts(dropna=False).to_dict()

# AGPO preference reservation
agpo_count = kdf['agpo_groups'].dropna().apply(lambda x: len(str(x).strip()) > 0).sum()
agpo_pct = (agpo_count / len(kdf)) * 100.0

# Addenda volatility
has_addenda = (kdf['addenda_count'] > 0).sum()
has_addenda_pct = (has_addenda / len(kdf)) * 100.0

# Tender fees
free_tenders_pct = (kdf['tender_fee'] == 0).sum() / len(kdf) * 100.0

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
        'statutory_short_notice_less_14d_pct': float(statutory_violation_pct)
    },
    'validity_in_days': {
        'mean': float(kdf['validity_in_days'].mean()),
        'median': float(kdf['validity_in_days'].median()),
        'min': float(kdf['validity_in_days'].min()),
        'max': float(kdf['validity_in_days'].max()),
        'distribution': kdf['validity_in_days'].value_counts().to_dict()
    },
    'preference_reservation_pct': float(agpo_pct),
    'spec_volatility_addenda_pct': float(has_addenda_pct),
    'free_access_tender_fee_0_pct': float(free_tenders_pct),
    'top_procuring_entities': kdf['procuring_entity_name'].value_counts().head(10).to_dict()
}

print(f"  Tenders Analyzed: {kenya_metrics['total_tenders']}")
print(f"  Notice Days (Advertising): Median={kenya_metrics['advertising_notice_days']['median']:.1f}d, Mean={kenya_metrics['advertising_notice_days']['mean']:.1f}d")
print(f"  Short Notice (<14d violation rate): {kenya_metrics['advertising_notice_days']['statutory_short_notice_less_14d_pct']:.2f}%")
print(f"  AGPO Preference Reservation Rate: {kenya_metrics['preference_reservation_pct']:.2f}%")
print(f"  Addenda Modification Rate: {kenya_metrics['spec_volatility_addenda_pct']:.2f}%")

with open(os.path.join(output_dir, "kenya_procurement_metrics.json"), "w") as f:
    json.dump(kenya_metrics, f, indent=2)


# ==============================================================================
# PART 2: BPI CHALLENGE 2019 SAP ERP SIGNAL EXTRACTION
# ==============================================================================
print("\n[PART 2] Processing BPI 2019 SAP Event Log (1.59M rows)...")
t0 = time.time()

# We analyze full dataset in streaming chunks, tracking:
# 1. Trace sequences & transitions for all cases
# 2. Maverick buying (IR timestamp < PO timestamp)
# 3. 3-way match ordering (PO vs GR vs IR)
# 4. Payment blocks and unblocking triggers
# 5. Price and Quantity revisions
# 6. Cycle durations (PO->GR, GR->IR, IR->Clear)

# Data structures for accumulation
case_events = defaultdict(list)
vendor_spends = defaultdict(float)
vendor_cases = defaultdict(set)
vendor_blocks = defaultdict(int)
vendor_price_changes = defaultdict(int)
company_cases = defaultdict(set)
doc_type_counts = Counter()
item_cat_counts = Counter()
all_activities = Counter()

# Sample 50,000 cases for exhaustive chronological trace analysis
# (50,000 cases is a massive, statistically rigorous sample of 20% of all cases)
TARGET_SAMPLE_CASES = 50000
selected_cases = set()

chunk_count = 0
for chunk in pd.read_csv(bpi_path, chunksize=250000, encoding='latin1', low_memory=False):
    chunk_count += 1
    chunk.columns = [c.strip() for c in chunk.columns]
    
    # Clean activities
    act_counts = chunk['event concept:name'].value_counts()
    for act, cnt in act_counts.items():
        all_activities[act] += cnt
        
    for doc, cnt in chunk['case Document Type'].value_counts().items():
        doc_type_counts[doc] += cnt
        
    for cat, cnt in chunk['case Item Category'].value_counts().items():
        item_cat_counts[cat] += cnt
        
    # Vendor spend accumulation
    vendor_chunk = chunk[['case Vendor', 'event Cumulative net worth (EUR)', 'case concept:name', 'event concept:name']].dropna(subset=['case Vendor'])
    for row in vendor_chunk.itertuples(index=False):
        v = row[0]
        amt = row[1]
        cid = row[2]
        act = row[3]
        vendor_cases[v].add(cid)
        if act == 'Create Purchase Order Item' and pd.notnull(amt):
            vendor_spends[v] += float(amt)
        if act == 'Remove Payment Block':
            vendor_blocks[v] += 1
        if act == 'Change Price':
            vendor_price_changes[v] += 1

    # Select cases for deep chronological sequencing
    if len(selected_cases) < TARGET_SAMPLE_CASES:
        unique_c = chunk['case concept:name'].dropna().unique()
        needed = TARGET_SAMPLE_CASES - len(selected_cases)
        selected_cases.update(unique_c[:needed])
        
    # Collect chronological events for selected cases
    sub = chunk[chunk['case concept:name'].isin(selected_cases)][
        ['case concept:name', 'case Item Category', 'case Spend area text', 'case Vendor',
         'event concept:name', 'event time:timestamp', 'event Cumulative net worth (EUR)', 'event User']
    ]
    for row in sub.itertuples(index=False):
        cid, cat, spend, vend, act, ts, val, user = row
        case_events[cid].append({
            'activity': act,
            'timestamp': ts,
            'value': val if pd.notnull(val) else 0.0,
            'user': user,
            'category': cat,
            'vendor': vend,
            'spend_area': spend
        })
        
    print(f"  Chunk {chunk_count}: Scanned {chunk_count * 250000:,} events ({time.time()-t0:.1f}s)...")

print(f"\nTrace accumulation finished in {time.time()-t0:.1f}s! Analyzing {len(case_events):,} sampled cases...")

# ==============================================================================
# CHRONOLOGICAL TRACE & MARKOV TRANSITION ANALYSIS
# ==============================================================================
transitions = defaultdict(Counter)
start_activities = Counter()
end_activities = Counter()

# Metric accumulators
maverick_count = 0
ir_before_gr_count = 0
three_way_cases = 0
two_way_cases = 0
cases_with_gr = 0
cases_with_ir = 0
cases_with_clear = 0
cases_with_block = 0
cases_with_price_change = 0
cases_with_qty_change = 0

# Cycle times (in days)
po_to_gr_days = []
po_to_ir_days = []
gr_to_ir_days = []
ir_to_clear_days = []
maverick_negative_days = []
price_delta_pcts = []

for cid, events in case_events.items():
    if not events:
        continue
        
    # Sort events chronologically
    # Timestamps are formatted as 'DD-MM-YYYY HH:MM:SS.fff'
    # Some legacy dummy dates exist (e.g. 1948); parse safely
    for e in events:
        try:
            e['dt'] = pd.to_datetime(e['timestamp'], format='%d-%m-%Y %H:%M:%S.%f', errors='coerce')
        except:
            e['dt'] = pd.NaT
            
    # Filter out null timestamps
    valid_events = [e for e in events if pd.notnull(e['dt'])]
    if not valid_events:
        continue
        
    # Sort strictly by timestamp
    valid_events.sort(key=lambda x: x['dt'])
    
    # Trace transitions
    start_activities[valid_events[0]['activity']] += 1
    end_activities[valid_events[-1]['activity']] += 1
    for i in range(len(valid_events) - 1):
        a_curr = valid_events[i]['activity']
        a_next = valid_events[i+1]['activity']
        transitions[a_curr][a_next] += 1
        
    # Activity presence and timestamps
    act_map = defaultdict(list)
    for e in valid_events:
        act_map[e['activity']].append(e)
        
    has_po = 'Create Purchase Order Item' in act_map
    has_gr = 'Record Goods Receipt' in act_map
    has_ir = 'Record Invoice Receipt' in act_map
    has_clear = 'Clear Invoice' in act_map
    has_block = 'Remove Payment Block' in act_map
    has_price_change = 'Change Price' in act_map
    has_qty_change = 'Change Quantity' in act_map
    
    cat = valid_events[0]['category']
    if '3-way match' in str(cat):
        three_way_cases += 1
    elif '2-way match' in str(cat):
        two_way_cases += 1
        
    if has_gr: cases_with_gr += 1
    if has_ir: cases_with_ir += 1
    if has_clear: cases_with_clear += 1
    if has_block: cases_with_block += 1
    if has_price_change: cases_with_price_change += 1
    if has_qty_change: cases_with_qty_change += 1
    
    # 1. Maverick Buying Check: Invoice Receipt before PO Item Creation
    if has_po and has_ir:
        t_po = act_map['Create Purchase Order Item'][0]['dt']
        t_ir = act_map['Record Invoice Receipt'][0]['dt']
        
        # Inversion condition: Invoice arrived before PO was officially issued
        if t_ir < t_po:
            maverick_count += 1
            diff_days = (t_po - t_ir).total_seconds() / 86400.0
            if diff_days < 365:  # filter extreme outliers
                maverick_negative_days.append(diff_days)
        else:
            diff_days = (t_ir - t_po).total_seconds() / 86400.0
            if 0 <= diff_days < 365:
                po_to_ir_days.append(diff_days)
                
    # 2. 3-Way Match Check: IR before GR vs GR before IR
    if has_gr and has_ir:
        t_gr = act_map['Record Goods Receipt'][0]['dt']
        t_ir = act_map['Record Invoice Receipt'][0]['dt']
        if t_ir < t_gr:
            ir_before_gr_count += 1
        else:
            diff_days = (t_ir - t_gr).total_seconds() / 86400.0
            if 0 <= diff_days < 365:
                gr_to_ir_days.append(diff_days)
                
    # 3. Fulfillment Delivery Lead Time (PO -> GR)
    if has_po and has_gr:
        t_po = act_map['Create Purchase Order Item'][0]['dt']
        t_gr = act_map['Record Goods Receipt'][0]['dt']
        diff_days = (t_gr - t_po).total_seconds() / 86400.0
        if 0 <= diff_days < 365:
            po_to_gr_days.append(diff_days)
            
    # 4. Payment Clearing Duration (IR -> Clear)
    if has_ir and has_clear:
        t_ir = act_map['Record Invoice Receipt'][0]['dt']
        t_clear = act_map['Clear Invoice'][0]['dt']
        diff_days = (t_clear - t_ir).total_seconds() / 86400.0
        if 0 <= diff_days < 365:
            ir_to_clear_days.append(diff_days)
            
    # 5. Price Creep / Volatility
    if has_price_change:
        v_first = valid_events[0]['value']
        v_last = valid_events[-1]['value']
        if v_first > 0 and v_last > 0:
            delta_pct = ((v_last - v_first) / v_first) * 100.0
            if -100 <= delta_pct <= 500:
                price_delta_pcts.append(delta_pct)

# Convert transitions to Markov Transition Probabilities
markov_matrix = {}
for src, targets in transitions.items():
    total_out = sum(targets.values())
    markov_matrix[src] = {dst: round(cnt / total_out, 4) for dst, cnt in targets.most_common(10)}

# Calculate Vendor Concentration (HHI & Top Shares)
total_spend = sum(vendor_spends.values())
sorted_spends = sorted(vendor_spends.values(), reverse=True)
top_1_spend = sum(sorted_spends[:int(len(sorted_spends)*0.01)]) / total_spend * 100.0 if total_spend > 0 else 0
top_5_spend = sum(sorted_spends[:int(len(sorted_spends)*0.05)]) / total_spend * 100.0 if total_spend > 0 else 0
top_20_spend = sum(sorted_spends[:int(len(sorted_spends)*0.20)]) / total_spend * 100.0 if total_spend > 0 else 0

# Herfindahl-Hirschman Index (HHI)
# s_i is percentage share (0 to 100)
hhi = sum([((s / total_spend) * 100)**2 for s in sorted_spends]) if total_spend > 0 else 0

# Summary Metrics Dict
bpi_metrics = {
    'total_events_in_dataset': sum(all_activities.values()),
    'sampled_cases_analyzed': len(case_events),
    'unique_vendors_total': len(vendor_cases),
    'vendor_concentration': {
        'total_spend_eur': round(total_spend, 2),
        'herfindahl_hirschman_index_hhi': round(hhi, 2),
        'top_1_pct_vendors_spend_share': round(top_1_spend, 2),
        'top_5_pct_vendors_spend_share': round(top_5_spend, 2),
        'top_20_pct_vendors_spend_share': round(top_20_spend, 2),
    },
    'control_flow_deviation_rates': {
        'maverick_buying_ir_before_po_rate_pct': round((maverick_count / len(case_events)) * 100.0, 2),
        'maverick_cases_count': maverick_count,
        'ir_before_gr_rate_pct': round((ir_before_gr_count / len(case_events)) * 100.0, 2),
        'payment_block_unblocking_rate_pct': round((cases_with_block / len(case_events)) * 100.0, 2),
        'retroactive_price_change_rate_pct': round((cases_with_price_change / len(case_events)) * 100.0, 2),
        'retroactive_quantity_change_rate_pct': round((cases_with_qty_change / len(case_events)) * 100.0, 2),
    },
    'latency_distributions_days': {
        'po_to_gr_delivery_lead_time': {
            'mean': round(float(np.mean(po_to_gr_days)), 2) if po_to_gr_days else None,
            'median': round(float(np.median(po_to_gr_days)), 2) if po_to_gr_days else None,
            'p25': round(float(np.percentile(po_to_gr_days, 25)), 2) if po_to_gr_days else None,
            'p75': round(float(np.percentile(po_to_gr_days, 75)), 2) if po_to_gr_days else None,
            'p95': round(float(np.percentile(po_to_gr_days, 95)), 2) if po_to_gr_days else None,
        },
        'gr_to_ir_invoicing_latency': {
            'mean': round(float(np.mean(gr_to_ir_days)), 2) if gr_to_ir_days else None,
            'median': round(float(np.median(gr_to_ir_days)), 2) if gr_to_ir_days else None,
            'p25': round(float(np.percentile(gr_to_ir_days, 25)), 2) if gr_to_ir_days else None,
            'p75': round(float(np.percentile(gr_to_ir_days, 75)), 2) if gr_to_ir_days else None,
            'p95': round(float(np.percentile(gr_to_ir_days, 95)), 2) if gr_to_ir_days else None,
        },
        'ir_to_clear_payment_latency': {
            'mean': round(float(np.mean(ir_to_clear_days)), 2) if ir_to_clear_days else None,
            'median': round(float(np.median(ir_to_clear_days)), 2) if ir_to_clear_days else None,
            'p25': round(float(np.percentile(ir_to_clear_days, 25)), 2) if ir_to_clear_days else None,
            'p75': round(float(np.percentile(ir_to_clear_days, 75)), 2) if ir_to_clear_days else None,
            'p95': round(float(np.percentile(ir_to_clear_days, 95)), 2) if ir_to_clear_days else None,
        },
        'maverick_invoice_precedence_lead_days': {
            'mean': round(float(np.mean(maverick_negative_days)), 2) if maverick_negative_days else None,
            'median': round(float(np.median(maverick_negative_days)), 2) if maverick_negative_days else None,
        }
    },
    'price_drift_impact': {
        'mean_price_delta_pct': round(float(np.mean(price_delta_pcts)), 2) if price_delta_pcts else None,
        'median_price_delta_pct': round(float(np.median(price_delta_pcts)), 2) if price_delta_pcts else None,
        'positive_creep_share_pct': round(float(np.mean([p > 0 for p in price_delta_pcts]) * 100.0), 2) if price_delta_pcts else None
    },
    'markov_transition_probabilities': markov_matrix
}

with open(os.path.join(output_dir, "bpi_2019_p2p_metrics.json"), "w") as f:
    json.dump(bpi_metrics, f, indent=2)

print("\n" + "=" * 80)
print("P2P EMPIRICAL SIGNAL RESULTS")
print("=" * 80)
print(f"Sampled Cases Analyzed: {len(case_events):,}")
print(f"Vendor HHI Concentration: {bpi_metrics['vendor_concentration']['herfindahl_hirschman_index_hhi']} (Top 20% Vendors Hold: {bpi_metrics['vendor_concentration']['top_20_pct_vendors_spend_share']}%)")
print(f"Maverick Buying Rate (Invoice Receipt < PO Creation): {bpi_metrics['control_flow_deviation_rates']['maverick_buying_ir_before_po_rate_pct']}% ({maverick_count:,} cases)")
print(f"Premature Invoicing (Invoice Receipt < Goods Receipt): {bpi_metrics['control_flow_deviation_rates']['ir_before_gr_rate_pct']}%")
print(f"Payment Block Rate (Set/Remove Payment Block): {bpi_metrics['control_flow_deviation_rates']['payment_block_unblocking_rate_pct']}%")
print(f"Retroactive Price Change Rate: {bpi_metrics['control_flow_deviation_rates']['retroactive_price_change_rate_pct']}%")
print(f"Retroactive Quantity Change Rate: {bpi_metrics['control_flow_deviation_rates']['retroactive_quantity_change_rate_pct']}%")
print(f"Fulfillment Delivery Lead Time (PO -> GR): Median={bpi_metrics['latency_distributions_days']['po_to_gr_delivery_lead_time']['median']}d, Mean={bpi_metrics['latency_distributions_days']['po_to_gr_delivery_lead_time']['mean']}d")
print(f"Invoicing Latency (GR -> IR): Median={bpi_metrics['latency_distributions_days']['gr_to_ir_invoicing_latency']['median']}d, Mean={bpi_metrics['latency_distributions_days']['gr_to_ir_invoicing_latency']['mean']}d")
print(f"Payment Clearing Latency (IR -> Clear): Median={bpi_metrics['latency_distributions_days']['ir_to_clear_payment_latency']['median']}d, Mean={bpi_metrics['latency_distributions_days']['ir_to_clear_payment_latency']['mean']}d")
print("=" * 80)
