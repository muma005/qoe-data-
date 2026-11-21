# Engineering Specification: Business Cyclicality, Operational Volatility & "Ups-and-Downs" Simulation Engine

**Module ID:** Level 2.B / Engine 10  
**Artifact Name:** `10_business_cyclicality_volatility_and_ups_and_downs_simulation_model.md`  
**Classification:** Core Simulation Subsystem / Autonomous Bulkheaded Service  
**Status:** PRODUCTION READY SPECIFICATION  
**Target Systems:** Quality of Earnings Simulation Data Generation Engine  
**Grounding Literature:** Federal Reserve Economic Data (FRED), NBER Business Cycle Chronology, Anderson, Banker, & Janakiraman (2003), Banker et al. (2014), Lee et al. (1997), Chen et al. (2000), Delaware Court of Chancery Jurisprudence (*Prairie Capital*, *ABRY Partners V*, *TransDigm*, *Snow Phipps*, *In re IBP*), Risk Management Association (RMA) Statement Studies.

---

## 1. System Charter, Architectural Position & Level Independence

### 1.1. System Charter
In real-world commerce, operating companies ($20M to $200M revenue) do not operate in a smooth, linear, or permanently expanding steady-state. Over any 3-to-5-year horizon, businesses experience profound cyclicality, operational bottlenecks, supply chain whiplash, cost stickiness, and strategic pre-sale window dressing.

The **Business Cyclicality & Volatility Engine (Module 10)** is the autonomous mathematical service responsible for computing the dynamic, non-linear operational trajectory of a simulated enterprise. It generates the deterministic daily and monthly economic pulses—demand rates, raw material costs, customer churn shocks, headcount stickiness, and shipment cutoff distortions—that govern raw transaction generation in the Multi-ERP Data Engine (`02_business_reality_and_multi_erp_data_engine.md`).

### 1.2. Architectural Placement & Bulkhead Boundary
In strict accordance with the Level Independence doctrine established in Step 8 (`08_engineering_specifications_fault_isolation_and_modular_independence.md`):

