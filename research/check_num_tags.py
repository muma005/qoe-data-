import pandas as pd
from collections import Counter

print("Scanning num.txt for top tags...")
tag_counter = Counter()

# Read 1M rows to see frequency
for chunk in pd.read_csv("research/original_datasets/financial_accounting/sec_fsds_2024q3/num.txt", sep="\t", chunksize=500000, nrows=1000000, usecols=["tag"]):
    tag_counter.update(chunk["tag"].dropna())

print("Top 30 most common tags in num.txt:")
for tag, count in tag_counter.most_common(30):
    print(f"{tag}: {count}")
