# Review & Dispute Adjudication Calculation Library
**Document Reference:** `QOE-CALC-LIB-08`  
**Engagement:** Apex Global Industrial Holding Inc. (Project Titanium)  
**Standard:** AICPA CS Section 100 / FDD Partner Review Governance  

---

## 1. Materiality & De Minimis Scoping Threshold Testing Formula

In professional Quality of Earnings engagements, technical review partners establish strict de minimis scoping thresholds to prevent engagement drag on immaterial items while ensuring comprehensive coverage of material risks.

### 1.1 Mathematical Formulation

$$\text{Scoping Threshold (De Minimis)} = \min\left( \alpha \cdot \text{Reported EBITDA}, \, \beta \cdot \text{Net Revenue}, \, \text{Absolute Floor} \right)$$

Where:
* $\alpha = 0.005$ (0.50% of Reported Historical EBITDA)
* $\beta = 0.001$ (0.10% of Reported Net Revenue)
* $\text{Absolute Floor} = \$15,000.00$
* $\text{Materiality Threshold} = \min\left( 0.025 \cdot \text{Reported EBITDA}, \, 0.005 \cdot \text{Net Revenue}, \, \$100,000.00 \right)$

### 1.2 Worked Example for Apex Global Industrial Holding Inc.
* Reported Historical EBITDA: $\$3,330,000.00$
  $$\alpha \cdot \text{EBITDA} = 0.005 \times \$3,330,000.00 = \$16,650.00$$
* Reported Net Revenue: $\$24,990,000.00$
  $$\beta \cdot \text{Revenue} = 0.001 \times \$24,990,000.00 = \$24,990.00$$
* Resulting De Minimis Scope Threshold:
  $$\text{De Minimis Cut-off} = \min(\$16,650.00, \$24,990.00, \$15,000.00) = \$15,000.00$$
* Materiality Threshold:
  $$\text{Materiality Cut-off} = \min(0.025 \times \$3,330,000, \, 0.005 \times \$24,990,000, \, \$100,000) = \min(\$83,250, \$124,950, \$100,000) = \$83,250.00$$

> **Rule of Review Scoping:** Any proposed adjustment below $\$15,000.00$ is rejected from the formal EBITDA bridge unless aggregated within a recognized systemic pattern (e.g., cumulative personal expenses). Any adjustment exceeding $\$83,250.00$ requires mandatory concurring review by the Quality Review Partner (QRP).

---

## 2. Cold Review Variance Error Rate & Sample Sufficiency Models

During internal technical cold review, the QRP evaluates whether the engagement team tested an adequate sample of transactions and assesses the cumulative extrapolated error rate across key subledgers.

### 2.1 Sample Size Determination Formula (Attribute & Monetary Unit Sampling)

$$n = \frac{z^2 \cdot p \cdot (1 - p)}{e^2 + \frac{z^2 \cdot p \cdot (1 - p)}{N}}$$

Where:
* $N$ = Total population count of journal entries or subledger transactions.
* $z$ = Critical value for desired confidence level ($z = 1.96$ for 95% confidence).
* $p$ = Estimated error rate in population (assumed conservative benchmark $p = 0.05$).
* $e$ = Tolerable margin of error ($e = 0.03$ or 3.0%).

### 2.2 Cold Review Tolerable Error Bound Formula

$$\text{Upper Error Limit (UEL)} = \text{Sample Discrepancy Rate} + \left( z \cdot \sqrt{\frac{p(1 - p)}{n}} \cdot \sqrt{\frac{N - n}{N - 1}} \right)$$

If $\text{UEL} > \text{Tolerable Rate} (5.0\%)$, the QRP rejects workpaper sign-off and orders expanded substantive testing.

