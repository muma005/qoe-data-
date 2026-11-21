import re

repo_path = r"research\original_datasets\internal_documentation\lehman_repo105_forensic_examiner_findings.txt"
with open(repo_path, 'r', encoding='utf-8') as f:
    print("--- Lehman Repo 105 Findings Content ---")
    print(f.read())

defm_path = r"research\original_datasets\qoe_transaction_advisory\sec_defm14a_financial_projections_and_fairness.htm"
with open(defm_path, 'r', encoding='utf-8', errors='ignore') as f:
    html_text = f.read()

print(f"\n--- SEC Form DEFM14A Text Length: {len(html_text):,} characters ---")

# Look for EBITDA, Adjusted EBITDA, Projections, Working Capital, Net Debt in the HTML
keywords = ['Adjusted EBITDA', 'EBITDA', 'Unlevered Free Cash Flow', 'Working Capital', 'Net Debt', 'Goldman Sachs', 'J.P. Morgan']
for kw in keywords:
    matches = [m.start() for m in re.finditer(re.escape(kw), html_text, re.IGNORECASE)]
    print(f"Keyword '{kw}': {len(matches)} occurrences")

# Find a snippet around Adjusted EBITDA or Financial Projections
idx = html_text.find("Adjusted EBITDA")
if idx != -1:
    print("\nSample Context around 'Adjusted EBITDA':")
    # Clean tags from snippet
    snippet = html_text[max(0, idx-200):idx+800]
    clean_snippet = re.sub(r'<[^>]+>', ' ', snippet)
    clean_snippet = re.sub(r'\s+', ' ', clean_snippet).strip()
    print(clean_snippet[:500] + "...")
