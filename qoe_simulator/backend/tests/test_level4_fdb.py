"""
Test harness for Level 4: Financial Databook (FDB) & Analytical Calculation Engine.

Validates the DAG/topological sort + cycle detection, additive PVM waterfall,
replacement-cost doctrine, anti-double-dipping checker, Row 1 check bars, modeling
hygiene linter, sandboxed worker, and the proto-contract for fdb_calc.proto.
"""

import os
import re
import sys
import tempfile
import unittest
from decimal import Decimal

from app.level4_databook.formula_graph import (
    CheckBarStatus,
    Cell,
    Databook,
    DoubleDipChecker,
    ExcelFormulaEvaluator,
    FormulaGraph,
    PVMProduct,
    PVMWaterfallEngine,
    ReplacementCostEngine,
)
from app.level4_databook.check_bars import (
    CheckBarEngine,
    ModelingHygieneLinter,
)
from app.level4_databook.sandbox_worker import (
    FdbCalculationService,
    SandboxWorker,
    XLSXSerializer,
)


class TestFormulaGraph(unittest.TestCase):
    def test_topological_sort(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "100"))
        g.add_cell(Cell("T", "A2", "200"))
        g.add_cell(Cell("T", "A3", "=A1+A2", dependencies=[("T", "A1"), ("T", "A2")]))
        order = g.topological_sort()
        self.assertEqual(set(order), {("T", "A1"), ("T", "A2"), ("T", "A3")})
        self.assertLess(order.index(("T", "A1")), order.index(("T", "A3")))

    def test_evaluate_simple_arithmetic(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "100"))
        g.add_cell(Cell("T", "A2", "200"))
        g.add_cell(Cell("T", "A3", "=A1+A2", dependencies=[("T", "A1"), ("T", "A2")]))
        g.evaluate()
        self.assertEqual(g.cells[("T", "A3")].evaluated_value, Decimal("300.0000"))

    def test_cycle_detection(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "=B1", dependencies=[("T", "B1")]))
        g.add_cell(Cell("T", "B1", "=A1", dependencies=[("T", "A1")]))
        cyclic = g.detect_cycles()
        self.assertEqual(set(cyclic), {("T", "A1"), ("T", "B1")})


class TestPVM(unittest.TestCase):
    def test_additive_identity_exact(self):
        engine = PVMWaterfallEngine()
        products = [
            PVMProduct(Decimal("100"), Decimal("10"), Decimal("120"), Decimal("11")),
            PVMProduct(Decimal("50"), Decimal("20"), Decimal("40"), Decimal("22")),
        ]
        r = engine.decompose(products)
        self.assertEqual(r["total_delta"], Decimal("200.0000"))
        self.assertEqual(r["price_effect"], Decimal("200.0000"))
        # Price + Volume + Mix == Delta (residual is sub-cent)
        self.assertLess(abs(r["residual"]), Decimal("0.001"))


class TestReplacementCost(unittest.TestCase):
    def test_net_adjustment_owner_comp(self):
        engine = ReplacementCostEngine()
        self.assertEqual(engine.net_adjustment(Decimal("750000"), Decimal("420000")),
                         Decimal("330000.0000"))

    def test_net_adjustment_capitalized_rnd(self):
        engine = ReplacementCostEngine()
        self.assertEqual(engine.net_adjustment(Decimal("650000"), Decimal("480000")),
                         Decimal("170000.0000"))


class TestDoubleDip(unittest.TestCase):
    def test_double_dipping_detected(self):
        checker = DoubleDipChecker()
        checker.register_deduction("NET_DEBT_ITEM_12", "201000", "NET_DEBT")
        r = checker.validate("HC_INV_01", "201000", "EBITDA_HAIRCUT")
        self.assertTrue(r["is_double_dipping"])
        self.assertEqual(r["conflicting_deduction_id"], "NET_DEBT_ITEM_12")
        self.assertIn("Mutual Exclusivity", r["legal_doctrine_rule"])

    def test_no_double_dipping(self):
        checker = DoubleDipChecker()
        checker.register_deduction("NET_DEBT_ITEM_12", "201000", "NET_DEBT")
        r = checker.validate("HC_INV_01", "301000", "EBITDA_HAIRCUT")
        self.assertFalse(r["is_double_dipping"])


