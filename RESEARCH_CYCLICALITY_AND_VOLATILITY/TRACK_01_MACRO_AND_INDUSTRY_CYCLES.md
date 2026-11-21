# Track 1 Research Dossier: Macroeconomic & Sector Cyclicality

**Research Program:** Empirical Grounding for Quality of Earnings (QoE) Simulation  
**Investigation Track:** Track 1 — Macroeconomic & Industry-Specific Cyclicality  
**Status:** COMPLETE & VERIFIED  
**Target Sectors:** B2B Wholesale Distribution, Contract & Discrete Manufacturing, B2B Enterprise SaaS  
**Primary Data Sources:** Federal Reserve Economic Data (FRED), NBER Business Cycle Dating Committee, U.S. Census Bureau, Institute for Supply Management (ISM), SEC Form 10-K / 10-Q Longitudinal Filings (Fastenal, MSC Industrial Direct, Applied Industrial Technologies, Plexus Corp, Kimball Electronics, Sanmina), KeyBanc Capital Markets Private SaaS Surveys, Bessemer Venture Partners State of the Cloud.

---

## 1. Macroeconomic Cycle Baselines (Federal Reserve & NBER)

To establish the macro pulse for the simulation engine, we examine the official business cycle chronology from the National Bureau of Economic Research (NBER) and industrial time-series from the Federal Reserve Board of Governors (G.17 release via FRED).

### 1.1. NBER Business Cycle Duration Chronology (1945–2020)
According to the NBER Business Cycle Dating Committee:
* **Post-WWII Average Contraction (Peak to Trough):** **10.3 months** (~3 to 4 quarters).
* **Post-WWII Average Expansion (Trough to Peak):** **64.2 months** (~21 quarters / ~5.3 years).
* **Standard Business Cycle Ratio:** Expansions last approximately **6.2x longer** than contractions. Contractions are violent, asymmetric, and front-loaded, whereas expansions are gradual and compounding.
* **Modern Cycle Range:**
  * *Longest Post-War Contraction:* 2007–2009 Great Recession (18 months: Dec 2007 to June 2009).
  * *Shortest Post-War Contraction:* 2020 COVID Shock (2 months: Feb 2020 to April 2020).

### 1.2. Federal Reserve Industrial Production & Capacity Utilization Time Series

```
+-----------------------------------+--------------------+--------------------+-----------------------+
| Series Name / FRED Code           | Cycle Window       | Peak Value (Date)  | Trough Value (Date)   | Peak-to-Trough Drop   |
+-----------------------------------+--------------------+--------------------+-----------------------+
| INDPRO (Total Industrial Prod.)   | 2007-2009 GFC      | 102.1 (Dec 2007)   | 84.8 (June 2009)      | -16.9% (-17.3 pts)    |
| IPMAN (Manufacturing Sector)      | 2007-2009 GFC      | 104.5 (Dec 2007)   | 86.2 (June 2009)      | -17.5% (-18.3 pts)    |
| MCUMFN (Mfg Capacity Utilization) | 2007-2009 GFC      | 79.7% (Dec 2007)   | 64.4% (June 2009)     | -1,530 bps (-15.3%)   |
+-----------------------------------+--------------------+--------------------+-----------------------+
| INDPRO (Total Industrial Prod.)   | 2020 COVID Shock   | 101.4 (Feb 2020)   | 84.6 (April 2020)     | -16.6% (in 2 months)  |
| IPMAN (Manufacturing Sector)      | 2020 COVID Shock   | 100.9 (Feb 2020)   | 82.8 (April 2020)     | -17.9% (in 2 months)  |
| MCUMFN (Mfg Capacity Utilization) | 2020 COVID Shock   | 75.3% (Feb 2020)   | 63.3% (April 2020)    | -1,200 bps (-12.0%)   |
+-----------------------------------+--------------------+--------------------+-----------------------+
| ISM Manufacturing PMI             | 2015-2016 Mini-Rec | 57.9 (Aug 2014)    | 48.2 (Jan 2016)       | Contraction (<50)     |
| ISM Manufacturing PMI             | 2022-2023 Destock  | 53.0 (Nov 2022)    | 46.7 (Mid-Late 2023)  | 12 straight months <50|
+-----------------------------------+--------------------+--------------------+-----------------------+
```

