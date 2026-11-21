import json

with open(r"research\original_datasets\procurement_expenses\kenya_procurement\kenya_tenders_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total raw items: {len(data)}")
first = data[0]
print("Keys in first item:", list(first.keys()))
for k, v in first.items():
    if v is not None and v != "" and v != []:
        if isinstance(v, (dict, list)):
            print(f"  {k}: ({type(v).__name__}) {str(v)[:120]}")
        else:
            print(f"  {k}: {v}")

# Check across all items which fields have non-null values
non_null_counts = {}
for item in data:
    for k, v in item.items():
        if v is not None and v != "" and v != []:
            non_null_counts[k] = non_null_counts.get(k, 0) + 1

print("\nNon-null counts across 200 items:")
for k, cnt in sorted(non_null_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {k}: {cnt} / 200")
