import os
import json
import pandas as pd
import numpy as np

kenya_csv = r"research\original_datasets\procurement_expenses\kenya_procurement\kenya_tenders_flattened.csv"
df = pd.read_csv(kenya_csv)

df['published_dt'] = pd.to_datetime(df['published_at'], errors='coerce')
df['close_dt'] = pd.to_datetime(df['close_at'], errors='coerce')
df['notice_days'] = (df['close_dt'] - df['published_dt']).dt.total_seconds() / 86400.0

print("=" * 80)
print("DEEP ANALYSIS OF KENYAN PUBLIC PROCUREMENT SIGNALS")
print("=" * 80)

print("\n1. Advertising Notice Days by Procurement Category:")
for cat, sub in df.groupby('procurement_category_title'):
    print(f"  Category: {cat:<25} | Count: {len(sub):>3} | Mean: {sub['notice_days'].mean():>5.1f}d | Median: {sub['notice_days'].median():>5.1f}d | <14d Violation: {(sub['notice_days']<14).mean()*100:>5.1f}%")

print("\n2. AGPO Preference Group Distribution:")
agpo_series = df['agpo_groups'].dropna()
print(f"  Tenders reserved for AGPO: {len(agpo_series)} / {len(df)} ({len(agpo_series)/len(df)*100:.1f}%)")
agpo_breakdown = df['agpo_groups'].value_counts()
print(agpo_breakdown)

print("\n3. Tender Fees and Commercial Barriers:")
fee_counts = df['tender_fee'].value_counts()
print(f"  Tenders with fee = 0 (Free Download): {(df['tender_fee'] == 0).sum()} ({(df['tender_fee'] == 0).mean()*100:.1f}%)")
print(f"  Tenders with fee > 0 (Pay-to-Bid): {(df['tender_fee'] > 0).sum()} ({(df['tender_fee'] > 0).mean()*100:.1f}%)")
if (df['tender_fee'] > 0).sum() > 0:
    fee_sub = df[df['tender_fee'] > 0]['tender_fee']
    print(f"  Fee Stats for Pay-to-Bid (KES): Mean={fee_sub.mean():,.2f}, Median={fee_sub.median():,.2f}, Min={fee_sub.min():,.2f}, Max={fee_sub.max():,.2f}")

print("\n4. Specification Amendments (Addenda Volatility):")
print(f"  Tenders with Amendments/Addenda: {(df['addenda_count'] > 0).sum()} ({(df['addenda_count'] > 0).mean()*100:.1f}%)")
print(f"  Total Addenda Issued across callset: {df['addenda_count'].sum()}")

print("\n5. Procuring Entity Concentration:")
pe_counts = df['procuring_entity_name'].value_counts()
print(f"  Total Unique Entities: {df['procuring_entity_name'].nunique()}")
print(f"  Top 5 Entities Share: {pe_counts.head(5).sum()} / {len(df)} ({pe_counts.head(5).sum()/len(df)*100:.1f}%)")
for pe, cnt in pe_counts.head(5).items():
    print(f"    - {pe}: {cnt} tenders ({cnt/len(df)*100:.1f}%)")
