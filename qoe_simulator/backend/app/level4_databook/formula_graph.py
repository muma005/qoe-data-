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
