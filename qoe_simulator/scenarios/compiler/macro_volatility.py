"""
QoE Simulator - Level 2.B / Engine 10: Business Cyclicality, Operational Volatility
and Ups-and-Downs Simulation Engine (Module 10).

Architectural Standards Compliance:
- FASB ASC 606 (Revenue Recognition), ASC 330 (Inventory & LCNRV), ASC 705-20 (Vendor Rebates), ASC 326 (CECL)
- Anderson, Banker, & Janakiraman (ABJ 2003) Asymmetric Cost Behavior
- Chen et al. (2000) Multi-Echelon Bullwhip Order Amplification
- Delaware Court of Chancery Precedents (Prairie Capital, ABRY Partners V)
- System Invariants INV10-1 through INV10-6

Self-Contained Autonomous Level (SCAL) Implementation.
Deterministic Seed-Based Reproducibility.
"""

from __future__ import annotations

import calendar
import datetime
import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class IndustrySector(Enum):
    SECTOR_UNSPECIFIED = 0
    SECTOR_WHOLESALE_DISTRIBUTION = 1  # NAICS 4238 (Target Apex Supply)
    SECTOR_PRECISION_MANUFACTURING = 2  # NAICS 3327 (Titan Precision Machining)
    SECTOR_B2B_ENTERPRISE_SAAS = 3      # NAICS 5112 (CloudScale SaaS)


class MacroArchetype(Enum):
    MACRO_ARCHETYPE_UNSPECIFIED = 0
    MACRO_GREAT_RECESSION_2008 = 1     # Protracted 18-mo curve (-24% drawdown)
    MACRO_COVID_SHOCK_2020 = 2         # Vertical 2-mo drop, rapid rebound
    MACRO_INDUSTRIAL_DESTOCK_2023 = 3  # 12-mo supply-chain inventory digestion
    MACRO_MID_CYCLE_STEADY = 4         # Mild +/-3% secular growth with random shocks


class ManagerialExpectationState(Enum):
    STATE_GROWTH = 1
    STATE_OPTIMISTIC_HOARDING = 2      # Period 1 contraction: labor hoarded
    STATE_CAUTIOUS_SQUEEZE = 3         # Period 2 contraction: overtime cut
    STATE_RESTRUCTURING_PANIC = 4      # Period 3+ contraction: WARN RIF cuts


@dataclass(frozen=True)
class DailyOperationalVector:
    """Daily operational telemetry vector."""
    month_index: int
    day_of_month: int
    is_shipping_day: bool
    daily_demand_multiplier: float
    scrap_rate_modifier: float
    is_held_open_cutoff: bool


@dataclass(frozen=True)
class ShockEvent:
    """Discrete idiosyncratic operational shock event."""
    month_index: int
    shock_type: str                   # "CUSTOMER_CHURN", "COMMODITY_SPIKE", "BAD_DEBT", "SCRAP_SPIKE"
    description: str
    revenue_impact_pct: float          # e.g. -0.12 (-12% revenue drop)
    cost_impact_pct: float             # e.g. +0.25 (+25% raw material price spike)
    discrete_cash_charge: float        # e.g. 250000.00 ($250k direct write-off)
    recovery_lag_months: int           # Months required to recover volume


@dataclass
class MonthlyTrajectoryVector:
    """Monthly operational trajectory state vector."""
    month_index: int
    calendar_year: int
    calendar_month: int
    billable_shipping_days: int        # Between 19 and 23
    calendar_multiplier: float         # W_m / 21.0
    macro_demand_factor: float         # Multiplier from Macro Wave Generator
    raw_material_price_index: float    # Commodity cost index (Baseline 1.0)
    customer_selling_price_index: float# Sticky customer selling price index
    opex_stickiness_beta: float        # Effective ABJ cost elasticity
    expected_dio: float                # Projected Days Inventory Outstanding
    asc330_eo_reserve_rate: float      # E&O inventory reserve percentage
    revenue_runrate: float             # In dollars
    cogs_runrate: float                # In dollars
    gross_margin: float                # Realized gross margin (0.0 to 1.0)
    opex_runrate: float                # In dollars
    ebitda_runrate: float              # In dollars
    active_shocks: List[ShockEvent] = field(default_factory=list)
    daily_vectors: List[DailyOperationalVector] = field(default_factory=list)


