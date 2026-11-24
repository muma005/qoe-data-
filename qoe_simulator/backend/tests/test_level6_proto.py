"""Exercise the existing audit_eval.proto over a real gRPC transport."""

import hashlib
import json
import unittest
from concurrent.futures import ThreadPoolExecutor

import grpc
from google.protobuf import message_factory

from app.level6_audit.rubric_scorer import EvaluationJobs, register_grpc_service
from tests.test_level6_adversarial import evidence_scenario
from tests.test_level6_workbook import fixture


class Level6ProtoRoundTripTests(unittest.TestCase):
    def setUp(self):
        self.workbook = fixture(formula="B2+1", cached="11")
        scenario = evidence_scenario()
        scenario["ledger"]["L"]["account_category"] = "COGS"
        self.jobs = EvaluationJobs(lambda scenario_id, seed: scenario, timeout=5)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.server = grpc.server(self.executor)
        self.pool = register_grpc_service(
            self.server, self.jobs, lambda uri: self.workbook,
            lambda engagement: ("s", "0x01"),
        )
        port = self.server.add_insecure_port("127.0.0.1:0")
        self.server.start()
        self.channel = grpc.insecure_channel(f"127.0.0.1:{port}")

    def tearDown(self):
        self.channel.close()
        self.server.stop(0).wait()
        self.jobs.wait(10)
        self.executor.shutdown(wait=True)

    def call(self, method, request_type, response_type, **values):
        request = message_factory.GetMessageClass(self.pool.FindMessageTypeByName(
            "qoe.audit.v1." + request_type))(**values)
        response = message_factory.GetMessageClass(self.pool.FindMessageTypeByName(
            "qoe.audit.v1." + response_type))
        rpc = self.channel.unary_unary(
            "/qoe.audit.v1.AuditEvaluationService/" + method,
            request_serializer=lambda message: message.SerializeToString(),
            response_deserializer=response.FromString,
        )
        return rpc(request, timeout=10)

    def test_all_five_rpc_methods_and_findings_round_trip(self):
        report = {"sections": {"03_Quality_of_Earnings": {"anomalies": [
            {"anomaly_id": "A", "cell": "S0!C2", "amount": "999"}]}}}
        spa = {}
        payload = json.dumps({"report": report, "spa": spa}, sort_keys=True,
                             separators=(",", ":")).encode()
        queued = self.call(
            "SubmitEngagementForGrading", "SubmitEngagementForGradingRequest", "GradingJobQueuedResponse",
            engagement_id="e", user_id="u", scenario_id="s", seed_hex_64="0x01",
            fdb_xlsx_blob_uri="artifact://book", report_memo_json=json.dumps(report),
            spa_exhibit_b_json=json.dumps(spa),
            submission_checksum_sha256=hashlib.sha256(self.workbook + payload).hexdigest(),
        )
        self.assertEqual(queued.status, "QUEUED")
        self.assertTrue(queued.HasField("queued_at"))
        self.assertTrue(self.jobs.wait(10))
        status = self.call("GetGradingStatus", "GradingJobStatusRequest", "GradingJobStatusResponse",
                           job_id=queued.job_id)
        self.assertEqual(status.status, "COMPLETED")
        self.assertTrue(status.HasField("completed_at"))
        self.assertGreater(status.ast_report.total_cells_scanned, 0)
        self.assertTrue(any(f.violation_type == "VIO_EMBEDDED_CONSTANT" for f in status.ast_report.findings))
        self.assertTrue(all(f.sheet_name and f.severity for f in status.ast_report.findings))
        self.assertTrue(status.HasField("scores"))
        self.assertEqual(status.benford_result.engagement_id, "e")

        memo = self.call("GenerateEQCRMemo", "GenerateEQCRMemoRequest", "EQCRMemoResponse",
                         job_id=queued.job_id, engagement_id="e")
        self.assertEqual(memo.engagement_id, "e")
        self.assertTrue(memo.memo_markdown_text)
        self.assertEqual(memo.scores.composite_score, status.scores.composite_score)

        ast = self.call("RunASTFormulaAudit", "RunASTFormulaAuditRequest", "ASTAuditReport",
                        engagement_id="e", fdb_xlsx_blob_uri="artifact://book")
        self.assertEqual(ast.engagement_id, "e")
        self.assertTrue(ast.findings)
        scan = self.call("ScanBenfordDistribution", "ScanBenfordDistributionRequest",
                         "BenfordDistributionResult", engagement_id="e", ledger_table_name="proj_gl",
                         account_category_filter="COGS")
        self.assertEqual(scan.engagement_id, "e")
        self.assertEqual(scan.total_transactions_scanned, 1)

    def test_proto_errors_are_typed_and_no_memo_before_completion(self):
        with self.assertRaises(grpc.RpcError) as invalid:
            self.call("ScanBenfordDistribution", "ScanBenfordDistributionRequest",
                      "BenfordDistributionResult", engagement_id="e", ledger_table_name="unknown")
        self.assertEqual(invalid.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)
        with self.assertRaises(grpc.RpcError) as absent:
            self.call("GetGradingStatus", "GradingJobStatusRequest", "GradingJobStatusResponse",
                      job_id="missing")
        self.assertEqual(absent.exception.code(), grpc.StatusCode.NOT_FOUND)
        with self.assertRaises(grpc.RpcError) as bad_checksum:
            self.call("SubmitEngagementForGrading", "SubmitEngagementForGradingRequest",
                      "GradingJobQueuedResponse", engagement_id="e", scenario_id="s",
                      seed_hex_64="0x01", fdb_xlsx_blob_uri="artifact://book",
                      report_memo_json="{}", spa_exhibit_b_json="{}",
                      submission_checksum_sha256="0" * 64)
        self.assertEqual(bad_checksum.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)
        empty = json.dumps({"report": {}, "spa": {}}, sort_keys=True, separators=(",", ":")).encode()
        queued = self.jobs.submit("e", "s", "0x01", self.workbook, {}, {},
                                  hashlib.sha256(self.workbook + empty).hexdigest(), operation="ast")
        self.assertTrue(self.jobs.wait(10))
        with self.assertRaises(grpc.RpcError) as forbidden:
            self.call("GenerateEQCRMemo", "GenerateEQCRMemoRequest", "EQCRMemoResponse",
                      job_id=queued["job_id"], engagement_id="another-engagement")
        self.assertEqual(forbidden.exception.code(), grpc.StatusCode.PERMISSION_DENIED)
        with self.assertRaises(grpc.RpcError) as no_memo:
            self.call("GenerateEQCRMemo", "GenerateEQCRMemoRequest", "EQCRMemoResponse",
                      job_id=queued["job_id"], engagement_id="e")
        self.assertEqual(no_memo.exception.code(), grpc.StatusCode.FAILED_PRECONDITION)