class TestCheckBars(unittest.TestCase):
    def _balanced_db(self):
        return {
            "01_Summary": {"net_income": Decimal("2000000")},
            "02_EBITDA_Bridges": {"reported_ebitda": Decimal("8200000")},
            "03_Income_Statement": {"net_income": Decimal("2000000"),
                                    "ebitda": Decimal("8200000"),
                                    "cogs": Decimal("30000000"),
                                    "tb_net": Decimal("0")},
            "05_Gross_Margin": {"materials": Decimal("12000000"), "labor": Decimal("9000000"),
                                "overhead": Decimal("9000000")},
            "07_Working_Capital": {"assets": Decimal("15000000"),
                                   "liabilities": Decimal("6000000"),
                                   "equity": Decimal("9000000"),
                                   "target_nwc_peg": Decimal("5000000")},
            "08_Net_Debt": {"bank_cash": Decimal("1200000"), "cash": Decimal("1200000")},
            "11_SPA_Exhibit_B": {"peg_inclusions": Decimal("5000000")},
        }

    def test_all_check_bars_pass(self):
        engine = CheckBarEngine()
        results = engine.evaluate(self._balanced_db())
        self.assertTrue(all(r.status == CheckBarStatus.CHECK_PASS for r in results))

    def test_balance_sheet_break_detected(self):
        db = self._balanced_db()
        db["07_Working_Capital"]["assets"] = Decimal("15310000")  # $310k break
        engine = CheckBarEngine()
        results = engine.evaluate(db)
        tab07 = next(r for r in results if r.tab_id == "07_Working_Capital")
        self.assertEqual(tab07.status, CheckBarStatus.CHECK_FAIL)
        self.assertEqual(tab07.imbalance_amount, Decimal("310000.0000"))


class TestLinter(unittest.TestCase):
    def setUp(self):
        self.linter = ModelingHygieneLinter()

    def test_ml01_embedded_constant(self):
        self.assertTrue(any("ML01" in v for v in self.linter.lint("=C14*1.08 + 50000")))

    def test_no_ml01_for_cell_refs(self):
        self.assertFalse(any("ML01" in v for v in self.linter.lint("=A1+B2")))

    def test_ml03_external_link(self):
        self.assertTrue(any("ML03" in v for v in self.linter.lint("='[C:\\Files\\Budget.xlsx]Sheet1'!A1")))

    def test_font_colors(self):
        self.assertEqual(self.linter.font_color("100"), "#0000FF")      # hardcoded -> blue
        self.assertEqual(self.linter.font_color("=A1+A2"), "#000000")   # intra-sheet -> black
        self.assertEqual(self.linter.font_color("=Tab!A1"), "#008000")  # cross-tab -> green


class TestSandboxWorker(unittest.TestCase):
    def test_circular_reference_isolated(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "=B1", dependencies=[("T", "B1")]))
        g.add_cell(Cell("T", "B1", "=A1", dependencies=[("T", "A1")]))
        worker = SandboxWorker()
        result = worker.run(g, [])
        self.assertFalse(result["success"])
        self.assertEqual(set(result["circular_cells"]), {("T", "A1"), ("T", "B1")})
        self.assertEqual(g.cells[("T", "A1")].error_flag, "#CIRCULAR!")

    def test_rollback_on_timeout(self):
        state = {"n": 0}

        def clock():
            state["n"] += 1
            return 0.0 if state["n"] == 1 else 10.0  # 10.0s -> 10000ms > 500ms quota

        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "100"))
        worker = SandboxWorker(timeout_ms=500, clock=clock)
        result = worker.run(g, [])
        self.assertFalse(result["success"])
        self.assertTrue(result["rolled_back"])


