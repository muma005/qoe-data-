import re

path = r"research/original_datasets/qoe_transaction_advisory/sec_defm14a_financial_projections_and_fairness.htm"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Search for discount rate, terminal growth rate, WACC
print("Searching for DCF parameters...")
for match in re.finditer(r"(?:discount rate|terminal value|perpetuity growth|weighted average cost of capital|WACC)", text, re.IGNORECASE):
    pos = match.start()
    snippet = text[max(0, pos-100): min(len(text), pos+300)]
    clean_snippet = re.sub(r"<[^>]+>", " ", snippet)
    clean_snippet = re.sub(r"\s+", " ", clean_snippet).strip()
    print(f"--- Pos {pos} ---: {clean_snippet[:250]}")
