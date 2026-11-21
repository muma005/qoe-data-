import os

# New content for Corporate Financial Accounting and M&A Advisory
accounting_and_mna_sections = """
---

## 8. Corporate Financial Accounting & Financial Statement Architecture (SEC EDGAR FSDS 2024 Q3)

### Empirical Discoveries across 6,699 Corporate Filers & 3.52M Numeric Facts:
- **Corporate Restatement Hazard (`prevrpt`):**
  - **Empirical Restatement Rate:** **2.5228%** (169 of 6,699 corporate submissions represent amendments, restatements, or previously reported revisions).
  - **The Filer Governance Gradient:**
    - Large Accelerated Filers (`1-LAF`): **0.2773%** restatement rate (6 of 2,164 filings).
    - Accelerated Filers (`2-ACC`): **0.6002%** restatement rate (5 of 833 filings).
    - Non-Accelerated Filers & Smaller Entities (`4-NON`): **4.2779%** restatement rate (157 of 3,670 filings).
  - **Hazard Ratio:** Non-accelerated corporate filers are **15.42x more likely** to restate financial figures than large accelerated peers, proving that financial reporting risk concentrates heavily in smaller entities with thinner internal audit resources.
- **Reporting Complexity & Opacity Ratio (`custom` tags):**
  - Out of 83,106 taxonomy tags analyzed, **74,953 tags (90.1896%)** are company-specific custom extensions, and only **8,153 tags (9.81%)** belong to the base US-GAAP taxonomy.
  - In monetary balance sheet and income statement concepts, custom tags account for **90.45%** (67,820 of 74,982 tags), demonstrating massive presentation heterogeneity and non-standard accounting schedules.
- **Financial Statement Line Architecture:**
  - Distribution across 741,760 presentation lines: Balance Sheet (**32.88%**), Cash Flows (**30.20%**), Income Statement (**18.90%**), Equity (**12.28%**), Comprehensive Income (**2.67%**), Unclassified/Notes (**2.62%**).
  - **Contra-Account / Negating Rate:** **14.1393%** of all financial statement lines represent deductions or contra-accounts (accumulated depreciation, treasury stock, allowances).
  - Statement density: Balance Sheet (mean 36.4 lines), Cash Flows (mean 33.4 lines), Income Statement (mean 20.9 lines).
- **Footnote Qualification Density:**
  - Out of 3,521,878 numeric facts, **7,274 facts (0.2065%)** carry explicit XBRL explanatory footnotes (approx. 1 in 484 facts). In QoE reviews, footnoted facts cluster around non-routine litigation, debt covenants, and related-party balances.

---

## 9. M&A Advisory, Adjusted EBITDA Bridges, Net Working Capital Pegs & Window-Dressing Hazards

### Empirical Discoveries from SEC Form DEFM14A ($44B Buyout) & Lehman Repo 105 Examiner Report:
- **Prospective Financial Projections & Cash Flow Bridges (Twitter DEFM14A):**
  - **The Operating Income vs. Adjusted EBITDA Chasm:** In the base year (2022E), GAAP Operating Income was negative at **$(47) Million (-0.79% margin)**, while Adjusted EBITDA was reported at **+$1,602 Million (+27.02% margin)**, driven by $864M in Stock-Based Compensation (SBC) and $702M in D&A add-backs.
  - Over the 6-year investment horizon (2022E–2027E), revenue was projected to grow at **16.86% CAGR** ($5,928M to $12,917M), while Adjusted EBITDA expands at **27.51% CAGR** ($1,602M to $5,399M; +1,478 bps margin expansion).
- **The Great Cash Flow Divide: Management vs. Investment Banker UFCF:**
  - Cumulative 6-year Management UFCF (adding back SBC): **$12,899 Million**.
  - Cumulative 6-year Banker UFCF (Goldman Sachs & J.P. Morgan, subtracting SBC): **$5,758 Million**.
  - **Cash Flow Haircut from SBC:** **-$7,141 Million** (**55.36% cash flow dilution**). Treating SBC as a real cash-equivalent expense eliminates more than half of the company's projected unlevered cash generation!
- **Working Capital Drag:** Cumulative 6-year Net Working Capital drain of **-$815 Million**, peaking at **-$259 Million** in 2023E, reflecting inventory and receivables commitments necessary to support growth.
- **Historical EBITDA Normalization (The $766M Litigation Add-Back):**
  - Reported FY21 Adjusted EBITDA was **$1,448 Million**, which included a one-time add-back of **$766 Million** for a shareholder litigation settlement (representing **52.90%** of total Adjusted EBITDA).
  - At transaction peer multiples of **28.0x to 36.0x EV/EBITDA**, this single add-back increased the implied enterprise value by **$21.45 Billion to $27.58 Billion**—highlighting the enormous economic stakes of QoE adjustments.
- **Fairness Opinion Valuation Benchmarks:**
  - WACC Discount Rates: **10.0% to 12.0%** (Goldman Sachs) and **10.25% to 11.25%** (J.P. Morgan), using mid-year discounting convention.
  - Terminal Growth Rates: **5.6% to 9.0%** implied (GS exit multiple 10.0x–15.0x) and **6.0% to 7.0%** (JPM perpetuity formula).
- **Forensic Window Dressing Mechanics (Lehman Brothers Repo 105):**
  - **Accounting Fiction Exploited:** SFAS 140 true-sale accounting for repos with **105% (equity)** or **108% (fixed income)** collateral haircuts.
  - **Balance Sheet Derecognition Scale:** Removed **$38.6B (Q4 2007)**, **$49.1B (Q1 2008)**, and **$50.38B (Q2 2008)** from the balance sheet immediately prior to reporting dates.
  - **Timing Dynamics:** Systematically executed **2 to 3 business days prior** to quarter-end; unwound and repurchased with cash plus interest **2 to 4 business days after** quarter-start.
  - **Leverage Distortion (Q2 2008):** Reported Net Leverage of **10.2x** vs actual **12.1x** (**15.70% underreported**); Gross Leverage reported at **12.1x** vs actual **13.9x** (**12.95% underreported**).
"""

