"""
Labor Cost & Payroll Composition Empirical Signal Extraction
=============================================================
Extracts empirical signals, base salary distributions, overtime premiums,
non-wage benefit loading multipliers, and departmental allocations from
the City of San Francisco Employee Compensation Dataset (50,000 records).
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd

sf_path = r"research\original_datasets\payroll_employees\sf_employee_compensation\sf_employee_compensation.csv"
output_dir = r"research\payroll_signals"
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("LABOR COST & PAYROLL COMPOSITION EMPIRICAL SIGNAL EXTRACTION")
print("=" * 80)
sys.stdout.flush()

t0 = time.time()
print("\n[PART 1] Loading San Francisco Employee Compensation Dataset (50k records)...")
sys.stdout.flush()

df = pd.read_csv(sf_path, low_memory=False)
print(f"Loaded {len(df):,} records in {time.time()-t0:.2f}s.")
sys.stdout.flush()

# Convert numeric columns
numeric_cols = [
    'salaries', 'overtime', 'other_salaries', 'total_salary',
    'retirement', 'health_and_dental', 'other_benefits',
    'total_benefits', 'total_compensation', 'hours'
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

# Filter out negative or extreme zero records for meaningful baseline stats
active_employees = df[df['total_compensation'] > 0].copy()
total_records = len(df)
active_count = len(active_employees)

print(f"Active Employees Analyzed: {active_count:,} / {total_records:,}")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 1. Total Compensation Decomposition
# ------------------------------------------------------------------------------
print("\n[PART 2] Decomposing Total Labor Cost Components...")
sys.stdout.flush()

tot_comp = float(active_employees['total_compensation'].sum())
tot_base = float(active_employees['salaries'].sum())
tot_ot = float(active_employees['overtime'].sum())
tot_other = float(active_employees['other_salaries'].sum())
tot_salary = float(active_employees['total_salary'].sum())
tot_ret = float(active_employees['retirement'].sum())
tot_health = float(active_employees['health_and_dental'].sum())
tot_other_ben = float(active_employees['other_benefits'].sum())
tot_benefits = float(active_employees['total_benefits'].sum())

# Shares of total compensation
share_base = (tot_base / tot_comp) * 100.0
share_ot = (tot_ot / tot_comp) * 100.0
share_other = (tot_other / tot_comp) * 100.0
share_benefits = (tot_benefits / tot_comp) * 100.0
share_ret = (tot_ret / tot_comp) * 100.0
share_health = (tot_health / tot_comp) * 100.0

# Benefit Loading Factor (Benefits as % of Base Salaries and % of Total Cash Salaries)
benefit_loading_on_base = (tot_benefits / tot_base) * 100.0 if tot_base > 0 else 0.0
benefit_loading_on_total_cash = (tot_benefits / tot_salary) * 100.0 if tot_salary > 0 else 0.0
labor_multiplier = tot_comp / tot_base if tot_base > 0 else 0.0

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

base_stats = calc_stats_series(active_employees[active_employees['salaries'] > 0]['salaries'])
ot_stats = calc_stats_series(active_employees[active_employees['overtime'] > 0]['overtime'])
total_comp_stats = calc_stats_series(active_employees['total_compensation'])

print(f"  Total Enterprise Labor Cost: ${tot_comp:,.2f}")
print(f"    - Base Salaries: ${tot_base:,.2f} ({share_base:.2f}%) | Median: ${base_stats['median']:,}")
print(f"    - Overtime Pay: ${tot_ot:,.2f} ({share_ot:.2f}%)")
print(f"    - Other Pay / Bonuses: ${tot_other:,.2f} ({share_other:.2f}%)")
print(f"    - Mandatory Benefits: ${tot_benefits:,.2f} ({share_benefits:.2f}%)")
print(f"      * Retirement / Pension: ${tot_ret:,.2f} ({share_ret:.2f}%)")
print(f"      * Health & Dental: ${tot_health:,.2f} ({share_health:.2f}%)")
print(f"  Non-Wage Benefit Loading Multiplier: {benefit_loading_on_base:.2f}% on Base Salary")
print(f"  Full Labor Cost Multiplier: {labor_multiplier:.2f}x of Base Salary")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 2. Overtime & Discretionary Compensation Dynamics
# ------------------------------------------------------------------------------
print("\n[PART 3] Analyzing Overtime Utilization & Discretionary Earnings...")
sys.stdout.flush()

ot_recipients = (active_employees['overtime'] > 0).sum()
ot_recipient_rate = (ot_recipients / active_count) * 100.0

# Employees with heavy overtime (>25% and >50% of base salary)
has_base = active_employees[active_employees['salaries'] > 10000]
ot_ratio = has_base['overtime'] / has_base['salaries']
ot_gt_25_pct = (ot_ratio > 0.25).sum()
ot_gt_50_pct = (ot_ratio > 0.50).sum()
ot_gt_100_pct = (ot_ratio > 1.00).sum()

print(f"  Overtime Recipients: {ot_recipients:,} / {active_count:,} ({ot_recipient_rate:.2f}%)")
print(f"  Overtime Mean for Recipients: ${ot_stats['mean']:,} (Median: ${ot_stats['median']:,})")
print(f"  Employees with Overtime > 25% of Base: {ot_gt_25_pct:,} ({(ot_gt_25_pct/len(has_base))*100:.2f}%)")
print(f"  Employees with Overtime > 50% of Base: {ot_gt_50_pct:,} ({(ot_gt_50_pct/len(has_base))*100:.2f}%)")
print(f"  Extreme Overtime (>100% of Base Salary): {ot_gt_100_pct:,} ({(ot_gt_100_pct/len(has_base))*100:.2f}%)")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 3. Departmental Labor Allocation & Overtime Exposure
# ------------------------------------------------------------------------------
print("\n[PART 4] Analyzing Departmental Labor Allocation & Concentration...")
sys.stdout.flush()

dept_summary = active_employees.groupby('department').agg(
    headcount=('employee_identifier', 'count'),
    total_spend=('total_compensation', 'sum'),
    total_base=('salaries', 'sum'),
    total_ot=('overtime', 'sum'),
    total_benefits=('total_benefits', 'sum'),
    mean_comp=('total_compensation', 'mean'),
    median_comp=('total_compensation', 'median')
)

dept_summary['ot_share_pct'] = (dept_summary['total_ot'] / dept_summary['total_spend']) * 100.0
dept_summary['benefit_loading_pct'] = (dept_summary['total_benefits'] / dept_summary['total_base']) * 100.0
dept_summary = dept_summary.sort_values(by='total_spend', ascending=False)

top_depts_spend = dept_summary.head(10).to_dict(orient='index')

print("Top 5 Departments by Total Labor Spend:")
for d, vals in list(top_depts_spend.items())[:5]:
    print(f"  {d:<30}: ${vals['total_spend']:,.0f} (HC: {vals['headcount']:,}, OT Share: {vals['ot_share_pct']:.1f}%, Benefit Loading: {vals['benefit_loading_pct']:.1f}%)")
sys.stdout.flush()

# ------------------------------------------------------------------------------
# 4. Employment Type & Benefit Disparities
# ------------------------------------------------------------------------------
print("\n[PART 5] Analyzing Employment Type & Benefit Disparities...")
sys.stdout.flush()

emp_type_summary = active_employees.groupby('employment_type').agg(
    headcount=('employee_identifier', 'count'),
    total_comp=('total_compensation', 'sum'),
    mean_base=('salaries', 'mean'),
    mean_benefits=('total_benefits', 'mean'),
    zero_benefit_rate=('total_benefits', lambda x: (x == 0).mean() * 100.0)
).to_dict(orient='index')

for et, vals in emp_type_summary.items():
    print(f"  {et:<30}: HC={vals['headcount']:>6,} | Mean Base=${vals['mean_base']:>8,.0f} | Mean Ben=${vals['mean_benefits']:>8,.0f} | Zero Benefits={vals['zero_benefit_rate']:>5.1f}%")
sys.stdout.flush()

# Assemble Full Payroll Metrics
payroll_metrics = {
    'total_records_analyzed': total_records,
    'active_employees_analyzed': active_count,
    'total_labor_cost_summary_usd': {
        'total_compensation': tot_comp,
        'base_salaries': tot_base,
        'overtime_pay': tot_ot,
        'other_salaries_and_bonuses': tot_other,
        'total_cash_salaries': tot_salary,
        'mandatory_retirement_pension': tot_ret,
        'mandatory_health_and_dental': tot_health,
        'other_benefits': tot_other_ben,
        'total_benefits': tot_benefits,
        'shares_of_total_compensation_pct': {
            'base_salary_share': round(share_base, 2),
            'overtime_share': round(share_ot, 2),
            'other_salaries_share': round(share_other, 2),
            'total_benefits_share': round(share_benefits, 2),
            'retirement_share': round(share_ret, 2),
            'health_share': round(share_health, 2)
        },
        'loading_multipliers': {
            'benefit_loading_on_base_salary_pct': round(benefit_loading_on_base, 2),
            'benefit_loading_on_total_cash_salary_pct': round(benefit_loading_on_total_cash, 2),
            'full_labor_cost_multiplier_on_base': round(labor_multiplier, 2)
        }
    },
    'compensation_statistical_distributions': {
        'base_salaries_usd': base_stats,
        'overtime_pay_usd': ot_stats,
        'total_compensation_usd': total_comp_stats
    },
    'overtime_dynamics': {
        'overtime_recipients_count': int(ot_recipients),
        'overtime_recipients_rate_pct': round(ot_recipient_rate, 2),
        'employees_with_ot_gt_25_pct_of_base': int(ot_gt_25_pct),
        'employees_with_ot_gt_50_pct_of_base': int(ot_gt_50_pct),
        'employees_with_ot_gt_100_pct_of_base': int(ot_gt_100_pct),
        'ot_gt_25_pct_rate': round(ot_gt_25_pct / len(has_base) * 100.0, 2),
        'ot_gt_50_pct_rate': round(ot_gt_50_pct / len(has_base) * 100.0, 2)
    },
    'top_departments': {d: {k: round(v, 2) if isinstance(v, float) else v for k, v in vals.items()} for d, vals in top_depts_spend.items()},
    'employment_type_breakdown': {et: {k: round(v, 2) if isinstance(v, float) else v for k, v in vals.items()} for et, vals in emp_type_summary.items()}
}

json_path = os.path.join(output_dir, "sf_employee_compensation_metrics.json")
with open(json_path, "w") as f:
    json.dump(payroll_metrics, f, indent=2)

print(f"\nSaved Payroll & Labor Cost Metrics: {json_path} ({os.path.getsize(json_path):,} bytes)")
print("=" * 80)
sys.stdout.flush()
