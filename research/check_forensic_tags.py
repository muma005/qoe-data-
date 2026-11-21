import pandas as pd
from collections import Counter

print("Searching num.txt for forensic add-back tags...")
target_keywords = [
    "ShareBasedCompensation", "Restructuring", "Impairment", 
    "Litigation", "AmortizationOfIntangibleAssets", "Depreciation",
    "ContractWithCustomerAsset", "Unbilled"
]

found_tags = Counter()

# Read in chunks
for chunk in pd.read_csv("research/original_datasets/financial_accounting/sec_fsds_2024q3/num.txt", sep="\t", chunksize=500000, usecols=["tag", "value"]):
    for kw in target_keywords:
        m = chunk[chunk["tag"].str.contains(kw, case=False, na=False)]
        for t in m["tag"].value_counts().items():
            found_tags[t[0]] += t[1]

print(f"Total matching forensic tags found: {len(found_tags)}")
print("\nTop 40 most common forensic add-back / accrual tags:")
for t, cnt in found_tags.most_common(40):
    print(f"{t}: {cnt:,} occurrences")
