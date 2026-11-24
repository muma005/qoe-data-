"""
Test harness for Level 6: Assessment, Forensic Audit & Diligence Turing Test Engine.

Validates the AST formula auditor (FA01-FA04, LP-06), Benford's Law scanner, the
4-quadrant rubric scorer, the EQCR memo generator, the AuditEvaluationService facade
(5 RPCs + job lifecycle), and the proto contract for audit_eval.proto.
"""

import hashlib
import json
import math
import os
import re
import unittest
from decimal import Decimal

from app.level6_audit.ast_audit import (
    AuditSeverity,
    ASTAuditor,
    find_hardcodes,
)
from app.level6_audit.benford_scanner import BenfordScanner
from app.level6_audit.rubric_scorer import EvaluationInputs, RubricScorer
from app.level6_audit.eqrc_memo import EQCRMemoGenerator
from app.level6_audit import AuditEvaluationService


class TestASTAuditor(unittest.TestCase):
    def setUp(self):
        self.ast = ASTAuditor()

    def test_hardcode_detection(self):
        self.assertEqual(find_hardcodes("=C14*1.08 + 50000"), ["1.08", "50000"])
        self.assertEqual(find_hardcodes("=SUM(C4:C10)"), [])
        self.assertEqual(find_hardcodes("=C14"), [])
        self.assertEqual(find_hardcodes("=D14*0.15 + 12000"), ["0.15", "12000"])

    def test_audit_formulas_flags_hardcodes(self):
        cells = [("06_OPEX", "D18", "=D14*0.15 + 12000"), ("03_IS", "C4", "=SUM(C5:C10)")]
        findings = self.ast.audit_formulas(cells)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].cell_coordinate, "D18")
        self.assertEqual(findings[0].violation_type, "VIO_EMBEDDED_CONSTANT")

    def test_pvm_additive(self):
        ok, residual = self.ast.verify_pvm_additive(
            Decimal("200.00"), Decimal("200.00"), Decimal("133.33"), Decimal("-133.33"))
        self.assertTrue(ok)
        self.assertLess(abs(residual), Decimal("0.01"))

    def test_check_bars(self):
        ok, passed = self.ast.verify_check_bars([("07", True, Decimal("0")), ("08", True, Decimal("0"))])
        self.assertTrue(ok)
        self.assertEqual(passed, 2)

    def test_recalculation_exact(self):
        ok, delta = self.ast.verify_recalculation(
            {"nwc": Decimal("100.0000")}, {"nwc": Decimal("100.0000")})
        self.assertTrue(ok)
        self.assertEqual(delta, Decimal("0"))
        ok2, _ = self.ast.verify_recalculation(
            {"nwc": Decimal("100.0000")}, {"nwc": Decimal("100.0100")})
        self.assertFalse(ok2)


class TestBenford(unittest.TestCase):
    def test_first_digit_expected(self):
        # Benford's Law: P(1) ~ 0.301, P(9) ~ 0.046
        from app.level6_audit.benford_scanner import BENFORD_EXPECTED
        self.assertAlmostEqual(BENFORD_EXPECTED[1], 0.30103, places=4)
        self.assertAlmostEqual(BENFORD_EXPECTED[9], 0.04576, places=4)

    def test_benford_conforming_population_passes(self):
        # A synthetic population whose first digits follow Benford exactly.
        values = []
        for d in range(1, 10):
            from app.level6_audit.benford_scanner import BENFORD_EXPECTED
            count = int(BENFORD_EXPECTED[d] * 10000)
            values.extend([d * 10**6 + i for i in range(count)])
        result = BenfordScanner().scan(values)
        self.assertTrue(result["passes_benford_uniformity"])

    def test_rounded_population_fails(self):
        # All leading digit 5 -> clearly non-Benford.
        values = [50000 + i for i in range(5000)]
        result = BenfordScanner().scan(values)
        self.assertFalse(result["passes_benford_uniformity"])