### 2.3 Worked Example: Accounts Payable Testing
* Population: $N = 3,420$ vendor disbursements in Q4.
* Sample tested by primary team: $n = 185$ invoices.
* Deficiencies identified: 6 invoices misclassified or delayed beyond cutoff.
* Sample error rate: $\hat{p} = \frac{6}{185} = 3.24\%$.
* Finite Population Correction: $\sqrt{\frac{3420 - 185}{3419}} = \sqrt{0.9462} = 0.9727$.
* Standard Error: $1.96 \times \sqrt{\frac{0.0324 \times 0.9676}{185}} \times 0.9727 = 1.96 \times 0.01302 \times 0.9727 = 2.48\%$.
* $\text{UEL} = 3.24\% + 2.48\% = 5.72\% > 5.00\%$.
* **Cold Review Finding:** Sample error exceeds tolerable limit. QRP issued Query `QRP-007` mandating 100% substantive audit of all AP invoices greater than $\$25,000.00$ over 60 days past due, uncovering the $\$250,000.00$ stretched AP balance.

---

## 3. Compromise Range & Sensitivity Scoring Algorithms

When an adjustment is contested on valuation or benchmark parameters (Gate 3), the FDD partner utilizes an objective compromise formulation rather than arbitrary splitting.

### 3.1 Benchmark Range Calibration Formula

$$\text{Adjudicated Concession} = \text{Preliminary Finding} - \left( \text{Revised Benchmark Metric} - \text{Baseline Operating Value} \right)$$

For Executive Replacement Compensation:
$$\text{Allowable Add-Back} = \text{Owner Actual Salary} - \text{Calibrated Benchmark Replacement GM Salary}$$

$$\text{Where: } \text{Calibrated Benchmark} = \text{Percentile}_{\text{Agreed}}(\text{Peer Survey Data})$$

### 3.2 Worked Example: Founder Salary (`PB-ARG-03`)
* Owner Historical Actual Salary & Benefits: $\$450,000.00$
* Management Proposal: Replace with junior manager at $\$100,000.00 \implies \text{Add-back } \$350,000.00$.
* QoE Preliminary Finding: Replace with full General Manager at 50th percentile (P50) $=\$250,000.00 \implies \text{Add-back } \$200,000.00$ (Haircut $\$150,000.00$).
* Seller Pushback Submission: Submitted regional Mercer compensation benchmark indicating Kansas City metro Distribution GM P40 base + target bonus $=\$225,000.00$.
* FDD Partner Adjudication Ruling: Accept P40 regional benchmark verified by Mercer survey.
  $$\text{Adjudicated Replacement Cost} = \$225,000.00$$
  $$\text{Final Adjudicated Add-Back} = \$450,000.00 - \$225,000.00 = \$225,000.00$$
  $$\text{Concession Delta Granted to Seller} = \$225,000.00 - \$200,000.00 = +\$25,000.00$$
  $$\text{Adjudicated Haircut Remaining} = \$350,000.00 - \$225,000.00 = \$125,000.00$$

---

## 4. Target Peg Collar Banding Formulation

To eliminate post-closing disputes over ordinary operational working capital volatility, professional QoE teams design collar bands around the target peg.

### 4.1 Collar True-Up Settlement Equation

$$\Delta \text{NWC Cash Flow} = 
\begin{cases}
\text{Closing NWC} - \text{Peg}_{\text{Upper}} & \text{if } \text{Closing NWC} > \text{Peg}_{\text{Upper}} \quad (\text{Buyer pays Seller}) \\
0.00 & \text{if } \text{Peg}_{\text{Lower}} \le \text{Closing NWC} \le \text{Peg}_{\text{Upper}} \quad (\text{Zero True-Up / Deadband}) \\
\text{Closing NWC} - \text{Peg}_{\text{Lower}} & \text{if } \text{Closing NWC} < \text{Peg}_{\text{Lower}} \quad (\text{Seller pays Buyer})
\end{cases}$$

Where:
* $\text{Peg}_{\text{Base}} = \$4,300,000.00$ (Run-Rate Normalized NWC Requirement)
* $\text{Collar Width } (C) = \pm \$75,000.00$
* $\text{Peg}_{\text{Lower}} = \text{Peg}_{\text{Base}} - C = \$4,300,000.00 - \$75,000.00 = \$4,225,000.00$
* $\text{Peg}_{\text{Upper}} = \text{Peg}_{\text{Base}} + C = \$4,300,000.00 + \$75,000.00 = \$4,375,000.00$

