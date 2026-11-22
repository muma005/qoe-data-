"""
QoE Simulator - Level 2: Business Reality & Multi-ERP Synthetic Data Generation Engine (`biz-gen`).

Implements, per `02_business_reality_and_multi_erp_data_engine.md`:

  1. The Standard 6-Digit Chart of Accounts (CoA) and account-category mapping.
  2. The Generative Double-Entry Accounting Core (atomic transaction builder) that
     gates every journal entry through the Level 0.5 Financial Physics Invariants.
  3. The Tri-Sector Operational Event Simulators (Wholesale / Manufacturing / SaaS),
     each bound to its governing GAAP standard (ASC 705-20, ASC 330, ASC 606/350-40).
  4. The Five Specialized Subledger Engines (AR, AP, Inventory, Fixed Assets, Deferred Revenue).
  5. The Multi-ERP Native Exporters (NetSuite, SAP S/4HANA ACDOCA, QuickBooks IIF, Dynamics 365).
  6. The Documentary Degradation Engine (Panko cell errors, unapplied cash, cutoffs, missing records).

Money is handled in fixed-point `Decimal` (4 decimal places). Zero floating-point math
enters the general ledger, satisfying LP-01. All output is deterministic for a given seed.
"""

from __future__ import annotations

import csv
import io
import os
import random
import sys
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Path bootstrap: the offline compiler lives outside the runtime package tree,
# but must reach the Level 0.5 invariant gate under backend/app/level0_physics.
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_BACKEND = os.path.join(_ROOT, "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from app.level0_physics.invariants import (  # noqa: E402
    AccountCategory,
    FinancialPhysicsEngine,
    InvariantViolationFatalError,
    JournalLine,
)

from macro_volatility import IndustrySector, MonthlyTrajectoryVector  # noqa: E402

# ---------------------------------------------------------------------------
# Fixed-point money helpers
# ---------------------------------------------------------------------------
_QUANT = Decimal("0.0001")


def _money(value: object) -> Decimal:
    """Normalize any numeric value into a 4-dp fixed-point Decimal."""
    if isinstance(value, Decimal):
        return value.quantize(_QUANT, rounding=ROUND_HALF_EVEN)
    if value is None:
        return Decimal("0.0000")
    return Decimal(str(value)).quantize(_QUANT, rounding=ROUND_HALF_EVEN)


# ---------------------------------------------------------------------------
# Chart of Accounts (CoA) - 6-digit institutional numbering from spec Section 4
# ---------------------------------------------------------------------------
class CoA:
    """Standard 6-digit Chart of Accounts with subledger integration accounts."""

    # Cash & Cash Equivalents (100000-109999)
    OPERATING_CASH = "101000"
    PAYROLL_CLEARING = "102000"
    # Trade Accounts Receivable (110000-119999)
    TRADE_AR = "111000"
    UNAPPLIED_CASH_CLEARING = "112000"
    # Prepaid Expenses & Other (130000-139999)
    PREPAID_INSURANCE = "131000"
    VENDOR_DEPOSITS = "132000"
    # Inventories (140000-149999)
    RAW_MATERIALS = "141000"
    WIP = "142000"
    FINISHED_GOODS = "143000"
    INVENTORY_RESERVE = "144000"  # ASC 330 LCNRV / E&O reserve (contra-asset)
    # Property, Plant & Equipment (150000-159999)
    MACHINERY = "151000"
    ACCUM_DEPRECIATION = "152000"
    # Capitalized Software / Intangibles (160000-169999)
    CAPITALIZED_SOFTWARE = "161000"
    ACCUM_AMORTIZATION = "162000"
    # Accounts Payable (200000-209999)
    TRADE_AP = "201000"
    STRETCHED_AP_RECLASS = "202000"
    # Accrued Expenses (210000-219999)
    ACCRUED_PAYROLL = "211000"
    ACCRUED_REBATES = "212000"
    # Deferred Revenue (240000-249999)
    DEFERRED_REVENUE_CURRENT = "241000"
    DEFERRED_REVENUE_NONCURRENT = "242000"
    # Senior Debt & Revolvers (260000-269999)
    REVOLVER = "261000"
    TERM_LOAN = "262000"
    # Stockholders' Equity (300000-399999)
    COMMON_STOCK = "301000"
    RETAINED_EARNINGS = "302000"
    # Revenues (400000-499999)
    SUBSCRIPTION_REVENUE = "401000"
    PRODUCT_SALES = "402000"
    # Cost of Goods Sold (500000-599999)
    COGS_MATERIALS = "501000"
    COGS_LABOR = "502000"
    COGS_OVERHEAD = "503000"
    # SG&A Operating Expenses (600000-699999)
    SALES_SALARIES = "601000"
    CLOUD_HOSTING = "602000"
    DEPRECIATION_EXPENSE = "603000"
    G_A_EXPENSE = "604000"
    AMORTIZATION_EXPENSE = "605000"
    # Executive Compensation (700000-799999)
    OWNER_SALARY = "701000"
    DISCRETIONARY_PERKS = "702000"

    _NAMES: Dict[str, str] = {
        OPERATING_CASH: "Operating Cash",
        PAYROLL_CLEARING: "Payroll Clearing",
        TRADE_AR: "Trade Accounts Receivable",
        UNAPPLIED_CASH_CLEARING: "Unapplied Cash Clearing",
        PREPAID_INSURANCE: "Prepaid Insurance",
        VENDOR_DEPOSITS: "Vendor Deposits",
        RAW_MATERIALS: "Inventory - Raw Materials",
        WIP: "Inventory - Work in Process",
        FINISHED_GOODS: "Inventory - Finished Goods",
        INVENTORY_RESERVE: "Inventory Obsolescence Reserve",
        MACHINERY: "Machinery & Equipment",
        ACCUM_DEPRECIATION: "Accumulated Depreciation",
        CAPITALIZED_SOFTWARE: "Capitalized Software (ASC 350-40)",
        ACCUM_AMORTIZATION: "Accumulated Amortization - Software",
        TRADE_AP: "Trade Accounts Payable",
        STRETCHED_AP_RECLASS: "Stretched AP Reclass (Debt-Like)",
        ACCRUED_PAYROLL: "Accrued Payroll",
        ACCRUED_REBATES: "Accrued Vendor Rebates",
        DEFERRED_REVENUE_CURRENT: "Deferred Revenue - Current",
        DEFERRED_REVENUE_NONCURRENT: "Deferred Revenue - Non-Current",
        REVOLVER: "Revolving Credit Facility",
        TERM_LOAN: "Term Loan",
        COMMON_STOCK: "Common Stock",
        RETAINED_EARNINGS: "Retained Earnings",
        SUBSCRIPTION_REVENUE: "Subscription Revenue",
        PRODUCT_SALES: "Product Sales",
        COGS_MATERIALS: "Cost of Goods Sold - Materials",
        COGS_LABOR: "Cost of Goods Sold - Labor",
        COGS_OVERHEAD: "Cost of Goods Sold - Overhead",
        SALES_SALARIES: "Sales Salaries & Wages",
        CLOUD_HOSTING: "Cloud AWS Hosting",
        DEPRECIATION_EXPENSE: "Depreciation Expense",
        G_A_EXPENSE: "General & Administrative Expense",
        AMORTIZATION_EXPENSE: "Amortization Expense - Software",
        OWNER_SALARY: "Owner Salary",
        DISCRETIONARY_PERKS: "Discretionary Perks",
    }

    @classmethod
    def name(cls, number: str) -> str:
        return cls._NAMES.get(number, f"Account {number}")

    @classmethod
    def category(cls, number: str) -> AccountCategory:
        prefix = number[:1]
        if prefix == "1":  # assets
            if number in (cls.ACCUM_DEPRECIATION, cls.INVENTORY_RESERVE, cls.ACCUM_AMORTIZATION):
                return AccountCategory.NON_CURRENT_ASSET
            if number.startswith("15") or number.startswith("16"):
                return AccountCategory.NON_CURRENT_ASSET
            return AccountCategory.CURRENT_ASSET
        if prefix == "2":  # liabilities
            if number.startswith("26"):
                return AccountCategory.NON_CURRENT_LIABILITY
            return AccountCategory.CURRENT_LIABILITY
        if prefix == "3":  # equity
            return AccountCategory.EQUITY
        if prefix == "4":  # revenue
            return AccountCategory.REVENUE
        if prefix == "5":  # COGS
            return AccountCategory.COGS
        if prefix in ("6", "7"):  # opex
            return AccountCategory.OPEX
        return AccountCategory.OPEX


