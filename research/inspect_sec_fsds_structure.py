import pandas as pd
import os

fsds_dir = r"research\original_datasets\financial_accounting\sec_fsds_2024q3"

print("--- Inspecting sub.txt ---")
sub_df = pd.read_csv(os.path.join(fsds_dir, "sub.txt"), sep='\t', nrows=5)
print("sub columns:", sub_df.columns.tolist())
print(sub_df[['adsh', 'cik', 'name', 'form', 'period', 'fy', 'fp', 'prevrpt', 'afs']].to_dict(orient='records'))

print("\n--- Inspecting tag.txt ---")
tag_df = pd.read_csv(os.path.join(fsds_dir, "tag.txt"), sep='\t', nrows=5)
print("tag columns:", tag_df.columns.tolist())
print(tag_df.head(2).to_dict(orient='records'))

print("\n--- Inspecting pre.txt ---")
pre_df = pd.read_csv(os.path.join(fsds_dir, "pre.txt"), sep='\t', nrows=5)
print("pre columns:", pre_df.columns.tolist())
print(pre_df.head(2).to_dict(orient='records'))

print("\n--- Inspecting num.txt ---")
num_df = pd.read_csv(os.path.join(fsds_dir, "num.txt"), sep='\t', nrows=5)
print("num columns:", num_df.columns.tolist())
print(num_df.head(2).to_dict(orient='records'))
