import pandas as pd

czech_dir = r"research\original_datasets\working_capital_banking\czech_bank"
sf_path = r"research\original_datasets\payroll_employees\sf_employee_compensation\sf_employee_compensation.csv"

print("--- Czech Bank trans.csv Sample ---")
trans_df = pd.read_csv(f"{czech_dir}\\trans.csv", nrows=5)
print("trans columns:", trans_df.columns.tolist())
print(trans_df.head(2).to_dict(orient='records'))

print("\n--- Czech Bank loan.csv Sample ---")
loan_df = pd.read_csv(f"{czech_dir}\\loan.csv", nrows=5)
print("loan columns:", loan_df.columns.tolist())
print(loan_df.head(2).to_dict(orient='records'))

print("\n--- Czech Bank order.csv Sample ---")
order_df = pd.read_csv(f"{czech_dir}\\order.csv", nrows=5)
print("order columns:", order_df.columns.tolist())
print(order_df.head(2).to_dict(orient='records'))

print("\n--- SF Employee Compensation Sample ---")
sf_df = pd.read_csv(sf_path, nrows=5)
print("sf columns:", sf_df.columns.tolist())
print(sf_df.head(2).to_dict(orient='records'))
