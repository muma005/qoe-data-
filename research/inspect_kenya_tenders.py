import os
import pandas as pd

kenya_csv = r"research\original_datasets\procurement_expenses\kenya_procurement\kenya_tenders_flattened.csv"
df = pd.read_csv(kenya_csv)

print("Kenya Tenders Shape:", df.shape)
print("\nColumns and non-null counts:")
print(df.info())

print("\nSample row:")
print(df.iloc[0].to_dict())

print("\nProcurement methods:")
print(df['procurement_method_name'].value_counts(dropna=False))

print("\nAGPO (preference) counts:")
print(df['is_agpo'].value_counts(dropna=False))

print("\nFee and bid security stats:")
print(df[['tender_fee', 'bid_security_percent', 'bid_security_value', 'passmark', 'validity_in_days']].describe())
