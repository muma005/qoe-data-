import pandas as pd

cf_tags = set()
for chunk in pd.read_csv("research/original_datasets/financial_accounting/sec_fsds_2024q3/num.txt", sep="\t", chunksize=500000, nrows=1500000, usecols=["tag"]):
    matches = chunk[chunk["tag"].str.contains("NetCashProvidedByUsedInOperatingActivities|OperatingActivities|CashAndCashEquivalents|AccountsReceivable|InventoryNet|AccountsPayableCurrent|Goodwill", case=False, na=False)]["tag"].unique()
    cf_tags.update(matches)

print("Matching tags found in num.txt sample:")
for t in sorted(cf_tags):
    print(t)