class TestFdbCalculationService(unittest.TestCase):
    def test_recalculate_batch_response_shape(self):
        svc = FdbCalculationService()
        svc.graph.add_cell(Cell("01_Summary", "A1", "100"))
        svc.graph.add_cell(Cell("01_Summary", "A2", "200"))
        svc.graph.add_cell(Cell("01_Summary", "A3", "=A1+A2",
                                dependencies=[("01_Summary", "A1"), ("01_Summary", "A2")]))
        r = svc.recalculate_batch("sim1", [{"tab_id": "01_Summary", "cell_coordinate": "A3",
                                            "formula_or_value": "=A1+A2"}], False)
        self.assertTrue(r["success"])
        for field in ("success", "calculation_time_ms", "dirty_cells", "check_bar_results"):
            self.assertIn(field, r)

    def test_validate_anti_double_dipping(self):
        svc = FdbCalculationService()
        r1 = svc.validate_anti_double_dipping("sim1", "NET_DEBT_ITEM_12", "201000", 250000, "NET_DEBT")
        self.assertFalse(r1["is_double_dipping"])
        r2 = svc.validate_anti_double_dipping("sim1", "HC_INV_01", "201000", 250000, "EBITDA_HAIRCUT")
        self.assertTrue(r2["is_double_dipping"])


class TestDatabook(unittest.TestCase):
    """Builds the 11-tab Databook from a real Level 2 .csp package and validates check bars."""

    @classmethod
    def _compiler_dir(cls) -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenarios", "compiler")

    def _build_package(self) -> str:
        compiler = self._compiler_dir()
        if compiler not in sys.path:
            sys.path.insert(0, compiler)
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        tmp = tempfile.mkdtemp()
        profile = SCENARIO_PROFILES["target_apex_supply"]
        result = compile_scenario(profile, 3, 42, tmp)
        return result["package_dir"]

    def test_databook_builds_all_eleven_tabs(self):
        pkg = self._build_package()
        databook = Databook().build(pkg)
        for tab_id in Databook.TAB_IDS:
            self.assertIn(tab_id, databook.tabs, tab_id)

    def test_databook_check_bars_all_pass(self):
        pkg = self._build_package()
        databook = Databook().build(pkg)
        engine = CheckBarEngine()
        results = engine.evaluate(databook.check_bar_input())
        failing = [r.tab_id for r in results if r.status != CheckBarStatus.CHECK_PASS]
        self.assertEqual(failing, [], f"check bars failed: {failing}")

    def test_databook_ebitda_bridge_normalizes(self):
        pkg = self._build_package()
        databook = Databook().build(pkg)
        bridge = databook.tabs["02_EBITDA_Bridges"]
        reported = bridge["reported_ebitda"]
        normalized = bridge["normalized_ebitda"]
        # SR-B01 anomaly is a haircut, so normalized EBITDA < reported EBITDA
        self.assertLess(normalized, reported)

    def test_databook_income_statement_monthly(self):
        pkg = self._build_package()
        databook = Databook().build(pkg)
        monthly = databook.tabs["03_Income_Statement"]["monthly"]
        self.assertEqual(len(monthly), 36)  # 3 years
        self.assertTrue(all(m["ebitda"] == m["revenue"] - m["cogs"] - m["opex"] for m in monthly))


class TestExcelLayer(unittest.TestCase):
    """Verifies real Excel formulas (via `formulas`) and a native .xlsx (via openpyxl)."""

    def test_excel_formula_evaluator_spec_check_bar(self):
        import numpy as np
        evaluator = ExcelFormulaEvaluator()
        formula = ('=IF(MAX(ABS(C28:AN28 - (C52:AN52 + C68:AN68))) < 0.01, '
                   '"OK: BALANCE SHEET BALANCED", "DISCREPANCY")')
        cells = {
            "C28:AN28": np.full((1, 39), 100.0),
            "C52:AN52": np.full((1, 39), 60.0),
            "C68:AN68": np.full((1, 39), 40.0),
        }
        result = evaluator.evaluate(formula, cells)
        self.assertEqual(result, "OK: BALANCE SHEET BALANCED")

    def test_xlsx_export_produces_native_workbook(self):
        import openpyxl
        compiler = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenarios", "compiler")
        if compiler not in sys.path:
            sys.path.insert(0, compiler)
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        tmp = tempfile.mkdtemp()
        result = compile_scenario(SCENARIO_PROFILES["target_apex_supply"], 3, 42, tmp)
        databook = Databook().build(result["package_dir"])
        xlsx_path = os.path.join(tmp, "fdb.xlsx")
        XLSXSerializer().serialize(databook, xlsx_path)

        wb = openpyxl.load_workbook(xlsx_path)
        self.assertEqual(len(wb.sheetnames), 11)
        # Row 1 check bar contains a live Excel formula
        ws = wb["07_Working_Capital"]
        self.assertTrue(str(ws["B1"].value).startswith("=IF("))
        self.assertIn("BALANCE SHEET BALANCED", str(ws["B1"].value))

    def test_hyperformula_sidecar(self):
        import shutil
        import subprocess
        import time
        if shutil.which("node") is None:
            self.skipTest("Node.js not installed")
        from app.level4_databook.formula_graph import HyperFormulaSidecarClient

        node_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "node_sidecar")
        env = dict(os.environ, HF_PORT="4418")
        proc = subprocess.Popen(["node", "hyperformula_server.js"], cwd=node_dir, env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            client = HyperFormulaSidecarClient("http://127.0.0.1:4418")
            for _ in range(50):
                if client.health():
                    break
                time.sleep(0.1)
            self.assertTrue(client.health(), "sidecar did not become healthy")
            result = client.evaluate(
                '=IF(ABS(B2-(B3+B4))<0.01,"OK: BALANCE SHEET BALANCED","DISCREPANCY")',
                {"B2": 15000000, "B3": 6000000, "B4": 9000000})
            self.assertEqual(result, "OK: BALANCE SHEET BALANCED")
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


# ---------------------------------------------------------------------------
# Proto-contract helpers (parse fdb_calc.proto text; no proto edits)
# ---------------------------------------------------------------------------
def _proto_path() -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "proto", "fdb_calc.proto")