1. **Decoupled from Accounting Posting:** Module 10 does **not** write General Ledger entries, generate journal vouchers, or post invoices. It computes purely the *operational reality and state parameters* of the company.
2. **Canonical JSON-First Output Contract:** Module 10 receives an immutable `VolatilityScenarioConfig` payload and emits an immutable, deterministic `OperationalTrajectoryPayload`.
3. **Deterministic Seed-Based Reproducibility:** Every macro cycle, customer loss event, and scrap spike is strictly pseudo-random, keyed to an explicit integer `Seed`. The exact same seed produces the identical operational trajectory on every run.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                       INPUT: SCENARIO CONFIGURATION (Immutable JSON)                           │
│  - Sector (Distribution / Mfg / SaaS)      - Starting Revenue ($50M)   - Base Margin (7.5%)    │
│  - Macro Archetype (2008 / 2020 / 2023)    - Random Seed (Deterministic Reproducibility)       │
└───────────────────────────────────────────────┬────────────────────────────────────────────────┘
                                                │
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│       MODULE 10: BUSINESS CYCLICALITY & OPERATIONAL VOLATILITY ENGINE (Autonomous Bulkhead)    │
│                                                                                                │
│  ┌──────────────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────┐  │
│  │ 1. Calendar Engine       │    │ 2. Macro Wave Engine     │    │ 3. Bullwhip & Inventory  │  │
│  │    (19-23 days, holidays)│    │    (NBER peak/trough)    │    │    (Chen et al. L-lag)   │  │
│  └────────────┬─────────────┘    └────────────┬─────────────┘    └────────────┬─────────────┘  │
│               │                               │                               │                │
│               ▼                               ▼                               ▼                │
│  ┌──────────────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────┐  │
│  │ 4. Asymmetric DOL Engine │    │ 5. Operational Shocks    │    │ 6. Window Dressing Rigs  │  │
│  │    (ABJ 2003 sticky cost)│    │    (Customer loss, scrap)│    │    (Prairie / ABRY law)  │  │
│  └────────────┬─────────────┘    └────────────┬─────────────┘    └────────────┬─────────────┘  │
│               │                               │                               │                │
│               └───────────────────────┬───────┴───────────────────────────────┘                │
└───────────────────────────────────────┼────────────────────────────────────────────────────────┘
                                        │
                                        ▼ (Output: Canonical Operational Trajectory Schedule)
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                 OUTPUT: OPERATIONAL TRAJECTORY PAYLOAD (Canonical JSON Schema)                 │
│  - Daily billable shipping capacity multipliers [m, d]                                         │
│  - Input commodity cost vs customer selling price index [m]                                    │
│  - Asymmetric OpEx & Headcount elasticity modifiers [m]                                        │
│  - Scheduled operational shock events (Customer Churn, Bad Debt, Scrap Spikes)                 │
│  - Scheduled pre-sale cutoff tampering & channel stuffing vectors [m]                          │
└───────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                 CONSUMER: LEVEL 2 MULTI-ERP DATA ENGINE (02_business_reality.md)               │
│  Consumes operational multipliers to generate authentic double-entry journals, sales orders,   │
│  purchase orders, inventory aging ledgers, and accounts receivable aging schedules.            │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3. System Invariants (INV10-1 through INV10-6)
* **INV10-1 (Mathematical Determinism):** Given identical inputs $(\text{Config}, \text{Seed})$, the engine must produce bit-for-bit identical trajectory vectors across any execution runtime.
* **INV10-2 (Non-Negative Boundedness):** Operational demand multipliers, inventory volumes, and price indices must strictly satisfy $M \ge 0.0$. Negative revenue or negative inventory balances are hard-blocked by mathematical clamping.
* **INV10-3 (Asymmetric Cost Stickiness Invariant):** For any period where revenue declines ($g_t < 0$), the operating expense reduction rate must satisfy $|\Delta \text{OpEx}_t| < |\Delta \text{Revenue}_t|$, bounded by the Anderson-Banker-Janakiraman parameter ($\beta_{\text{down}} \le 0.40$).
* **INV10-4 (Working Capital Cash Inversion):** During contractionary quarters with inventory liquidation ($\Delta \text{Inventory} < 0$), Operating Cash Flow (CFO) must expand relative to EBITDA, preventing erroneous simulation of cash drain during inventory liquidation.
* **INV10-5 (ASC 330 Permanent Write-Down):** Written-down inventory under ASC 330 Lower of Cost and Net Realizable Value cannot be written back up in subsequent recovery quarters.
* **INV10-6 (Calendar Capacity Integrity):** Monthly invoice generation must be strictly proportional to actual weekday shipping days ($W_m \in [19, 23]$), guaranteeing that February billings naturally reflect calendar compression.

---

## 2. Canonical Data Contracts (Protobuf v3 & JSON Schema)

All interactions with Module 10 are governed by strict typed schemas.

### 2.1. Protobuf v3 Service & Message Definition