# New rows for the parameter table
new_param_rows = """| **Acct: Restatements** | Overall Corporate Restatement Rate | **2.52%** (169 filings) | Bernoulli($p = 0.0252$) | SEC EDGAR FSDS 2024 Q3 |
| **Acct: Hazard Gradient**| Non-Accelerated vs Large Accel. Ratio | **15.42x Risk Multiplier** | 4.28% (NON) vs 0.28% (LAF) | SEC EDGAR FSDS 2024 Q3 |
| **Acct: Opacity** | Custom Taxonomy Extension Tag Share | **90.19%** (74,953 tags) | Beta($\alpha = 9.2$, $\beta = 1.0$); Monetary: 90.45% | SEC EDGAR FSDS 2024 Q3 |
| **Acct: Structure** | Financial Statement Negating Lines | **14.14%** (104,879 lines) | Contra-accounts & deduction line items | SEC EDGAR FSDS 2024 Q3 |
| **Acct: Footnotes** | XBRL Numeric Footnote Density | **0.21%** (7,274 facts) | Bernoulli($p = 0.00206$) (1 in 484 facts) | SEC EDGAR FSDS 2024 Q3 |
| **M&A: Projections** | Revenue CAGR (6-Year Model) | **16.86% CAGR** | $5,928M (2022E) to $12,917M (2027E) | SEC Form DEFM14A |
| **M&A: EBITDA Growth** | Adjusted EBITDA CAGR (6-Year Model) | **27.51% CAGR** | $1,602M (2022E) to $5,399M (2027E) | SEC Form DEFM14A |
| **M&A: SBC Dilution** | UFCF Haircut via Equity Compensation | **55.36% Dilution** | $7.14B cumulative SBC / $12.90B Mgmt UFCF | SEC Form DEFM14A |
| **M&A: SBC Intensity** | SBC Share of Cumulative Revenue | **12.85% of Revenue** | Normal($\mu = 0.1285$, $\sigma = 0.015$) | SEC Form DEFM14A |
| **M&A: Working Capital**| Cumulative NWC Cash Flow Drag | **-$815 Million** | Peaks in 2023E at -$259M; $\Delta\text{NWC} \approx -1.47\\% \Delta\text{Rev}$ | SEC Form DEFM14A |
| **M&A: Normalization** | Single Litigation Add-Back Share | **52.90% of EBITDA** | $766M add-back on $1,448M FY21 Adj. EBITDA | SEC Form DEFM14A |
| **M&A: EV Impact** | Enterprise Value Swing from Add-Back | **$21.45B to $27.58B** | Multiple range: 28.0x to 36.0x EV/EBITDA | SEC Form DEFM14A |
| **M&A: Valuation WACC**| Discount Rate Reference Range | **10.0% to 12.0%** | Uniform($0.10, 0.12$); mid-year convention | Goldman Sachs / JPM |
| **Forensic: Window Dress**| Quarter-End Balance Sheet Reduction | **$50.38 Billion** | Peak derecognition scale in Q2 2008 | Lehman Repo 105 Examiner |
| **Forensic: Haircut** | True-Sale Overcollateralization Hurdle| **105% / 108%** | 105% equities, 108% fixed income (SFAS 140) | Lehman Repo 105 Examiner |
| **Forensic: Timing** | Window Dressing Execution Lead/Lag | **2-3d Pre / 2-4d Post** | Discrete Uniform($\\{2, 3\\}$ pre, $\\{2, 3, 4\\}$ post) | Lehman Repo 105 Examiner |
| **Forensic: Leverage** | Leverage Underreporting Suppression | **15.70% (Net) / 12.95% (Gross)**| Net: 10.2x rep vs 12.1x real; Gross: 12.1x vs 13.9x | Lehman Repo 105 Examiner |
"""