class TestRubricScorer(unittest.TestCase):
    def test_perfect_score(self):
        inputs = EvaluationInputs(detected_anomalies=5, missed_anomalies=0, hardcode_count=0,
                                  double_dipping_count=0, scope_limitation="escrow",
                                  replacement_cost_net=True)
        scores = RubricScorer().score(inputs)
        self.assertEqual(scores["q1_investigative_rigor"], 100.0)
        self.assertEqual(scores["q2_modeling_hygiene"], 100.0)
        self.assertEqual(scores["q3_commercial_judgment"], 100.0)
        self.assertEqual(scores["q4_legal_protection"], 100.0)
        self.assertAlmostEqual(scores["composite_score"], 100.0, places=1)
        self.assertTrue(scores["passed_institutional_threshold"])
        self.assertTrue(scores["institutional_honors"])

    def test_missed_all_anomalies(self):
        inputs = EvaluationInputs(detected_anomalies=0, missed_anomalies=5, hardcode_count=2,
                                  double_dipping_count=1, scope_limitation="missed",
                                  replacement_cost_net=False)
        scores = RubricScorer().score(inputs)
        self.assertEqual(scores["q1_investigative_rigor"], 0.0)
        self.assertEqual(scores["q4_legal_protection"], 0.0)
        self.assertFalse(scores["passed_institutional_threshold"])

    def test_composite_weights(self):
        # Verify the exact weight formula on a known vector.
        scorer = RubricScorer()
        inputs = EvaluationInputs(detected_anomalies=3, missed_anomalies=1, hardcode_count=1,
                                  double_dipping_count=1, scope_limitation="caveated",
                                  replacement_cost_net=True)
        scores = scorer.score(inputs)
        expected = (0.30 * scores["q1_investigative_rigor"] +
                    0.25 * scores["q2_modeling_hygiene"] +
                    0.25 * scores["q3_commercial_judgment"] +
                    0.20 * scores["q4_legal_protection"])
        self.assertAlmostEqual(scores["composite_score"], expected, places=1)

    def test_deterministic(self):
        scorer = RubricScorer()
        inputs = EvaluationInputs(detected_anomalies=2, missed_anomalies=3, hardcode_count=1,
                                  double_dipping_count=0, scope_limitation="escrow",
                                  replacement_cost_net=True)
        self.assertEqual(scorer.score(inputs), scorer.score(inputs))

    def test_grade_letters(self):
        scorer = RubricScorer()
        self.assertIn("HONORS", scorer.grade_letter(95.0))
        self.assertIn("MERIT", scorer.grade_letter(85.0))
        self.assertIn("CONDITIONAL", scorer.grade_letter(70.0))
        self.assertEqual("FAIL", scorer.grade_letter(50.0))


class TestEQCRMemo(unittest.TestCase):
    def test_memo_deterministic_and_sections(self):
        gen = EQCRMemoGenerator()
        scores = {"q1_investigative_rigor": 27.0, "q2_modeling_hygiene": 23.5,
                  "q3_commercial_judgment": 21.0, "q4_legal_protection": 17.0,
                  "composite_score": 88.5, "passed_institutional_threshold": True,
                  "institutional_honors": False}
        m1 = gen.generate("sim1", "USR_8921", "Robert Sterling, CPA", scores, "PASS WITH MERIT",
                          ["Missed X"], ["Found Y"])
        m2 = gen.generate("sim1", "USR_8921", "Robert Sterling, CPA", scores, "PASS WITH MERIT",
                          ["Missed X"], ["Found Y"])
        self.assertEqual(m1, m2)
        self.assertIn("INVESTIGATIVE RIGOR", m1["memo_markdown_text"])
        self.assertIn("Robert Sterling", m1["memo_markdown_text"])