@dataclass
class VolatilityScenarioConfig:
    """Input scenario configuration for business cyclicality and volatility."""
    scenario_id: str = "SCEN_APEX_SUPPLY"
    seed: int = 42
    sector: IndustrySector = IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION
    macro_archetype: MacroArchetype = MacroArchetype.MACRO_MID_CYCLE_STEADY
    simulation_months: int = 36
    base_annual_revenue: float = 50_000_000.00
    base_gross_margin: float = 0.26
    base_ebit_margin: float = 0.075
    enable_window_dressing: bool = False
    deal_closing_month: int = 24
    start_year: int = 2021
    start_month: int = 1


@dataclass
class OperationalTrajectoryPayload:
    """Output canonical operational trajectory schedule emitted by Module 10."""
    scenario_id: str
    seed: int
    monthly_trajectories: List[MonthlyTrajectoryVector]


# ==============================================================================
# Pipeline Subsystems (Stages 1 through 6)
# ==============================================================================

class CalendarVolatilityGenerator:
    """Stage 1: Computes billable shipping capacity and non-holiday working days (W_m in [19, 23])."""

    FEDERAL_HOLIDAYS_FIXED = {
        (1, 1),    # New Year's Day
        (7, 4),    # Independence Day
        (12, 24),  # Christmas Eve
        (12, 25),  # Christmas Day
    }

    @staticmethod
    def is_floating_holiday(year: int, month: int, day: int) -> bool:
        """Evaluates floating corporate holidays: Memorial Day, Labor Day, Thanksgiving Day + Black Friday."""
        dt = datetime.date(year, month, day)
        # Memorial Day: Last Monday in May
        if month == 5 and dt.weekday() == 0 and day >= 25:
            return True
        # Labor Day: First Monday in September
        if month == 9 and dt.weekday() == 0 and day <= 7:
            return True
        # Thanksgiving: 4th Thursday in November
        if month == 11 and dt.weekday() == 3:
            # Check if this is the 4th Thursday (day between 22 and 28)
            if 22 <= day <= 28:
                return True
        # Day after Thanksgiving (Black Friday): 4th Friday in November
        if month == 11 and dt.weekday() == 4:
            if 23 <= day <= 29:
                return True
        return False

    @classmethod
    def compute_month_calendar(
        cls, year: int, month: int, sector: IndustrySector
    ) -> tuple[int, list[tuple[int, bool, bool]]]:
        """Returns (billable_days_count, list of (day, is_shipping_day, is_maintenance_shutdown))."""
        num_days = calendar.monthrange(year, month)[1]
        days_info = []
        billable_count = 0

        for day in range(1, num_days + 1):
            dt = datetime.date(year, month, day)
            is_weekend = dt.weekday() >= 5
            is_holiday = (month, day) in cls.FEDERAL_HOLIDAYS_FIXED or cls.is_floating_holiday(year, month, day)

            # Sector maintenance shutdown (Manufacturing plant July shutdown: Days 1-7)
            is_shutdown = False
            if sector == IndustrySector.SECTOR_PRECISION_MANUFACTURING and month == 7 and 1 <= day <= 7:
                is_shutdown = True

            if not is_weekend and not is_holiday and not is_shutdown:
                is_shipping = True
                billable_count += 1
            else:
                is_shipping = False

        # Invariant INV10-6: Non-holiday working days strictly bounded [19, 23]
        clamped_billable = max(19, min(23, billable_count))
        return clamped_billable, days_info


