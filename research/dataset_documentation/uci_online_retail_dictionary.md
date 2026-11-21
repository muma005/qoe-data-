# Data Dictionary: UCI Online Retail Dataset

**Source:** Great Britain Online Giftware Wholesaler / Retailer  
**Classification:** `Real-world, Anonymized`  
**License:** CC BY 4.0  

## Fields
- `InvoiceNo` (VARCHAR(10), PK part): 6-digit integer assigned to each transaction. If prepended with letter `'C'`, it indicates a cancellation / credit note.
- `StockCode` (VARCHAR(20)): Product / SKU identifier code. Contains 3,684 distinct SKU items, plus administrative charge codes (e.g. `POST`, `D`, `CRUK`, `BANK CHARGES`, `AMAZONFEE`).
- `Description` (VARCHAR(256)): Descriptive product trade name.
- `Quantity` (INT): Number of units sold (positive) or returned/cancelled (negative).
- `InvoiceDate` (DATETIME): Invoice creation timestamp.
- `UnitPrice` (FLOAT): Selling price per unit in British Pounds (£).
- `CustomerID` (INT/FLOAT): Unique 5-digit customer identification number. Null/NaN for guest walk-in transactions (135,080 rows).
- `Country` (VARCHAR(50)): Name of country where customer resides (38 distinct countries, 90%+ United Kingdom).
