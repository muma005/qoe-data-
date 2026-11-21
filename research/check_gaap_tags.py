import pandas as pd

df_tag = pd.read_csv("research/original_datasets/financial_accounting/sec_fsds_2024q3/tag.txt", sep="\t", low_memory=False)

keywords = ["Revenue", "CostOf", "GrossProfit", "OperatingIncome", "NetIncome", "OperatingActivities", "Receivable", "Inventory", "Payable", "Assets", "Debt", "Goodwill"]

for kw in keywords:
    matches = df_tag[df_tag["tag"].str.contains(kw, case=False, na=False)]
    std_matches = matches[matches["custom"] == 0]
    print(f"=== Keyword: {kw} (Total: {len(matches)}, Standard US-GAAP: {len(std_matches)}) ===")
    top_tags = std_matches["tag"].value_counts().head(5).index.tolist()
    print("Top Standard Tags:", top_tags)