class MacroeconomicWaveGenerator:
    """Stage 2: Synthesizes multi-year NBER macroeconomic cycles and sectoral drawdowns."""

    @staticmethod
    def compute_macro_factor(
        month_index: int,
        archetype: MacroArchetype,
        sector: IndustrySector,
        total_months: int,
    ) -> float:
        """Computes the macro demand factor (1.0 = baseline run-rate)."""
        # Secular growth trend: ~3.0% per annum
        secular_trend = 0.03 * (month_index / 12.0)

        # Sectoral drawdown depths and response lags
        if sector == IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION:
            drawdown_amp = 0.20
            lag = 0
        elif sector == IndustrySector.SECTOR_PRECISION_MANUFACTURING:
            drawdown_amp = 0.28
            lag = 1
        elif sector == IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS:
            drawdown_amp = 0.08
            lag = 9  # 9-month deferred revenue lag
        else:
            drawdown_amp = 0.15
            lag = 0

        effective_month = max(1, month_index - lag)

        cycle_component = 0.0
        if archetype == MacroArchetype.MACRO_GREAT_RECESSION_2008:
            # 18-month cycle: peak at m=6, contraction trough at m=18, recovery m=18-36
            t_peak = 6
            t_contract = 12
            t_trough = t_peak + t_contract  # 18
            t_recover = 18

            if effective_month <= t_peak:
                # Mild expansion leading into peak
                cycle_component = 0.04 * math.sin((math.pi / 2.0) * (effective_month / t_peak))
            elif t_peak < effective_month <= t_trough:
                # Contraction phase
                progress = (effective_month - t_peak) / t_contract
                cycle_component = -drawdown_amp * math.sin((math.pi / 2.0) * progress)
            else:
                # Recovery phase
                progress = min(1.0, (effective_month - t_trough) / t_recover)
                cycle_component = -drawdown_amp * math.cos((math.pi / 2.0) * progress)

        elif archetype == MacroArchetype.MACRO_COVID_SHOCK_2020:
            # Vertical 2-month drop (-25%), rapid 4-month recovery
            t_drop = 8
            if effective_month in (t_drop, t_drop + 1):
                cycle_component = -drawdown_amp * 1.15
            elif t_drop + 2 <= effective_month <= t_drop + 6:
                progress = (effective_month - (t_drop + 1)) / 5.0
                cycle_component = -drawdown_amp * (1.0 - progress)
            else:
                cycle_component = 0.02 * math.sin(effective_month / 4.0)

        elif archetype == MacroArchetype.MACRO_INDUSTRIAL_DESTOCK_2023:
            # 12-month shallow supply-chain inventory destock (-12%)
            t_start = 10
            t_len = 12
            if t_start <= effective_month <= t_start + t_len:
                progress = (effective_month - t_start) / t_len
                cycle_component = -(drawdown_amp * 0.6) * math.sin(math.pi * progress)
            else:
                cycle_component = 0.015 * math.sin(effective_month / 6.0)

        elif archetype == MacroArchetype.MACRO_MID_CYCLE_STEADY:
            # Mild +/-3% secular oscillations around trend
            cycle_component = 0.03 * math.sin((2.0 * math.pi * effective_month) / 24.0)

        macro_factor = 1.0 + secular_trend + cycle_component
        # Invariant INV10-2: Non-negative boundedness
        return max(0.10, macro_factor)


class CommodityPriceLagEngine:
    """Stage 3: Computes raw material price index and lagged customer price pass-through."""

    def __init__(self, rng: random.Random, sector: IndustrySector):
        self.rng = rng
        self.sector = sector
        self.raw_price = 1.0
        self.selling_price = 1.0
        self.pass_through_lag_months = 2 if sector != IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS else 0
        self.history_raw_prices: list[float] = []

    def step(self, month: int, shock: Optional[ShockEvent] = None) -> tuple[float, float, float]:
        """Steps forward 1 month; returns (raw_material_price_index, customer_selling_price_index, gross_margin_multiplier)."""
        if self.sector == IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS:
            # SaaS has no commodity exposure
            return 1.0, 1.0, 1.0

        # Mean-reverting Ornstein-Uhlenbeck drift with small noise
        drift = 0.15 * (1.0 - self.raw_price)
        noise = self.rng.gauss(0.0, 0.012)
        shock_impact = shock.cost_impact_pct if (shock and shock.cost_impact_pct > 0) else 0.0

        self.raw_price = max(0.60, self.raw_price + drift + noise + shock_impact)
        self.history_raw_prices.append(self.raw_price)

        # Customer price adjusts with pass-through lag (45-60 days / 2 months)
        if len(self.history_raw_prices) > self.pass_through_lag_months:
            target_p = self.history_raw_prices[-1 - self.pass_through_lag_months]
            # 85% pass-through efficiency
            self.selling_price += 0.85 * (target_p - self.selling_price)
        else:
            self.selling_price = 1.0

        # Margin multiplier (P_m / C_m)
        margin_mult = self.selling_price / max(0.01, self.raw_price)
        # Clamped to realistic boundaries
        margin_mult = max(0.70, min(1.30, margin_mult))
        return self.raw_price, self.selling_price, margin_mult


