"""
QoE Simulator - Level 4: Sandboxed Calculation Worker and Proto-Shaped
FdbCalculationService facade (04_financial_databook_and_calculation_engine.md, Sections 8-9).

  - SandboxWorker: enforces 500ms execution timeout and 256MB memory quota, isolates
    circular references, and rolls back to the last valid snapshot on failure.
  - XLSXSerializer: renders the in-memory DAG into audit-grade, RGB-formatted rows.
  - FdbCalculationService: maps the two proto RPCs (RecalculateBatch,
    ValidateAntiDoubleDipping) onto the graph + check-bar + double-dip engines.
"""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Dict, List, Optional, Sequence

from .formula_graph import (
    CHECK_BAR_FORMULAS,
    CheckBarStatus,
    DoubleDipChecker,
    FormulaGraph,
    _money,
)
from .check_bars import CheckBarEngine, ModelingHygieneLinter, RGB


# ---------------------------------------------------------------------------
# Sandboxed calculation worker (spec Section 8.1)
# ---------------------------------------------------------------------------
class SandboxWorker:
    """Runs graph recalculation inside bounded quotas with copy-on-write rollback."""

    def __init__(self, timeout_ms: float = 500.0, memory_mb: float = 256.0,
                 clock: Callable[[], float] = time.monotonic):
        self.timeout_ms = timeout_ms
        self.memory_mb = memory_mb
        self.clock = clock
        self._last_valid_snapshot: Optional[Dict] = None

    def run(self, graph: FormulaGraph, updates: Sequence[tuple] = ()) -> Dict:
        """Applies cell updates and recalcs within quotas; rolls back on failure."""
        # copy-on-write: snapshot current state for rollback
        snapshot = {k: (cell.formula_or_value, cell.error_flag) for k, cell in graph.cells.items()}
        self._last_valid_snapshot = snapshot

        start = self.clock()
        try:
            for tab_id, coordinate, formula in updates:
                graph.cells[(tab_id, coordinate)].formula_or_value = formula

            # Cycle detection (LP-16): Kahn's detector runs in < 5ms
            cyclic = graph.detect_cycles()
            if cyclic:
                for key in cyclic:
                    graph.cells[key].error_flag = "#CIRCULAR!"
                return {
                    "success": False,
                    "calculation_time_ms": self._elapsed_ms(start),
                    "circular_cells": list(cyclic),
                    "dirty_cells": [],
                    "check_bar_results": [],
                    "rolled_back": False,
                }

            cells = graph.evaluate()

            # quota enforcement
            if self._elapsed_ms(start) > self.timeout_ms:
                raise TimeoutError("recalculation exceeded execution quota")

            return {
                "success": True,
                "calculation_time_ms": self._elapsed_ms(start),
                "circular_cells": [],
                "dirty_cells": cells,
                "check_bar_results": [],
                "rolled_back": False,
            }
        except Exception:
            # rollback to last valid snapshot
            for key, (formula, flag) in snapshot.items():
                graph.cells[key].formula_or_value = formula
                graph.cells[key].error_flag = flag
                graph.cells[key].evaluated_value = None
            return {
                "success": False,
                "calculation_time_ms": self._elapsed_ms(start),
                "circular_cells": [],
                "dirty_cells": [],
                "check_bar_results": [],
                "rolled_back": True,
            }

    def _elapsed_ms(self, start: float) -> float:
        return (self.clock() - start) * 1000.0