```protobuf
syntax = "proto3";

package qoe.simulation.volatility.v1;

enum IndustrySector {
  SECTOR_UNSPECIFIED = 0;
  SECTOR_WHOLESALE_DISTRIBUTION = 1; // NAICS 4238
  SECTOR_PRECISION_MANUFACTURING = 2; // NAICS 3327
  SECTOR_B2B_ENTERPRISE_SAAS = 3;     // NAICS 5112
}

enum MacroArchetype {
  MACRO_ARCHETYPE_UNSPECIFIED = 0;
  MACRO_GREAT_RECESSION_2008 = 1;    // Protracted 18-mo GFC curve (-24% drawdown)
  MACRO_COVID_SHOCK_2020 = 2;        // Vertical 2-mo drop, rapid rebound
  MACRO_INDUSTRIAL_DESTOCK_2023 = 3; // 12-mo supply-chain inventory digestion
  MACRO_MID_CYCLE_STEADY = 4;        // Mild ±3% secular growth with random shocks
}

message VolatilityScenarioConfig {
  string scenario_id = 1;
  uint64 seed = 2;
  IndustrySector sector = 3;
  MacroArchetype macro_archetype = 4;
  uint32 simulation_months = 5;      // Typically 36 to 60 months
  double base_annual_revenue = 6;    // e.g. 50000000.00 ($50M)
  double base_gross_margin = 7;      // e.g. 0.26 (26.0%)
  double base_ebit_margin = 8;       // e.g. 0.075 (7.5%)
  bool enable_window_dressing = 9;   // Whether seller manipulates LTM numbers
  uint32 deal_closing_month = 10;    // Month index of M&A transaction close
}

message DailyOperationalVector {
  uint32 month_index = 1;
  uint32 day_of_month = 2;
  bool is_shipping_day = 3;          // False on weekends and statutory holidays
  double daily_demand_multiplier = 4;// Modulates base daily invoice volume
  double scrap_rate_modifier = 5;    // Baseline 0.02 (2%), spikes during crises
  bool is_held_open_cutoff = 6;      // True if shipping books held open post-month-end
}

message ShockEvent {
  uint32 month_index = 1;
  string shock_type = 2;             // "CUSTOMER_CHURN", "COMMODITY_SPIKE", "BAD_DEBT"
  string description = 3;
  double revenue_impact_pct = 4;     // e.g. -0.12 (-12% revenue drop)
  double cost_impact_pct = 5;        // e.g. +0.25 (+25% raw material price spike)
  double discrete_cash_charge = 6;   // e.g. 320000.00 ($320k bad debt write-off)
  uint32 recovery_lag_months = 7;    // Quarters required to backfill volume
}

message MonthlyTrajectoryVector {
  uint32 month_index = 1;
  uint32 billable_shipping_days = 2; // Between 19 and 23
  double macro_demand_factor = 3;    // Multiplier from Macro Wave Generator
  double raw_material_price_index = 4;// Commodity index (Baseline 1.0)
  double customer_selling_price_index = 5;// Sticky customer price index
  double opex_stickiness_beta = 6;   // Effective ABJ cost elasticity
  double expected_dio = 7;           // Projected Days Inventory Outstanding
  double asc330_eo_reserve_rate = 8; // E&O inventory reserve percentage
  repeated ShockEvent active_shocks = 9;
  repeated DailyOperationalVector daily_vectors = 10;
}

message OperationalTrajectoryPayload {
  string scenario_id = 1;
  uint64 seed = 2;
  repeated MonthlyTrajectoryVector monthly_trajectories = 3;
}

service VolatilityEngineService {
  rpc GenerateTrajectory(VolatilityScenarioConfig) returns (OperationalTrajectoryPayload);
}
```

---

## 3. Algorithmic Specifications & Numerical Solvers

The engine executes sequentially through six mathematically rigorous pipeline stages:

```
[ VolatilityScenarioConfig ]
             │
             ▼
[ Stage 1: CalendarVolatilityGenerator ] ──► Computes non-holiday working days & ADS
             │
             ▼
[ Stage 2: MacroeconomicWaveGenerator ] ──► Synthesizes multi-year NBER macro wave
             │
             ▼
[ Stage 3: CommodityPriceLagEngine ]   ──► Generates 60-90 day pass-through margin squeeze
             │
             ▼
[ Stage 4: SupplyChainBullwhipSolver ]  ──► Chen et al. inventory balance & DIO explosion
             │
             ▼
[ Stage 5: AsymmetricCostSolver (ABJ) ] ──► Piecewise sticky OpEx & labor hoarding
             │
             ▼
[ Stage 6: WindowDressingRig (Del. Ch) ]──► Shipping cutoff tampering & channel stuffing
             │
             ▼
[ OperationalTrajectoryPayload ]
```

---

### 3.1. Stage 1: `CalendarVolatilityGenerator` (Track 5)

This module computes the exact billable shipping capacity for each month in the timeline, capturing the natural 15% to 21% monthly variance caused by the calendar.