class SupplyChainBullwhipSolver:
    """Stage 4: Chen et al. (2000) bullwhip order amplification and DIO explosion."""

    def __init__(self, sector: IndustrySector):
        self.sector = sector
        if sector == IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION:
            self.base_dio = 70.0
            self.lead_time_months = 3
            self.bullwhip_alpha = 3.5
        elif sector == IndustrySector.SECTOR_PRECISION_MANUFACTURING:
            self.base_dio = 60.0
            self.lead_time_months = 3
            self.bullwhip_alpha = 7.5
        else:  # SaaS
            self.base_dio = 0.0
            self.lead_time_months = 0
            self.bullwhip_alpha = 1.0

        self.past_demands: list[float] = []

    def compute_dio_and_reserve(self, month: int, demand_factor: float) -> tuple[float, float]:
        """Computes current month Days Inventory Outstanding (DIO) and ASC 330 E&O reserve rate."""
        if self.sector == IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS:
            return 0.0, 0.0

        self.past_demands.append(demand_factor)
        # Check demand trend over the last 3 months
        if len(self.past_demands) >= 3:
            recent_avg = sum(self.past_demands[-3:]) / 3.0
            older_avg = sum(self.past_demands[-6:-3]) / 3.0 if len(self.past_demands) >= 6 else 1.0
            demand_change = (recent_avg - older_avg) / max(0.01, older_avg)
        else:
            demand_change = 0.0

        # During a downturn, pre-ordered purchase orders continue arriving, driving DIO up
        if demand_change < 0:
            dio_surge = min(50.0, abs(demand_change) * 45.0 * (self.bullwhip_alpha / 3.0))
            current_dio = self.base_dio + dio_surge
        else:
            current_dio = max(self.base_dio - 5.0, self.base_dio + (demand_change * 10.0))

        # FASB ASC 330 Lower of Cost and Net Realizable Value (LCNRV) E&O reserve rate
        # When DIO exceeds baseline by > 20 days, E&O reserve rate scales up from 1.5% to 5.5%
        excess_days = max(0.0, current_dio - self.base_dio)
        reserve_rate = 0.015 + (excess_days / 50.0) * 0.040
        return current_dio, reserve_rate


class AsymmetricCostSolver:
    """Stage 5: Anderson, Banker, & Janakiraman (ABJ 2003) asymmetric cost stickiness solver."""

    def __init__(self, base_opex_monthly: float):
        self.current_opex = base_opex_monthly
        self.consecutive_declines = 0

    def step(self, revenue_t: float, revenue_prev: float) -> tuple[float, float, ManagerialExpectationState]:
        """Calculates current OpEx based on sequential revenue growth and managerial expectations."""
        growth = (revenue_t - revenue_prev) / max(1.0, revenue_prev)

        if growth >= 0.0:
            self.consecutive_declines = 0
            state = ManagerialExpectationState.STATE_GROWTH
            beta = 0.55
        else:
            self.consecutive_declines += 1
            if self.consecutive_declines == 1:
                state = ManagerialExpectationState.STATE_OPTIMISTIC_HOARDING
                beta = 0.30  # Labor hoarded
            elif self.consecutive_declines == 2:
                state = ManagerialExpectationState.STATE_CAUTIOUS_SQUEEZE
                beta = 0.45  # Overtime cut
            else:
                state = ManagerialExpectationState.STATE_RESTRUCTURING_PANIC
                beta = 0.85  # Severance, WARN RIF cuts

        # Invariant INV10-3: For declines, beta <= 0.40 in Month 1
        self.current_opex = self.current_opex * (1.0 + beta * growth)
        self.current_opex = max(1000.0, self.current_opex)
        return self.current_opex, beta, state


