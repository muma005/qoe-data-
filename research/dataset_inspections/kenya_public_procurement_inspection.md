# Technical Dataset Inspection: Kenyan Public Procurement Portal (PPIP) Active Tenders

## 1. Metadata and Provenance
- **Dataset Title:** Kenya Public Procurement Information Portal (PPIP) Active Tenders & Bidding Controls
- **Originating Organization:** Public Procurement Regulatory Authority (PPRA), Republic of Kenya
- **Primary Source / API Endpoint:** `https://tenders.go.ke/api/active-tenders` (Open Contracting Data Standard - OCDS compliant API)
- **Authenticity Category:** Real-World, Identifiable (Official sovereign statutory notices and bidding controls published directly by Kenyan state procuring entities).
- **Physical Files on Disk:**
  - Flattened Table: [kenya_tenders_flattened.csv](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/original_datasets/procurement_expenses/kenya_procurement/kenya_tenders_flattened.csv) (68,039 bytes, 200 tenders, 38 columns)
  - Raw Nested JSON: [kenya_tenders_raw.json](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/original_datasets/procurement_expenses/kenya_procurement/kenya_tenders_raw.json) (2,094,103 bytes, complete API responses including nested entities, officers, documents, and preference groups)

---

## 2. Structural Dimensions & Field Architecture
- **Sample Records:** 200 active sovereign tenders across FY 2026/2027
- **Unique Procuring Entities:** 41 distinct public bodies (County Governments, National CDF Committees, TVET Colleges, State Authorities)
- **Procurement Methods:** Open Tender (190), Request for Proposals (5), Expression of Interest (4), Disposal of Assets (1)
- **Procurement Categories:** Works / Civil Construction (148), Goods (25), Non-Consultancy Services (18), Consultancy Services (8), Asset Disposal (1)

### Key Attributes Analyzed:
| Column Name | Semantic Role & Forensic Value |
| :--- | :--- |
| `tender_id` / `ocid` | Sovereign Open Contracting Identifier (`ocds-5whusi-XXXXXX`) |
| `tender_ref` | Official tender reference code |
| `title` | Procurement scope of work / goods description |
| `procuring_entity_name` | Public purchasing organization (e.g., Bungoma County, Nakuru County) |
| `procurement_method_title`| Solicitation method (Open Tender, RFP, EOI) |
| `published_at` | Official public advertisement timestamp |
| `close_at` | Bid submission closing deadline timestamp |
| `validity_in_days` | Legal tender validity period (contract award window) |
| `tender_fee` | Pay-to-bid barrier fee in Kenya Shillings (KES) |
| `is_reservation` / `agpo_groups`| Affirmative action reservations (Youth, Women, Persons with Disabilities) |
| `addenda_count` | Number of specification modifications issued post-publication |
| `created_by_user` / `created_by_email` | Procurement officer identity and official contact |

---

## 3. Empirical Findings & Forensic Procurement Signals

### A. Statutory Notice Squeeze (Section 102 PPADA Violation)
Under Section 102 of the Kenya Public Procurement and Asset Disposal Act (PPADA 2015), national open tenders must be advertised for a **statutory minimum of 14 calendar days** to allow adequate competitive bidding.
- **Empirical Median Advertising Duration:** **11.4 days**
- **Empirical Mean Advertising Duration:** **11.1 days**
- **Statutory Non-Compliance Rate:** **88.0% of tenders (176 of 200)** provide less than the mandatory 14-day notice period!
- **Works/Infrastructure Non-Compliance:** In high-value civil construction ("Works"), **92.6% of tenders** violate the 14-day rule (median 11.4 days).
- **Forensic Due Diligence Implication:** In public-private investigations and QoE reviews of government contractors, artificially compressed bidding windows represent a classic indicator of restrictive solicitation or pre-arranged bidding.

### B. Affirmative Action & AGPO Allocation
- **33.0% of tenders (66 of 200)** are explicitly reserved for preferential target groups under the Access to Government Procurement Opportunities (AGPO) program:
  - Women: 27 tenders (40.9% of reserved)
  - Youth: 19 tenders (28.8% of reserved)
  - People with Disabilities: 10 tenders (15.2% of reserved)
  - Combined Target Groups: 10 tenders (15.2% of reserved)
- This empirical rate directly reflects compliance with Kenya's constitutional mandate requiring 30% of public procurement spend to be allocated to marginalized demographic groups.

### C. Commercial Barriers & Pay-to-Bid Fees
- **93.0% of tenders** provide open, barrier-free access with zero tender fees (`tender_fee = 0`).
- **7.0% of tenders (14 tenders)** enforce monetary tender purchase fees ranging from **KES 1,000 to KES 560,000** (mean: KES 55,413.26), creating financial gating for potential competitors.

### D. Specification Volatility (Pre-Bid Addenda)
- **5.0% of tenders** experienced post-publication modifications, with 14 official addenda issued modifying technical specifications, submission deadlines, or qualification criteria during the active bidding window.