def dr(number: str, amount: object) -> Tuple[str, str, AccountCategory, Decimal, Decimal]:
    """Build a debit line tuple: (account, name, category, debit, credit)."""
    return (number, CoA.name(number), CoA.category(number), _money(amount), Decimal("0.0000"))


def cr(number: str, amount: object) -> Tuple[str, str, AccountCategory, Decimal, Decimal]:
    """Build a credit line tuple: (account, name, category, debit, credit)."""
    return (number, CoA.name(number), CoA.category(number), Decimal("0.0000"), _money(amount))


# ---------------------------------------------------------------------------
# Ledger entry model
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TransactionLine:
    account_number: str
    account_name: str
    category: AccountCategory
    debit: Decimal
    credit: Decimal
    entity_name: str = ""
    memo: str = ""
    document_ref: str = ""


@dataclass
class JournalEntry:
    entry_id: str
    entry_date: str  # ISO-8601
    sim_year: int
    sim_month: int
    entry_type: str
    entity_name: str
    memo: str
    document_ref: str
    lines: List[TransactionLine]


# ---------------------------------------------------------------------------
# Generative Double-Entry Accounting Core
# ---------------------------------------------------------------------------
class AccountingCore:
    """Atomic transaction builder + subledger state. Gates every entry on INV1."""

    def __init__(self, scenario_id: str, seed: int, base_annual_revenue: float,
                 start_year: int = 2021, start_month: int = 1):
        self.scenario_id = scenario_id
        self.seed = seed
        self.base_annual_revenue = _money(base_annual_revenue)
        self.base_monthly_revenue = _money(base_annual_revenue / 12.0)
        self.rng = random.Random((seed & 0x7FFFFFFF) ^ 0x5DEECE66D)
        self.engine = FinancialPhysicsEngine()
        self.entries: List[JournalEntry] = []
        self.anomalies: List[dict] = []
        self._seq = 0

        # Subledger balances (running, signed in the natural direction)
        self.cash = _money(0)
        self.ar = _money(0)
        self.unapplied_cash = _money(0)
        self.inventory = _money(0)
        self.accum_depreciation = _money(0)
        self.capitalized_software = _money(0)
        self.accum_amortization = _money(0)
        self.ap = _money(0)
        self.accrued_payroll = _money(0)
        self.deferred_revenue = _money(0)
        self.common_stock = _money(0)

        # ASC 606 cumulative waterfall counters (INV5)
        self.total_contract_invoiced = _money(0)
        self.cumulative_recognized = _money(0)

        # Opening balance sheet: fund a going-concern via a single balanced entry,
        # dated to the last day of the month preceding the simulation start.
        opening_cash = _money(base_annual_revenue * 0.05)
        opening_inventory = _money(base_annual_revenue * 0.12)
        opening_ppe = _money(base_annual_revenue * 0.20)
        py, pm = self._prior_month(start_year, start_month)
        opening_day = 31 if pm in (1, 3, 5, 7, 8, 10, 12) else 30
        self.post(
            "OPENING_BALANCE",
            py, pm, opening_day,
            [dr(CoA.OPERATING_CASH, opening_cash),
             dr(CoA.RAW_MATERIALS, opening_inventory),
             dr(CoA.MACHINERY, opening_ppe),
             cr(CoA.COMMON_STOCK, opening_cash + opening_inventory + opening_ppe)],
            entity="Opening Balance",
            memo="Going-concern opening balance sheet",
            document_ref="OPEN-001",
        )

    @staticmethod
    def _prior_month(year: int, month: int) -> Tuple[int, int]:
        if month == 1:
            return year - 1, 12
        return year, month - 1

    # -- core primitive -----------------------------------------------------
    def post(
        self,
        entry_type: str,
        year: int,
        month: int,
        day: int,
        lines: Sequence[Tuple[str, str, AccountCategory, Decimal, Decimal]],
        entity: str = "",
        memo: str = "",
        document_ref: str = "",
    ) -> JournalEntry:
        """Build a balanced journal entry, gate it on INV1, and update subledgers."""
        jlines = [
            JournalLine(
                account_number=acct,
                account_name=name,
                category=cat,
                debit=debit,
                credit=credit,
                entity_name=entity,
                memo=memo,
                document_ref=document_ref,
            )
            for (acct, name, cat, debit, credit) in lines
        ]

        # INV1: double-entry equilibrium (raises on any imbalance)
        self.engine.assert_inv1_double_entry(jlines)

        self._seq += 1
        entry = JournalEntry(
            entry_id=f"JE-{self._seq:08d}",
            entry_date=f"{year:04d}-{month:02d}-{day:02d}",
            sim_year=year,
            sim_month=month,
            entry_type=entry_type,
            entity_name=entity,
            memo=memo,
            document_ref=document_ref,
            lines=jlines,
        )
        self.entries.append(entry)
        self._apply_subledgers(jlines)
        return entry

    def _apply_subledgers(self, jlines: Sequence[JournalLine]) -> None:
        for line in jlines:
            net = line.debit - line.credit
            num = line.account_number
            if num == CoA.OPERATING_CASH:
                self.cash += net
            elif num == CoA.TRADE_AR:
                self.ar += net
            elif num == CoA.UNAPPLIED_CASH_CLEARING:
                self.unapplied_cash += net
            elif num in (CoA.RAW_MATERIALS, CoA.WIP, CoA.FINISHED_GOODS, CoA.INVENTORY_RESERVE):
                # INVENTORY_RESERVE is a contra-asset: credits reduce net inventory.
                self.inventory += net
            elif num == CoA.ACCUM_DEPRECIATION:
                self.accum_depreciation += (line.credit - line.debit)
            elif num == CoA.CAPITALIZED_SOFTWARE:
                self.capitalized_software += net
            elif num == CoA.ACCUM_AMORTIZATION:
                self.accum_amortization += (line.credit - line.debit)
            elif num == CoA.TRADE_AP:
                self.ap += (line.credit - line.debit)
            elif num == CoA.ACCRUED_PAYROLL:
                self.accrued_payroll += (line.credit - line.debit)
            elif num in (CoA.DEFERRED_REVENUE_CURRENT, CoA.DEFERRED_REVENUE_NONCURRENT):
                self.deferred_revenue += (line.credit - line.debit)
            elif num == CoA.COMMON_STOCK:
                self.common_stock += (line.credit - line.debit)

    # -- aggregate diagnostics ---------------------------------------------
    def aggregate(self) -> Dict[str, Decimal]:
        """Aggregate ledger balances by account category for invariant checks."""
        totals: Dict[str, Decimal] = {c.value: Decimal("0.0000") for c in AccountCategory}
        for entry in self.entries:
            for line in entry.lines:
                totals[line.category.value] += (line.debit - line.credit)
        return totals

    def total_debits(self) -> Decimal:
        return sum((line.debit for e in self.entries for line in e.lines), Decimal("0.0000"))

    def total_credits(self) -> Decimal:
        return sum((line.credit for e in self.entries for line in e.lines), Decimal("0.0000"))

    def net_income(self) -> Decimal:
        agg = self.aggregate()  # net = debit - credit per category
        revenue = -agg[AccountCategory.REVENUE.value]  # credit balance -> positive
        cogs = agg[AccountCategory.COGS.value]          # debit balance -> positive
        opex = agg[AccountCategory.OPEX.value]          # debit balance -> positive
        return revenue - cogs - opex

    def assert_inv2_balance_sheet(self) -> Tuple[bool, Decimal]:
        """Assert Assets == Liabilities + Equity + NetIncome from aggregated ledger."""
        agg = self.aggregate()  # net = debit - credit per category
        total_assets = (
            agg[AccountCategory.CURRENT_ASSET.value] + agg[AccountCategory.NON_CURRENT_ASSET.value]
        )
        # Liabilities and equity carry credit balances; negate to express positive.
        total_liabilities = -(
            agg[AccountCategory.CURRENT_LIABILITY.value] + agg[AccountCategory.NON_CURRENT_LIABILITY.value]
        )
        total_equity = -agg[AccountCategory.EQUITY.value]
        cumulative_ni = self.net_income()
        return self.engine.assert_inv2_balance_sheet(
            total_assets, total_liabilities, total_equity, cumulative_ni
        )


