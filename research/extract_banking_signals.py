"""
Working Capital, Cash Movements & Credit Risk Signal Extraction
==============================================================
Extracts empirical signals, cashflow volatility, authorized overdraft dynamics,
and loan default hazard rates from the Czech Bank Berka Database (1.05M trans, 682 loans).
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd

czech_dir = r"research\original_datasets\working_capital_banking\czech_bank"
output_dir = r"research\banking_signals"
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("WORKING CAPITAL, CASH MOVEMENTS & CREDIT RISK SIGNAL EXTRACTION")
print("=" * 80)
sys.stdout.flush()

t0 = time.time()
print("\n[PART 1] Loading Czech Bank Database Tables...")
sys.stdout.flush()

trans_df = pd.read_csv(os.path.join(czech_dir, "trans.csv"), low_memory=False)
loan_df = pd.read_csv(os.path.join(czech_dir, "loan.csv"))
order_df = pd.read_csv(os.path.join(czech_dir, "order.csv"))
account_df = pd.read_csv(os.path.join(czech_dir, "account.csv"))

print(f"Loaded in {time.time()-t0:.2f}s:")
print(f"  trans.csv: {len(trans_df):,} records")
print(f"  loan.csv: {len(loan_df):,} loans")
print(f"  order.csv: {len(order_df):,} standing orders")
print(f"  account.csv: {len(account_df):,} accounts")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 1. Transaction Flow & Inflow/Outflow Topology
# ------------------------------------------------------------------------------
print("\n[PART 2] Analyzing Inflows vs Outflows Topology across 1.05M Transactions...")
sys.stdout.flush()

trans_df['date_dt'] = pd.to_datetime(trans_df['date'], errors='coerce')
trans_df['amount'] = pd.to_numeric(trans_df['amount'], errors='coerce')
trans_df['balance'] = pd.to_numeric(trans_df['balance'], errors='coerce')

# Type translation & categorization
# PRIJEM = Inflow/Credit, VYDAJ = Outflow/Debit, VYBER = Withdrawal
type_counts = trans_df['type'].value_counts().to_dict()
op_counts = trans_df['operation'].value_counts(dropna=False).to_dict()
k_symbol_counts = trans_df['k_symbol'].value_counts(dropna=False).to_dict()

# Inflows vs Outflows
inflows = trans_df[trans_df['type'] == 'PRIJEM']
outflows = trans_df[trans_df['type'].isin(['VYDAJ', 'VYBER'])]

total_inflow_vol = float(inflows['amount'].sum())
total_outflow_vol = float(outflows['amount'].sum())
net_cash_drift = total_inflow_vol - total_outflow_vol

def get_stats(series):
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

inflow_stats = get_stats(inflows['amount'])
outflow_stats = get_stats(outflows['amount'])
balance_stats = get_stats(trans_df['balance'])

print(f"  Total Inflow Volume: CZK {total_inflow_vol:,.2f} ({len(inflows):,} transactions)")
print(f"  Total Outflow Volume: CZK {total_outflow_vol:,.2f} ({len(outflows):,} transactions)")
print(f"  Net Cash Drift: CZK {net_cash_drift:,.2f}")
print(f"  Running Balance: Median=CZK {balance_stats['median']:,}, Mean=CZK {balance_stats['mean']:,}")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 2. Account-Level Working Capital & Overdraft Dynamics
# ------------------------------------------------------------------------------
print("\n[PART 3] Analyzing Account-Level Working Capital & Authorized Overdrafts...")
sys.stdout.flush()

# Group by account to get min balance, avg balance, overdraft occurrences
acc_summary = trans_df.groupby('account_id').agg(
    trans_count=('trans_id', 'count'),
    min_balance=('balance', 'min'),
    max_balance=('balance', 'max'),
    mean_balance=('balance', 'mean'),
    median_balance=('balance', 'median'),
    first_date=('date_dt', 'min'),
    last_date=('date_dt', 'max')
)

total_accounts = len(acc_summary)
overdraft_accounts = (acc_summary['min_balance'] < 0).sum()
overdraft_rate_pct = (overdraft_accounts / total_accounts) * 100.0

# Negative balances distribution
negative_trans = trans_df[trans_df['balance'] < 0]
negative_trans_count = len(negative_trans)
negative_trans_pct = (negative_trans_count / len(trans_df)) * 100.0
overdraft_depth_stats = get_stats(abs(negative_trans['balance']))

# Accounts with persistent overdrafts (min balance < -1000 CZK)
severe_overdraft_accounts = (acc_summary['min_balance'] < -1000).sum()

print(f"  Total Accounts Analyzed: {total_accounts:,}")
print(f"  Accounts with Overdraft (Min Balance < 0): {overdraft_accounts:,} ({overdraft_rate_pct:.2f}%)")
print(f"  Severe Overdraft Accounts (Min Balance < -1,000 CZK): {severe_overdraft_accounts:,} ({(severe_overdraft_accounts/total_accounts)*100:.2f}%)")
print(f"  Negative Balance Transactions: {negative_trans_count:,} ({negative_trans_pct:.2f}% of all transactions)")
if overdraft_depth_stats:
    print(f"  Overdraft Exposure Depth: Median=CZK {overdraft_depth_stats['median']:,}, Mean=CZK {overdraft_depth_stats['mean']:,}, Max=CZK {overdraft_depth_stats['max']:,}")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 3. Permanent Standing Orders & Committed Monthly Fixed Outflows
# ------------------------------------------------------------------------------
print("\n[PART 4] Analyzing Permanent Standing Orders (order.csv)...")
sys.stdout.flush()

order_acc = order_df.groupby('account_id').agg(
    order_count=('order_id', 'count'),
    total_monthly_committed=('amount', 'sum')
)
order_k_symbols = order_df['k_symbol'].value_counts(dropna=False).to_dict()
committed_stats = get_stats(order_acc['total_monthly_committed'])

print(f"  Accounts with Standing Orders: {len(order_acc):,} / {total_accounts:,} ({len(order_acc)/total_accounts*100:.2f}%)")
print(f"  Monthly Committed Outflow per Account: Median=CZK {committed_stats['median']:,}, Mean=CZK {committed_stats['mean']:,}")
print(f"  Standing Order Types: {order_k_symbols}")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 4. Credit Risk, Debt Servicing & Loan Default Hazards (loan.csv)
# ------------------------------------------------------------------------------
print("\n[PART 5] Analyzing Loan Portfolio Credit Risk & Default Hazards (loan.csv)...")
sys.stdout.flush()

total_loans = len(loan_df)
total_loan_principal = float(loan_df['amount'].sum())
status_counts = loan_df['status'].value_counts().to_dict()
duration_counts = loan_df['duration'].value_counts().to_dict()

# Status definition:
# A: Contract finished, no problem
# B: Contract finished, loan unpaid / default
# C: Running contract, OK so far
# D: Running contract, client in debt / arrears
n_A = status_counts.get('A', 0)
n_B = status_counts.get('B', 0)
n_C = status_counts.get('C', 0)
n_D = status_counts.get('D', 0)

default_count = n_B + n_D
performing_count = n_A + n_C
overall_default_rate_pct = (default_count / total_loans) * 100.0
closed_loan_default_rate_pct = (n_B / (n_A + n_B)) * 100.0 if (n_A + n_B) > 0 else 0.0

# Capital at risk
default_principal = float(loan_df[loan_df['status'].isin(['B', 'D'])]['amount'].sum())
performing_principal = float(loan_df[loan_df['status'].isin(['A', 'C'])]['amount'].sum())
capital_at_risk_pct = (default_principal / total_loan_principal) * 100.0

# Correlate loan status with account balance & overdraft metrics
merged_loan = loan_df.merge(acc_summary, on='account_id', how='left')
loan_perf_by_status = merged_loan.groupby('status').agg(
    loan_count=('loan_id', 'count'),
    mean_loan_amount=('amount', 'mean'),
    median_loan_amount=('amount', 'median'),
    mean_acc_balance=('mean_balance', 'mean'),
    median_acc_balance=('median_balance', 'median'),
    overdraft_incidence=('min_balance', lambda x: (x < 0).mean() * 100.0),
    mean_monthly_payment=('payments', 'mean')
).to_dict(orient='index')

print(f"  Total Loans: {total_loans:,} | Total Principal: CZK {total_loan_principal:,.2f}")
print(f"  Status Breakdown: A (Finished OK)={n_A}, B (Finished Default)={n_B}, C (Running OK)={n_C}, D (Running Default)={n_D}")
print(f"  Overall Default Rate (B+D): {overall_default_rate_pct:.2f}% ({default_count} defaulted loans)")
print(f"  Closed Loan Default Rate (B / [A+B]): {closed_loan_default_rate_pct:.2f}%")
print(f"  Capital at Risk: CZK {default_principal:,.2f} ({capital_at_risk_pct:.2f}% of total loan book)")
print(f"  Overdraft Incidence by Loan Status:")
for st, vals in loan_perf_by_status.items():
    print(f"    Status {st}: Overdraft Rate = {vals['overdraft_incidence']:.1f}%, Mean Acc Balance = CZK {vals['mean_acc_balance']:,.1f}")
sys.stdout.flush()

# Assemble Full Banking & Working Capital Metrics
banking_metrics = {
    'total_transactions': len(trans_df),
    'total_accounts': total_accounts,
    'total_loans': total_loans,
    'cash_flow_summary_czk': {
        'total_inflow_volume': total_inflow_vol,
        'total_outflow_volume': total_outflow_vol,
        'net_cash_drift': net_cash_drift,
        'inflow_transaction_stats': inflow_stats,
        'outflow_transaction_stats': outflow_stats,
        'running_balance_stats': balance_stats
    },
    'working_capital_and_overdrafts': {
        'total_accounts_analyzed': total_accounts,
        'accounts_with_overdraft_count': int(overdraft_accounts),
        'accounts_with_overdraft_pct': round(overdraft_rate_pct, 2),
        'severe_overdraft_accounts_count': int(severe_overdraft_accounts),
        'severe_overdraft_accounts_pct': round((severe_overdraft_accounts / total_accounts) * 100.0, 2),
        'negative_balance_transactions_count': int(negative_trans_count),
        'negative_balance_transactions_pct': round(negative_trans_pct, 2),
        'overdraft_exposure_depth_stats_czk': overdraft_depth_stats
    },
    'standing_orders_commitments': {
        'total_standing_orders': len(order_df),
        'accounts_with_orders': len(order_acc),
        'accounts_with_orders_pct': round(len(order_acc) / total_accounts * 100.0, 2),
        'monthly_committed_per_account_czk': committed_stats,
        'order_type_distribution': {str(k): int(v) for k, v in order_k_symbols.items()}
    },
    'credit_risk_and_loan_defaults': {
        'total_loan_facilities': total_loans,
        'total_principal_lent_czk': total_loan_principal,
        'status_distribution': {str(k): int(v) for k, v in status_counts.items()},
        'duration_distribution': {str(k): int(v) for k, v in duration_counts.items()},
        'overall_default_rate_pct': round(overall_default_rate_pct, 2),
        'closed_loan_default_rate_pct': round(closed_loan_default_rate_pct, 2),
        'total_defaulted_loans_count': int(default_count),
        'capital_at_risk_czk': total_loan_principal,
        'capital_at_risk_pct': round(capital_at_risk_pct, 2),
        'loan_metrics_by_status': loan_perf_by_status
    }
}

json_path = os.path.join(output_dir, "czech_bank_working_capital_metrics.json")
with open(json_path, "w") as f:
    json.dump(banking_metrics, f, indent=2)

print(f"\nSaved Banking & Working Capital Metrics: {json_path} ({os.path.getsize(json_path):,} bytes)")
print("=" * 80)
sys.stdout.flush()