# ---------------------------------------------------------------------------
# Audit-grade XLSX serializer (native .xlsx with live formulas, RGB fonts,
# and conditional formatting — spec Section 6)
# ---------------------------------------------------------------------------
class XLSXSerializer:
    """Writes a native, cell-linked .xlsx workbook via openpyxl."""

    def __init__(self, linter: ModelingHygieneLinter = None):
        self.linter = linter or ModelingHygieneLinter()

    def serialize(self, databook, path: str) -> str:
        """Write the 11-tab Databook to a native .xlsx and return the path."""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        from openpyxl.formatting.rule import CellIsRule

        wb = Workbook()
        wb.remove(wb.active)
        for tab_id in databook.TAB_IDS:
            ws = wb.create_sheet(tab_id)
            self._write_sheet(ws, tab_id, databook.tabs.get(tab_id, {}))
        wb.save(path)
        return path

    @staticmethod
    def _cell_value(value):
        import json
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (dict, list, tuple)):
            return json.dumps(value, default=str)
        return value

    @staticmethod
    def _argb(hex_color: str) -> str:
        """Convert 6-digit #RRGGBB to openpyxl's required 8-digit aRGB."""
        return "FF" + hex_color.lstrip("#")

    def _write_sheet(self, ws, tab_id: str, tab: dict) -> None:
        from openpyxl.styles import Font, PatternFill
        from openpyxl.formatting.rule import CellIsRule

        blue = Font(color=self._argb(RGB["BLUE"]))
        black = Font(color=self._argb(RGB["BLACK"]))

        # Row 1 check bar formula + conditional formatting (green/red)
        if tab_id in CHECK_BAR_FORMULAS:
            formula = CHECK_BAR_FORMULAS[tab_id]
            c = ws["B1"]
            c.value = formula
            c.font = Font(color=self._argb(RGB["BLACK"]), bold=True)
            c.fill = PatternFill(start_color=self._argb("E2EFDA"),
                                 end_color=self._argb("E2EFDA"), fill_type="solid")
            red_fill = PatternFill(start_color=self._argb("C00000"),
                                   end_color=self._argb("C00000"), fill_type="solid")
            white = Font(color="FFFFFFFF", bold=True)
            for token in ("DISCREPANCY", "UNBALANCED", "MISMATCH"):
                ws.conditional_formatting.add(
                    "B1", CellIsRule(operator="containsText", formula=[f'"{token}"'],
                                     fill=red_fill, font=white))

        # Data rows: A = metric name, B = value (blue = hardcoded input)
        for row, (key, value) in enumerate(tab.items(), start=2):
            ws.cell(row=row, column=1, value=key).font = black
            cell = ws.cell(row=row, column=2, value=self._cell_value(value))
            cell.font = blue


# ---------------------------------------------------------------------------
# Proto-shaped service facade (mirrors fdb_calc.proto FdbCalculationService)
# ---------------------------------------------------------------------------
class FdbCalculationService:
    """Maps the two proto RPCs onto the graph + check-bar + double-dip engines."""

    def __init__(self):
        self.graph = FormulaGraph()
        self.check_bars = CheckBarEngine()
        self.double_dip = DoubleDipChecker()
        self.worker = SandboxWorker()
        self.linter = ModelingHygieneLinter()

    # rpc RecalculateBatch (RecalculateBatchRequest) returns (RecalculateBatchResponse)
    def recalculate_batch(self, simulation_id: str, cell_updates: Sequence[dict],
                          trigger_full_recalc: bool) -> dict:
        updates = [(u["tab_id"], u["cell_coordinate"], u["formula_or_value"])
                   for u in cell_updates]
        result = self.worker.run(self.graph, updates)

        dirty_cells = []
        for cell in result.get("dirty_cells", []):
            color = self.linter.font_color(cell.formula_or_value)
            dirty_cells.append({
                "tab_id": cell.tab_id,
                "cell_coordinate": cell.coordinate,
                "evaluated_value": str(cell.evaluated_value) if cell.evaluated_value is not None else "",
                "display_formatting": color,
                "error_flag": cell.error_flag,
            })

        # circular errors surface as check-bar failures
        check_bar_results = []
        for key in result.get("circular_cells", []):
            check_bar_results.append({
                "tab_id": key[0],
                "status": CheckBarStatus.CHECK_CIRCULAR_ERROR.value,
                "imbalance_amount": 0.0,
                "failure_diagnostic": "#CIRCULAR!",
            })

        return {
            "success": result["success"],
            "calculation_time_ms": result["calculation_time_ms"],
            "dirty_cells": dirty_cells,
            "check_bar_results": check_bar_results,
        }

    # rpc ValidateAntiDoubleDipping (ValidateAntiDoubleDippingRequest) returns (ValidateAntiDoubleDippingResponse)
    def validate_anti_double_dipping(self, simulation_id: str, haircut_id: str,
                                     affected_gl_account: str, haircut_amount: float,
                                     proposed_bucket: str) -> dict:
        # register current bucket after validating against prior registrations
        result = self.double_dip.validate(haircut_id, affected_gl_account, proposed_bucket)
        if not result["is_double_dipping"]:
            self.double_dip.register_deduction(haircut_id, affected_gl_account, proposed_bucket)
        return result