# ---------------------------------------------------------------------------
# Base sector simulator
# ---------------------------------------------------------------------------
class BaseSectorSimulator:
    """Shared operational machinery for the three sector simulators."""

    def __init__(self, core: AccountingCore, sector: IndustrySector, anomaly_ids: Sequence[str]):
        self.core = core
        self.sector = sector
        self.anomaly_ids = set(anomaly_ids)
        self._sku_units = 0  # physical units on hand (INV4)

        # Lazy import avoids a circular dependency (expense_engine imports CoA
        # from this module). Instantiated here so it shares the scenario seed.
        from expense_engine import ExpenseEngine
        self.expense_engine = ExpenseEngine(sector, core.seed)

    def simulate_month(self, traj: MonthlyTrajectoryVector, month_index: int) -> None:
        raise NotImplementedError

    def _collection_ratio(self) -> Decimal:
        return _money(0.82 + self.core.rng.uniform(-0.05, 0.05))

    def _payable_ratio(self) -> Decimal:
        return _money(0.80 + self.core.rng.uniform(-0.05, 0.05))

    def _settle_payroll(self, year: int, month: int, day: int) -> None:
        """Settle the outstanding payroll accrual to cash."""
        amount = self.core.accrued_payroll
        if amount <= 0:
            return
        self.core.post(
            "PAYROLL_SETTLEMENT", year, month, day,
            [dr(CoA.ACCRUED_PAYROLL, amount), cr(CoA.OPERATING_CASH, amount)],
            entity="Payroll", memo="Bi-weekly payroll settlement", document_ref=f"PR-{year}{month:02d}",
        )

    def _inv4_units(self, money_flow: Decimal, unit_cost: Decimal) -> int:
        if money_flow <= 0:
            return 0
        return int((money_flow / unit_cost).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN))

    def _assert_inv4(self, beg: int, end: int, recv: int, ship: int, scrap: int) -> None:
        FinancialPhysicsEngine.assert_inv4_sku_mass_balance(beg, end, recv, ship, scrap)


