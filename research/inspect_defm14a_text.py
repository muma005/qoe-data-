import re
from bs4 import BeautifulSoup

defm_path = r"research\original_datasets\qoe_transaction_advisory\sec_defm14a_financial_projections_and_fairness.htm"

with open(defm_path, 'r', encoding='utf-8', errors='ignore') as f:
    html_text = f.read()

pos = html_text.find("Unlevered Free Cash Flow")
print(f"Position: {pos}")
snippet = html_text[pos-200:pos+2500]
soup = BeautifulSoup(snippet, 'html.parser')
print(soup.get_text(separator='\n'))