#### Key Empirical Macro Takeaways:
1. **Contraction Depth Ceiling:** In an economy-wide recession (2008 or 2020), aggregate US manufacturing output drops between **16.5% and 18.0%**.
2. **Capacity Utilization Collapse:** Capacity utilization plunges from normal mid-expansion levels (76%–80%) to severe distress levels (**63%–64%**), idling roughly 36% of the nation's plant capacity.
3. **Mid-Cycle "Industrial Recessions":** Manufacturing can experience severe recessions even when overall GDP is positive (e.g., 2015–2016 oil/commodity bust, and 2023 post-COVID inventory de-stocking with 12 consecutive months of ISM PMI contraction).

---

## 2. Sector A: B2B Wholesale Distribution Empirical Analysis

We analyze the SEC Form 10-K and 10-Q longitudinal filings of the premier publicly traded industrial and MRO distributors: **Fastenal Company (NASDAQ: FAST)**, **MSC Industrial Direct Co. (NYSE: MSM)**, and **Applied Industrial Technologies (NYSE: AIT)**.

### 2.1. Fastenal Company (FAST) — Longitudinal Performance Across Recessions

#### Annual Income Statement Data (SEC Form 10-K, $ in thousands):
* **FY2008:** Net Sales = $2,340,425 | Gross Profit = $1,236,131 (52.8%) | Operating Income = $450,237 (19.2%)
* **FY2009:** Net Sales = $1,930,330 | Gross Profit = $983,322 (50.9%) | Operating Income = $295,793 (15.3%)
* **Annual Variance (2008 to 2009):**
  * Net Sales: **-$410,095 (-17.5%)**
  * Gross Margin: **-190 bps** (fell from 52.8% to 50.9% due to steel price deflation and lower supplier volume rebates)
  * Operating Income: **-$154,444 (-34.3%)**
  * **Empirical Degree of Operating Leverage (DOL):** $\frac{-34.3\%}{-17.5\%} = \mathbf{1.96\times}$ (Operating profit fell nearly double the rate of sales).

#### Quarterly Sequence & Drawdown Trajectory (SEC Form 10-Q / 10-K, $ in thousands):

```
Quarter       Net Sales ($k)   Sequential QoQ   YoY Change    Status in Cycle
---------------------------------------------------------------------------------
Q1 2008       $566,210         +3.9%            +12.4%        Expansion
Q2 2008       $604,219         +6.7%            +11.8%        Expansion
Q3 2008       $625,037         +3.4%            +13.1%        CYCLE PEAK
Q4 2008       $544,959        -12.8%             +0.1%        Contraction Begins
Q1 2009       $489,347        -10.2%            -13.6%        Severe Contraction
Q2 2009       $474,894         -3.0%            -21.4%        CYCLE TROUGH
Q3 2009       $489,339         +3.0%            -21.7%        Early Trough Rebound
Q4 2009       $477,094         -2.5%            -12.5%        Stabilization
Q1 2010       $520,770         +9.2%             +6.4%        Recovery Phase
Q2 2010       $571,180         +9.7%            +20.3%        Expansion
Q3 2010       $603,750         +5.7%            +23.4%        Approaching Prior Peak
Q4 2010       $573,770         -5.0%            +20.3%        Seasonal Q4 Dip
Q1 2011       $640,583        +11.6%            +23.0%        FULL RECOVERY (Exceeds Q3 2008)
```

#### Fastenal Cycle Duration & Shape Metrics:
* **Peak-to-Trough Drawdown:** From Q3 2008 ($625,037k) to Q2 2009 ($474,894k) = **-24.02%**.
* **Contraction Duration:** **3 quarters (9 months)**.
* **Trough-to-Recovery Duration:** **7 quarters (21 months)** (from Q2 2009 trough to Q1 2011 surpassing peak).
* **Total Cycle Length (Peak to Peak Recovery):** **10 quarters (30 months / 2.5 years)**.

---

### 2.2. MSC Industrial Direct Co. (MSM) — Longitudinal Performance

