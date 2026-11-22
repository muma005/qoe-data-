"""
QoE Simulator - Level 4: Row 1 Dual-Tier Check Bars and Universal RGB Modeling
Hygiene Linter (04_financial_databook_and_calculation_engine.md, Sections 3-4).

  - Universal RGB font color coding (Blue/Black/Green/Red/Purple).
  - Strict modeling hygiene linter rules (ML01 embedded constants, ML02 dynamic
    aggregations, ML03 external links).
  - Row 1 check-bar engine: per-tab mathematical assertions with red/green status.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

from .formula_graph import CheckBarStatus, _money


# ---------------------------------------------------------------------------
# Universal RGB font color coding (spec Section 3)
# ---------------------------------------------------------------------------
RGB = {
    "BLUE": "#0000FF",     # hardcoded inputs & assumptions
    "BLACK": "#000000",    # intra-sheet formulas
    "GREEN": "#008000",    # inter-sheet / cross-tab references
    "RED": "#FF0000",      # check-bar flags & warnings
    "PURPLE": "#800080",   # external ERP links
}

RGB_USAGE = {
    RGB["BLUE"]: "Hardcoded Inputs & Base Assumptions",
    RGB["BLACK"]: "Formulas & Intra-Sheet References",
    RGB["GREEN"]: "Inter-Sheet / Cross-Tab References",
    RGB["RED"]: "Check Bar Flags & System Warnings",
    RGB["PURPLE"]: "External System Links / Raw ERP Dumps",
}


# ---------------------------------------------------------------------------
# Modeling hygiene linter (ML01 / ML02 / ML03)
# ---------------------------------------------------------------------------
class ModelingHygieneLinter:
    """Flags formula-level hygiene violations (spec Section 3.1)."""

    def lint(self, formula: str) -> List[str]:
        violations: List[str] = []
        f = formula or ""
        if f.startswith("="):
            body = f[1:]
            # ML01: embedded numeric constants (a digit not part of a cell ref like "A1")
            if re.search(r"(?<![A-Za-z_])\d", body):
                violations.append("ML01: embedded numeric constant in formula")
            # ML02: manual point-and-click aggregation (3+ direct refs summed)
            refs = re.findall(r"\b[A-Za-z]+\d+\b", body)
            if len(refs) >= 3:
                violations.append("ML02: use dynamic aggregation (SUMIFS/XLOOKUP), not point-and-click")
        # ML03: external workbook links
        if re.search(r"\[.*\.(xlsx|xlsm|xls)\]\w*!|\b[A-Za-z]:\\", f, re.IGNORECASE):
            violations.append("ML03: external workbook link is prohibited")
        return violations

    def font_color(self, formula: str) -> str:
        """Assign the structural font color for a cell's content."""
        f = (formula or "").strip()
        if not f.startswith("="):
            return RGB["BLUE"]  # hardcoded input
        if re.search(r"\[.*\]!|\b[A-Za-z]:\\", f, re.IGNORECASE):
            return RGB["PURPLE"]
        if "!" in f:  # cross-tab reference
            return RGB["GREEN"]
        return RGB["BLACK"]


# ---------------------------------------------------------------------------
# Row 1 check-bar engine (spec Section 4)
# ---------------------------------------------------------------------------
@dataclass
class CheckBarResult:
    tab_id: str
    status: CheckBarStatus
    imbalance_amount: Decimal = Decimal("0")
    failure_diagnostic: str = ""

    def to_dict(self) -> dict:
        return {
            "tab_id": self.tab_id,
            "status": self.status.value,
            "imbalance_amount": float(self.imbalance_amount),
            "failure_diagnostic": self.failure_diagnostic,
        }


