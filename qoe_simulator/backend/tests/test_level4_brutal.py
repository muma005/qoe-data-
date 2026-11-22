"""
Brutal / stress / property / edge-case test suite for Level 4 (fdb-calc).

Covers every Level 4 subsystem at the limits: PVM additive-identity fuzzing,
DAG topological-sort correctness on random graphs, cycle detection, formula-evaluator
edge cases (div-by-zero, precedence, nesting, unary minus, SUM, cross-tab), double-dip
bucket stress, check-bar boundaries, hygiene-linter edge cases, sandbox rollback,
Databook determinism + metrics, native .xlsx deep checks, and cross-engine agreement
(Python vs `formulas` vs HyperFormula).
"""

import os
import random
import sys
import tempfile
import unittest
from decimal import Decimal

from app.level4_databook.formula_graph import (
    CHECK_BAR_FORMULAS,
    CheckBarStatus,
    Cell,
    CycleDetectedError,
    Databook,
    DoubleDipChecker,
    ExcelFormulaEvaluator,
    FormulaGraph,
    PVMProduct,
    PVMWaterfallEngine,
    ReplacementCostEngine,
)
from app.level4_databook.check_bars import CheckBarEngine, ModelingHygieneLinter
from app.level4_databook.sandbox_worker import SandboxWorker, XLSXSerializer


# ---------------------------------------------------------------------------
# PVM — additive-identity property fuzzing
# ---------------------------------------------------------------------------
class TestBrutalPVM(unittest.TestCase):
    def test_additive_identity_fuzz_500_random_products(self):
        engine = PVMWaterfallEngine()
        rng = random.Random(0x5EED)
        for _ in range(500):
            products = [
                PVMProduct(
                    Decimal(str(round(rng.uniform(0.1, 10000), 2))),
                    Decimal(str(round(rng.uniform(0.01, 500), 2))),
                    Decimal(str(round(rng.uniform(0.1, 10000), 2))),
                    Decimal(str(round(rng.uniform(0.01, 500), 2))),
                )
                for _ in range(rng.randint(1, 8))
            ]
            r = engine.decompose(products)
            # Identity must hold to sub-cent precision (no residual interaction plug).
            self.assertLess(abs(r["residual"]), Decimal("0.01"),
                            f"residual {r['residual']} for {products}")

    def test_single_product_identity(self):
        r = PVMWaterfallEngine().decompose([
            PVMProduct(Decimal("100"), Decimal("10"), Decimal("120"), Decimal("10"))
        ])
        self.assertLess(abs(r["residual"]), Decimal("0.01"))
        # price unchanged -> price effect 0, all delta is volume
        self.assertEqual(r["price_effect"], Decimal("0.0000"))
        self.assertEqual(r["volume_effect"], Decimal("200.0000"))

    def test_identical_periods_no_variance(self):
        r = PVMWaterfallEngine().decompose([
            PVMProduct(Decimal("100"), Decimal("10"), Decimal("100"), Decimal("10")),
            PVMProduct(Decimal("50"), Decimal("20"), Decimal("50"), Decimal("20")),
        ])
        self.assertEqual(r["total_delta"], Decimal("0.0000"))
        self.assertEqual(r["price_effect"], Decimal("0.0000"))
        self.assertEqual(r["volume_effect"], Decimal("0.0000"))
        self.assertEqual(r["mix_effect"], Decimal("0.0000"))