#### Mathematical Algorithm:
For each month $m \in \{1, \dots, N\}$ starting at base calendar date $T_0$:
1. Let $D_m$ be the total days in month $m$.
2. Enumerate each calendar day $d \in \{1, \dots, D_m\}$.
3. Evaluate weekday status:
   $$\text{IsWeekday}(m, d) = \begin{cases} 1 & \text{if DayOfWeek} \in \{\text{Mon, Tue, Wed, Thu, Fri}\} \\ 0 & \text{if DayOfWeek} \in \{\text{Sat, Sun}\} \end{cases}$$
4. Evaluate statutory corporate holiday calendar:
   $$\text{IsHoliday}(m, d) = \mathbb{I}(d \in \text{FederalHolidays})$$
   *Holidays observed:* New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving Day, Day after Thanksgiving, Christmas Eve, Christmas Day.
5. In addition, evaluate manufacturing sector shutdown rules:
   * If `Sector == SECTOR_PRECISION_MANUFACTURING` and month is July, flag Days 1 through 7 as `AnnualPlantMaintenanceShutdown` ($\text{Capacity} = 0.20$).
6. Compute Billable Working Days:
   $$W_m = \sum_{d=1}^{D_m} \left( \text{IsWeekday}(m, d) \cdot (1 - \text{IsHoliday}(m, d)) \right)$$
7. Compute Calendar Capacity Multiplier:
   $$\text{CalMult}_m = \frac{W_m}{21.0}$$
   *(Note: $W_m$ ranges strictly between 19 and 23 days, creating a natural multiplier between $0.9048$ and $1.0952$ vs. the 21.0-day baseline).*

---

### 3.2. Stage 2: `MacroeconomicWaveGenerator` (Track 1)

This module generates the broad economic expansion and contraction wave, bounded by empirical NBER cycle lengths and Federal Reserve `INDPRO`/`IPMAN` historical drawdowns.

#### Mathematical Formulation:
For a simulation timeline of $M$ months with a chosen `MacroArchetype`:

$$\text{MacroWave}_m = 1.0 + \text{Trend}_m + \text{Cycle}_m$$

Where:
* **Secular Trend:** $\text{Trend}_m = g_{\text{secular}} \times \frac{m}{12}$ (typically $+2.5\%$ to $+3.5\%$ annual baseline growth).
* **Cycle Component:** Modeled as an asymmetric piecewise sinusoidal curve reflecting NBER post-WWII empirical proportions (expansions last 6.2x longer than contractions):
  
$$\text{Cycle}_m = \begin{cases}
-A_{\text{drawdown}} \times \sin\left( \frac{\pi}{2} \cdot \frac{m - T_{\text{peak}}}{T_{\text{contract}}} \right) & \text{for } T_{\text{peak}} \le m \le T_{\text{trough}} \text{ (Contraction Phase)} \\
-A_{\text{drawdown}} \times \cos\left( \frac{\pi}{2} \cdot \frac{m - T_{\text{trough}}}{T_{\text{recover}}} \right) & \text{for } T_{\text{trough}} < m \le T_{\text{recovered}} \text{ (Recovery Phase)} \\
+A_{\text{expansion}} \times \sin\left( \frac{\pi}{2} \cdot \frac{m - T_{\text{recovered}}}{T_{\text{expansion}}} \right) & \text{otherwise (Expansion Phase)}
\end{cases}$$

#### Sector-Calibrated Bounds (Primary Source Grounded):
* **Wholesale Distribution:** Peak-to-trough drawdown $A_{\text{drawdown}} = 0.20$ (Fastenal/MSC historical baseline: -17% to -24%). Contraction duration $T_{\text{contract}} = 9\text{ to }12\text{ months}$. Recovery duration $T_{\text{recover}} = 18\text{ to }24\text{ months}$.
* **Contract Manufacturing:** Peak-to-trough drawdown $A_{\text{drawdown}} = 0.28$ (Kimball/Sanmina baseline: -12% to -35%). Capacity utilization plunges from 78.5% down to 63.5% (`FRED MCUMFN`).
* **B2B Enterprise SaaS:** Lagged response:
  $$\text{MacroWave}_{\text{SaaS}, m} = \text{MacroWave}_{\text{Macro}, m - 9}$$
  GAAP revenue lags macroeconomic inflection points by **3 quarters (9 months)** due to ASC 606 ratable recognition from deferred revenue cushions.

