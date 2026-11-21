import pandas as pd

uci_path = r"research\original_datasets\revenue_commercial\uci_online_retail\online_retail.csv"
olist_path = r"research\original_datasets\operational_performance\olist_orders_dataset.csv"

print("--- UCI Retail Sample ---")
uci_df = pd.read_csv(uci_path, nrows=5, encoding='latin1')
print(uci_df.columns.tolist())
print(uci_df.head(2).to_dict(orient='records'))

print("\n--- Olist Sample ---")
olist_df = pd.read_csv(olist_path, nrows=5)
print(olist_df.columns.tolist())
print(olist_df.head(2).to_dict(orient='records'))
