import re
from bs4 import BeautifulSoup

path = r"research/original_datasets/qoe_transaction_advisory/sec_defm14a_financial_projections_and_fairness.htm"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Search for 766 or litigation
print("Searching for litigation / settlement / 766...")
for match in re.finditer(r"(?:litigation|settlement|766|add-back|restructuring)", text, re.IGNORECASE):
    pos = match.start()
    snippet = text[max(0, pos-200): min(len(text), pos+300)]
    clean_snippet = re.sub(r"<[^>]+>", " ", snippet)
    clean_snippet = re.sub(r"\s+", " ", clean_snippet).strip()
    print(f"--- Pos {pos} ---: {clean_snippet[:200]}")
    if pos > 1000000:
        break