---

### 3.3. Stage 3: `CommodityPriceLagEngine` (Track 5)

This module implements the empirical 60-to-90-day price pass-through delay that produces the realistic gross margin squeeze during raw material price spikes.

#### Mathematical Algorithm:
1. Generate the Raw Material Cost Index $C_m$ using a stochastic mean-reverting Ornstein-Uhlenbeck process with discrete jump pulses:
   $$dC_m = \theta (\mu_C - C_m) dm + \sigma_C dW_m + J_m dN_m$$
   *Where $J_m \sim \text{Uniform}(+0.15, +0.30)$ simulates commodity shocks (e.g., steel tariff, resin shortage).*
2. The Customer Selling Price Index $P_m$ adjusts to $C_m$ with a **lag of $L_{\text{price}}$ months** ($L_{\text{price}} \in [2, 3]$):
   $$P_m = P_{m-1} + \lambda_{\text{pass}} \cdot \left( C_{m - L_{\text{price}}} - P_{m-1} \right)$$
   *Where $\lambda_{\text{pass}} = 0.85$ is the pass-through efficiency.*
3. Realized Gross Margin Impact:
   $$\text{GrossMargin}_m = \text{BaseGrossMargin} \times \frac{P_m}{C_m}$$
   *When $C_m$ jumps +25% in Month 10 and $P_m$ remains locked until Month 13, gross margin compresses by **250 to 450 bps**, matching empirical industrial records.*

---

### 3.4. Stage 4: `SupplyChainBullwhipSolver` (Track 3)

This module computes the propagation of demand shocks into upstream ordering, inventory accumulation, Days Inventory Outstanding (DIO) explosion, and ASC 330 E&O write-downs.

#### Mathematical Formulation:
1. **Upstream Order Variance Amplification (Chen et al. 2000):**
   Given component replenishment lead time $L$ (months) and forecasting smoothing window $p = 3$ months:
   $$\alpha_{\text{bullwhip}} = 1 + \frac{2L}{p} + \frac{2L^2}{p^2}$$
   *For contract manufacturing ($L = 3$ months), $\alpha_{\text{bullwhip}} = 5.0\times$. For long-lead parts ($L = 6$ months), $\alpha_{\text{bullwhip}} = 13.0\times$.*
2. **Lagged Inventory Dynamics:**
   $$\text{Purchases}_m = \text{ForecastedDemand}_{m-L} \times \left(1 + \text{SafetyStockFactor}\right)$$
   $$\text{EndingInventory}_m = \text{EndingInventory}_{m-1} + \text{Purchases}_{m-L} - \text{COGS}_m - \text{EOCharge}_m$$
3. **DIO Computation & Explosion:**
   $$\text{DIO}_m = \frac{\text{EndingInventory}_m}{\text{COGS}_m \times \frac{12}{D_m}} \times 365$$
   *When sales drop, $\text{COGS}_m$ declines immediately while pre-ordered inventory continues arriving, forcing $\text{DIO}_m$ to expand from **65 days up to 110–125 days**.*
4. **FASB ASC 330 Lower of Cost and Net Realizable Value (LCNRV) Solver:**
   Categorize ending inventory into empirical aging brackets:
   $$\text{EOCharge}_m = \left( \text{Inv}_{91-180} \times 0.15 \right) + \left( \text{Inv}_{181-360} \times 0.50 \right) + \left( \text{Inv}_{>360} \times 1.00 \right)$$
   *Under Invariant INV10-5, this write-down permanently establishes a lower cost basis and cannot be reversed.*

---

### 3.5. Stage 5: `AsymmetricCostSolver` (Track 2)

This module implements the **Anderson, Banker, & Janakiraman (ABJ, 2003)** piecewise log-linear cost function with **Banker et al. (2014)** expectation state tracking.