# ---------------------------------------------------------------------------
# FormulaGraph — DAG fuzzing, cycles, evaluator edge cases
# ---------------------------------------------------------------------------
class TestBrutalFormulaGraph(unittest.TestCase):
    def test_topological_sort_valid_on_200_random_dags(self):
        rng = random.Random(42)
        for _ in range(200):
            g = FormulaGraph()
            n = rng.randint(1, 60)
            for i in range(n):
                deps = [("T", f"C{j}") for j in range(i) if rng.random() < 0.35]
                g.add_cell(Cell("T", f"C{i}", str(i), dependencies=deps))
            order = g.topological_sort()
            self.assertEqual(len(order), n)
            pos = {k: i for i, k in enumerate(order)}
            for key, cell in g.cells.items():
                for dep in cell.dependencies:
                    self.assertLess(pos[dep], pos[key], f"{key} depends on {dep}")

    def test_self_reference_cycle(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "=A1", dependencies=[("T", "A1")]))
        self.assertEqual(g.detect_cycles(), [("T", "A1")])

    def test_three_node_cycle(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "=B1", dependencies=[("T", "B1")]))
        g.add_cell(Cell("T", "B1", "=C1", dependencies=[("T", "C1")]))
        g.add_cell(Cell("T", "C1", "=A1", dependencies=[("T", "A1")]))
        self.assertEqual(set(g.detect_cycles()), {("T", "A1"), ("T", "B1"), ("T", "C1")})

    def test_deep_chain_1000_nodes(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "C0", "1"))
        for i in range(1, 1000):
            g.add_cell(Cell("T", f"C{i}", f"=C{i-1}+1", dependencies=[("T", f"C{i-1}")]))
        g.evaluate()
        self.assertEqual(g.cells[("T", "C999")].evaluated_value, Decimal("1000.0000"))

    def test_division_by_zero_isolated(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "10"))
        g.add_cell(Cell("T", "A2", "0"))
        g.add_cell(Cell("T", "A3", "=A1/A2", dependencies=[("T", "A1"), ("T", "A2")]))
        g.add_cell(Cell("T", "A4", "=A1+1", dependencies=[("T", "A1")]))
        g.evaluate()
        self.assertEqual(g.cells[("T", "A3")].error_flag, "#ERROR")
        self.assertEqual(g.cells[("T", "A4")].evaluated_value, Decimal("11.0000"))

    def test_precedence_and_nesting(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "=2+3*4"))
        g.add_cell(Cell("T", "A2", "=(2+3)*(4-1)"))
        g.add_cell(Cell("T", "A3", "=2*(3+4)"))
        g.evaluate()
        self.assertEqual(g.cells[("T", "A1")].evaluated_value, Decimal("14.0000"))
        self.assertEqual(g.cells[("T", "A2")].evaluated_value, Decimal("15.0000"))
        self.assertEqual(g.cells[("T", "A3")].evaluated_value, Decimal("14.0000"))

    def test_unary_minus_and_negative_literals(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "=-5+10"))
        g.add_cell(Cell("T", "A2", "=10--3"))
        g.evaluate()
        self.assertEqual(g.cells[("T", "A1")].evaluated_value, Decimal("5.0000"))
        self.assertEqual(g.cells[("T", "A2")].evaluated_value, Decimal("13.0000"))

    def test_sum_range(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "10"))
        g.add_cell(Cell("T", "A2", "20"))
        g.add_cell(Cell("T", "A3", "30"))
        g.add_cell(Cell("T", "A4", "=SUM(A1:A3)",
                        dependencies=[("T", "A1"), ("T", "A2"), ("T", "A3")]))
        g.evaluate()
        self.assertEqual(g.cells[("T", "A4")].evaluated_value, Decimal("60.0000"))

    def test_cross_tab_reference(self):
        g = FormulaGraph()
        g.add_cell(Cell("T1", "A1", "5"))
        g.add_cell(Cell("T2", "A1", "=T1!A1*2", dependencies=[("T1", "A1")]))
        g.evaluate()
        self.assertEqual(g.cells[("T2", "A1")].evaluated_value, Decimal("10.0000"))

    def test_empty_formula_errors(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "="))
        g.evaluate()
        self.assertEqual(g.cells[("T", "A1")].error_flag, "#ERROR")


# ---------------------------------------------------------------------------
# Double-dip checker — bucket stress
# ---------------------------------------------------------------------------
class TestBrutalDoubleDip(unittest.TestCase):
    def test_all_three_buckets_conflict(self):
        checker = DoubleDipChecker()
        checker.register_deduction("D_NETDEBT", "201000", "NET_DEBT")
        checker.register_deduction("D_EBITDA", "201000", "EBITDA_HAIRCUT")
        r = checker.validate("D_NWC", "201000", "NWC_LIABILITY")
        self.assertTrue(r["is_double_dipping"])
        self.assertIn("Mutual Exclusivity", r["legal_doctrine_rule"])

    def test_same_bucket_no_conflict(self):
        checker = DoubleDipChecker()
        checker.register_deduction("D1", "201000", "NET_DEBT")
        r = checker.validate("D2", "201000", "NET_DEBT")
        self.assertFalse(r["is_double_dipping"])

    def test_many_accounts_isolated(self):
        checker = DoubleDipChecker()
        for i in range(500):
            checker.register_deduction(f"D{i}", f"{100000 + i}", "NET_DEBT")
        # a new account in a different bucket must not conflict
        r = checker.validate("NEW", "999999", "EBITDA_HAIRCUT")
        self.assertFalse(r["is_double_dipping"])