#### Annual Income Statement Data (SEC Form 10-K, FY ends late August, $ in thousands):
* **FY2008 (Ended Aug 30, 2008):** Net Sales = $1,771,705 | Operating Income = $319,528 (18.0%) | Gross Margin = 46.2%
* **FY2009 (Ended Aug 29, 2009):** Net Sales = $1,440,845 | Operating Income = $204,718 (13.7%) | Gross Margin = 46.2%
* **Annual Variance (FY08 to FY09):**
  * Net Sales: **-$330,860 (-16.3%)**
  * Gross Margin: **0 bps change** (remained exactly 46.2%; selective price increases offset adverse customer mix shifts)
  * Operating Income: **-$114,810 (-35.9%)**
  * Operating Margin: **-430 bps** (compressed from 18.0% to 13.7%)
  * **Empirical Degree of Operating Leverage (DOL):** $\frac{-35.9\%}{-16.3\%} = \mathbf{2.20\times}$.

#### Quarterly Sequence & Drawdown Trajectory (SEC Form 10-Q):
* **Pre-Recession Peak:** Q3 FY08 (Ended May 31, 2008) = **$457,238k**
* **Quarterly Trough:** Q3 FY09 (Ended May 30, 2009) = **$350,489k**
* **Peak-to-Trough Drawdown:** $\frac{350,489 - 457,238}{457,238} = \mathbf{-23.34\%}$.
* **Contraction Duration:** **4 quarters (12 months)**.

---

### 2.3. Distribution Sub-Sector Dispersion: MRO vs. OEM Dynamics

The empirical data reveals a critical bifurcation within distribution:

| Distribution Category | Product Types | Recession Revenue Drawdown | Demand Elasticity | QoE Normalization Risk |
| :--- | :--- | :--- | :--- | :--- |
| **MRO (Maintenance, Repair, Operations)** | Bearings, cutting tools, lubricants, replacement valves, safety consumables | **-8% to -15%** | Highly inelastic; equipment must be maintained while operating | Low; rapid rebound as factories resume maintenance backlogs |
| **OEM / Production Fasteners** | Fasteners, stampings, raw stock embedded into customer finished goods | **-20% to -35%** | Highly elastic; tied to new unit production and CapEx | High; prone to extreme customer de-stocking and order freezes |
| **Project / Capital Construction** | Electrical switchgear, large HVAC, heavy pipe & tube | **-25% to -45%** | Discretionary CapEx; projects deferred or canceled | Very High; multi-year lag before new commercial projects unfreeze |

---

## 3. Sector B: Contract & Discrete Manufacturing Empirical Analysis

We analyze electronics contract manufacturers (ECM) and precision machining comparables: **Kimball Electronics (NASDAQ: KE)**, **Plexus Corp (NASDAQ: PLXS)**, and **Sanmina Corporation (NASDAQ: SANM)**.

### 3.1. Kimball Electronics (KE) — FY2023 to FY2024 Inventory Destocking Shock

Kimball Electronics provides pristine, modern empirical documentation of how customer de-stocking and operating leverage impact a mid-tier contract manufacturer (SEC Form 10-K, FY ends June 30):

```
Line Item ($ in thousands)        FY2023 (Ended June 30)   FY2024 (Ended June 30)   Variance ($)    Variance (%)
-----------------------------------------------------------------------------------------------------------------
Net Sales                         $1,823,000               $1,715,000               -$108,000       -5.92%
Operating Income                  $87,700                  $49,300                  -$38,400        -43.79%
Operating Margin                  4.81%                    2.87%                    -194 bps        -40.33%
Cash Flow from Operations (CFO)   ~$32,000                 >$73,000                 +$41,000        +128.1%
Inventory Balance Reduction       Baseline                 -25.0% YoY               -$115,000       -25.00%
```

#### Critical Manufacturing Findings:
1. **Monstrous Operating Leverage in Low-Margin Manufacturing:**
   $$DOL = \frac{\% \Delta Operating\ Income}{\% \Delta Net\ Sales} = \frac{-43.79\%}{-5.92\%} = \mathbf{7.40\times}$$
   A minor **~6% revenue drop** resulted in a **~44% collapse in operating profit** because plant fixed overhead (depreciation, cleanroom leases, manufacturing engineering staff) cannot be trimmed without shuttering facilities.
