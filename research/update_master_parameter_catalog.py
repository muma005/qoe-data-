import os
import json

base_dir = r"research"
out_dir = os.path.join(base_dir, "consolidated_findings")
cat_path = os.path.join(out_dir, "qoe_simulator_parameter_catalog.json")

with open(cat_path, "r") as f:
    catalog = json.load(f)

# Load Banking metrics
with open(os.path.join(base_dir, "banking_signals", "czech_bank_working_capital_metrics.json"), "r") as f:
    banking_metrics = json.load(f)

# Load Payroll metrics
with open(os.path.join(base_dir, "payroll_signals", "sf_employee_compensation_metrics.json"), "r") as f:
    payroll_metrics = json.load(f)

# Add sources
catalog["metadata"]["sources"]["working_capital_banking"] = "Czech Commercial Bank (Berka) Database - 1,056,320 transactions, 682 loan facilities"
catalog["metadata"]["sources"]["labor_and_payroll"] = "City of San Francisco Employee Compensation - 50,000 workforce records, $7.0B total spend"

# Add Banking & Working Capital Parameters
catalog["working_capital_and_banking_parameters"] = {
    "cashflow_summary_czk": banking_metrics["cash_flow_summary_czk"],
    "authorized_overdraft_dynamics": banking_metrics["working_capital_and_overdrafts"],
    "standing_orders_commitments": banking_metrics["standing_orders_commitments"],
    "credit_risk_and_loan_defaults": banking_metrics["credit_risk_and_loan_defaults"]
}

# Add Payroll & Labor Cost Parameters
catalog["labor_cost_and_payroll_parameters"] = {
    "total_labor_cost_summary_usd": payroll_metrics["total_labor_cost_summary_usd"],
    "compensation_statistical_distributions": payroll_metrics["compensation_statistical_distributions"],
    "overtime_dynamics": payroll_metrics["overtime_dynamics"],
    "top_departments_spend": payroll_metrics["top_departments"],
    "employment_type_breakdown": payroll_metrics["employment_type_breakdown"]
}

with open(cat_path, "w") as f:
    json.dump(catalog, f, indent=2)

print(f"Successfully updated {cat_path} with Banking and Payroll parameters ({os.path.getsize(cat_path):,} bytes)!")
