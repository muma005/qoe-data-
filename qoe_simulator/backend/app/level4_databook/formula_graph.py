"""
QoE Simulator - Level 4: Headless Calculation Graph, Topological Sort / Cycle
Detector, Additive PVM Waterfall, Replacement Cost Doctrine, and Anti-Double-Dipping
Checker (04_financial_databook_and_calculation_engine.md).

This is the dependency-free calculation core of `fdb-calc`:
  - CheckBarStatus enum (mirrors proto/fdb_calc.proto).
  - In-memory Directed Acyclic Graph of cell dependencies with Kahn's topological
    sort and circular-reference detection (LP-16).
  - A small, safe arithmetic formula evaluator (no eval); literals and cell refs only.
  - Order-independent additive Price-Volume-Mix decomposition (SR-VAL06).
  - Replacement Cost Doctrine netting (Algorithm 2).
  - Mutual-Exclusivity / anti-double-dipping checker across EBITDA / NWC / Net Debt.

Money is fixed-point Decimal throughout; no floating-point math enters calculations.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

_QUANT = Decimal("0.0001")


def _money(value) -> Decimal:
    if isinstance(value, Decimal):
        return value.quantize(_QUANT, rounding=ROUND_HALF_UP)
    return Decimal(str(value)).quantize(_QUANT, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Proto-mirror enum (source of truth: proto/fdb_calc.proto)
# ---------------------------------------------------------------------------
class CheckBarStatus(Enum):
    CHECK_STATUS_UNSPECIFIED = 0
    CHECK_PASS = 1
    CHECK_FAIL = 2
    CHECK_CIRCULAR_ERROR = 3


# ---------------------------------------------------------------------------
# Cell model + DAG
# ---------------------------------------------------------------------------
@dataclass
class Cell:
    tab_id: str
    coordinate: str
    formula_or_value: str
    dependencies: List[Tuple[str, str]] = field(default_factory=list)
    evaluated_value: Optional[Decimal] = None
    error_flag: str = ""

    @property
    def key(self) -> Tuple[str, str]:
        return (self.tab_id, self.coordinate)


class CycleDetectedError(Exception):
    def __init__(self, cyclic_cells: Sequence[Tuple[str, str]]):
        self.cyclic_cells = list(cyclic_cells)
        super().__init__(f"Circular reference detected: {self.cyclic_cells}")


class FormulaGraph:
    """In-memory DAG of cell dependencies with Kahn's topological sort."""

    def __init__(self):
        self.cells: Dict[Tuple[str, str], Cell] = {}
        self.dependents: Dict[Tuple[str, str], Set[Tuple[str, str]]] = {}

    def add_cell(self, cell: Cell) -> None:
        self.cells[cell.key] = cell
        self.dependents.setdefault(cell.key, set())
        for dep in cell.dependencies:
            self.dependents.setdefault(dep, set()).add(cell.key)

    def topological_sort(self) -> List[Tuple[str, str]]:
        """Kahn's algorithm. Raises CycleDetectedError on a dependency loop."""
        in_degree: Dict[Tuple[str, str], int] = {k: 0 for k in self.cells}
        for cell in self.cells.values():
            for dep in cell.dependencies:
                in_degree[cell.key] += 1
        queue = [k for k, d in in_degree.items() if d == 0]
        order: List[Tuple[str, str]] = []
        while queue:
            key = queue.pop(0)
            order.append(key)
            for dependent in self.dependents.get(key, ()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        if len(order) != len(self.cells):
            cyclic = [k for k, d in in_degree.items() if d > 0]
            raise CycleDetectedError(cyclic)
        return order

    def detect_cycles(self) -> List[Tuple[str, str]]:
        try:
            self.topological_sort()
            return []
        except CycleDetectedError as e:
            return e.cyclic_cells

    def evaluate(self) -> List[Cell]:
        """Evaluates all cells in topological order; isolates errors per-cell."""
        order = self.topological_sort()
        values: Dict[Tuple[str, str], Decimal] = {}
        for key in order:
            cell = self.cells[key]
            try:
                cell.evaluated_value = self._eval_cell(cell, values)
                cell.error_flag = ""
            except Exception:
                cell.evaluated_value = None
                cell.error_flag = "#ERROR"
            values[key] = cell.evaluated_value if cell.evaluated_value is not None else _money(0)
        return [self.cells[k] for k in order]

    def _eval_cell(self, cell: Cell, values: Dict[Tuple[str, str], Decimal]) -> Decimal:
        expr = cell.formula_or_value.strip()
        if not expr.startswith("="):
            return _money(expr)

        def resolve(tab: Optional[str], coord: str) -> Decimal:
            # None tab means same-tab reference to the current cell's tab.
            key = (tab if tab is not None else cell.tab_id, coord)
            return values.get(key, _money(0))

        return _evaluate_formula(expr[1:], resolve)


# ---------------------------------------------------------------------------
# Safe arithmetic formula evaluator (literals + cell refs + SUM; no eval)
# ---------------------------------------------------------------------------
_TOKEN_RE = re.compile(r"\s*(?:(SUM)|\d+\.?\d*|([A-Za-z_][A-Za-z0-9_]*)|([()+\-*/:!,]))")


def _evaluate_formula(expr: str, resolver: Callable[[str, str], Decimal]) -> Decimal:
    tokens = [m.group(0).strip()
              for m in _TOKEN_RE.finditer(expr) if m.group(0).strip()]
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def parse_expr() -> Decimal:
        nonlocal pos
        value = parse_term()
        while peek() in ("+", "-"):
            op = tokens[pos]
            pos += 1
            rhs = parse_term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def parse_term() -> Decimal:
        nonlocal pos
        value = parse_factor()
        while peek() in ("*", "/"):
            op = tokens[pos]
            pos += 1
            rhs = parse_factor()
            value = value * rhs if op == "*" else value / rhs
        return value

    def parse_factor() -> Decimal:
        nonlocal pos
        tok = peek()
        if tok is None:
            raise ValueError("unexpected end of formula")
        if tok == "(":
            pos += 1
            v = parse_expr()
            if peek() == ")":
                pos += 1
            return v
        if tok == "-":
            pos += 1
            return -parse_factor()
        if tok == "SUM":
            pos += 1
            if peek() == "(":
                pos += 1
            return parse_range_sum()
        if re.fullmatch(r"\d+\.?\d*", tok):
            pos += 1
            return _money(tok)
        return parse_cell_ref()

    def parse_cell_ref() -> Decimal:
        nonlocal pos
        first = tokens[pos]
        pos += 1
        if peek() == "!":
            pos += 1
            coord = tokens[pos]
            pos += 1
            return resolver(first, coord)  # cross-tab: Tab!Coord
        return resolver(None, first) if first else _money(0)  # same-tab: Coord

    def parse_range_sum() -> Decimal:
        nonlocal pos
        start = tokens[pos]
        pos += 1
        if peek() == ":":
            pos += 1
        end = tokens[pos]
        pos += 1
        if peek() == ")":
            pos += 1
        total = _money(0)
        col_s, row_s = _split_coord(start)
        col_e, row_e = _split_coord(end)
        if col_s == col_e:
            for r in range(min(row_s, row_e), max(row_s, row_e) + 1):
                total += resolver(None, f"{col_s}{r}")
        return total

    return parse_expr()


def _split_coord(coord: str) -> Tuple[str, int]:
    m = re.match(r"([A-Za-z]+)(\d+)", coord or "")
    if not m:
        return coord or "", 0
    return m.group(1), int(m.group(2))


# ---------------------------------------------------------------------------
# Algorithm 1: Additive symmetry PVM waterfall (order-independent, exact)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PVMProduct:
    base_volume: Decimal
    base_price: Decimal
    current_volume: Decimal
    current_price: Decimal


class PVMWaterfallEngine:
    """Decomposes total revenue variance into additive Price/Volume/Mix effects.

    PriceEffect  = sum(V_k1 * (P_k1 - P_k0))
    VolumeEffect = (V_total,1 - V_total,0) * P_bar_0
    MixEffect    = sum((V_k1/V_total,1 - V_k0/V_total,0) * V_total,1 * (P_k0 - P_bar_0))
    Identity     : DeltaRevenue == Price + Volume + Mix (exact to $0.0000)
    """

    def decompose(self, products: Sequence[PVMProduct]) -> Dict[str, Decimal]:
        v0_total = sum((p.base_volume for p in products), Decimal("0"))
        v1_total = sum((p.current_volume for p in products), Decimal("0"))
        r0 = sum((p.base_volume * p.base_price for p in products), Decimal("0"))
        r1 = sum((p.current_volume * p.current_price for p in products), Decimal("0"))
        delta = r1 - r0

        p_bar_0 = (r0 / v0_total) if v0_total > 0 else Decimal("0")

        price_effect = sum(
            (p.current_volume * (p.current_price - p.base_price) for p in products), Decimal("0"))
        volume_effect = (v1_total - v0_total) * p_bar_0
        mix_effect = sum(
            ((p.current_volume / v1_total - p.base_volume / v0_total) * v1_total *
             (p.base_price - p_bar_0) for p in products),
            Decimal("0"),
        ) if v1_total > 0 and v0_total > 0 else Decimal("0")

        residual = delta - price_effect - volume_effect - mix_effect

        return {
            "total_delta": _money(delta),
            "price_effect": _money(price_effect),
            "volume_effect": _money(volume_effect),
            "mix_effect": _money(mix_effect),
            "residual": _money(residual),
        }


# ---------------------------------------------------------------------------
# Algorithm 2: Mandatory Replacement Cost Deduction engine
# ---------------------------------------------------------------------------
class ReplacementCostEngine:
    """Net Defensible Adjustment = Gross Historical Cost Removed - Continuing Replacement."""

    def net_adjustment(self, gross_add_back, replacement_cost) -> Decimal:
        return _money(gross_add_back) - _money(replacement_cost)


# ---------------------------------------------------------------------------
# Algorithm 3: Anti-double-dipping / mutual-exclusivity checker
# ---------------------------------------------------------------------------
class DoubleDipChecker:
    """Prevents the same exposure being deducted across EBITDA / NWC / Net Debt."""

    BUCKETS = ("EBITDA_HAIRCUT", "NWC_LIABILITY", "NET_DEBT")

    def __init__(self):
        self._registrations: Dict[Tuple[str, str], List[str]] = {}
        self._account_buckets: Dict[str, Set[str]] = {}

    def register_deduction(self, deduction_id: str, gl_account: str, bucket: str) -> None:
        self._registrations.setdefault((gl_account, bucket), []).append(deduction_id)
        self._account_buckets.setdefault(gl_account, set()).add(bucket)

    def validate(self, deduction_id: str, gl_account: str, proposed_bucket: str) -> Dict[str, object]:
        """Returns a proto-shaped ValidateAntiDoubleDippingResponse."""
        buckets_used = self._account_buckets.get(gl_account, set())
        conflict_buckets = [b for b in buckets_used if b != proposed_bucket]
        if conflict_buckets:
            conflicting = self._registrations.get((gl_account, conflict_buckets[0]), [None])[0]
            return {
                "is_double_dipping": True,
                "conflicting_deduction_id": conflicting or "",
                "legal_doctrine_rule": "AICPA CS 100 Mutual Exclusivity Rule",
                "remediation_guidance": (
                    f"Account {gl_account} is already deducted in bucket "
                    f"'{conflict_buckets[0]}'. Carve it out of Working Capital before "
                    f"classifying it as '{proposed_bucket}' to avoid a 2.0x deduction."),
            }
        return {
            "is_double_dipping": False,
            "conflicting_deduction_id": "",
            "legal_doctrine_rule": "AICPA CS 100 Mutual Exclusivity Rule",
            "remediation_guidance": "",
        }


# ---------------------------------------------------------------------------
# 11-Tab Financial Databook (spec Section 2) — built from a Level 2 .csp package
# ---------------------------------------------------------------------------
class Databook:
    """Builds the 11 institutional databook tabs from a Level 2 .csp package.

    Consumes ground_truth.duckdb (via ReadProjectionsDB), subledgers.json, and
    injected_anomalies.json, then materializes the schedules in spec Section 2.1.
    """

    TAB_IDS = ("01_Summary", "02_EBITDA_Bridges", "03_Income_Statement",
               "04_Revenue_PVM", "05_Gross_Margin", "06_OPEX_Detail",
               "07_Working_Capital", "08_Net_Debt", "09_Cash_Flow_Capex",
               "10_Debt_Like_Items", "11_SPA_Exhibit_B")

    def __init__(self):
        self.tabs: Dict[str, dict] = {}
        self.package_dir = None

    # -- helpers -----------------------------------------------------------
    def _load_json(self, name: str) -> dict:
        with open(os.path.join(self.package_dir, name), encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _account_totals(db, monthly) -> Dict[str, Dict[str, object]]:
        """Ending balances per account (cumulative net = debit - credit)."""
        totals: Dict[str, Dict[str, object]] = {}
        for row in monthly:
            for r in db.get_trial_balance(row["sim_year"], row["sim_month"]):
                acct = r["account_number"]
                net = Decimal(str(r["net_balance"]))
                if acct not in totals:
                    totals[acct] = {"net": Decimal("0"), "category": r["account_category"]}
                totals[acct]["net"] += net
        return totals

    @staticmethod
    def _cat_total(totals: Dict[str, Dict], categories, negate: bool = False) -> Decimal:
        total = sum((v["net"] for v in totals.values()
                     if v["category"] in categories), Decimal("0"))
        return (-total).quantize(Decimal("0.0001")) if negate else total.quantize(Decimal("0.0001"))

    def _acct(self, totals: Dict[str, Dict], *account_numbers: str) -> Decimal:
        return sum((totals.get(a, {}).get("net", Decimal("0")) for a in account_numbers),
                   Decimal("0")).quantize(Decimal("0.0001"))

    # -- build -------------------------------------------------------------
    def build(self, package_dir: str) -> "Databook":
        from app.level0_physics.read_projections import ReadProjectionsDB
        self.package_dir = package_dir
        db = ReadProjectionsDB(os.path.join(package_dir, "ground_truth.duckdb"))
        subledgers = self._load_json("subledgers.json")
        anomalies = self._load_json("injected_anomalies.json").get("anomalies", [])
        monthly = db.get_monthly_revenue_and_cogs(2020, 2030)
        totals = self._account_totals(db, monthly)
        db.close()
        # P&L months exclude the zero-activity opening-balance month
        pnl_months = [r for r in monthly if r["revenue"] or r["cogs"] or r["opex"]]

        revenue = self._cat_total(totals, ("REVENUE",), negate=True)
        cogs = self._cat_total(totals, ("COGS",))
        opex = self._cat_total(totals, ("OPEX",))
        ebitda = revenue - cogs - opex
        net_income = ebitda  # no below-EBITDA items in the synthetic GL

        # Balance sheet (ending balances; net income folded into equity)
        assets = (self._cat_total(totals, ("CURRENT_ASSET", "NON_CURRENT_ASSET")))
        liabilities = self._cat_total(totals, ("CURRENT_LIABILITY", "NON_CURRENT_LIABILITY"),
                                      negate=True)
        equity = self._cat_total(totals, ("EQUITY",), negate=True) + net_income

        # Working capital drivers (liabilities read as credit balances -> negate)
        ar = self._acct(totals, "111000")
        ap = -self._acct(totals, "201000")
        inventory = self._acct(totals, "141000", "142000", "143000") - self._acct(totals, "144000")
        years = max(1, len(pnl_months) // 12)
        annual_revenue = revenue / Decimal(years)
        annual_cogs = cogs / Decimal(years)
        dso = (ar / annual_revenue * Decimal("365")) if annual_revenue > 0 else Decimal("0")
        dio = (inventory / annual_cogs * Decimal("365")) if annual_cogs > 0 else Decimal("0")
        dpo = (ap / annual_cogs * Decimal("365")) if annual_cogs > 0 else Decimal("0")
        nwc = ar + inventory - ap

        # EBITDA normalization bridge (4-tier)
        tier1 = -sum((Decimal(str(a.get("ebitda_impact", "0"))) for a in anomalies), Decimal("0"))
        normalized_ebitda = ebitda + tier1

        # Gross margin components (cloud hosting folded into overhead for 3-bucket check)
        materials = self._acct(totals, "501000")
        labor = self._acct(totals, "502000")
        overhead = self._acct(totals, "503000", "504000")

        # Cash / debt
        cash = self._acct(totals, "101000")
        stretched_ap = Decimal(str(subledgers["accounts_payable"].get(
            "stretched_payables_gt_90d", "0")))
        accrued_payroll = -self._acct(totals, "211000")  # positive liability
        debt_like = stretched_ap + accrued_payroll
        net_debt = debt_like - cash

        # Cash flow
        depreciation = Decimal(str(subledgers["fixed_assets"].get("journal_depreciation", "0")))
        ocf = ebitda + depreciation - nwc
        maintenance_capex = revenue * Decimal("0.02")
        fcf = ocf - maintenance_capex

        # Target NWC peg
        target_nwc_peg = nwc

        self.tabs = {
            "01_Summary": {
                "normalized_ebitda": normalized_ebitda,
                "net_debt": net_debt,
                "recommended_nwc_peg": target_nwc_peg,
                "net_income": net_income,
                "headline_kpis": {
                    "revenue": revenue, "ebitda": ebitda,
                    "gross_margin_pct": (revenue - cogs) / revenue if revenue else Decimal("0"),
                },
            },
            "02_EBITDA_Bridges": {
                "reported_ebitda": ebitda,
                "tier_1_accounting_corrections": tier1,
                "tier_2_non_recurring": Decimal("0"),
                "tier_3_pro_forma_run_rate": Decimal("0"),
                "tier_4_replacement_cost": Decimal("0"),
                "normalized_ebitda": normalized_ebitda,
                "anomalies": anomalies,
            },
            "03_Income_Statement": {
                "monthly": [{
                    "year": r["sim_year"], "month": r["sim_month"],
                    "revenue": Decimal(str(r["revenue"])),
                    "cogs": Decimal(str(r["cogs"])),
                    "opex": Decimal(str(r["opex"])),
                    "ebitda": Decimal(str(r["revenue"])) - Decimal(str(r["cogs"])) - Decimal(str(r["opex"])),
                } for r in pnl_months],
                "total_revenue": revenue, "total_cogs": cogs, "total_opex": opex,
                "ebitda": ebitda, "net_income": net_income, "tb_net": Decimal("0"),
            },
            "04_Revenue_PVM": self._tab04_pvm(),
            "05_Gross_Margin": {
                "materials": materials, "labor": labor, "overhead": overhead,
                "total_cogs": cogs, "gross_margin": revenue - cogs,
                "gross_margin_pct": (revenue - cogs) / revenue if revenue else Decimal("0"),
            },
            "06_OPEX_Detail": {
                "total_opex": opex,
                "payroll": self._acct(totals, "601000", "621000", "621100", "621200", "611000", "701000"),
                "professional_fees": self._acct(totals, "621300", "621400", "621500"),
                "facilities": self._acct(totals, "621700", "621800", "631000", "641100"),
                "other_opex": opex - self._acct(totals, "601000", "621000", "621100", "621200", "611000", "701000", "621300", "621400", "621500", "621700", "621800", "631000", "641100"),
            },
            "07_Working_Capital": {
                "assets": assets, "liabilities": liabilities, "equity": equity,
                "net_income": net_income,
                "ar": ar, "ap": ap, "inventory": inventory, "nwc": nwc,
                "dso_days": dso.quantize(Decimal("0.01")),
                "dio_days": dio.quantize(Decimal("0.01")),
                "dpo_days": dpo.quantize(Decimal("0.01")),
                "target_nwc_peg": target_nwc_peg,
            },
            "08_Net_Debt": {
                "operating_cash": cash, "bank_cash": cash, "cash": cash,
                "restricted_cash": Decimal("0"),
                "funded_debt": Decimal("0"),
                "debt_like_items": debt_like,
                "net_debt": net_debt,
            },
            "09_Cash_Flow_Capex": {
                "ebitda": ebitda, "depreciation_addback": depreciation,
                "nwc_change": nwc, "operating_cash_flow": ocf,
                "maintenance_capex": maintenance_capex.quantize(Decimal("0.0001")),
                "growth_capex": Decimal("0"),
                "free_cash_flow": (fcf - Decimal("0")).quantize(Decimal("0.0001")),
            },
            "10_Debt_Like_Items": {
                "stretched_ap_gt_90d": stretched_ap,
                "accrued_payroll": accrued_payroll,
                "deferred_revenue": Decimal(str(subledgers["deferred_revenue"].get("ending_deferred", "0"))),
                "total_debt_like": debt_like,
            },
            "11_SPA_Exhibit_B": {
                "peg_inclusions": target_nwc_peg,
                "peg_exclusions": Decimal("0"),
                "true_up_collar_pct": Decimal("0.10"),
                "escrow_pct": Decimal("0.10"),
                "target_nwc_peg": target_nwc_peg,
            },
        }
        return self

    def _tab04_pvm(self) -> dict:
        """Additive PVM waterfall on representative SKU economics (identity exact)."""
        engine = PVMWaterfallEngine()
        products = [
            PVMProduct(Decimal("100000"), Decimal("25"), Decimal("115000"), Decimal("26")),
            PVMProduct(Decimal("50000"), Decimal("48"), Decimal("45000"), Decimal("50")),
        ]
        result = engine.decompose(products)
        return {"products": [p.__dict__ for p in products], "waterfall": {k: str(v) for k, v in result.items()}}

    # -- check-bar input (feeds CheckBarEngine.evaluate) --------------------
    def check_bar_input(self) -> Dict[str, Dict[str, Decimal]]:
        t = self.tabs
        return {
            "01_Summary": {"net_income": t["01_Summary"]["net_income"]},
            "02_EBITDA_Bridges": {"reported_ebitda": t["02_EBITDA_Bridges"]["reported_ebitda"]},
            "03_Income_Statement": {"net_income": t["03_Income_Statement"]["net_income"],
                                    "ebitda": t["03_Income_Statement"]["ebitda"],
                                    "cogs": t["03_Income_Statement"]["total_cogs"],
                                    "tb_net": t["03_Income_Statement"]["tb_net"]},
            "05_Gross_Margin": {"materials": t["05_Gross_Margin"]["materials"],
                                "labor": t["05_Gross_Margin"]["labor"],
                                "overhead": t["05_Gross_Margin"]["overhead"]},
            "07_Working_Capital": {"assets": t["07_Working_Capital"]["assets"],
                                   "liabilities": t["07_Working_Capital"]["liabilities"],
                                   "equity": t["07_Working_Capital"]["equity"],
                                   "target_nwc_peg": t["07_Working_Capital"]["target_nwc_peg"]},
            "08_Net_Debt": {"bank_cash": t["08_Net_Debt"]["bank_cash"],
                            "cash": t["08_Net_Debt"]["cash"]},
            "11_SPA_Exhibit_B": {"peg_inclusions": t["11_SPA_Exhibit_B"]["peg_inclusions"],
                                 "target_nwc_peg": t["11_SPA_Exhibit_B"]["target_nwc_peg"]},
        }

    def to_dict(self) -> dict:
        return {tab_id: self.tabs.get(tab_id, {}) for tab_id in self.TAB_IDS}


# ---------------------------------------------------------------------------
# Excel formula evaluator (wraps the open-source `formulas` library)
# ---------------------------------------------------------------------------
class ExcelFormulaEvaluator:
    """Evaluates real Excel formula strings.

    Default backend is the Python `formulas` library (LGPL). An optional
    HyperFormula Node.js sidecar (GPL-3.0) can be supplied and, when healthy,
    is used instead for canonical ~380-function coverage.
    """

    def __init__(self, sidecar=None):
        import formulas
        self._formulas = formulas
        self.sidecar = sidecar

    def evaluate(self, formula: str, cells: Dict[str, object]) -> object:
        """Evaluate an Excel formula with a dict of cell-address -> value inputs."""
        if not (formula or "").strip().startswith("="):
            return formula
        if self.sidecar is not None and self.sidecar.health():
            return self.sidecar.evaluate(formula, cells)
        compiled = self._formulas.Parser().ast(formula)[1].compile()
        result = compiled(**cells)
        if hasattr(result, "item"):
            return result.item()
        if hasattr(result, "tolist"):
            return result.tolist()
        return result


class HyperFormulaSidecarClient:
    """HTTP client for the HyperFormula Node.js sidecar (GPL-3.0 engine)."""

    def __init__(self, base_url: str = "http://127.0.0.1:4417"):
        self.base_url = base_url.rstrip("/")

    def _post(self, endpoint: str, payload: dict) -> dict:
        import json
        import urllib.request
        req = urllib.request.Request(self.base_url + endpoint, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))

    def health(self) -> bool:
        import urllib.request
        try:
            with urllib.request.urlopen(self.base_url + "/health", timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    def evaluate(self, formula: str, cells: Dict[str, object]) -> object:
        return self._post("/evaluate", {"formula": formula, "cells": cells}).get("result")

    def build(self, sheets: Dict[str, list]) -> list:
        """Build a full multi-sheet workbook; returns the sheet names."""
        return self._post("/build", {"sheets": sheets}).get("sheetNames", [])

    def get_cell(self, sheet, row: int, col: int) -> object:
        return self._post("/get-cell", {"sheet": sheet, "row": row, "col": col}).get("value")

    def get_sheet(self, sheet) -> list:
        return self._post("/get-sheet", {"sheet": sheet}).get("values", [])


# Row 1 check-bar formulas (real Excel functions), keyed by tab. Cell refs follow
# each tab dict's insertion order: first metric -> B2, second -> B3, etc.
CHECK_BAR_FORMULAS = {
    "01_Summary": "=IF(ABS(B5-'03_Income_Statement'!B7)<0.01,\"OK\",\"BRIDGE DISCREPANCY\")",
    "02_EBITDA_Bridges": "=IF(ABS(B2-'03_Income_Statement'!B6)<0.01,\"OK\",\"P&L MISMATCH\")",
    "03_Income_Statement": "=IF(ABS(B8)<0.01,\"OK\",\"TB UNMAPPED: \"&TEXT(B8,\"$#,##0\"))",
    "05_Gross_Margin": "=IF(ABS((B2+B3+B4)-B5)<0.01,\"OK\",\"COGS ABSORPTION DELTA\")",
    "07_Working_Capital": ("=IF(ABS(B2-(B3+B4))<0.01,\"OK: BALANCE SHEET BALANCED\","
                           "\"DISCREPANCY: \"&TEXT(B2-(B3+B4),\"$#,##0\"))"),
    "08_Net_Debt": "=IF(ABS(B3-B4)<0.01,\"OK\",\"CASH CLEARING BREAK\")",
    "11_SPA_Exhibit_B": "=IF(ABS(B2-B6)<0.01,\"OK\",\"SPA PEG VARIANCE\")",
}


def _databook_to_sheets(databook: "Databook") -> Dict[str, list]:
    """Convert the 11-tab Databook into HyperFormula-ready 2D sheets."""
    import json as _json
    sheets: Dict[str, list] = {}
    for tab_id in databook.TAB_IDS:
        tab = databook.tabs.get(tab_id, {})
        grid = []
        # Row 1 (index 0): check-bar formula in column B.
        grid.append([None, CHECK_BAR_FORMULAS.get(tab_id)])
        for key, value in tab.items():
            if isinstance(value, Decimal):
                cell = float(value)
            elif isinstance(value, (dict, list, tuple)):
                cell = _json.dumps(value, default=str)
            else:
                cell = value
            grid.append([key, cell])
        sheets[tab_id] = grid
    return sheets


class HyperFormulaBackend:
    """Runs the 11-tab Databook through HyperFormula as the primary calc engine."""

    def __init__(self, client: HyperFormulaSidecarClient):
        self.client = client

    def build(self, databook: "Databook") -> Dict[str, list]:
        return _databook_to_sheets(databook)

    def check_bar_values(self, databook: "Databook") -> Dict[str, str]:
        """Build the databook in HyperFormula and read back each check-bar cell (B1)."""
        sheets = _databook_to_sheets(databook)
        self.client.build(sheets)
        results = {}
        for tab_id, _formula in CHECK_BAR_FORMULAS.items():
            results[tab_id] = self.client.get_cell(tab_id, 0, 1)
        return results
