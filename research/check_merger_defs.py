import re

path = r"research/original_datasets/tax_legal_contracts/sec_merger_agreement_exhibit.htm"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("Searching for Indebtedness and definitions in Merger Agreement...")
for match in re.finditer(r'Indebtedness', text):
    pos = match.start()
    snippet = text[max(0, pos-100): min(len(text), pos+600)]
    clean_snippet = re.sub(r"<[^>]+>", " ", snippet)
    clean_snippet = re.sub(r"\s+", " ", clean_snippet).strip()
    if "means" in clean_snippet.lower() or "defined" in clean_snippet.lower():
        print(f"--- Indebtedness Pos {pos} ---:\n{clean_snippet[:400]}\n")
        break

for match in re.finditer(r'Company Material Adverse Effect', text):
    pos = match.start()
    snippet = text[max(0, pos-100): min(len(text), pos+600)]
    clean_snippet = re.sub(r"<[^>]+>", " ", snippet)
    clean_snippet = re.sub(r"\s+", " ", clean_snippet).strip()
    if "means" in clean_snippet.lower():
        print(f"--- Company Material Adverse Effect Pos {pos} ---:\n{clean_snippet[:400]}\n")
        break