class CheckBarEngine:
    """Evaluates the dual-tier Row 1 check bars across all databook tabs."""

    # (tab_id, metric) -> assertion over a Databook snapshot
    def evaluate(self, databook: Dict[str, Dict[str, Decimal]]) -> List[CheckBarResult]:
        results: List[CheckBarResult] = []
        results.append(self._check_01_summary(databook))
        results.append(self._check_02_ebitda_bridge(databook))
        results.append(self._check_03_income_statement(databook))
        results.append(self._check_05_gross_margin(databook))
        results.append(self._check_07_working_capital(databook))
        results.append(self._check_08_net_debt(databook))
        results.append(self._check_11_spa_exhibit(databook))
        return results

    def _result(self, tab_id: str, ok: bool, delta: Decimal, fail_msg: str) -> CheckBarResult:
        return CheckBarResult(
            tab_id=tab_id,
            status=CheckBarStatus.CHECK_PASS if ok else CheckBarStatus.CHECK_FAIL,
            imbalance_amount=delta,
            failure_diagnostic="" if ok else fail_msg,
        )

    def _check_01_summary(self, db: Dict[str, Dict[str, Decimal]]) -> CheckBarResult:
        bridge_ni = self._get(db, "01_Summary", "net_income")
        pnl_ni = self._get(db, "03_Income_Statement", "net_income")
        delta = bridge_ni - pnl_ni
        return self._result("01_Summary", delta == 0, delta, "BRIDGE DISCREPANCY")

    def _check_02_ebitda_bridge(self, db: Dict[str, Dict[str, Decimal]]) -> CheckBarResult:
        bridge = self._get(db, "02_EBITDA_Bridges", "reported_ebitda")
        pnl = self._get(db, "03_Income_Statement", "ebitda")
        delta = bridge - pnl
        return self._result("02_EBITDA_Bridges", delta == 0, delta, f"P&L MISMATCH: ${delta}")

    def _check_03_income_statement(self, db: Dict[str, Dict[str, Decimal]]) -> CheckBarResult:
        tb_net = self._get(db, "03_Income_Statement", "tb_net")
        return self._result("03_Income_Statement", tb_net == 0, tb_net, f"TB UNMAPPED: ${tb_net}")

    def _check_05_gross_margin(self, db: Dict[str, Dict[str, Decimal]]) -> CheckBarResult:
        components = (self._get(db, "05_Gross_Margin", "materials")
                      + self._get(db, "05_Gross_Margin", "labor")
                      + self._get(db, "05_Gross_Margin", "overhead"))
        total_cogs = self._get(db, "03_Income_Statement", "cogs")
        delta = components - total_cogs
        return self._result("05_Gross_Margin", delta == 0, delta, "COGS ABSORPTION DELTA")

    def _check_07_working_capital(self, db: Dict[str, Dict[str, Decimal]]) -> CheckBarResult:
        assets = self._get(db, "07_Working_Capital", "assets")
        liabilities = self._get(db, "07_Working_Capital", "liabilities")
        equity = self._get(db, "07_Working_Capital", "equity")
        delta = assets - (liabilities + equity)
        return self._result("07_Working_Capital", delta == 0, delta, "BALANCE SHEET UNBALANCED")

    def _check_08_net_debt(self, db: Dict[str, Dict[str, Decimal]]) -> CheckBarResult:
        bank = self._get(db, "08_Net_Debt", "bank_cash")
        cash = self._get(db, "08_Net_Debt", "cash")
        delta = bank - cash
        return self._result("08_Net_Debt", delta == 0, delta, "CASH CLEARING BREAK")

    def _check_11_spa_exhibit(self, db: Dict[str, Dict[str, Decimal]]) -> CheckBarResult:
        inclusions = self._get(db, "11_SPA_Exhibit_B", "peg_inclusions")
        target = self._get(db, "07_Working_Capital", "target_nwc_peg")
        delta = inclusions - target
        return self._result("11_SPA_Exhibit_B", delta == 0, delta, "SPA PEG VARIANCE")

    @staticmethod
    def _get(db: Dict[str, Dict[str, Decimal]], tab: str, metric: str) -> Decimal:
        return db.get(tab, {}).get(metric, Decimal("0"))