# ---------------------------------------------------------------------------
# Sector 1: Wholesale / Distribution (NAICS 4238, ASC 705-20 vendor rebates)
# ---------------------------------------------------------------------------
class WholesaleDistributionSimulator(BaseSectorSimulator):
    """Distribution: SKU velocity, landed cost, drop-ship split, volume rebates."""

    UNIT_COST = Decimal("25.0000")

    def simulate_month(self, traj: MonthlyTrajectoryVector, month_index: int) -> None:
        core = self.core
        y, m = traj.calendar_year, traj.calendar_month
        rev = _money(traj.revenue_runrate)
        cogs = _money(traj.cogs_runrate)

        # 1. Sales recognition -> AR / Product Sales
        core.post("INVOICE", y, m, 28, [dr(CoA.TRADE_AR, rev), cr(CoA.PRODUCT_SALES, rev)],
                  entity="Customers", memo="Monthly distribution sales", document_ref=f"INV-{y}{m:02d}")

        # 2. COGS (relieve finished goods)
        core.post("COGS_RELIEF", y, m, 28, [dr(CoA.COGS_MATERIALS, cogs), cr(CoA.FINISHED_GOODS, cogs)],
                  entity="Inventory", memo="COGS inventory relief", document_ref=f"CGS-{y}{m:02d}")

        # 3. Restock purchases -> AP (bullwhip: order slightly ahead during drawdown)
        restock_mult = Decimal("1.0") + Decimal(str(traj.expected_dio)) / Decimal("1000.0")
        purchases = (cogs * restock_mult).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
        core.post("PURCHASE", y, m, 20, [dr(CoA.RAW_MATERIALS, purchases), cr(CoA.TRADE_AP, purchases)],
                  entity="Vendors", memo="Inventory restock purchases", document_ref=f"PO-{y}{m:02d}")

        # 4. Inventory unit mass-balance (INV4)
        recv = self._inv4_units(purchases, self.UNIT_COST)
        ship = self._inv4_units(cogs, self.UNIT_COST)
        beg = self._sku_units
        end = beg + recv - ship
        self._assert_inv4(beg, end, recv, ship, 0)
        self._sku_units = end

        # 5. Cash collections
        collected = (self.core.ar * self._collection_ratio()).quantize(_QUANT, rounding=ROUND_HALF_EVEN) if self.core.ar > 0 else _money(0)
        if collected > 0:
            core.post("COLLECTION", y, m, 15, [dr(CoA.OPERATING_CASH, collected), cr(CoA.TRADE_AR, collected)],
                      entity="Customers", memo="Customer payment application", document_ref=f"PY-{y}{m:02d}")

        # 6. AP payment
        paid = (self.core.ap * self._payable_ratio()).quantize(_QUANT, rounding=ROUND_HALF_EVEN) if self.core.ap > 0 else _money(0)
        if paid > 0:
            core.post("AP_PAYMENT", y, m, 25, [dr(CoA.TRADE_AP, paid), cr(CoA.OPERATING_CASH, paid)],
                      entity="Vendors", memo="Vendor payment disbursement", document_ref=f"AP-{y}{m:02d}")

        # 7. OpEx: driver-based decomposition into granular vendor invoices / payroll
        self.expense_engine.generate_month(core, traj, y, m)
        self._settle_payroll(y, m, 28)

        # 8. Vendor volume rebate (ASC 705-20) - annual fiscal-year-end event with SR-B01
        if m == 12:
            self._vendor_rebate(y, m, cogs)

    def _vendor_rebate(self, y: int, m: int, cogs: Decimal) -> None:
        """ASC 705-20 tiered volume rebate. SR-B01: target credits 100% to COGS."""
        annual_purchases = cogs * 12
        total_rebate = (annual_purchases * Decimal("0.0100")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)

        if "SR-B01" in self.anomaly_ids:
            rebate_cogs = total_rebate
            rebate_inventory = _money(0)
            self.core.anomalies.append({
                "anomaly_id": "SR-B01",
                "accounting_standard": "ASC_705_20",
                "description": "Vendor volume rebate credited 100% to COGS; portion attributable to unsold inventory must be capitalized",
                "amount": str((total_rebate * Decimal("0.25")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)),
                "ebitda_impact": str((total_rebate * Decimal("0.25")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)),
                "target_gl_accounts": [CoA.FINISHED_GOODS, CoA.COGS_MATERIALS],
            })
        else:
            rebate_cogs = (total_rebate * Decimal("0.75")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
            rebate_inventory = (total_rebate - rebate_cogs).quantize(_QUANT, rounding=ROUND_HALF_EVEN)

        self.core.post("VENDOR_REBATE", y, m, 31,
                       [cr(CoA.COGS_MATERIALS, rebate_cogs),
                        cr(CoA.FINISHED_GOODS, rebate_inventory),
                        dr(CoA.TRADE_AP, total_rebate)],
                       entity="Fastenal Inc", memo="Volume rebate true-up (ASC 705-20)",
                       document_ref=f"RB-{y}{m:02d}")


# ---------------------------------------------------------------------------
# Sector 2: Precision Manufacturing (NAICS 3327, ASC 330 standard costing)
# ---------------------------------------------------------------------------
class PrecisionManufacturingSimulator(BaseSectorSimulator):
    """Manufacturing: standard costing, OEE/scrap, idle plant overhead absorption."""

    UNIT_COST = Decimal("120.0000")

    def simulate_month(self, traj: MonthlyTrajectoryVector, month_index: int) -> None:
        core = self.core
        y, m = traj.calendar_year, traj.calendar_month
        rev = _money(traj.revenue_runrate)
        cogs = _money(traj.cogs_runrate)
        opex = _money(traj.opex_runrate)
        scrap_rate = Decimal(str(traj.asc330_eo_reserve_rate)) if traj.asc330_eo_reserve_rate else Decimal("0.015")

        # 1. Sales recognition
        core.post("INVOICE", y, m, 28, [dr(CoA.TRADE_AR, rev), cr(CoA.PRODUCT_SALES, rev)],
                  entity="OEM Customers", memo="Monthly precision machining sales", document_ref=f"INV-{y}{m:02d}")

        # 2. COGS relief from finished goods
        core.post("COGS_RELIEF", y, m, 28, [dr(CoA.COGS_MATERIALS, cogs), cr(CoA.FINISHED_GOODS, cogs)],
                  entity="Inventory", memo="COGS inventory relief", document_ref=f"CGS-{y}{m:02d}")

        # 3. Raw material purchases -> AP
        purchases = (cogs * Decimal("1.05")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
        core.post("PURCHASE", y, m, 18, [dr(CoA.RAW_MATERIALS, purchases), cr(CoA.TRADE_AP, purchases)],
                  entity="Suppliers", memo="Raw material purchases", document_ref=f"PO-{y}{m:02d}")

        # 4. Production: convert raw -> finished goods (standard costing)
        core.post("PRODUCTION", y, m, 20, [dr(CoA.FINISHED_GOODS, cogs), cr(CoA.RAW_MATERIALS, cogs)],
                  entity="Plant", memo="Finished goods production from raw materials", document_ref=f"MFG-{y}{m:02d}")

        # 5. Scrap write-off (OEE quality loss)
        scrap_cost = (cogs * scrap_rate).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
        core.post("SCRAP_WRITEOFF", y, m, 26, [dr(CoA.COGS_OVERHEAD, scrap_cost), cr(CoA.FINISHED_GOODS, scrap_cost)],
                  entity="Plant", memo="Machine scrap & tooling failure write-off", document_ref=f"SC-{y}{m:02d}")

        # 6. Idle plant overhead (ASC 330-10-30) with SR-B06 anomaly
        self._idle_overhead(y, m, traj, opex)

        # 7. Inventory SKU mass-balance (INV4)
        recv = self._inv4_units(purchases, self.UNIT_COST)
        ship = self._inv4_units(cogs, self.UNIT_COST)
        scrap = self._inv4_units(scrap_cost, self.UNIT_COST)
        beg = self._sku_units
        end = beg + recv - ship - scrap
        self._assert_inv4(beg, end, recv, ship, scrap)
        self._sku_units = end

        # 8. Collections / AP payment
        collected = (self.core.ar * self._collection_ratio()).quantize(_QUANT, rounding=ROUND_HALF_EVEN) if self.core.ar > 0 else _money(0)
        if collected > 0:
            core.post("COLLECTION", y, m, 15, [dr(CoA.OPERATING_CASH, collected), cr(CoA.TRADE_AR, collected)],
                      entity="Customers", memo="Customer payment application", document_ref=f"PY-{y}{m:02d}")
        paid = (self.core.ap * self._payable_ratio()).quantize(_QUANT, rounding=ROUND_HALF_EVEN) if self.core.ap > 0 else _money(0)
        if paid > 0:
            core.post("AP_PAYMENT", y, m, 25, [dr(CoA.TRADE_AP, paid), cr(CoA.OPERATING_CASH, paid)],
                      entity="Suppliers", memo="Supplier payment disbursement", document_ref=f"AP-{y}{m:02d}")

        # 9. OpEx: driver-based decomposition into granular vendor invoices / payroll
        self.expense_engine.generate_month(core, traj, y, m)
        self._settle_payroll(y, m, 28)

    def _idle_overhead(self, y: int, m: int, traj: MonthlyTrajectoryVector, opex: Decimal) -> None:
        """Unabsorbed fixed overhead under ASC 330-10-30. SR-B06: capitalized into WIP."""
        if traj.macro_demand_factor >= 0.90:
            return
        unabsorbed = (opex * Decimal("0.10")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
        if "SR-B06" in self.anomaly_ids:
            # Anomaly: capitalize idle overhead into WIP instead of expensing
            self.core.post("IDLE_OVERHEAD", y, m, 30,
                           [dr(CoA.WIP, unabsorbed), cr(CoA.ACCRUED_PAYROLL, unabsorbed)],
                           entity="Plant", memo="Idle plant overhead capitalized (ASC 330)", document_ref=f"IDLE-{y}{m:02d}")
            self.core.anomalies.append({
                "anomaly_id": "SR-B06",
                "accounting_standard": "ASC_330_10_30",
                "description": "Unabsorbed fixed plant overhead capitalized into WIP instead of expensed",
                "amount": str(unabsorbed),
                "ebitda_impact": str(unabsorbed),
                "target_gl_accounts": [CoA.WIP, CoA.COGS_OVERHEAD],
            })
        else:
            # Correct: expense unabsorbed overhead immediately
            self.core.post("IDLE_OVERHEAD", y, m, 30,
                           [dr(CoA.COGS_OVERHEAD, unabsorbed), cr(CoA.ACCRUED_PAYROLL, unabsorbed)],
                           entity="Plant", memo="Unabsorbed idle overhead expensed (ASC 330-10-30)", document_ref=f"IDLE-{y}{m:02d}")


# ---------------------------------------------------------------------------
# Sector 3: Enterprise B2B SaaS (NAICS 5112, ASC 606 / ASC 350-40 / ASC 340-40)
# ---------------------------------------------------------------------------
class SaaSSubscriptionSimulator(BaseSectorSimulator):
    """SaaS: ASC 606 ratable recognition, deferred revenue waterfall, software capitalization."""

    def simulate_month(self, traj: MonthlyTrajectoryVector, month_index: int) -> None:
        core = self.core
        y, m = traj.calendar_year, traj.calendar_month
        recognized = _money(traj.revenue_runrate)
        cogs = _money(traj.cogs_runrate)

        # 1. New bookings invoiced (billing > recognized to build deferred revenue)
        billings = (recognized * Decimal("1.12")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
        core.post("BOOKING", y, m, 28, [dr(CoA.TRADE_AR, billings), cr(CoA.DEFERRED_REVENUE_CURRENT, billings)],
                  entity="Enterprise Customers", memo="Annual subscription invoice (ASC 606)", document_ref=f"SUB-{y}{m:02d}")
        core.total_contract_invoiced += billings

        # 2. Ratable recognition from deferred revenue (ASC 606 waterfall)
        core.post("REVENUE_RECOGNITION", y, m, 28, [dr(CoA.DEFERRED_REVENUE_CURRENT, recognized), cr(CoA.SUBSCRIPTION_REVENUE, recognized)],
                  entity="Enterprise Customers", memo="Ratable subscription revenue recognition", document_ref=f"RR-{y}{m:02d}")
        core.cumulative_recognized += recognized

        # 3. ASC 606 revenue waterfall invariant (INV5)
        self._assert_inv5()

        # 4. COGS (cloud hosting)
        core.post("HOSTING_COGS", y, m, 28, [dr(CoA.CLOUD_HOSTING, cogs), cr(CoA.TRADE_AP, cogs)],
                  entity="AWS", memo="Cloud infrastructure hosting costs", document_ref=f"AWS-{y}{m:02d}")

        # 5. OpEx: driver-based decomposition into granular vendor invoices / payroll
        self.expense_engine.generate_month(core, traj, y, m)

        # 6. Software development capitalization (ASC 350-40) with SR-B14 anomaly
        self._software_capitalization(y, m)

        # 7. Software amortization (ASC 350-40)
        amort = (self.core.capitalized_software * Decimal("0.02")).quantize(_QUANT, rounding=ROUND_HALF_EVEN) if self.core.capitalized_software > 0 else _money(0)
        if amort > 0:
            core.post("SOFTWARE_AMORT", y, m, 28, [dr(CoA.AMORTIZATION_EXPENSE, amort), cr(CoA.ACCUM_AMORTIZATION, amort)],
                      entity="Engineering", memo="Capitalized software amortization", document_ref=f"AM-{y}{m:02d}")

        # 8. Collections / AP payment
        collected = (self.core.ar * self._collection_ratio()).quantize(_QUANT, rounding=ROUND_HALF_EVEN) if self.core.ar > 0 else _money(0)
        if collected > 0:
            core.post("COLLECTION", y, m, 15, [dr(CoA.OPERATING_CASH, collected), cr(CoA.TRADE_AR, collected)],
                      entity="Customers", memo="Customer payment application", document_ref=f"PY-{y}{m:02d}")
        paid = (self.core.ap * self._payable_ratio()).quantize(_QUANT, rounding=ROUND_HALF_EVEN) if self.core.ap > 0 else _money(0)
        if paid > 0:
            core.post("AP_PAYMENT", y, m, 25, [dr(CoA.TRADE_AP, paid), cr(CoA.OPERATING_CASH, paid)],
                      entity="AWS", memo="Vendor payment disbursement", document_ref=f"AP-{y}{m:02d}")

        # 9. Settle payroll accrual
        self._settle_payroll(y, m, 28)

    def _software_capitalization(self, y: int, m: int) -> None:
        """ASC 350-40: capitalize only Application-Development-Stage labor."""
        rnd_spend = self.expense_engine.last_month_rnd
        if rnd_spend <= 0:
            return
        if "SR-B14" in self.anomaly_ids:
            # Anomaly: capitalize maintenance labor (65% of sprint velocity) that must be expensed
            capitalized = rnd_spend
            self.core.post("SOFTWARE_CAPITALIZE", y, m, 20,
                           [dr(CoA.CAPITALIZED_SOFTWARE, capitalized),
                            cr("611000", capitalized)],
                           entity="Engineering", memo="Software development capitalized (ASC 350-40)", document_ref=f"CAP-{y}{m:02d}")
            over_capitalized = (capitalized * Decimal("0.65")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
            self.core.anomalies.append({
                "anomaly_id": "SR-B14",
                "accounting_standard": "ASC_350_40",
                "description": "Routine maintenance & bug-fix labor capitalized as internal-use software",
                "amount": str(over_capitalized),
                "ebitda_impact": str(over_capitalized),
                "target_gl_accounts": [CoA.CAPITALIZED_SOFTWARE, "611000"],
            })
        else:
            capitalized = (rnd_spend * Decimal("0.35")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
            self.core.post("SOFTWARE_CAPITALIZE", y, m, 20,
                           [dr(CoA.CAPITALIZED_SOFTWARE, capitalized),
                            cr("611000", capitalized)],
                           entity="Engineering", memo="Capitalizable application development labor", document_ref=f"CAP-{y}{m:02d}")

    def _assert_inv5(self) -> None:
        FinancialPhysicsEngine.assert_inv5_asc606_revenue_waterfall(
            self.core.total_contract_invoiced,
            self.core.cumulative_recognized,
            self.core.deferred_revenue,
        )


# ---------------------------------------------------------------------------
# Multi-ERP Native Exporters
# ---------------------------------------------------------------------------
class ERPSchemaType(Enum):
    """Mirrors proto/biz_gen.proto enum ERPSchemaType (source of truth)."""
    ERP_UNSPECIFIED = 0
    ERP_ORACLE_NETSUITE = 1
    ERP_SAP_S4HANA = 2
    ERP_QUICKBOOKS_DESKTOP = 3
    ERP_MICROSOFT_DYNAMICS_365 = 4


# Maps the proto enum to the exporter's string keys.
ERP_TYPE_TO_EXPORTER: Dict[ERPSchemaType, str] = {
    ERPSchemaType.ERP_ORACLE_NETSUITE: "NETSUITE",
    ERPSchemaType.ERP_SAP_S4HANA: "SAP_S4HANA",
    ERPSchemaType.ERP_QUICKBOOKS_DESKTOP: "QUICKBOOKS",
    ERPSchemaType.ERP_MICROSOFT_DYNAMICS_365: "DYNAMICS365",
}


class ERPExporter:
    """Renders the GL into the four native ERP schemas (spec Section 5)."""

    ERP_NETSUITE = "NETSUITE"
    ERP_SAP_S4HANA = "SAP_S4HANA"
    ERP_QUICKBOOKS = "QUICKBOOKS"
    ERP_DYNAMICS365 = "DYNAMICS365"

    _TYPE_MAP = {
        "INVOICE": ("CustInvc", "DR", "INVOICE", "Sales invoice"),
        "BOOKING": ("CustInvc", "DR", "INVOICE", "Sales invoice"),
        "COLLECTION": ("Check", "DZ", "CHECK", "Customer payment"),
        "AP_PAYMENT": ("Check", "KZ", "CHECK", "Vendor payment"),
        "PURCHASE": ("VendBill", "KR", "BILL", "Vendor invoice"),
        "COGS_RELIEF": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
        "OPEX": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
        "PRODUCTION": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
        "SCRAP_WRITEOFF": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
        "IDLE_OVERHEAD": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
        "VENDOR_REBATE": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
        "REVENUE_RECOGNITION": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
        "HOSTING_COGS": ("VendBill", "KR", "BILL", "Vendor invoice"),
        "SOFTWARE_CAPITALIZE": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
        "SOFTWARE_AMORT": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
        "PAYROLL_SETTLEMENT": ("Check", "KZ", "CHECK", "Vendor payment"),
        "OPENING_BALANCE": ("Journal", "SA", "GENERAL JOURNAL", "General journal"),
    }

    @classmethod
    def export(cls, erp_type: str, entries: List[JournalEntry]) -> str:
        if erp_type == cls.ERP_NETSUITE:
            return cls._netsuite(entries)
        if erp_type == cls.ERP_SAP_S4HANA:
            return cls._sap(entries)
        if erp_type == cls.ERP_QUICKBOOKS:
            return cls._quickbooks(entries)
        if erp_type == cls.ERP_DYNAMICS365:
            return cls._dynamics365(entries)
        raise ValueError(f"Unknown ERP type: {erp_type}")

    @classmethod
    def _type(cls, entry_type: str) -> Tuple[str, str, str, str]:
        return cls._TYPE_MAP.get(entry_type, ("Journal", "SA", "GENERAL JOURNAL", "General journal"))

    @classmethod
    def _netsuite(cls, entries: List[JournalEntry]) -> str:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["Internal ID", "Date", "Type", "Doc Number", "Account Number", "Account Name",
                    "Entity", "Debit", "Credit", "Memo", "Subsidiary", "Department"])
        internal_id = 490000
        for e in entries:
            ns_type, _, _, _ = cls._type(e.entry_type)
            for line in e.lines:
                w.writerow([internal_id, e.entry_date, ns_type, e.document_ref or e.entry_id,
                            line.account_number, line.account_name, e.entity_name,
                            f"{line.debit:.2f}", f"{line.credit:.2f}", e.memo, "Sub 01: Apex US", "100: Operations"])
                internal_id += 1
        return buf.getvalue()

    @classmethod
    def _sap(cls, entries: List[JournalEntry]) -> str:
        rows = ["RCLNT\tRBUKRS\tGJAHR\tBELNR\tDOCLN\tBLART\tBLDAT\tBUDAT\tBSCHL\tRACCT\tPRCTR\tHSL"]
        belnr = 100094000
        for e in entries:
            _, sap_type, _, _ = cls._type(e.entry_type)
            docln = 0
            for line in e.lines:
                docln += 1
                posting_key = "40" if line.debit > 0 else "50"
                hsl = line.debit if line.debit > 0 else -line.credit
                rows.append(f"100\t1010\t{e.sim_year}\t{belnr:010d}\t{docln:06d}\t{sap_type}\t"
                            f"{e.entry_date.replace('-', '')}\t{e.entry_date.replace('-', '')}\t"
                            f"{posting_key}\t{line.account_number}\tPC_COMM_01\t{hsl:.2f}")
            belnr += 1
        return "\n".join(rows) + "\n"

    @classmethod
    def _quickbooks(cls, entries: List[JournalEntry]) -> str:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["!TRNS", "TRNSID", "TRNSTYPE", "DATE", "ACCNT", "NAME", "AMOUNT", "MEMO", "CLASS", "CLEAR"])
        for e in entries:
            _, _, qb_type, _ = cls._type(e.entry_type)
            for line in e.lines:
                amount = line.debit - line.credit
                w.writerow(["TRNS", e.entry_id, qb_type, e.entry_date,
                            line.account_name.replace(" - ", ":"), e.entity_name,
                            f"{amount:.2f}", e.memo, "Operations", "N"])
        return buf.getvalue()

    @classmethod
    def _dynamics365(cls, entries: List[JournalEntry]) -> str:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["Voucher", "TransDate", "AccountDisplayValue", "MainAccount",
                    "Department_Dimension", "CostCenter_Dimension", "TransactionCurrency",
                    "AmountCurDebit", "AmountCurCredit", "AmountMSTDebit", "Description"])
        for e in entries:
            for line in e.lines:
                w.writerow([e.entry_id, e.entry_date, f"{line.account_number} - {line.account_name}",
                            line.account_number, "100", "CC_01", "USD",
                            f"{line.debit:.2f}", f"{line.credit:.2f}", f"{line.debit:.2f}", e.memo])
        return buf.getvalue()


# ---------------------------------------------------------------------------
# Documentary Degradation Engine (spec Section 6)
# ---------------------------------------------------------------------------
class DegradationEngine:
    """Injects authentic documentary defects into the VDR artifacts (not the GL)."""

    def __init__(self, seed: int):
        self.rng = random.Random((seed & 0x7FFFFFFF) ^ 0x2545F491)
        self.defects: List[dict] = []

    def render_working_capital_schedule(self, core: AccountingCore) -> Tuple[str, List[dict]]:
        """Renders a management Excel schedule with an injected Panko cell error."""
        ar = core.ar
        ap = core.ap
        inventory = core.inventory
        unapplied = core.unapplied_cash

        plug = _money(35000)
        self.defects.append({
            "defect_type": "PANko_CELL_ERROR",
            "description": "Working capital schedule omits accrued warranty reserve; hardcoded plug forces subledger balance",
            "amount": str(plug),
        })

        rows = [
            ["Working Capital Component", "Amount (USD)"],
            ["Trade Accounts Receivable", f"{ar:.2f}"],
            ["Unapplied Cash Clearing", f"{unapplied:.2f}"],
            ["Inventory (Net)", f"{inventory:.2f}"],
            ["Less: Trade Accounts Payable", f"{-ap:.2f}"],
            ["Net Working Capital (with plug)", f"{(ar + unapplied + inventory - ap + plug):.2f}"],
        ]
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerows(rows)
        return buf.getvalue(), self.defects

    def render_aged_ar_schedule(self, core: AccountingCore) -> Tuple[str, List[dict]]:
        """Renders an aged AR schedule showing unapplied-cash-induced 90+ day aging."""
        ar = core.ar
        unapplied = core.unapplied_cash
        overdue = (ar * Decimal("0.35")).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
        self.defects.append({
            "defect_type": "UNAPPLIED_CASH",
            "description": f"Aged AR shows 90+ day balances while ${unapplied:.2f} sits in unapplied cash clearing",
            "amount": str(unapplied),
        })
        rows = [
            ["Aging Bucket", "Balance (USD)"],
            ["Current", f"{(ar - overdue):.2f}"],
            ["1-30 Days", f"{overdue * Decimal('0.4'):.2f}"],
            ["31-60 Days", f"{overdue * Decimal('0.25'):.2f}"],
            ["61-90 Days", f"{overdue * Decimal('0.15'):.2f}"],
            ["90+ Days", f"{overdue * Decimal('0.20'):.2f}"],
        ]
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerows(rows)
        return buf.getvalue(), self.defects

    def missing_records(self) -> List[dict]:
        """Deterministic missing-record flags requiring a scope limitation disclosure."""
        return [
            {"document_type": "WARRANTY_CLAIMS_FY21", "status": "MISSING_LEGACY_SERVER_MIGRATION",
             "recommended_action": "Scope limitation + $500,000 specific indemnity escrow"},
        ]


# ---------------------------------------------------------------------------
# Sector simulator factory
# ---------------------------------------------------------------------------
def build_simulator(
    core: AccountingCore,
    sector: IndustrySector,
    anomaly_ids: Sequence[str],
) -> BaseSectorSimulator:
    if sector == IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION:
        return WholesaleDistributionSimulator(core, sector, anomaly_ids)
    if sector == IndustrySector.SECTOR_PRECISION_MANUFACTURING:
        return PrecisionManufacturingSimulator(core, sector, anomaly_ids)
    if sector == IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS:
        return SaaSSubscriptionSimulator(core, sector, anomaly_ids)
    raise ValueError(f"Unsupported sector: {sector}")
