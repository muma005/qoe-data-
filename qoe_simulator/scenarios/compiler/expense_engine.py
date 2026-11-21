"""
QoE Simulator - Level 2 Expense Generation Engine (biz-gen submodule).

Replaces the trivial fixed-ratio OpEx split with a driver-based decomposition
of Module 10's aggregate `opex_runrate` control total into hundreds of granular
vendor invoices, payroll lines, and non-cash charges.

Design (per 02_business_reality_and_multi_erp_data_engine.md core axiom):
  - Module 10's `opex_runrate` is the TOP-DOWN control total (how much is spent).
  - This engine decomposes it BOTTOM-UP across an expense taxonomy (~30 accounts),
    each driven by a cost driver (headcount, revenue, capacity, volume, fixed,
    discretionary) and realized as N vendor invoices / payroll lines per month.
  - The decomposition reconciles EXACTLY to the control total using fixed-point
    Decimal largest-remainder allocation, so INV1/INV2 remain exact.

Deterministic for a given (sector, seed).
"""

from __future__ import annotations

import os
import random
import sys
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Dict, List, Sequence, Tuple

_COMPILER_DIR = os.path.dirname(os.path.abspath(__file__))
if _COMPILER_DIR not in sys.path:
    sys.path.insert(0, _COMPILER_DIR)

from macro_volatility import IndustrySector, MonthlyTrajectoryVector  # noqa: E402
from sector_models import CoA, _money, _QUANT, cr, dr  # noqa: E402

# ---------------------------------------------------------------------------
# Expense account names (registered into the CoA so ledger/ERP exports render)
# ---------------------------------------------------------------------------
EXPENSE_ACCOUNT_NAMES: Dict[str, str] = {
    "601100": "Sales Commissions",
    "601200": "Marketing & Advertising",
    "601300": "Trade Shows & Events",
    "601400": "Travel & Entertainment",
    "601500": "CRM & Sales Tools",
    "611000": "Engineering & Product Development Salaries",
    "611100": "Product Development",
    "611200": "QA & Testing Tools",
    "621000": "Executive Salaries",
    "621100": "Finance & Accounting Salaries",
    "621200": "HR & Recruiting",
    "621300": "Legal Fees",
    "621400": "Audit & Tax Fees",
    "621500": "Consulting Fees",
    "621600": "Insurance Premiums",
    "621700": "Office Rent & Lease",
    "621800": "Utilities",
    "621900": "Office Supplies & Postage",
    "631000": "Facility Rent & Lease",
    "631100": "Equipment Maintenance & Repair",
    "631200": "Fleet & Freight-Out",
    "631300": "Packaging Materials",
    "631400": "Safety & Compliance",
    "641000": "IT Hardware & Software Licenses",
    "641100": "Telecommunications & Internet",
    "641200": "Data Backup & Security",
    "701100": "Executive Bonuses",
    "702100": "Board Fees",
}
CoA._NAMES.update(EXPENSE_ACCOUNT_NAMES)

# ---------------------------------------------------------------------------
# Vendor pools (LP-15: verified, realistic third-party entities)
# ---------------------------------------------------------------------------
_LEGAL = ("Baker McKenzie LLP", "Jones Day LLP", "Latham & Watkins LLP")
_AUDIT = ("Deloitte & Touche LLP", "PricewaterhouseCoopers LLP", "Ernst & Young LLP", "KPMG LLP")
_INSURANCE = ("Chubb Insurance", "The Hartford", "Travelers Companies")
_RENT = ("ProLogis Leasing", "Duke Realty", "Boston Properties")
_UTILITIES = ("Pacific Gas & Electric", "Duke Energy", "National Grid")
_TELECOM = ("AT&T Business", "Verizon Business", "Comcast Business")
_IT_SOFTWARE = ("Microsoft Corporation", "Salesforce.com Inc.", "Adobe Inc.", "CrowdStrike Holdings")
_OFFICE = ("Staples Business Advantage", "Amazon Business", "Office Depot")
_MARKETING = ("Google Ads", "Meta Platforms Inc.", "LinkedIn Corporation", "The Trade Desk")
_TRAVEL = ("Delta Air Lines", "Marriott International", "United Airlines", "Uber for Business")
_CONSULTING = ("McKinsey & Company", "Boston Consulting Group", "Bain & Company")
_RECRUITING = ("LinkedIn Talent Solutions", "Robert Half International", "Indeed Inc.")
_FREIGHT = ("FedEx Freight", "UPS Freight", "XPO Logistics", "Old Dominion Freight Line")
_PACKAGING = ("WestRock Company", "International Paper", "Packaging Corp of America")
_RM = ("W.W. Grainger Inc.", "Fastenal Company", "MSC Industrial Supply")
_SAFETY = ("3M Company", "Honeywell Safety Products", "Ansell Limited")
_DEVTOOLS = ("GitHub Inc.", "Atlassian Corporation", "JetBrains s.r.o.", "Datadog Inc.")
_QA = ("BrowserStack", "Sauce Labs Inc.", "LambdaTest")
_EVENTS = ("Informa Markets", "Gartner Inc.", "Eventbrite")


