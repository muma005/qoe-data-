# Data Dictionary: SEC EDGAR Financial Statement Data Sets (FSDS)

**Source:** U.S. Securities and Exchange Commission (DERA Data Library)  
**Classification:** `Real-world, Identifiable`  
**License:** Public Domain  

## Table: sub.txt (Submissions Master)
- `adsh` (VARCHAR(20), PK): Accession Submission Number assigned by EDGAR.
- `cik` (INT): Central Index Key identifying the corporate filer.
- `name` (VARCHAR): Legal entity name of the registrant.
- `sic` (INT): Standard Industrial Classification code.
- `countryba` / `stprba` / `cityba`: Business address location.
- `form` (VARCHAR(10)): Filing form type (`10-K`, `10-Q`, `8-K`, `20-F`).
- `period` (DATE): Balance sheet reporting period end date (YYYYMMDD).
- `fy` (INT): Fiscal year.
- `fp` (VARCHAR(2)): Fiscal period (`FY`, `Q1`, `Q2`, `Q3`, `Q4`).
- `filed` (DATE): Official SEC receipt timestamp.
- `prevrpt` (BOOLEAN): Restatement flag (1 if an amendment of an earlier report, 0 otherwise).

## Table: num.txt (Reported Numeric Facts)
- `adsh` (VARCHAR(20), FK): Submission identifier.
- `tag` (VARCHAR(256), FK): Taxonomy accounting tag (e.g. `Revenues`, `Assets`).
- `version` (VARCHAR(20), FK): Taxonomy release version (e.g. `us-gaap/2024`).
- `ddate` (DATE): Effective balance sheet date of the fact.
- `qtrs` (INT): Duration in quarters (0 for point-in-time balance sheet items; 1, 2, 4 for income statement flows).
- `uom` (VARCHAR(20)): Unit of measure (e.g. `USD`, `shares`).
- `value` (NUMERIC): Reported numerical amount.
- `segments` (VARCHAR): Segment dimensional qualifiers (e.g. business segment, geographic region).

## Table: tag.txt (Accounting Tag Definitions)
- `tag` (VARCHAR(256), PK): Name of the XBRL accounting tag.
- `version` (VARCHAR(20), PK): Taxonomy of origin.
- `custom` (BOOLEAN): 1 if company-specific custom tag; 0 if standard US-GAAP.
- `abstract` (BOOLEAN): 1 if structural header tag; 0 if monetary fact tag.
- `datatype` (VARCHAR(20)): Data type (e.g. `monetaryItemType`).
- `crdr` (CHAR(1)): Normal balance indicator (`C` for Credit, `D` for Debit).
- `doc` (TEXT): Official US-GAAP definition and accounting literature reference.

## Table: pre.txt (Statement Presentation Structure)
- `adsh` (VARCHAR(20), FK): Submission identifier.
- `report` (INT): Sequential statement index within the filing.
- `line` (INT): Presentation line number within that statement.
- `stmt` (CHAR(2)): Statement classification (`BS` = Balance Sheet, `IS` = Income Statement, `CF` = Cash Flows, `EQ` = Equity, `CP` = Comprehensive Income).
- `tag` (VARCHAR(256)): Tag mapped to this line.
- `version` (VARCHAR(20)): Taxonomy version.
- `prompt` (VARCHAR): Company-specific line label printed on face statements.