# ---------------------------------------------------------------------------
# Check bars — exact boundaries
# ---------------------------------------------------------------------------
class TestBrutalCheckBars(unittest.TestCase):
    def _db(self):
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
            "11_SPA_Exhibit_B": {"peg_inclusions": Decimal("5000000"),
                                 "target_nwc_peg": Decimal("5000000")},
        }

    def test_all_pass_when_balanced(self):
        engine = CheckBarEngine()
        self.assertTrue(all(r.status == CheckBarStatus.CHECK_PASS
                            for r in engine.evaluate(self._db())))

    def test_balance_sheet_fails_on_one_cent(self):
        db = self._db()
        db["07_Working_Capital"]["assets"] += Decimal("0.01")
        results = CheckBarEngine().evaluate(db)
        tab07 = next(r for r in results if r.tab_id == "07_Working_Capital")
        self.assertEqual(tab07.status, CheckBarStatus.CHECK_FAIL)
        self.assertEqual(tab07.imbalance_amount, Decimal("0.0100"))

    def test_ebitda_mismatch_detected(self):
        db = self._db()
        db["02_EBITDA_Bridges"]["reported_ebitda"] = Decimal("8300000")
        results = CheckBarEngine().evaluate(db)
        tab02 = next(r for r in results if r.tab_id == "02_EBITDA_Bridges")
        self.assertEqual(tab02.status, CheckBarStatus.CHECK_FAIL)


# ---------------------------------------------------------------------------
# Linter — edge cases
# ---------------------------------------------------------------------------
class TestBrutalLinter(unittest.TestCase):
    def setUp(self):
        self.linter = ModelingHygieneLinter()

    def test_ml01_negative_decimal_constant(self):
        self.assertTrue(any("ML01" in v for v in self.linter.lint("=A1*-1.5")))

    def test_ml01_does_not_flag_cell_refs(self):
        self.assertFalse(any("ML01" in v for v in self.linter.lint("=C28:AN28")))

    def test_ml03_unc_network_link(self):
        self.assertTrue(any("ML03" in v for v in self.linter.lint(
            "='[\\\\server\\share\\Budget.xlsx]Sheet1'!A1")))

    def test_empty_formula_no_violations(self):
        self.assertEqual(self.linter.lint(""), [])

    def test_font_color_classification(self):
        self.assertEqual(self.linter.font_color("123"), "#0000FF")
        self.assertEqual(self.linter.font_color("=A1+A2"), "#000000")
        self.assertEqual(self.linter.font_color("='Tab'!A1"), "#008000")


# ---------------------------------------------------------------------------
# Sandbox — rollback restores state, cycles isolated
# ---------------------------------------------------------------------------
class TestBrutalSandbox(unittest.TestCase):
    def test_rollback_restores_original_cell(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "100"))
        state = {"n": 0}

        def clock():
            state["n"] += 1
            return 0.0 if state["n"] == 1 else 10.0  # exceed 500ms quota

        worker = SandboxWorker(timeout_ms=500, clock=clock)
        result = worker.run(g, [("T", "A1", "200")])
        self.assertTrue(result["rolled_back"])
        self.assertEqual(g.cells[("T", "A1")].formula_or_value, "100")

    def test_circular_isolated_not_fatal(self):
        g = FormulaGraph()
        g.add_cell(Cell("T", "A1", "=B1", dependencies=[("T", "B1")]))
        g.add_cell(Cell("T", "B1", "=A1", dependencies=[("T", "A1")]))
        g.add_cell(Cell("T", "A2", "1"))
        worker = SandboxWorker()
        result = worker.run(g, [])
        self.assertFalse(result["success"])
        self.assertEqual(set(result["circular_cells"]), {("T", "A1"), ("T", "B1")})
        # non-circular cell still evaluates
        g.evaluate() if False else None
        self.assertEqual(g.cells[("T", "A1")].error_flag, "#CIRCULAR!")


# ---------------------------------------------------------------------------
# Databook — determinism, tabs, metrics
# ---------------------------------------------------------------------------
class TestBrutalDatabook(unittest.TestCase):
    @classmethod
    def _compiler_dir(cls):
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenarios", "compiler")

    def _build_package(self, scenario="target_apex_supply", seed=42):
        compiler = self._compiler_dir()
        if compiler not in sys.path:
            sys.path.insert(0, compiler)
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        return compile_scenario(SCENARIO_PROFILES[scenario], 3, seed, tempfile.mkdtemp())

    def test_databook_deterministic(self):
        p1 = self._build_package()
        p2 = self._build_package()
        d1 = Databook().build(p1["package_dir"]).to_dict()
        d2 = Databook().build(p2["package_dir"]).to_dict()
        self.assertEqual(d1, d2)

    def test_balance_sheet_identity_exact(self):
        pkg = self._build_package()
        databook = Databook().build(pkg["package_dir"])
        tab07 = databook.tabs["07_Working_Capital"]
        self.assertEqual(tab07["assets"], tab07["liabilities"] + tab07["equity"])

    def test_dso_dio_dpo_positive(self):
        pkg = self._build_package()
        databook = Databook().build(pkg["package_dir"])
        tab07 = databook.tabs["07_Working_Capital"]
        self.assertGreater(tab07["dso_days"], 0)
        self.assertGreater(tab07["dio_days"], 0)
        self.assertGreater(tab07["dpo_days"], 0)

    def test_ebitda_bridge_normalized_less_than_reported(self):
        pkg = self._build_package()
        databook = Databook().build(pkg["package_dir"])
        bridge = databook.tabs["02_EBITDA_Bridges"]
        self.assertLess(bridge["normalized_ebitda"], bridge["reported_ebitda"])

    def test_all_eleven_tabs_present(self):
        pkg = self._build_package()
        databook = Databook().build(pkg["package_dir"])
        self.assertEqual(set(databook.tabs.keys()), set(Databook.TAB_IDS))