# ---------------------------------------------------------------------------
# Expense category model
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ExpenseCategory:
    account: str
    name: str
    driver: str          # HEADCOUNT | REVENUE | CAPACITY | VOLUME | FIXED | DISCRETIONARY | NON_CASH
    weight: float        # base share of opex (normalized at runtime)
    settlement: str      # ACCRUED (payroll) | AP (vendor) | NON_CASH
    vendors: Tuple[str, ...] = ()
    min_invoices: int = 3
    max_invoices: int = 10
    term: str = "NET_30"
    contra_account: str = ""  # for NON_CASH (e.g. accumulated depreciation)


def _c(account, name, driver, weight, vendors=(), min_n=3, max_n=10,
       settlement="AP", term="NET_30", contra=""):
    return ExpenseCategory(account, name, driver, weight, settlement,
                           tuple(vendors), min_n, max_n, term, contra)


# ---------------------------------------------------------------------------
# Sector expense profiles (the taxonomy of ~30 accounts per sector)
# ---------------------------------------------------------------------------
_COMMON_GNA = [
    # Salaries / payroll (ACCRUED)
    _c("621000", "Executive Salaries", "HEADCOUNT", 0.08, settlement="ACCRUED"),
    _c("621100", "Finance & Accounting Salaries", "HEADCOUNT", 0.06, settlement="ACCRUED"),
    _c("621200", "HR & Recruiting", "HEADCOUNT", 0.04, settlement="ACCRUED"),
    # Vendor AP expenses
    _c("621300", "Legal Fees", "FIXED", 0.020, _LEGAL, max_n=6),
    _c("621400", "Audit & Tax Fees", "FIXED", 0.015, _AUDIT, max_n=6),
    _c("621500", "Consulting Fees", "DISCRETIONARY", 0.010, _CONSULTING, max_n=6),
    _c("621600", "Insurance Premiums", "CAPACITY", 0.020, _INSURANCE, max_n=6),
    _c("621700", "Office Rent & Lease", "CAPACITY", 0.030, _RENT, max_n=4),
    _c("621800", "Utilities", "CAPACITY", 0.020, _UTILITIES, max_n=6),
    _c("621900", "Office Supplies & Postage", "VOLUME", 0.010, _OFFICE),
    _c("641000", "IT Hardware & Software Licenses", "FIXED", 0.020, _IT_SOFTWARE, max_n=6),
    _c("641100", "Telecommunications & Internet", "CAPACITY", 0.015, _TELECOM, max_n=6),
    _c("641200", "Data Backup & Security", "FIXED", 0.010, _IT_SOFTWARE, max_n=4),
    # Executive compensation
    _c("701000", "Owner Salary", "HEADCOUNT", 0.040, settlement="ACCRUED"),
    _c("701100", "Executive Bonuses", "DISCRETIONARY", 0.010, settlement="ACCRUED", min_n=1, max_n=4),
    _c("702000", "Discretionary Perks", "DISCRETIONARY", 0.005, (), min_n=1, max_n=3),
    _c("702100", "Board Fees", "FIXED", 0.005, (), min_n=1, max_n=3),
    # Non-cash
    _c("603000", "Depreciation Expense", "NON_CASH", 0.100, settlement="NON_CASH",
       contra=CoA.ACCUM_DEPRECIATION),
]

