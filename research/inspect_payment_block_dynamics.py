import pandas as pd
import numpy as np
from collections import Counter

bpi_path = r"research\original_datasets\procurement_expenses\bpi_2019\BPI_Challenge_2019.csv"
cols = ['case concept:name', 'case Vendor', 'case Item Category', 'event concept:name', 'event time:timestamp', 'event Cumulative net worth (EUR)']

print("Analyzing payment block dynamics and unblocking triggers...")
df = pd.read_csv(bpi_path, usecols=cols, encoding='latin1', low_memory=False)
df.columns = [c.strip() for c in df.columns]

# Parse timestamps
df['dt'] = pd.to_datetime(df['event time:timestamp'], format='%d-%m-%Y %H:%M:%S.%f', errors='coerce')
df = df.dropna(subset=['case concept:name', 'dt']).sort_values(by=['case concept:name', 'dt']).reset_index(drop=True)

# Cases with payment block removal
block_cases = df[df['event concept:name'] == 'Remove Payment Block']['case concept:name'].unique()
print(f"Total Cases with 'Remove Payment Block': {len(block_cases):,} / {df['case concept:name'].nunique():,} ({len(block_cases)/df['case concept:name'].nunique()*100:.2f}%)")

# What event immediately precedes 'Remove Payment Block'?
df['prev_case'] = df['case concept:name'].shift(1)
df['prev_activity'] = df['event concept:name'].shift(1)

sub_blocks = df[(df['event concept:name'] == 'Remove Payment Block') & (df['case concept:name'] == df['prev_case'])]
print("\nEvent immediately PRECEDING 'Remove Payment Block':")
print(sub_blocks['prev_activity'].value_counts().head(10))

# Trace timeline for blocked cases:
# Latency between 'Record Invoice Receipt' and 'Remove Payment Block'
ts_ir = df[df['event concept:name'] == 'Record Invoice Receipt'].groupby('case concept:name')['dt'].first()
ts_unblock = df[df['event concept:name'] == 'Remove Payment Block'].groupby('case concept:name')['dt'].first()
ts_clear = df[df['event concept:name'] == 'Clear Invoice'].groupby('case concept:name')['dt'].first()

b_df = pd.DataFrame(index=block_cases)
b_df['t_ir'] = ts_ir
b_df['t_unblock'] = ts_unblock
b_df['t_clear'] = ts_clear

both_ir_unblock = b_df.dropna(subset=['t_ir', 't_unblock'])
block_duration_days = (both_ir_unblock['t_unblock'] - both_ir_unblock['t_ir']).dt.total_seconds() / 86400.0
clean_duration = block_duration_days[(block_duration_days >= 0) & (block_duration_days <= 365)]

print("\n--- Latency: Time under Payment Block (Invoice Receipt -> Remove Payment Block) ---")
print(f"Count: {len(clean_duration):,}")
print(f"Mean: {clean_duration.mean():.2f} days")
print(f"Median: {clean_duration.median():.2f} days")
print(f"P25: {clean_duration.quantile(0.25):.2f} days")
print(f"P75: {clean_duration.quantile(0.75):.2f} days")
print(f"P95: {clean_duration.quantile(0.95):.2f} days")

# Vendor analysis for blocks
vendor_total_cases = df.groupby('case Vendor')['case concept:name'].nunique()
vendor_blocked_cases = df[df['case concept:name'].isin(block_cases)].groupby('case Vendor')['case concept:name'].nunique()

vendor_block_stats = pd.DataFrame({
    'total_cases': vendor_total_cases,
    'blocked_cases': vendor_blocked_cases
}).fillna(0)
vendor_block_stats['block_rate_pct'] = (vendor_block_stats['blocked_cases'] / vendor_block_stats['total_cases']) * 100.0
# filter vendors with at least 50 cases
v_sig = vendor_block_stats[vendor_block_stats['total_cases'] >= 50].sort_values(by='block_rate_pct', ascending=False)

print("\nTop 10 Vendors by Payment Block Rate (min 50 cases):")
print(v_sig.head(10))