### 4.2 Mathematical Impact on Closing True-Up
* Normalized Delivered Closing NWC: $\$4,375,000.00$
* Under Point-Peg (Zero Collar):
  $$\text{Cash Flow} = \$4,375,000.00 - \$4,300,000.00 = +\$75,000.00 \quad (\text{Buyer would owe Seller})$$
* Under Agreed Collar Band ($[\$4,225,000.00, \, \$4,375,000.00]$):
  $$\text{Closing NWC} = \$4,375,000.00 = \text{Peg}_{\text{Upper}}$$
  $$\text{Post-Closing Cash True-Up} = \$0.00$$
* **Negotiation Consequence:** By agreeing to the $\$75,000.00$ collar mechanism, the buyer eliminates an immediate $\$75,000.00$ cash payment at closing while insulating against post-closing true-up disputes.

---

## 5. Arbitration Settlement Expected Value & Risk Scoring Model

Prior to entering formal post-closing arbitration under the SPA, the diligence team models the expected financial outcome of contested items before an independent accounting referee.

### 5.1 Expected Value Formula

$$\mathbb{E}[\text{Arbitration Outcome}] = \sum_{i=1}^{k} P_i \cdot V_i$$

Where:
* $P_{\text{Full Win}}$ = Probability that referee adopts buyer's QoE position in full.
* $P_{\text{Split}}$ = Probability that referee splits the difference (50/50 compromise).
* $P_{\text{Full Loss}}$ = Probability that referee adopts seller's position in full.
* $\sum P = 1.00$.

### 5.2 Mathematical Expected Value Schedule

$$\mathbb{E}[\text{Cash Recovery}] = \left( P_{\text{Full Win}} \times \text{QoE Value} \right) + \left( P_{\text{Split}} \times \frac{\text{QoE Value} + \text{Seller Value}}{2} \right) + \left( P_{\text{Full Loss}} \times \text{Seller Value} \right)$$

#### Worked Application: Stretched Accounts Payable (`ARB-001`)
* QoE Diligence Position: $\$250,000.00$ Debt Deduction.
* Seller Position: $\$0.00$ (Retain in NWC).
* Legal/Evidentiary Assessment:
  * $P_{\text{Full Win}} = 85.0\%$ (Vendor statements and credit holds provide overwhelming proof).
  * $P_{\text{Split}} = 15.0\%$ (Referee assigns portion to ordinary trade credit).
  * $P_{\text{Full Loss}} = 0.0\%$ (Clear evidence of credit holds precludes complete rejection).
* Expected Value Calculation:
  $$\mathbb{E}[\text{ARB-001}] = (0.85 \times \$250,000.00) + \left(0.15 \times \frac{\$250,000.00 + \$0.00}{2}\right) + (0.00 \times \$0.00)$$
  $$\mathbb{E}[\text{ARB-001}] = \$212,500.00 + \$18,750.00 + \$0.00 = \$231,250.00$$
* **Strategic Implication:** Expected value of $\$231,250.00$ (92.5% recovery) confirms the buyer should refuse any pre-arbitration settlement offer below $\$230,000.00$.

---

## 6. Final Purchase Price Sensitivity & Haircut Concession Re-Footing Engine

Every concession granted during pushback adjudication flows mathematically through the transaction valuation engine to recalculate the final cash paid at close.

### 6.1 Transaction Bridge Re-Footing Equation

$$\text{Final Equity Purchase Price} = \left( \text{Normalized EBITDA}_{\text{Adj}} \times M \right) - \text{Net Debt}_{\text{Adj}} + \Delta \text{NWC}_{\text{Adj}}$$