paths = [
    r"research/consolidated_findings/master_qoe_research_compendium.md",
    r"C:/Users/ADMIN/.gemini/antigravity/brain/17a2156a-bb0b-4984-9fcb-c4d1718eae93/master_qoe_findings_compendium.md"
]

for p in paths:
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()

    # Insert accounting and mna sections before Cross-Dataset Relational Topology
    target_marker = "## 8. Cross-Dataset Relational Topology"
    if target_marker in content:
        content = content.replace(target_marker, accounting_and_mna_sections.strip() + "\n\n---\n\n## 10. Cross-Dataset Relational Topology")
    elif "## 10. Cross-Dataset Relational Topology" not in content:
        print(f"Warning: Marker not found in {p}")

    # Renumber subsequent sections
    content = content.replace("## 7. The Seven Missing Private-Domain Records", "## 11. The Seven Missing Private-Domain Records")
    content = content.replace("## 8. Master Simulator Parameter Specification Table", "## 12. Master Simulator Parameter Specification Table")
    content = content.replace("## 9. Master File Architecture & Directory Sitemap", "## 13. Master File Architecture & Directory Sitemap")

    # Insert new parameter rows before the end of the table
    target_table_end = "| **Payroll: Multiplier**| Full Labor Cost Multiplier | **1.53x** of Base Wage | $M_{\\text{labor}} = \\text{Total Comp} / \\text{Base Wage}$ | SF Employee Comp |\n"
    if target_table_end in content:
        content = content.replace(target_table_end, target_table_end + new_param_rows)
    else:
        # Try without double backslash
        target_table_end_single = "| **Payroll: Multiplier**| Full Labor Cost Multiplier | **1.53x** of Base Wage | $M_{\\text{labor}} = \\text{Total Comp} / \\text{Base Wage}$ | SF Employee Comp |\n"
        print("Checking table end replacement...")

    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {p}")