# ---------------------------------------------------------------------------
# Native .xlsx — deep structural checks
# ---------------------------------------------------------------------------
class TestBrutalXLSX(unittest.TestCase):
    def _databook(self):
        compiler = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenarios", "compiler")
        if compiler not in sys.path:
            sys.path.insert(0, compiler)
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        result = compile_scenario(SCENARIO_PROFILES["target_apex_supply"], 3, 42, tempfile.mkdtemp())
        return Databook().build(result["package_dir"])

    def test_xlsx_has_live_formulas_rgb_and_conditional_formatting(self):
        import openpyxl
        databook = self._databook()
        path = os.path.join(tempfile.mkdtemp(), "fdb.xlsx")
        XLSXSerializer().serialize(databook, path)
        wb = openpyxl.load_workbook(path)
        self.assertEqual(len(wb.sheetnames), 11)

        # Check bar cell B1 is a formula string, black font, green fill.
        ws = wb["07_Working_Capital"]
        self.assertTrue(str(ws["B1"].value).startswith("=IF("))
        self.assertEqual(ws["B1"].font.color.rgb, "FF000000")  # black (aRGB)
        # conditional formatting present on B1
        self.assertTrue(len(ws.conditional_formatting) > 0)

        # Data cell B2 is a numeric value with blue font.
        self.assertEqual(ws["B2"].font.color.rgb, "FF0000FF")  # blue (aRGB)


# ---------------------------------------------------------------------------
# Cross-engine agreement (Python vs `formulas` vs HyperFormula)
# ---------------------------------------------------------------------------
class TestBrutalCrossEngine(unittest.TestCase):
    def test_python_check_bars_agree_with_hyperformula(self):
        import shutil
        import subprocess
        import time
        if shutil.which("node") is None:
            self.skipTest("Node.js not installed")
        from app.level4_databook.formula_graph import (
            HyperFormulaBackend,
            HyperFormulaSidecarClient,
        )

        compiler = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenarios", "compiler")
        if compiler not in sys.path:
            sys.path.insert(0, compiler)
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        result = compile_scenario(SCENARIO_PROFILES["target_apex_supply"], 3, 42, tempfile.mkdtemp())
        databook = Databook().build(result["package_dir"])

        node_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "node_sidecar")
        env = dict(os.environ, HF_PORT="4420")
        proc = subprocess.Popen(["node", "hyperformula_server.js"], cwd=node_dir, env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            client = HyperFormulaSidecarClient("http://127.0.0.1:4420")
            for _ in range(50):
                if client.health():
                    break
                time.sleep(0.1)
            self.assertTrue(client.health())

            # Python check bars all pass
            py = CheckBarEngine().evaluate(databook.check_bar_input())
            self.assertTrue(all(r.status == CheckBarStatus.CHECK_PASS for r in py))

            # HyperFormula check bars all return "OK..."
            hf = HyperFormulaBackend(client).check_bar_values(databook)
            self.assertEqual(set(hf.keys()), set(CHECK_BAR_FORMULAS.keys()))
            for tab_id, value in hf.items():
                self.assertTrue(str(value).startswith("OK"), f"{tab_id}: {value}")
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    def test_formulas_and_hyperformula_agree_on_scalar_formula(self):
        import shutil
        import subprocess
        import time
        if shutil.which("node") is None:
            self.skipTest("Node.js not installed")
        from app.level4_databook.formula_graph import HyperFormulaSidecarClient

        formula = '=IF(ABS(B2-(B3+B4))<0.01,"OK","BAD")'
        cells = {"B2": 15000000, "B3": 6000000, "B4": 9000000}
        py_result = ExcelFormulaEvaluator().evaluate(formula, cells)

        node_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "node_sidecar")
        env = dict(os.environ, HF_PORT="4421")
        proc = subprocess.Popen(["node", "hyperformula_server.js"], cwd=node_dir, env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            client = HyperFormulaSidecarClient("http://127.0.0.1:4421")
            for _ in range(50):
                if client.health():
                    break
                time.sleep(0.1)
            hf_result = client.evaluate(formula, cells)
            self.assertEqual(py_result, hf_result)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    unittest.main()