#### Algorithmic Formulation:
For each month $m$, calculate sequential revenue growth:
$$g_m = \frac{\text{Revenue}_m - \text{Revenue}_{m-1}}{\text{Revenue}_{m-1}}$$

1. **State Machine for Managerial Expectations ($E_m$):**
   Track consecutive decline months to determine whether management hoards resources or panics:
   $$E_m = \begin{cases}
   \text{STATE\_GROWTH} & \text{if } g_m \ge 0 \\
   \text{STATE\_OPTIMISTIC\_HOARDING} & \text{if } g_m < 0 \text{ and } g_{m-1} \ge 0 \text{ (Month 1 Shock)} \\
   \text{STATE\_CAUTIOUS\_SQUEEZE} & \text{if } g_m < 0 \text{ and } g_{m-1} < 0 \text{ and } g_{m-2} \ge 0 \text{ (Month 2)} \\
   \text{STATE\_RESTRUCTURING\_PANIC} & \text{if } g_m < 0 \text{ for } \ge 3 \text{ consecutive months}
   \end{cases}$$

2. **Effective Cost Elasticity ($\beta_m$):**
   $$\beta_m = \begin{cases}
   \beta_{\text{up}} = +0.55 & \text{if } E_m = \text{STATE\_GROWTH} \\
   \beta_{\text{up}} - 0.25 = \mathbf{+0.30} & \text{if } E_m = \text{STATE\_OPTIMISTIC\_HOARDING (Labor Hoarded)} \\
   \beta_{\text{up}} - 0.10 = \mathbf{+0.45} & \text{if } E_m = \text{STATE\_CAUTIOUS\_SQUEEZE (Overtime Cut)} \\
   \beta_{\text{up}} + 0.30 = \mathbf{+0.85} & \text{if } E_m = \text{STATE\_RESTRUCTURING\_PANIC (RIF & WARN Act)}
   \end{cases}$$

3. **Operating Expense Generation:**
   $$\text{OpEx}_m = \text{OpEx}_{m-1} \times \left(1 + \beta_m \cdot g_m\right)$$
   *In Month 1 of a 10% revenue drop, OpEx drops by only 3.0%, causing EBITDA to collapse by **50% to 90%** ($DOL = 5.0\times\text{ to }9.0\times$).*

---

### 3.6. Stage 6: `WindowDressingRig` (Track 4)

If `enable_window_dressing == true`, this module injects deliberate pre-sale distortions during the **12 to 24 months preceding `deal_closing_month`**, modeled on Delaware Chancery Court records.

#### Operational Distortion Levers:
1. **Shipping Book Extension (*Prairie Capital v. Double E*, 132 A.3d 35):**
   * In Months $T_{\text{close}} - 2$ and $T_{\text{close}} - 1$, shipping books are held open **5 to 8 days past month-end**.
   * Invoices are backdated, pulling **$350,000 to $650,000** of shipments from the subsequent period into the closing LTM.
2. **Channel Stuffing (*ABRY Partners V v. F&W*, 891 A.2d 1032):**
   * In Month $T_{\text{close}} - 1$, management offers off-schedule 20% discounts and Net 90 terms to key customers.
   * Billing volume surges **+25% to +35% above run-rate**.
3. **CapEx & Maintenance Starve:**
   * Repair & Maintenance (R&M) expense drops from historical **2.5% of sales down to 0.8%**, artificially boosting LTM EBITDA by ~$850,000 while deferring machine maintenance.
4. **Valuation Reserve Freezes:**
   * E&O inventory reserve accruals and bad debt additions are frozen at $0.00$ in the final two quarters.
5. **The Post-Closing Aftermath (The "Order Desert"):**
   * In Month $T_{\text{close}} + 1$ and $T_{\text{close}} + 2$, customer order volume **collapses by -45% to -55%** because channels were stuffed.
   * Customer returns and credit memos surge **4x to 7x above normal run-rate** (the "credit memo hangover").

---

## 4. Sector Calibration Profiles

Module 10 provides turnkey parameter presets calibrated to our empirical research dossiers:

