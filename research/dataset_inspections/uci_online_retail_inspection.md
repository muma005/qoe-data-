# Technical Inspection Report: UCI Online Retail Dataset

**Category:** `Category 2: Revenue and Commercial Activity`  
**Inspection Date:** `2026-11-12 10:51:24`  
**Originating Organization:** UK Non-Store Online Retail Wholesaler  
**Classification:** `Real-world, Anonymized`  
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Total Records:** 541,909 invoice line items  
**Temporal Span:** `2010-12-01 08:26:00` to `2011-12-09 12:50:00` (1 year, 10 days)  

## 1. Schema & Field Inventory
- `InvoiceNo` (object): 6-digit integer per transaction; prepended with `'C'` if transaction is a cancellation/credit note.
- `StockCode` (object): Product identifier code (3,684 distinct SKU items).
- `Description` (object): Product description text.
- `Quantity` (int64): Units purchased or returned.
- `InvoiceDate` (datetime/object): Transaction timestamp.
- `UnitPrice` (float64): Unit selling price in GBP (£).
- `CustomerID` (float64): Unique 5-digit customer identifier (135,080 rows are NaN for guest checkouts).
- `Country` (object): Delivery country name (38 distinct countries, dominated by United Kingdom).

## 2. Commercial & Revenue Profile
- **Gross Commercial Invoices:** £10,666,684.54
- **Returns, Cancellations & Credit Notes:** £-918,936.61 (8.62% return rate)
- **Net Recognized Revenue:** £9,747,747.93
- **Cancellation / Credit Note Volume:** `9,288` records (1.71% of all lines).
- **Negative Quantity Records:** `10,624` records.
- **Negative Unit Price Anomalies:** `2` records (e.g. debt write-offs or accounting adjustments).

## 3. Customer Concentration & Quality of Earnings Implications
- **Total Unique Active Customers:** `4,372`
- **Top 10 Customer Concentration:** `14.42%` of total gross revenue.
- **Top 20 Customer Concentration:** `19.93%` of total gross revenue.
- **Missing Customer IDs (Guest Checkout Risk):** 135,080 records (24.93%) lack customer identifiers, creating significant blind spots for cohort retention and recurring revenue verification.

## 4. Forensic Anomalies Discovered
1. **Post-Closing / Out-of-Period Returns:** High volumes of cancellations referencing original invoice numbers from preceding months.
2. **Pricing Concessions & Adjustments:** Zero unit price entries (`UnitPrice = 0.0`) totaling 2,515 records representing promotional giveaways, samples, or manual invoice overrides.
3. **Severe Return Spikes:** Certain individual cancellation records exceed £10,000 (e.g. manual inventory write-down codes disguised as invoices like `AMAZONFEE`, `Manual`, `CRUK`).

## 5. QoE Simulator Value
- **Proof of Return Reserve Requirements:** Simulates the QoE requirement to calculate returns reserves and adjust reported revenue for trailing returns.
- **Customer Concentration Risk Analysis:** Directly feeds into quality of earnings revenue concentration risk haircuts and sensitivity modeling.