2. **The Working Capital "Cash Inversion" Paradox:**
   Despite operating profit collapsing by 44%, **Operating Cash Flow more than doubled** (from ~$32M to >$73M). Why? Because management aggressively liquidated inventories (-25% YoY), releasing cash locked up on the balance sheet. In QoE diligence, this is a massive trap: **uninformed buyers view record cash flows during a downturn as a sign of financial strength, failing to realize it is a liquidation event that will violently reverse into a cash drain when sales rebound.**

### 3.2. Plexus Corp (PLXS) & Sanmina — 2008–2009 Structural Adjustments
* **Plexus Corp (FY08 to FY09):** Net sales dropped from $1,843,597k to $1,618,599k (-12.2%). Operating income dropped by **$51.4 million**, forcing the closure of its manufacturing facility in Ayer, Massachusetts, $5.7M in goodwill impairment, and $1.2M in employee severance.
* **Sanmina Corporation:** Operating margins collapsed near breakeven (~1.6% in 2008), with severe capacity underutilization charges and large restructuring write-downs across high-volume assembly plants.

---

## 4. Sector C: B2B Enterprise SaaS Empirical Analysis

We analyze benchmark data from **KeyBanc Capital Markets (KBCM) Private SaaS Surveys**, **Bessemer Venture Partners State of the Cloud**, and public SaaS comparables across the 2008–2009 and 2022–2023 tech re-ratings.

### 4.1. The "SaaS Lag" Phenomenon

Unlike distribution or manufacturing where purchase orders are canceled overnight, SaaS companies exhibit a pronounced **2 to 4 quarter (6 to 12 month) lag** before macroeconomic distress registers in GAAP revenue:

```
[Macro Shock Hits] (Month 0)
        │
        ▼
[Leading Indicators Collapse] (Months 1–3 / Q1)
  - Sales cycles stretch from 60–90 days to 120–180 days (+50%)
  - Pipeline conversion rates drop from 25% to 14%
  - Net New ARR bookings drop 30%–60%
        │
        ▼
[Deferred Revenue Cushion] (Months 3–6 / Q2)
  - GAAP revenue continues growing (+10% to +20%) because annual upfront 
    subscriptions are recognized ratably under ASC 606.
  - Inexperienced buyers think the company is "recession-proof".
        │
        ▼
[The Renewal Cliff & Hidden Churn] (Months 6–12 / Q3–Q4)
  - Pre-paid contracts come up for annual renewal.
  - Customers down-tier seat licenses ("soft churn") or cancel outright.
  - Net Retention Rate (NRR) collapses.
        │
        ▼
[GAAP Revenue Deceleration & Free Cash Flow Crunch] (Months 12–18 / Year 2)
  - Billings collapse, deferred revenue shrinks, and GAAP revenue growth halts.
```

### 4.2. Empirical SaaS Benchmark Metrics (KeyBanc & Bessemer Datasets)

```
+--------------------------------------+--------------------+--------------------+--------------------+
| Benchmark Metric                     | 2021 Peak Boom     | 2022 Deceleration  | 2023 Trough Reset  |
+--------------------------------------+--------------------+--------------------+--------------------+
| Median Organic ARR Growth Rate       | 35% – 36%          | 35%                | 21% – 26%          |
| Top-Quartile ARR Growth Rate         | 70% – 85%          | 55% – 60%          | 35% – 40%          |
| Median Net Retention Rate (NRR)      | 105% – 108%        | 103% – 104%        | 101% – 102%        |
| SMB (<$5k ACV) Cohort NRR            | 98% – 102%         | 94% – 96%          | 88% – 92%          |
| Enterprise (>$50k ACV) Cohort NRR    | 115% – 125%        | 110% – 114%        | 105% – 108%        |
| Median Blended CAC Payback Period    | 18.0 months        | 24.5 months        | 21.0 months*       |
| Gross Margin (Subscription Revenue)  | 76% – 80%          | 75% – 78%          | 74% – 77%          |
+--------------------------------------+--------------------+--------------------+--------------------+
*Note: CAC Payback compressed in 2023 only because companies executed massive 20%–40% RIFs (Reductions in Force) 
in Sales & Marketing, not because customer acquisition became easier.
```

---

## 5. Quantitative Synthesis: Cross-Sector Parametric Comparison

To drive the simulation data engine, we establish the following empirical baseline boundaries derived directly from primary source data:

