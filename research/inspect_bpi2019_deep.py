import os
import time
import pandas as pd
import numpy as np
from collections import Counter

bpi_path = r"research\original_datasets\procurement_expenses\bpi_2019\BPI_Challenge_2019.csv"

print("Starting deep inspection of BPI Challenge 2019 SAP ERP event log...")
t0 = time.time()

# Let's inspect columns first
sample = pd.read_csv(bpi_path, nrows=5, encoding='latin1')
cols = [c.strip() for c in sample.columns]
print("Cleaned Columns:", cols)

# Read necessary columns in chunks to optimize memory and speed
chunksize = 250000
total_events = 0
cases = set()
purch_docs = set()
vendors = set()
companies = set()
event_counts = Counter()
item_categories = Counter()
spend_areas = Counter()
doc_types = Counter()
users = Counter()

# Track sequence anomalies across cases
# Sample 10,000 cases to do exact trace timeline analysis
sample_case_events = {}
tracked_cases = set()
sample_limit = 15000

for chunk_idx, chunk in enumerate(pd.read_csv(bpi_path, chunksize=chunksize, low_memory=False, encoding='latin1')):
    chunk.columns = [c.strip() for c in chunk.columns]
    total_events += len(chunk)
    
    cases.update(chunk['case concept:name'].dropna().unique())
    purch_docs.update(chunk['case Purchasing Document'].dropna().unique())
    vendors.update(chunk['case Vendor'].dropna().unique())
    companies.update(chunk['case Company'].dropna().unique())
    
    event_counts.update(chunk['event concept:name'].value_counts().to_dict())
    item_categories.update(chunk['case Item Category'].value_counts().to_dict())
    spend_areas.update(chunk['case Spend area text'].value_counts().to_dict())
    doc_types.update(chunk['case Document Type'].value_counts().to_dict())
    users.update(chunk['event User'].value_counts().to_dict())
    
    # Collect events for sampled cases
    if len(tracked_cases) < sample_limit:
        new_cases = chunk['case concept:name'].unique()[:sample_limit - len(tracked_cases)]
        tracked_cases.update(new_cases)
        
    subset = chunk[chunk['case concept:name'].isin(tracked_cases)]
    for _, row in subset[['case concept:name', 'event concept:name', 'event time:timestamp', 'event Cumulative net worth (EUR)']].iterrows():
        cid = row['case concept:name']
        if cid not in sample_case_events:
            sample_case_events[cid] = []
        sample_case_events[cid].append((
            row['event concept:name'],
            row['event time:timestamp'],
            row['event Cumulative net worth (EUR)']
        ))
        
    print(f"Processed chunk {chunk_idx+1}: {total_events:,} events scanned ({time.time()-t0:.1f}s)...")

print(f"\nInspection complete in {time.time()-t0:.1f}s!")
print(f"Total Events: {total_events:,}")
print(f"Total Unique Cases (PO Line Items): {len(cases):,}")
print(f"Total Unique Purchasing Documents (POs): {len(purch_docs):,}")
print(f"Total Unique Vendors: {len(vendors):,}")
print(f"Total Unique Companies (Subsidiaries): {len(companies):,}")

print("\n--- Top Event Types (Control-flow activities) ---")
for evt, count in event_counts.most_common(20):
    pct = (count / total_events) * 100
    print(f"  {evt:<35}: {count:>8,} ({pct:>5.2f}%)")

print("\n--- Item Categories (Matching Rules) ---")
for cat, count in item_categories.most_common():
    print(f"  {cat:<35}: {count:>8,}")

print("\n--- Top Document Types ---")
for dt, count in doc_types.most_common(5):
    print(f"  {dt:<35}: {count:>8,}")

print("\n--- Top Spend Areas ---")
for sa, count in spend_areas.most_common(5):
    print(f"  {sa:<35}: {count:>8,}")

print("\n--- Top User Types (Automation vs Human) ---")
for u, count in users.most_common(10):
    print(f"  {u:<35}: {count:>8,}")