_SALES_MARKETING = [
    _c("601000", "Sales Salaries & Wages", "HEADCOUNT", 0.160, settlement="ACCRUED"),
    _c("601100", "Sales Commissions", "REVENUE", 0.040, settlement="ACCRUED"),
    _c("601200", "Marketing & Advertising", "DISCRETIONARY", 0.040, _MARKETING, max_n=15),
    _c("601300", "Trade Shows & Events", "DISCRETIONARY", 0.010, _EVENTS, max_n=6),
    _c("601400", "Travel & Entertainment", "DISCRETIONARY", 0.020, _TRAVEL, max_n=12),
    _c("601500", "CRM & Sales Tools", "FIXED", 0.015, _IT_SOFTWARE, max_n=4),
]

WHOLESALE_OPS = [
    _c("631000", "Warehouse Rent", "CAPACITY", 0.060, _RENT, max_n=4),
    _c("631100", "Equipment Maintenance & Repair", "VOLUME", 0.020, _RM, max_n=8),
    _c("631200", "Fleet & Freight-Out", "VOLUME", 0.050, _FREIGHT, max_n=15),
    _c("631300", "Packaging Materials", "VOLUME", 0.030, _PACKAGING, max_n=12),
    _c("631400", "Safety & Compliance", "FIXED", 0.010, _SAFETY, max_n=4),
]

MANUFACTURING_OPS = [
    _c("611000", "Engineering & Product Development Salaries", "HEADCOUNT", 0.060, settlement="ACCRUED"),
    _c("611200", "QA & Testing Tools", "FIXED", 0.010, _QA, max_n=4),
    _c("631000", "Plant Rent & Lease", "CAPACITY", 0.050, _RENT, max_n=4),
    _c("631100", "Machine Maintenance & Repair", "VOLUME", 0.035, _RM, max_n=12),
    _c("631200", "Tooling & Consumables", "VOLUME", 0.025, _RM, max_n=12),
    _c("631300", "Quality Control & Inspection", "VOLUME", 0.015, _QA, max_n=6),
    _c("631400", "Safety & Compliance", "FIXED", 0.010, _SAFETY, max_n=4),
]

SAAS_OPS = [
    _c("611000", "Engineering & Product Development Salaries", "HEADCOUNT", 0.320, settlement="ACCRUED"),
    _c("611200", "QA & Testing Tools", "FIXED", 0.015, _QA, max_n=6),
    _c("601100", "Sales Commissions", "REVENUE", 0.060, settlement="ACCRUED"),
    _c("641000", "Developer Tooling & SaaS Subscriptions", "FIXED", 0.025, _DEVTOOLS, max_n=12),
]


SECTOR_PROFILES: Dict[IndustrySector, List[ExpenseCategory]] = {
    IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION: _COMMON_GNA + _SALES_MARKETING + WHOLESALE_OPS,
    IndustrySector.SECTOR_PRECISION_MANUFACTURING: _COMMON_GNA + _SALES_MARKETING + MANUFACTURING_OPS,
    IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS: _COMMON_GNA + _SALES_MARKETING + SAAS_OPS,
}

# R&D labor account that SaaS ASC 350-40 capitalization reclassifies from.
RND_CAPITALIZABLE = "611000"


