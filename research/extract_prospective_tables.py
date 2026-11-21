import re
from bs4 import BeautifulSoup

defm_path = r"research\original_datasets\qoe_transaction_advisory\sec_defm14a_financial_projections_and_fairness.htm"

with open(defm_path, 'r', encoding='utf-8', errors='ignore') as f:
    html_text = f.read()

matches = [m.start() for m in re.finditer(re.escape("Unaudited Prospective Financial Information"), html_text)]
print(f"Matches found: {len(matches)} at positions {matches}")

for idx, pos in enumerate(matches):
    if idx > 0: # Check the body occurrence
        snippet = html_text[pos:pos+25000]
        soup = BeautifulSoup(snippet, 'html.parser')
        tables = soup.find_all('table')
        print(f"\n--- Occurrence {idx+1} (pos {pos}): {len(tables)} tables ---")
        for ti, t in enumerate(tables):
            print(f"\n--- Table {ti+1} ---")
            for row in t.find_all('tr'):
                cols = [c.get_text(strip=True) for c in row.find_all(['td', 'th']) if c.get_text(strip=True)]
                if cols:
                    print(" | ".join(cols))
