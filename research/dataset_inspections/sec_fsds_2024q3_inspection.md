# Technical Inspection Report: SEC EDGAR Financial Statement Data Sets (2024 Q3)

**Category:** `Category 1: Financial Accounting & General Ledger`  
**Inspection Date:** `2026-11-12 10:51:24`  
**Originating Organization:** U.S. Securities and Exchange Commission (DERA Data Library)  
**Classification:** `Real-world, Identifiable`  
**License:** Public Domain (U.S. Federal Government Work)  
**Total Corporate Filings Monitored (Quarterly):** 6,699 filings across 6,008 reporting entities  

## 1. Relational File Architecture
The SEC Financial Statement Data Sets provide flattened relational tables extracted from XBRL corporate filings:
- `sub.txt` (6,699 rows, 36 columns): Submission metadata (CIK, company name, form type, fiscal year, period end date, restatement flags, SIC industry code).
- `num.txt`: Numeric facts reported on primary financial statements (tag, version, period end date, quarters duration, unit of measure, reported value).
- `tag.txt`: Defining taxonomy metadata, standard US-GAAP accounting tags, debit/credit balance definitions.
- `pre.txt`: Presentation structure mapping financial statement line items (Balance Sheet, Income Statement, Cash Flows) in sequential order.

## 2. Filing Population Breakdown
- **Unique Reporting Entities (CIKs):** 6,008 companies
- **Filing Form Distribution:**
{
  "10-Q": 5390,
  "10-K": 403,
  "6-K": 291,
  "S-1/A": 102,
  "10-Q/A": 94,
  "10-K/A": 87,
  "20-F": 83,
  "S-1": 64
}

## 3. Accounting Restatements & Amendments (`prevrpt = 1`)
- **Total Amended / Restatement Filings:** `169` filings (2.52% of quarter submissions).
- **QoE Significance:** In transaction diligence, prior period restatements represent severe red flags regarding management accounting reliability, internal controls, and earnings quality.

## 4. QoE Simulator Value
1. **Gold Standard Financial Statement Benchmark:** Supplies authentic, audited balance sheets, income statements, and cash flow statements across thousands of companies.
2. **Standard US-GAAP Chart of Accounts:** Tag taxonomy (`tag.txt`) establishes the definitive real-world standard for chart of accounts definitions, debit/credit indicators, and financial statement roll-ups.
3. **Footnote & Disclosure Modeling:** Contains disaggregated segment disclosures and footnote schedules vital for pro forma adjustments and carve-out diligence.