# ---------------------------------------------------------------------------
# Expense engine
# ---------------------------------------------------------------------------
class ExpenseEngine:
    """Decomposes the opex control total into granular expense transactions."""

    def __init__(self, sector: IndustrySector, seed: int):
        self.sector = sector
        self.rng = random.Random((seed & 0x7FFFFFFF) ^ 0x0BADC0DE)
        self.categories = SECTOR_PROFILES[sector]
        self.invoice_seq = 0
        self.last_month_amounts: Dict[str, Decimal] = {}
        self.last_month_rnd = Decimal("0.0000")

    # -- driver factors ----------------------------------------------------
    @staticmethod
    def _driver_factor(cat: ExpenseCategory, revenue_index: Decimal) -> Decimal:
        d = cat.driver
        if d == "REVENUE":
            return revenue_index
        if d == "VOLUME":
            return revenue_index
        if d == "DISCRETIONARY":
            # discretionary spend is cut in downturns, floored
            return max(Decimal("0.50"), revenue_index)
        # HEADCOUNT (sticky/hoarded), CAPACITY, FIXED, NON_CASH: constant
        return Decimal("1.0")

    # -- exact fixed-point allocation --------------------------------------
    @staticmethod
    def _allocate(total: Decimal, weights: Sequence[Decimal]) -> List[Decimal]:
        """Largest-remainder allocation: shares sum EXACTLY to `total` (4 dp)."""
        n = len(weights)
        total_weight = sum(weights, Decimal("0.0000"))
        if total_weight <= 0 or n == 0:
            return [Decimal("0.0000") for _ in range(n)]
        shares = [
            (total * w / total_weight).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
            for w in weights
        ]
        residual = (total - sum(shares, Decimal("0.0000"))).quantize(_QUANT, rounding=ROUND_HALF_EVEN)
        if residual != 0:
            unit = Decimal("0.0001")
            steps = int((residual / unit).to_integral_value())
            # distribute residual round-robin to largest-weight items
            order = sorted(range(n), key=lambda i: weights[i], reverse=True)
            idx = 0
            while steps != 0:
                sign = 1 if steps > 0 else -1
                shares[order[idx % n]] = (shares[order[idx % n]] + (unit * sign)).quantize(
                    _QUANT, rounding=ROUND_HALF_EVEN)
                steps -= sign
                idx += 1
        return shares

    # -- main monthly entry point ------------------------------------------
    def generate_month(self, core, traj: MonthlyTrajectoryVector, year: int, month: int) -> None:
        control = _money(traj.opex_runrate)
        base_rev = core.base_monthly_revenue
        revenue_index = (Decimal(str(traj.revenue_runrate)) / base_rev) if base_rev > 0 else Decimal("1.0")
        revenue_index = max(Decimal("0.40"), min(Decimal("1.60"), revenue_index))

        weights = [Decimal(str(cat.weight)) * self._driver_factor(cat, revenue_index)
                   for cat in self.categories]
        amounts = self._allocate(control, weights)

        self.last_month_amounts = {}
        for cat, amount in zip(self.categories, amounts):
            if amount <= 0:
                continue
            self.last_month_amounts[cat.account] = amount
            self._post_category(core, cat, amount, year, month)
        self.last_month_rnd = self.last_month_amounts.get(RND_CAPITALIZABLE, Decimal("0.0000"))

    # -- per-category posting ----------------------------------------------
    def _post_category(self, core, cat: ExpenseCategory, amount: Decimal,
                       year: int, month: int) -> None:
        if cat.settlement == "NON_CASH":
            self._post_line(core, cat, amount, year, month, entity="Fixed Assets",
                            doc_ref=f"{cat.account}-{year}{month:02d}", day=28)
            return

        n = self.rng.randint(cat.min_invoices, cat.max_invoices)
        weights = [Decimal(str(self.rng.uniform(0.50, 1.50))) for _ in range(n)]
        parts = self._allocate(amount, weights)
        for part in parts:
            if part <= 0:
                continue
            if cat.settlement == "ACCRUED":
                self._post_line(core, cat, part, year, month, entity="Payroll",
                                doc_ref=f"PR-{year}{month:02d}",
                                day=self.rng.randint(1, 28))
            else:  # AP vendor invoice
                vendor = self.rng.choice(cat.vendors) if cat.vendors else "General Vendor"
                self.invoice_seq += 1
                self._post_line(core, cat, part, year, month, entity=vendor,
                                doc_ref=f"INV-{year}{month:02d}-{self.invoice_seq:06d}",
                                day=self.rng.randint(1, 28))

    def _post_line(self, core, cat: ExpenseCategory, amount: Decimal,
                   year: int, month: int, day: int, entity: str, doc_ref: str) -> None:
        if cat.settlement == "NON_CASH":
            entry_type = "DEPRECIATION" if cat.account == CoA.DEPRECIATION_EXPENSE else "AMORTIZATION"
            core.post(entry_type, year, month, day,
                      [dr(cat.account, amount), cr(cat.contra_account, amount)],
                      entity=entity, memo=cat.name, document_ref=doc_ref)
        elif cat.settlement == "ACCRUED":
            core.post("PAYROLL", year, month, day,
                      [dr(cat.account, amount), cr(CoA.ACCRUED_PAYROLL, amount)],
                      entity=entity, memo=cat.name, document_ref=doc_ref)
        else:
            core.post("EXPENSE", year, month, day,
                      [dr(cat.account, amount), cr(CoA.TRADE_AP, amount)],
                      entity=entity, memo=cat.name, document_ref=doc_ref)