class TestAuditEvaluationService(unittest.TestCase):
    def _submit(self, svc):
        report = json.dumps({"sections": {"03_Quality_of_Earnings": {"anomalies": [
            {"anomaly_id": "SR-B01"}]},
            "10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities": {"caveats": ["warranty"]}}})
        spa = json.dumps({"4_indemnity_escrow": {"amount": "$500,000"},
                          "double_dipping_count": 0, "replacement_cost_netted": True})
        checksum = hashlib.sha256(json.dumps([report, spa, "uri"], sort_keys=True).encode()).hexdigest()
        return svc.submit_engagement_for_grading("sim1", "USR", "apex", "0x1", "uri",
                                                 report, spa, checksum)

    def test_submit_and_status(self):
        svc = AuditEvaluationService()
        queued = self._submit(svc)
        self.assertEqual(queued["status"], "QUEUED")
        result = svc.process_job(queued["job_id"], [("03_IS", "C4", "=SUM(C5:C10)")],
                                 [100, 200, 300], ["SR-B01"])
        self.assertEqual(result["detected_anomalies_count"], 1)
        self.assertEqual(result["missed_anomalies_count"], 0)
        status = svc.get_grading_status(queued["job_id"])
        self.assertEqual(status["status"], "COMPLETED")
        self.assertAlmostEqual(status["scores"]["q4_legal_protection"], 100.0)

    def test_checksum_mismatch(self):
        svc = AuditEvaluationService()
        with self.assertRaises(PermissionError):
            svc.submit_engagement_for_grading("sim1", "USR", "apex", "0x1", "uri",
                                              "{}", "{}", "deadbeef")

    def test_scope_decision_tree(self):
        svc = AuditEvaluationService()
        # missed -> 0, caveated -> 14, escrow -> 20
        self.assertEqual(svc._scope_from({}, {}), "missed")
        self.assertEqual(svc._scope_from({}, {"sections": {"10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities": {"caveats": ["x"]}}}), "caveated")
        self.assertEqual(svc._scope_from({"4_indemnity_escrow": {"amount": "$500,000"}}, {}), "missed")

    def test_cloudevents(self):
        svc = AuditEvaluationService()
        queued = self._submit(svc)
        svc.process_job(queued["job_id"], [], [100, 200], ["SR-B01"])
        types = {e["type"] for e in svc.events}
        self.assertIn("qoe.audit.job.started.v1", types)
        self.assertIn("qoe.audit.evaluation.incomplete.v1", types)

    def test_standalone_rpcs(self):
        svc = AuditEvaluationService()
        ast = svc.run_ast_formula_audit("sim1", [("03_IS", "C4", "=1.5+2")])
        self.assertEqual(ast["hardcoded_constants_flagged"], 1)
        benford = svc.scan_benford_distribution("sim1", values=[100, 200, 300, 400, 500])
        self.assertEqual(benford["total_transactions_scanned"], 5)


# ---------------------------------------------------------------------------
# Proto contract (audit_eval.proto; no edits)
# ---------------------------------------------------------------------------
def _proto_path():
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "proto", "audit_eval.proto")


class TestAuditProtoContract(unittest.TestCase):
    RPC_TO_METHOD = {
        "SubmitEngagementForGrading": "submit_engagement_for_grading",
        "GetGradingStatus": "get_grading_status",
        "RunASTFormulaAudit": "run_ast_formula_audit",
        "ScanBenfordDistribution": "scan_benford_distribution",
        "GenerateEQCRMemo": "generate_eqcr_memo",
    }

    @classmethod
    def setUpClass(cls):
        with open(_proto_path(), encoding="utf-8") as f:
            cls.proto = f.read()
        cls.enums = {}
        for name, body in re.findall(r"enum\s+(\w+)\s*\{(.*?)\}", cls.proto, re.DOTALL):
            cls.enums[name] = {k: int(v) for k, v in re.findall(r"(\w+)\s*=\s*(\d+)\s*;", body)}
        cls.rpcs = re.findall(r"rpc\s+(\w+)\s*\(\s*(\w+)\s*\)\s*returns\s*\(\s*(\w+)\s*\)",
                              re.search(r"service\s+\w+\s*\{(.*?)\}", cls.proto, re.DOTALL).group(1))

    def test_audit_severity_enum_matches(self):
        self.assertEqual(self.enums["AuditSeverity"], {e.name: e.value for e in AuditSeverity})

    def test_five_rpcs(self):
        self.assertEqual(len(self.rpcs), 5)

    def test_rpc_methods_present(self):
        svc = AuditEvaluationService()
        for rpc_name, _req, _resp in self.rpcs:
            self.assertTrue(hasattr(svc, self.RPC_TO_METHOD[rpc_name]), rpc_name)


if __name__ == "__main__":
    unittest.main()