def _read_proto() -> str:
    with open(_proto_path(), encoding="utf-8") as f:
        return f.read()


def _parse_enum(text: str, enum_name: str) -> dict:
    m = re.search(r"enum\s+" + enum_name + r"\s*\{(.*?)\}", text, re.DOTALL)
    body = m.group(1)
    return {k: int(v) for k, v in re.findall(r"(\w+)\s*=\s*(\d+)\s*;", body)}


def _parse_service_rpcs(text: str) -> list:
    m = re.search(r"service\s+\w+\s*\{(.*?)\}", text, re.DOTALL)
    body = m.group(1)
    return re.findall(r"rpc\s+(\w+)\s*\(\s*(\w+)\s*\)\s*returns\s*\(\s*(\w+)\s*\)", body)


def _parse_message_fields(text: str) -> dict:
    messages = {}
    for name, body in re.findall(r"message\s+(\w+)\s*\{(.*?)\}", text, re.DOTALL):
        messages[name] = [f for f in re.findall(r"(\w+)\s*=\s*\d+\s*;", body)]
    return messages


class TestFdbProtoContract(unittest.TestCase):
    """Confirms Level 4 is wired to proto/fdb_calc.proto without editing the proto."""

    RPC_TO_METHOD = {
        "RecalculateBatch": "recalculate_batch",
        "ValidateAntiDoubleDipping": "validate_anti_double_dipping",
    }

    @classmethod
    def setUpClass(cls):
        cls.proto = _read_proto()
        cls.proto_enum = _parse_enum(cls.proto, "CheckBarStatus")
        cls.rpcs = _parse_service_rpcs(cls.proto)
        cls.messages = _parse_message_fields(cls.proto)

    def test_check_bar_status_enum_matches_proto(self):
        py_enum = {e.name: e.value for e in CheckBarStatus}
        self.assertEqual(py_enum, self.proto_enum)

    def test_service_rpcs_have_python_methods(self):
        svc = FdbCalculationService()
        for rpc_name, _req, _resp in self.rpcs:
            self.assertTrue(hasattr(svc, self.RPC_TO_METHOD[rpc_name]), rpc_name)

    def test_response_fields_align_with_proto(self):
        svc = FdbCalculationService()
        for rpc_name, _req, resp_msg in self.rpcs:
            method = self.RPC_TO_METHOD[rpc_name]
            result = self._call(svc, method)
            expected_fields = self.messages[resp_msg]
            self.assertTrue(expected_fields, f"no fields parsed for {resp_msg}")
            for field in expected_fields:
                self.assertIn(field, result, f"{rpc_name} response missing field '{field}'")

    def _call(self, svc, method):
        if method == "recalculate_batch":
            return svc.recalculate_batch("sim1", [], True)
        if method == "validate_anti_double_dipping":
            return svc.validate_anti_double_dipping("sim1", "HC_1", "201000", 250000, "NET_DEBT")
        raise AssertionError(f"unknown method {method}")


if __name__ == "__main__":
    unittest.main()