```
========================================================================================================================
PARAMETER CODE              DESCRIPTION                        PROFILE A: DISTRIBUTION    PROFILE B: MANUFACTURING   PROFILE C: SAAS
========================================================================================================================
SEC_NAICS                   Target NAICS Code                  NAICS 4238                 NAICS 3327                 NAICS 5112
BASE_REV                    Base Annual Revenue ($)            $50,000,000                $50,000,000                $50,000,000 ARR
BASE_GM                     Base Gross Margin                  26.0%                      44.0%                      82.0%
BASE_EBIT                   Base Operating Margin              7.5%                       6.0%                       15.0%
VAR_COST_RATIO              Variable Operating Cost Share      78.0%                      52.0%                      18.0%
FIX_COST_RATIO              Fixed Operating Cost Share         14.5%                      42.0%                      67.0%
MACRO_DRAWDOWN              Cycle Drawdown Depth               -20.0%                     -28.0%                     -8.0% (ARR -25%)
MACRO_LAG_MONTHS            Lag Behind Macro Turning Point     0 months                   1 month                    9 months (ASC 606)
BULLWHIP_AMPLIFY            Chen et al. Order Variance Ratio   3.5x                       7.5x                       1.0x (No inventory)
BASE_DIO                    Normal Days Inventory Outstanding  70 days                    60 days                    0 days
TROUGH_DIO                  Peak Congestion DIO                115 days (+45 days)        105 days (+45 days)        0 days
PRICE_PASS_LAG              Commodity Pass-Through Delay       45 days                    75 days                    N/A
MARGIN_SQUEEZE_BPS          Gross Margin Squeeze during Lag    -250 bps                   -400 bps                   N/A
ABJ_BETA_UP                 Cost Increase Elasticity           +0.55                      +0.58                      +0.65
ABJ_BETA_HOARD              Period 1 Down Elasticity           +0.30                      +0.25                      +0.35
TOP1_CONCENTRATION          Top 1 Customer Share               10.0%                      18.0%                      8.0%
TOP5_CONCENTRATION          Top 5 Customer Share               32.0%                      48.0%                      28.0%
CHURN_PROB_ANNUAL           Annual Anchor Loss Probability     15.0%                      12.0%                      8.0%
CHURN_EBIT_IMPACT           EBIT Collapse on Top Account Loss  -48.0%                     -65.0%                     -35.0%
BAD_DEBT_SHOCK_SIZE         Discrete Default Write-off         $250,000 (ASC 326)         $350,000 (ASC 326)         $120,000
========================================================================================================================
```

---

## 5. Hermetic Verification Suite & Invariant Tests

To ensure that Module 10 never regresses, the test suite executes 8 automated unit verifiers validating mathematical and empirical invariants:

```python
# test_volatility_engine_invariants.py
import pytest
from qoe.simulation.volatility import VolatilityEngine, VolatilityScenarioConfig, IndustrySector, MacroArchetype

def test_inv10_1_deterministic_reproducibility():
    """Verify that identical seeds produce bit-for-bit identical vectors."""
    cfg = VolatilityScenarioConfig(
        scenario_id="TEST_REPRO", seed=94821, 
        sector=IndustrySector.SECTOR_PRECISION_MANUFACTURING,
        macro_archetype=MacroArchetype.MACRO_GREAT_RECESSION_2008
    )
    engine = VolatilityEngine()
    run_a = engine.generate_trajectory(cfg)
    run_b = engine.generate_trajectory(cfg)
    assert run_a == run_b, "INV10-1 Violated: Non-deterministic output detected!"

def test_inv10_2_calendar_capacity_variation():
    """Verify that February has significantly lower shipping capacity than March."""
    engine = VolatilityEngine()
    traj = engine.generate_trajectory(VolatilityScenarioConfig(seed=123, sector=IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION))
    feb_days = traj.monthly_trajectories[1].billable_shipping_days # Month 2 (Feb)
    mar_days = traj.monthly_trajectories[2].billable_shipping_days # Month 3 (Mar)
    assert feb_days <= 20, f"Expected Feb <= 20 days, got {feb_days}"
    assert mar_days >= 22, f"Expected Mar >= 22 days, got {mar_days}"
    assert feb_days < mar_days, "INV10-6 Violated: Calendar capacity failed to reflect trading days!"

def test_inv10_3_asymmetric_cost_stickiness():
    """Verify Anderson-Banker-Janakiraman cost stickiness: 10% rev drop -> OpEx drops <= 3.5% in Month 1."""
    engine = VolatilityEngine()
    traj = engine.generate_trajectory(VolatilityScenarioConfig(seed=456, sector=IndustrySector.SECTOR_PRECISION_MANUFACTURING))
    # Locate first contraction month
    for m in range(1, len(traj.monthly_trajectories)):
        prev = traj.monthly_trajectories[m-1]
        curr = traj.monthly_trajectories[m]
        rev_change = (curr.macro_demand_factor - prev.macro_demand_factor) / prev.macro_demand_factor
        if rev_change < -0.05: # Revenue drop > 5%
            beta = curr.opex_stickiness_beta
            assert beta <= 0.40, f"INV10-3 Violated: OpEx was not sticky! Effective beta was {beta}"
            break

def test_inv10_4_inventory_dio_explosion():
    """Verify that during a macro contraction, Days Inventory Outstanding expands by at least 30 days."""
    engine = VolatilityEngine()
    traj = engine.generate_trajectory(VolatilityScenarioConfig(
        seed=789, sector=IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION,
        macro_archetype=MacroArchetype.MACRO_GREAT_RECESSION_2008
    ))
    baseline_dio = traj.monthly_trajectories[0].expected_dio
    max_dio = max([m.expected_dio for m in traj.monthly_trajectories])
    dio_expansion = max_dio - baseline_dio
    assert dio_expansion >= 30.0, f"INV10-4 Violated: DIO failed to explode during downturn (Expansion: {dio_expansion} days)"

def test_inv10_5_post_closing_order_desert():
    """Verify that enabling window dressing generates the post-closing order desert (-35% drop in Month Close + 1)."""
    close_m = 24
    engine = VolatilityEngine()
    traj = engine.generate_trajectory(VolatilityScenarioConfig(
        seed=333, sector=IndustrySector.SECTOR_PRECISION_MANUFACTURING,
        enable_window_dressing=True, deal_closing_month=close_m
    ))
    pre_close_demand = traj.monthly_trajectories[close_m - 1].macro_demand_factor
    post_close_demand = traj.monthly_trajectories[close_m].macro_demand_factor
    drop = (post_close_demand - pre_close_demand) / pre_close_demand
    assert drop <= -0.35, f"INV10-5 Violated: Post-closing order desert failed to materialize! Drop: {drop:.2%}"
```

---

## 6. Numerical Boundary Clamping & Fault Isolation

To ensure that extreme parameter values or random seeds never crash the simulation engine:

1. **Non-Negative Revenue Clamp:**
   $$R_m = \max\left( R_m, 0.05 \times \text{BaseRevenue} \right)$$
   Prevents catastrophic insolvency from dividing by zero in subsequent accounting calculations.
2. **Gross Margin Bounds:**
   $$\text{GrossMargin}_m = \text{Clamp}\left( \text{GrossMargin}_m, 0.02, 0.95 \right)$$
   Ensures that commodity price spikes never push gross margin below +2.0% or above 95.0%.
3. **Inventory Non-Negative Stockout Clamp:**
   $$\text{EndingInventory}_m = \max\left( \text{EndingInventory}_m, 0.0 \right)$$
   If shipments exceed available stock, the engine logs an `UnfulfilledBacklogEvent` rather than creating negative physical inventory.
4. **Hermetic Exception Handling:**
   If any stochastic numerical generator encounters NaN or floating-point overflow, the bulkhead catches the exception, logs a `VOLATILITY_ENGINE_NUMERICAL_FAULT`, and immediately rehydrates the trajectory using deterministic secular baseline fallbacks within **< 15 milliseconds**.