Where:
$$\text{Normalized EBITDA}_{\text{Adj}} = \text{Reported EBITDA} + \sum \text{Upheld Add-Backs} + \sum \text{Conceded Add-Backs}$$
$$\text{Net Debt}_{\text{Adj}} = \text{Funded Debt} + \left( \text{Preliminary Debt-Like} - \sum \text{Conceded Debt Deductions} \right) - \text{Unrestricted Cash}$$
$$\Delta \text{NWC}_{\text{Adj}} = f(\text{Delivered NWC}, \, \text{Peg}_{\text{Adj}}, \, \text{Collar})$$

### 6.2 Master Re-Footing Reconciliation Proof for Project Titanium
1. **Adjudicated Normalized EBITDA:**
   $$\text{Preliminary Normalized EBITDA} = \$3,610,500.00$$
   $$\text{Conceded Consulting Add-Back (PB-ARG-01)} = +\$25,000.00$$
   $$\text{Conceded Founder Salary Add-Back (PB-ARG-03)} = +\$25,000.00$$
   $$\mathbf{\text{Final Adjudicated Normalized EBITDA}} = \$3,610,500.00 + \$25,000.00 + \$25,000.00 = \mathbf{\$3,660,500.00}$$
   $$\text{Enterprise Value at 8.0x Multiple} = \$3,660,500.00 \times 8.0 = \mathbf{\$29,284,000.00}$$
   $$\text{EV Variance vs Preliminary (\$28,884,000.00)} = +\$400,000.00$$

2. **Adjudicated Net Debt:**
   $$\text{Funded Bank & Shareholder Debt} = \$4,024,500.00$$
   $$\text{Preliminary Debt-Like Items} = \$768,000.00$$
   $$\text{Concession on Deferred Revenue (PB-ARG-09)} = -\$30,000.00$$
   $$\text{Concession on Deferred Maintenance (PB-ARG-10)} = -\$60,000.00$$
   $$\text{Final Adjudicated Debt-Like Items} = \$768,000.00 - \$90,000.00 = \mathbf{\$678,000.00}$$
   $$\text{Less: Unrestricted Cash & ERC Refund} = -\$216,050.00$$
   $$\mathbf{\text{Final Adjudicated Net Debt}} = \$4,024,500.00 + \$678,000.00 - \$216,050.00 = \mathbf{\$4,486,450.00}$$
   $$\text{Net Debt Variance vs Preliminary (\$4,576,450.00)} = -\$90,000.00$$

3. **Adjudicated Working Capital Adjustment:**
   $$\text{Delivered NWC} = \$4,375,000.00$$
   $$\text{Agreed Collar Range} = [\$4,225,000.00, \, \$4,375,000.00]$$
   $$\mathbf{\text{Adjudicated Post-Closing True-Up}} = \mathbf{\$0.00}$$
   $$\text{True-Up Variance vs Preliminary (+\$75,000.00 uncollared)} = -\$75,000.00$$

4. **Final Adjudicated Equity Purchase Price:**
   $$\text{Equity Purchase Price} = \$29,284,000.00 - \$4,486,450.00 + \$0.00 = \mathbf{\$24,797,550.00}$$

5. **Net Concession Waterfall Verification:**
   $$\text{Preliminary Diligence Equity Price} = \$24,382,550.00$$
   $$+ \text{ EV Increase from EBITDA Concessions (+\$50k } \times 8.0) = +\$400,000.00$$
   $$+ \text{ Debt Reduction from Debt-Like Concessions} = +\$90,000.00$$
   $$- \text{ Working Capital True-Up Reduction from Collar} = -\$75,000.00$$
   $$\mathbf{\text{Net Seller Concessions Across Transaction}} = +\$400,000.00 + \$90,000.00 - \$75,000.00 = \mathbf{+\$415,000.00}$$
   $$\mathbf{\text{Final Adjudicated Price}} = \$24,382,550.00 + \$415,000.00 = \mathbf{\$24,797,550.00}$$

$$\text{Check: } \$24,797,550.00 - \$24,797,550.00 \equiv \$0.00 \quad \text{[TIES TO THE EXACT CENT]}$$
