import re
from bs4 import BeautifulSoup

defm_path = r"research\original_datasets\qoe_transaction_advisory\sec_defm14a_financial_projections_and_fairness.htm"

with open(defm_path, 'r', encoding='utf-8', errors='ignore') as f:
    html_text = f.read()

# Let's search for "Financial Projections" section
pos = html_text.find("Certain Twitter Forecasts")
if pos == -1:
    pos = html_text.find("Management Projections")
if pos == -1:
    pos = html_text.find("Unlevered Free Cash Flow")

print(f"Position found: {pos}")
if pos != -1:
    snippet = html_text[pos:pos+4000]
    soup = BeautifulSoup(snippet, 'html.parser')
    tables = soup.find_all('table')
    print(f"Tables found in snippet: {len(tables)}")
    for i, t in enumerate(tables):
        print(f"\n--- Table {i+1} ---")
        for row in t.find_all('tr'):
            cols = [c.get_text(strip=True) for c in row.find_all(['td', 'th']) if c.get_text(strip=True)]
            if cols:
                print(" | ".join(cols))
