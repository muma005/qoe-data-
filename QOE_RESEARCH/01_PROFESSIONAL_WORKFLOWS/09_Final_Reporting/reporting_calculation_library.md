# Executive Reporting & Presentation Calculation Library
**Document Reference:** `QOE-CALC-LIB-09`  
**Engagement:** Apex Global Industrial Holding Inc. (Project Titanium)  
**Standard:** AICPA CS Section 100 / Big 4 FDD Reporting Governance / ABA Model SPA  

---

## 1. Free Cash Flow (FCF) Conversion Rate Formulation

In financial due diligence reporting, senior lenders and private equity investment committees evaluate how effectively Normalized EBITDA converts into actual cash available for debt service and equity reinvestment.

### 1.1 Mathematical Formulations

$$\text{Operating Cash Flow (OCF)} = \text{Normalized EBITDA} - \Delta \text{Operating NWC} - \text{Cash Taxes Paid}$$

$$\text{Unlevered Free Cash Flow (uFCF)} = \text{OCF} - \text{Maintenance CapEx}$$

$$\text{EBITDA-to-uFCF Conversion Rate} = \frac{\text{Unlevered Free Cash Flow}}{\text{Normalized EBITDA}} \times 100\%$$

$$\text{Cash Flow Available for Debt Service (CFADS)} = \text{uFCF} - \Delta \text{Minimum Operating Cash Buffer}$$

### 1.2 Worked Application for Project Titanium (FY23 Normalized Baseline)
* **Normalized Operating EBITDA:** $\$3,660,500.00$
* **Less: Investment in Operating NWC:** $-\$145,000.00$ (Funding annual volume growth of $6.2\%$)
* **Less: Normalized Cash Taxes Paid:** $-\$480,000.00$ (Effective cash tax rate $15.5\%$ on taxable operating income)
* **Resulting Operating Cash Flow (OCF):**
  $$\text{OCF} = \$3,660,500.00 - \$145,000.00 - \$480,000.00 = \mathbf{\$3,035,500.00}$$
  $$\text{OCF Conversion Rate} = \frac{\$3,035,500.00}{\$3,660,500.00} = \mathbf{82.9\%}$$
* **Less: Maintenance Capital Expenditures:** $-\$420,000.00$
* **Resulting Unlevered Free Cash Flow (uFCF):**
  $$\text{uFCF} = \$3,035,500.00 - \$420,000.00 = \mathbf{\$2,615,500.00}$$
  $$\mathbf{\text{EBITDA-to-uFCF Conversion Rate}} = \frac{\$2,615,500.00}{\$3,660,500.00} = \mathbf{71.5\%}$$

> **Senior Lender Underwriting Implication:** An unlevered free cash flow conversion rate of $71.5\%$ yields $\$2,615,500.00$ in annual unencumbered cash, comfortably supporting senior debt service (Senior Term Loan $\$11.0M$ at $8.5\%$ interest + $1.0\%$ annual amortization = $\$1,045,000.00$ annual debt service), establishing an audited **Fixed Charge Coverage Ratio (FCCR)** of:
> $$\text{FCCR} = \frac{\text{uFCF}}{\text{Debt Service}} = \frac{\$2,615,500.00}{\$1,045,000.00} = \mathbf{2.50x} \quad (\text{Threshold requirement: } \ge 1.35x)$$

---

## 2. Maintenance vs. Growth CapEx Segregation Formulation

Diligence reports must isolate capital expenditures required to maintain existing operating capability from growth investments, preventing buyers from confusing discretionary growth with baseline capital drag.

### 2.1 Segregation Logic & Mathematical Allocation

$$\text{Total Historical CapEx} = \text{CapEx}_{\text{Maint}} + \text{CapEx}_{\text{Growth}}$$

$$\text{CapEx}_{\text{Maint}} = \sum_{k=1}^{M} \text{Asset Overhaul Expense}_k + \min\left( \text{Depreciation}_{\text{Book}}, \, \text{Baseline Replacement Budget} \right)$$

$$\text{CapEx}_{\text{Growth}} = \sum_{j=1}^{G} \text{Capacity Expansion Additions}_j + \text{New Product Tooling}$$

### 2.2 Worked Segregation for Apex Global Industrial Holding (FY23)
* **Total Audited Cash CapEx (PP&E Additions):** $\$785,000.00$
* **Maintenance CapEx Components:**
  * Distribution facility dock levelers and forklift maintenance: $\$110,000.00$
  * Vanguard CNC machine tooling replacement & routine maintenance: $\$210,000.00$
  * CloudMatrix IT hardware server replacements: $\$40,000.00$
  * General corporate IT and facility leasehold repairs: $\$60,000.00$
  * **Total Maintenance CapEx:** $\mathbf{\$420,000.00}$ ($53.5\%$ of total CapEx; $1.7\%$ of Net Revenue)