class WindowDressingRig:
    """Stage 6: Pre-sale financial statement tampering based on Delaware Court of Chancery jurisprudence."""

    @staticmethod
    def apply_distortions(
        month: int,
        closing_month: int,
        daily_vectors: list[DailyOperationalVector],
        revenue_runrate: float,
        opex_runrate: float,
        eo_reserve_rate: float,
    ) -> tuple[float, float, float, list[DailyOperationalVector]]:
        """Applies shipping book extension, channel stuffing, CapEx freeze, reserve freeze, and post-close collapse."""
        adjusted_rev = revenue_runrate
        adjusted_opex = opex_runrate
        adjusted_reserve = eo_reserve_rate
        new_daily_vectors = list(daily_vectors)

        # 1. Shipping Book Extension (T_close - 2 and T_close - 1)
        if month in (closing_month - 2, closing_month - 1):
            # Books held open 5-8 days past month-end
            held_open_days = 6
            # Modify the last 6 shipping days
            count = 0
            updated_daily = []
            for d in reversed(new_daily_vectors):
                if d.is_shipping_day and count < held_open_days:
                    updated_daily.append(DailyOperationalVector(
                        month_index=d.month_index,
                        day_of_month=d.day_of_month,
                        is_shipping_day=d.is_shipping_day,
                        daily_demand_multiplier=d.daily_demand_multiplier * 1.35,
                        scrap_rate_modifier=d.scrap_rate_modifier,
                        is_held_open_cutoff=True
                    ))
                    count += 1
                else:
                    updated_daily.append(d)
            new_daily_vectors = list(reversed(updated_daily))
            adjusted_rev *= 1.12

        # 2. Channel Stuffing (T_close - 1)
        if month == closing_month - 1:
            adjusted_rev *= 1.25  # +25% volume pull-forward with off-schedule terms

        # 3. CapEx & Maintenance Starve in pre-close year
        if closing_month - 12 <= month <= closing_month - 1:
            # R&M expenses cut from 2.5% to 0.8% of revenue
            rm_savings = adjusted_rev * (0.025 - 0.008)
            adjusted_opex = max(1000.0, adjusted_opex - rm_savings)

        # 4. Valuation Reserve Freeze (T_close - 6 to T_close - 1)
        if closing_month - 6 <= month <= closing_month - 1:
            adjusted_reserve = 0.0

        # 5. The Post-Closing "Order Desert" (T_close + 1 and T_close + 2)
        if month in (closing_month + 1, closing_month + 2):
            adjusted_rev *= 0.52  # -48% collapse due to stuffed channels
            # Customer returns surge
            updated_daily = []
            for d in new_daily_vectors:
                updated_daily.append(DailyOperationalVector(
                    month_index=d.month_index,
                    day_of_month=d.day_of_month,
                    is_shipping_day=d.is_shipping_day,
                    daily_demand_multiplier=d.daily_demand_multiplier * 0.52,
                    scrap_rate_modifier=d.scrap_rate_modifier * 3.5,
                    is_held_open_cutoff=False
                ))
            new_daily_vectors = updated_daily

        return adjusted_rev, adjusted_opex, adjusted_reserve, new_daily_vectors


# ==============================================================================
# Master Engine: VolatilityEngine
# ==============================================================================