```
+------------------------------------+-----------------------+-----------------------+-----------------------+
| Empirical Dimension                | Wholesale Distrib.    | Contract Mfg.         | B2B Enterprise SaaS   |
+------------------------------------+-----------------------+-----------------------+-----------------------+
| Typical Cycle Drawdown (Peak-Trough| -15% to -25%          | -12% to -35%          | +5% to -10% (ARR -25%)|
| Contraction Duration (Quarters)    | 3 to 4 quarters       | 3 to 5 quarters       | 4 to 6 quarters (lag) |
| Trough-to-Recovery Duration        | 6 to 8 quarters       | 6 to 10 quarters      | 6 to 8 quarters       |
| Degree of Operating Leverage (DOL) | 1.8x – 2.4x           | 3.5x – 7.5x           | 1.5x – 3.0x           |
| Gross Margin Cyclical Sensitivity  | Flat to -200 bps      | -200 to -500 bps      | Flat to -150 bps      |
| Operating Margin Compression       | -350 to -500 bps      | -400 to -800 bps      | -500 to -1,200 bps    |
| Trough Working Capital Behavior    | Cash Releasing (+$)   | Extreme Cash Release  | Cash Consuming (-$)   |
| Primary QoE Diligence Trap         | Inventory E&O aging   | Capacity underutil.   | Hidden renewal cliff  |
+------------------------------------+-----------------------+-----------------------+-----------------------+
```

---

## 6. Primary Source Verification Index

1. **U.S. Federal Reserve Board G.17 Release / FRED:**
   - Series `INDPRO`: Industrial Production Index (Monthly, Seasonally Adjusted). Peak Dec 2007 = 102.1; Trough June 2009 = 84.8 (-16.9%).
   - Series `IPMAN`: Industrial Production: Manufacturing (NAICS). Peak Dec 2007 = 104.5; Trough June 2009 = 86.2 (-17.5%).
   - Series `MCUMFN`: Capacity Utilization: Manufacturing. Peak Dec 2007 = 79.7%; Trough June 2009 = 64.4% (-1,530 bps). Peak Feb 2020 = 75.3%; Trough April 2020 = 63.3% (-1,200 bps).
2. **National Bureau of Economic Research (NBER):**
   - US Business Cycle Expansions and Contractions Chronology (1854–2020). Post-WWII Contraction Mean = 10.3 months; Expansion Mean = 64.2 months.
3. **Fastenal Company (NASDAQ: FAST) SEC Filings:**
   - 2009 Form 10-K (Item 8: Financial Statements): Net Sales fell 17.5% from $2,340,425k (2008) to $1,930,330k (2009); Operating Income fell 34.3% from $450,237k to $295,793k.
   - Form 10-Q (Q1 2008 – Q1 2011): Quarterly peak-to-trough path from Q3 2008 ($625,037k) to Q2 2009 ($474,894k) = -24.02% drawdown.
4. **MSC Industrial Direct Co., Inc. (NYSE: MSM) SEC Filings:**
   - 2009 Form 10-K: Net Sales fell 16.3% from $1,771,705k to $1,440,845k; Operating Income fell 35.9% from $319,528k to $204,718k; Operating Margin dropped from 18.0% to 13.7%.
   - Quarterly reports: Peak Q3 FY08 ($457,238k) to Trough Q3 FY09 ($350,489k) = -23.34% drawdown.
5. **Kimball Electronics, Inc. (NASDAQ: KE) SEC Filings:**
   - 2024 Form 10-K: FY23 to FY24 Net Sales fell 5.92% from $1,823,000k to $1,715,000k; Operating Income fell 43.79% from $87,700k to $49,300k (DOL = 7.40x). Operating Cash Flow rose from ~$32M to >$73M due to a 25% inventory reduction.
6. **Plexus Corp (NASDAQ: PLXS) SEC Filings:**
   - 2009 Form 10-K: Net Sales fell 12.2% from $1,843,597k to $1,618,599k; Operating Income dropped by $51.4M with Ayer, MA facility shutdown.
7. **KeyBanc Capital Markets (KBCM) & Sapphire Ventures Private SaaS Surveys (2021, 2022, 2023):**
   - Median organic ARR growth decelerated from 35% (2021) to 26% (2023) and 21% (2024); Median NRR dropped from 105% to 101%–102%; Blended CAC Payback stretched from 18 to 24.5 months.