* **Growth CapEx Components:**
  * Vanguard 5-axis CNC expansion machine installation (Machine #5): $\$265,000.00$
  * CloudMatrix proprietary AI analytics platform infrastructure build: $\$100,000.00$
  * **Total Growth CapEx:** $\mathbf{\$365,000.00}$ ($46.5\%$ of total CapEx)

$$\text{Reconciliation: } \$420,000.00 \text{ (Maint)} + \$365,000.00 \text{ (Growth)} = \mathbf{\$785,000.00} \quad \text{[TIES TO CASH FLOW STATEMENT]}$$

---

## 3. Weighted Average Trailing & Run-Rate EBITDA Formulations

When target companies experience mid-year restructuring, acquisitions, or customer losses, the QoE report models both historical trailing earnings and annualized run-rate maintainable EBITDA.

### 3.1 Mathematical Formulations

$$\text{Historical Trailing Normalized EBITDA (LTM)} = \sum_{t=1}^{12} \text{Monthly Normalized EBITDA}_t$$

$$\text{Weighted Multi-Year Normalized EBITDA} = \sum_{y=1}^{3} w_y \cdot \text{Normalized EBITDA}_y$$

Where standard institutional PE weighting is:
$$w_{\text{FY21}} = 0.20, \quad w_{\text{FY22}} = 0.30, \quad w_{\text{FY23}} = 0.50 \quad \left(\sum w = 1.00\right)$$

$$\text{Annualized Run-Rate EBITDA (Exit Run-Rate)} = \left( \sum_{m=10}^{12} \text{Normalized EBITDA}_m \right) \times 4.0$$

### 3.2 Worked Calculation for Project Titanium
* FY21 Normalized EBITDA: $\$2,890,000.00$
* FY22 Normalized EBITDA: $\$3,240,000.00$
* FY23 Normalized EBITDA: $\$3,660,500.00$
* **3-Year Weighted Average Normalized EBITDA:**
  $$\text{Weighted EBITDA} = (0.20 \times \$2,890,000) + (0.30 \times \$3,240,000) + (0.50 \times \$3,660,500)$$
  $$\text{Weighted EBITDA} = \$578,000.00 + \$972,000.00 + \$1,830,250.00 = \mathbf{\$3,380,250.00}$$
* **Q4 Exit Run-Rate EBITDA:**
  * Q4 Normalized EBITDA (Oct: $\$310.5k$, Nov: $\$305.0k$, Dec: $\$312.0k$): $\$927,500.00$
  $$\text{Annualized Exit Run-Rate EBITDA} = \$927,500.00 \times 4 = \mathbf{\$3,710,000.00}$$

---

## 4. Definitive Purchase Price Walk Equation

The definitive purchase price walk converts theoretical Enterprise Value into the net cash delivered to selling shareholders at closing.

### 4.1 Master Purchase Price Walk Formulation

$$\text{Equity Purchase Price} = (\text{Normalized EBITDA} \times M) - \text{Net Debt} + \Delta \text{NWC}_{\text{Collar}}$$

Where:
$$\text{Enterprise Value (EV)} = \text{Normalized EBITDA} \times M = \$3,660,500.00 \times 8.0 = \mathbf{\$29,284,000.00}$$

$$\text{Net Debt} = \text{Funded Debt} + \text{Debt-Like Items} - \text{Unrestricted Cash Offsets}$$
$$\text{Funded Debt} = \$3,500,000.00 \text{ (Bank)} + \$524,500.00 \text{ (Shareholder)} = \mathbf{\$4,024,500.00}$$
$$\text{Debt-Like Items} = \$250k \text{ (AP)} + \$145k \text{ (Bonus)} + \$68k \text{ (Tax)} + \$45k \text{ (PTO)} + \$110k \text{ (SaaS Def)} + \$60k \text{ (CapEx)} = \mathbf{\$678,000.00}$$
$$\text{Unrestricted Cash} = \$524,050.00 \text{ (Gross)} - \$100k \text{ (LC)} - \$250k \text{ (Float)} + \$42k \text{ (ERC)} = \mathbf{\$216,050.00}$$
$$\mathbf{\text{Net Debt Deduction}} = \$4,024,500.00 + \$678,000.00 - \$216,050.00 = \mathbf{\$4,486,450.00}$$

$$\Delta \text{NWC}_{\text{Collar}} = 
\begin{cases}
\text{Closing NWC} - \$4,375,000.00 & \text{if Closing NWC} > \$4,375,000.00 \\
\$0.00 & \text{if } \$4,225,000.00 \le \text{Closing NWC} \le \$4,375,000.00 \\
\text{Closing NWC} - \$4,225,000.00 & \text{if Closing NWC} < \$4,225,000.00
\end{cases}$$

Since Delivered Closing NWC $=\$4,375,000.00$ (upper boundary):
$$\Delta \text{NWC}_{\text{Collar}} = \mathbf{\$0.00}$$

### 4.2 Definitive Purchase Price Footing
$$\text{Equity Purchase Price} = \$29,284,000.00 - \$4,486,450.00 + \$0.00 = \mathbf{\$24,797,550.00}$$

$$\text{Check: } \$24,797,550.00 - \$24,797,550.00 \equiv \mathbf{\$0.00} \quad \text{[TIES TO THE EXACT CENT]}$$

---

## 5. Dynamic Closing Funds Flow Settlement Equation

At transaction closing, the funds flow model must satisfy strict mathematical equality where total capital sources equal total cash disbursements:

### 5.1 Sources and Uses Mathematical Formulation

$$\sum_{i=1}^{S} \text{Sources of Funds}_i \equiv \sum_{j=1}^{U} \text{Uses of Funds}_j$$

Where:
$$\mathbf{\text{Total Sources of Funds}} = \text{Sponsor Equity} + \text{Co-Invest Equity} + \text{Rollover Equity} + \text{Senior Debt} + \text{Seller Note} + \text{Target Cash}$$
$$\text{Total Sources} = \$16,000,000 + \$2,000,000 + \$1,500,000 + \$11,000,000 + \$1,000,000 + \$524,050 = \mathbf{\$32,024,050.00}$$

$$\mathbf{\text{Total Uses of Funds}} = \text{Net Cash to Seller} + \text{Rollover} + \text{Seller Note} + \text{Escrows} + \text{Debt Payoffs} + \text{Debt-Like Payoffs} + \text{Fees} + \text{Cash Retained}$$
$$\text{Net Cash to Seller} = \$20,479,550.00$$
$$\text{Non-Cash Consideration (Rollover + Note)} = \$1,500,000.00 + \$1,000,000.00 = \$2,500,000.00$$
$$\text{Escrows (Indemnity } \$1.5\text{M} + \text{WC } \$250\text{k} + \text{Tax } \$68\text{k)} = \$1,818,000.00$$
$$\text{Funded Debt Payoffs (Term } \$2.5\text{M} + \text{Revolver } \$1.0\text{M} + \text{Insider } \$524.5\text{k)} = \$4,024,500.00$$
$$\text{Debt-Like Payoffs (Stretched AP } \$250\text{k} + \text{Bonuses } \$145\text{k} + \text{CNC Repair } \$60\text{k)} = \$455,000.00$$
$$\text{Transaction & Financing Fees (M&A Fees } \$1.85\text{M} + \text{OID/Financing Fees } \$547\text{k)} = \$2,397,000.00$$
$$\text{Target Cash Retained (Operating Float } \$250\text{k} + \text{Restricted LC Cash } \$100\text{k)} = \$350,000.00$$

$$\mathbf{\text{Total Uses}} = \$20,479,550 + \$2,500,000 + \$1,818,000 + \$4,024,500 + \$455,000 + \$2,397,000 + \$350,000 = \mathbf{\$32,024,050.00}$$

$$\mathbf{\text{Closing Balance Variance}} = \text{Total Sources} - \text{Total Uses} = \$32,024,050.00 - \$32,024,050.00 \equiv \mathbf{\$0.00}$$

---

## 6. Post-Closing True-Up Settlement & Escrow Release Mechanics

Under Section 2.5 of the American Bar Association (ABA) Model Stock Purchase Agreement, post-closing settlement is governed by formal true-up equations:

### 6.1 True-Up Settlement Equation

$$\text{Post-Closing Net True-Up Cash Flow } (\Omega) = \Delta \text{NWC}_{\text{Actual}} + \Delta \text{Net Debt}_{\text{Actual}} + \Delta \text{Transaction Expenses}_{\text{Actual}}$$

Where:
$$\Delta \text{NWC}_{\text{Actual}} = f(\text{Final Closing NWC}, \, \text{Peg}_{\text{Target}} = \$4,300,000.00, \, \text{Collar} = \pm \$75,000.00)$$

If $\Omega > 0$: Buyer pays Seller from operating cash.  
If $\Omega < 0$: Seller pays Buyer, disbursed first from the **$\mathbf{\$250,000.00}$ Working Capital Escrow Account**, with any excess drawn from the **$\mathbf{\$1,500,000.00}$ Indemnity Escrow Account**.

### 6.2 Escrow Release Schedule
* **Day 90 Post-Close:** Working Capital Escrow released to Seller net of resolved true-up adjustments.
* **Month 18 Post-Close:** General Indemnity Escrow released to Seller net of pending representation breach claims.
* **Month 24 Post-Close:** Special State Sales Tax Escrow ($\$68,000.00$) released upon receipt of formal state voluntary disclosure agreements (VDAs) or audit clearance certificates.