class VolatilityEngine:
    """Master Module 10 Volatility & Cyclicality Engine.

    Produces canonical OperationalTrajectoryPayload given a VolatilityScenarioConfig.
    Deterministic, seed-based, and fully isolated.
    """

    def __init__(self):
        pass

    def generate_trajectory(self, config: VolatilityScenarioConfig) -> OperationalTrajectoryPayload:
        """Executes the 6-stage pipeline to generate the multi-year trajectory."""
        rng = random.Random(config.seed)

        base_monthly_revenue = config.base_annual_revenue / 12.0
        base_monthly_cogs = base_monthly_revenue * (1.0 - config.base_gross_margin)
        base_monthly_ebit = base_monthly_revenue * config.base_ebit_margin
        base_monthly_opex = base_monthly_revenue - base_monthly_cogs - base_monthly_ebit

        # Initialize sub-engines
        macro_gen = MacroeconomicWaveGenerator()
        price_lag_engine = CommodityPriceLagEngine(rng, config.sector)
        bullwhip_solver = SupplyChainBullwhipSolver(config.sector)
        cost_solver = AsymmetricCostSolver(base_monthly_opex)

        # Scheduled discrete shocks (anchored by seed)
        scheduled_shocks: dict[int, list[ShockEvent]] = {}
        if config.sector == IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION:
            # Commodity price hike at Month 10
            scheduled_shocks[10] = [
                ShockEvent(
                    month_index=10,
                    shock_type="COMMODITY_SPIKE",
                    description="Global steel tariff shock (+25% inbound raw materials cost)",
                    revenue_impact_pct=0.0,
                    cost_impact_pct=0.22,
                    discrete_cash_charge=0.0,
                    recovery_lag_months=2,
                )
            ]
        elif config.sector == IndustrySector.SECTOR_PRECISION_MANUFACTURING:
            # Lost anchor customer at Month 14
            scheduled_shocks[14] = [
                ShockEvent(
                    month_index=14,
                    shock_type="CUSTOMER_CHURN",
                    description="Loss of Tier-1 aerospace sub-assembly contract (14% revenue)",
                    revenue_impact_pct=-0.14,
                    cost_impact_pct=0.0,
                    discrete_cash_charge=350_000.0,
                    recovery_lag_months=9,
                )
            ]
        elif config.sector == IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS:
            # Enterprise customer down-tier churn at Month 18
            scheduled_shocks[18] = [
                ShockEvent(
                    month_index=18,
                    shock_type="CUSTOMER_CHURN",
                    description="Fortune 500 client reduces seat count by 40%",
                    revenue_impact_pct=-0.08,
                    cost_impact_pct=0.0,
                    discrete_cash_charge=0.0,
                    recovery_lag_months=6,
                )
            ]

        monthly_trajectories: list[MonthlyTrajectoryVector] = []
        prev_revenue = base_monthly_revenue

        curr_year = config.start_year
        curr_month = config.start_month

        for m in range(1, config.simulation_months + 1):
            # Stage 1: Calendar
            billable_days, _ = CalendarVolatilityGenerator.compute_month_calendar(
                curr_year, curr_month, config.sector
            )
            cal_multiplier = billable_days / 21.0

            # Stage 2: Macro Wave
            macro_factor = macro_gen.compute_macro_factor(
                m, config.macro_archetype, config.sector, config.simulation_months
            )

            # Check active shocks
            active_shock_list = scheduled_shocks.get(m, [])
            shock = active_shock_list[0] if active_shock_list else None

            # Stage 3: Commodity price lag & realized margin
            raw_p, sell_p, margin_mult = price_lag_engine.step(m, shock)
            realized_gm = max(0.02, min(0.95, config.base_gross_margin * margin_mult))

            # Stage 4: Bullwhip DIO & ASC 330 reserve
            dio, eo_reserve_rate = bullwhip_solver.compute_dio_and_reserve(m, macro_factor)

            # Calculate preliminary monthly revenue
            shock_rev_mult = (1.0 + shock.revenue_impact_pct) if shock else 1.0
            prelim_revenue = base_monthly_revenue * cal_multiplier * macro_factor * shock_rev_mult
            # Invariant INV10-2: Non-negative clamp
            prelim_revenue = max(0.05 * base_monthly_revenue, prelim_revenue)

            # Stage 5: Asymmetric cost solver
            opex, beta, _ = cost_solver.step(prelim_revenue, prev_revenue)

            # Daily vectors generation
            num_days_in_month = calendar.monthrange(curr_year, curr_month)[1]
            daily_vectors = []
            for d in range(1, num_days_in_month + 1):
                dt = datetime.date(curr_year, curr_month, d)
                is_weekday = dt.weekday() < 5
                is_holiday = (curr_month, d) in CalendarVolatilityGenerator.FEDERAL_HOLIDAYS_FIXED or \
                             CalendarVolatilityGenerator.is_floating_holiday(curr_year, curr_month, d)
                is_ship = is_weekday and not is_holiday
                daily_mult = 1.0 if is_ship else 0.0
                daily_vectors.append(DailyOperationalVector(
                    month_index=m,
                    day_of_month=d,
                    is_shipping_day=is_ship,
                    daily_demand_multiplier=daily_mult,
                    scrap_rate_modifier=0.02,
                    is_held_open_cutoff=False
                ))

            # Stage 6: Window dressing if enabled
            if config.enable_window_dressing:
                rev, opex, eo_reserve_rate, daily_vectors = WindowDressingRig.apply_distortions(
                    m, config.deal_closing_month, daily_vectors, prelim_revenue, opex, eo_reserve_rate
                )
            else:
                rev = prelim_revenue

            # Derived financials
            cogs = rev * (1.0 - realized_gm)
            ebitda = rev - cogs - opex

            trajectory_vector = MonthlyTrajectoryVector(
                month_index=m,
                calendar_year=curr_year,
                calendar_month=curr_month,
                billable_shipping_days=billable_days,
                calendar_multiplier=cal_multiplier,
                macro_demand_factor=macro_factor,
                raw_material_price_index=raw_p,
                customer_selling_price_index=sell_p,
                opex_stickiness_beta=beta,
                expected_dio=dio,
                asc330_eo_reserve_rate=eo_reserve_rate,
                revenue_runrate=round(rev, 2),
                cogs_runrate=round(cogs, 2),
                gross_margin=round(realized_gm, 4),
                opex_runrate=round(opex, 2),
                ebitda_runrate=round(ebitda, 2),
                active_shocks=active_shock_list,
                daily_vectors=daily_vectors,
            )
            monthly_trajectories.append(trajectory_vector)
            prev_revenue = rev

            # Increment calendar
            curr_month += 1
            if curr_month > 12:
                curr_month = 1
                curr_year += 1

        return OperationalTrajectoryPayload(
            scenario_id=config.scenario_id,
            seed=config.seed,
            monthly_trajectories=monthly_trajectories,
        )
