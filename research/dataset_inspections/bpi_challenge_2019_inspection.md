# Technical Dataset Inspection: BPI Challenge 2019 (AkzoNobel SAP ERP Event Log)

## 1. Metadata and Provenance
- **Dataset Title:** BPI Challenge 2019: Real-World SAP ERP Purchase-to-Pay (P2P) Event Log
- **Originating Organization:** AkzoNobel (Multinational Paints & Performance Coatings Manufacturer, Netherlands)
- **Primary Host / DOI:** 4TU.ResearchData / Eindhoven University of Technology (`https://doi.org/10.4121/uuid:d06aff4b-79f0-45e6-8ec8-e19730c248f1`)
- **Direct Acquisition URL:** `http://icpmconference.org/2019/wp-content/uploads/sites/6/2019/02/BPIChallenge2019CSV.zip`
- **Authenticity Category:** Real-World, Anonymized (Authentic SAP ERP event logs extracted directly from production instances across 4 European operating subsidiaries).
- **Physical File on Disk:** [BPI_Challenge_2019.csv](file:///c:/Users/ADMIN/Desktop/QOE%20%20data%20aquisition/research/original_datasets/procurement_expenses/bpi_2019/BPI_Challenge_2019.csv) (527,457,189 bytes / 503.02 MB)

---

## 2. Structural Characteristics & Dimensions
- **Total Event Records:** 1,595,923 events
- **Total Unique Cases (PO Line Items):** 251,734 line-item traces (`case concept:name` = Purchasing Document + Item)
- **Total Unique Purchasing Documents (POs):** 76,349 Purchase Orders
- **Total Unique Vendors:** 1,975 vendors
- **Total Enterprise Operating Subsidiaries:** 4 distinct legal entities
- **Cumulative Procurement Spend:** €996,818,747.00 (~€1.0 Billion)
- **Temporal Span:** Operational records spanning 2018–2019 (with historical baseline reference timestamps)

---

## 3. Schema & Attribute Architecture
The dataset contains 22 operational and case-level attributes extracted directly from SAP MM (Materials Management) and SAP FI-AP (Financial Accounting - Accounts Payable):

| Column Name | SAP Field Mapping | Data Type | Description & Semantic Role |
| :--- | :--- | :--- | :--- |
| `eventID` | Technical PK | String | Unique event record identifier |
| `case Spend area text` | Spend Taxonomy | String | High-level procurement category (Packaging, Sales, Logistics, etc.) |
| `case Company` | BUKRS | String | Company Code / Legal Operating Subsidiary ID (`companyID_0000` to `companyID_0003`) |
| `case Document Type` | BSART | String | Purchasing Document Type (`Standard PO`, `Framework order`, `EC Purchase order`) |
| `case Sub spend area text` | Category Sub-tax | String | Granular commodity classification |
| `case Purchasing Document` | EBELN | String | SAP Purchase Order Number (10 digits) |
| `case Purch. Doc. Category name` | BSTYP | String | Document category (Purchase order, Contract) |
| `case Vendor` | LIFNR | String | Anonymized Vendor Master ID (`vendorID_0001` to `vendorID_1975`) |
| `case Item Type` | PSTYP | String | Item processing category (`Standard`, `Consignment`, `Subcontracting`) |
| `case Item Category` | Matching Rule | String | 3-way match rule (`3-way match, invoice before GR`, `3-way match, invoice after GR`, `2-way match`) |
| `case Spend classification text`| Spend Class | String | Productive/Direct (`PR`) vs Non-Productive/Indirect (`NPR`) |
| `case Source` | SYSID | String | Source ERP instance identifier |
| `case Name` | NAME1 | String | Vendor trading name alias |
| `case GR-Based Inv. Verif.` | WEBRE | Boolean | Goods-Receipt-Based Invoice Verification flag (`true`/`false`) |
| `case Item` | EBELP | String | PO line item line counter (`00010`, `00020`, etc.) |
| `case concept:name` | Case Key | String | Composite Case ID (`EBELN_EBELP`) |
| `case Goods Receipt` | WEPOS | Boolean | Goods Receipt expected indicator (`true`/`false`) |
| `event User` | ERNAM | String | User ID performing transaction (`user_001` to `user_999`, `NONE`, or `batch_xx`) |
| `event org:resource` | Resource | String | Organizational resource role |
| `event concept:name` | Activity | String | Business process activity name (SAP transaction execution) |
| `event Cumulative net worth (EUR)`| NETPR / WRBTR | Float | Cumulative monetary value in EUR at event time |
| `event time:timestamp` | CPUDT / CPUTM | Datetime | Execution timestamp down to millisecond (`DD-MM-YYYY HH:MM:SS.fff`) |

---

## 4. Empirical Frequency of Process Activities

| Activity Name (`event concept:name`) | Event Count | Frequency (%) | Functional Domain |
| :--- | :--- | :--- | :--- |
| `Record Goods Receipt` | 314,097 | 19.68% | Warehouse / Inventory Fulfillment (`MIGO`) |
| `Create Purchase Order Item` | 251,734 | 15.77% | Purchasing Commitment (`ME21N`) |
| `Record Invoice Receipt` | 228,760 | 14.33% | Accounts Payable Posting (`MIRO`) |
| `Vendor creates invoice` | 219,919 | 13.78% | Vendor External Billing / EDI Receipt |
| `Clear Invoice` | 194,393 | 12.18% | Treasury / Bank Cash Disbursement (`F-53` / `F110`) |
| `Record Service Entry Sheet` | 164,975 | 10.34% | Service Procurement Verification (`ML81N`) |
| `Remove Payment Block` | 57,136 | 3.58% | AP Gating Release (`MRBR`) |
| `Create Purchase Requisition Item` | 46,592 | 2.92% | Internal Pre-commitment Requisition (`ME51N`) |
| `Receive Order Confirmation` | 32,065 | 2.01% | Supplier Order Acknowledgement |
| `Change Quantity` | 21,449 | 1.34% | Retroactive Quantity Modification |
| `Change Price` | 12,423 | 0.78% | Retroactive Price Revision |
| `Delete Purchase Order Item` | 8,875 | 0.56% | Purchase Order Cancellation |
| `Change Approval for Purchase Order` | 7,541 | 0.47% | Approval Hierarchy Intervention |
| `Cancel Invoice Receipt` | 7,096 | 0.44% | Invoice Reversal / Rejection |
| `Vendor creates debit memo` | 6,255 | 0.39% | Adjustment Memo |
| `Change Delivery Indicator` | 3,289 | 0.21% | Delivery Term Alteration |
| `Cancel Goods Receipt` | 3,096 | 0.19% | Warehouse Return / Reversal |

---

## 5. Core Forensic & Quality of Earnings Insights
1. **Requisition Governance Breakdown:** Over **81.49% of all PO items (205,142 cases)** bypass internal Purchase Requisitions entirely, transitioning straight into PO issuance without formal pre-approval.
2. **Maverick / Unauthorized Procurement:** In **3,693 cases (1.47%)**, `Vendor creates invoice` occurs *prior* to `Create Purchase Order Item`, representing unauthorized spend that was only ratified retroactively upon invoice arrival.
3. **Severe Payment Friction (Blocked Cash Outflows):** Over **22.18% of all cases (55,839 cases)** trigger a formal payment block requiring manual AP release (`Remove Payment Block`). Blocked invoices experience a median delay of **6.18 days** and a 95th percentile delay of **81.10 days**, artificially deferring operating cash outflows.
4. **Vendor Concentration & Billing Irregularities:** The top 20% of vendors command **89.61% of total enterprise spend**. Specific vendors exhibit persistent billing dispute rates exceeding **80%** (e.g. `vendorID_0721`: 81.95% block rate, `vendorID_0818`: 80.00% block rate).
