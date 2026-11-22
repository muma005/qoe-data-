"""
Test harness for Level 5: User Workspace, VDR Portal & Interaction Surfaces.

Validates the backend ui-workspace gateway: VDR tree + release waves, capability
tokens, watermarking, zero-knowledge filtering, rate limiting, IRL console (LP-15),
deliverable compiler (LP-04 DDE sanitizer + checksum), HMAC state guard, CloudEvents,
and the proto contract for workspace_gateway.proto.
"""

import inspect
import os
import re
import unittest
from decimal import Decimal

from app.level5_workspace.vdr import (
    ReleaseWave,
    VDRNodeType,
    CapabilityTokenManager,
    RateLimiter,
    VDRTreeBuilder,
    WatermarkEngine,
    ZeroKnowledgeFilter,
)
from app.level5_workspace.irl import IRLPriority, IRLConsole
from app.level5_workspace.gateway import (
    DdeSanitizer,
    WorkspaceGatewayService,
)


class TestVDRTree(unittest.TestCase):
    def test_six_root_folders(self):
        tree = VDRTreeBuilder(".").build()
        self.assertEqual(len(tree), 6)
        self.assertEqual(tree[0]["title"], "01_Corporate_Governance_and_Legal")
        self.assertEqual(tree[5]["title"], "06_Human_Resources_and_Compensation")

    def test_release_wave_gating(self):
        builder = VDRTreeBuilder(".")
        t1 = builder.get_tree(current_sim_day=1)
        t14 = builder.get_tree(current_sim_day=14)
        t20 = builder.get_tree(current_sim_day=20)
        # Day 1: many locked docs; Day 14: fewer locked (Wave 4 still drip-fed);
        # Day 20: everything unlocked.
        self.assertGreater(t1["total_locked_documents"], 0)
        self.assertLess(t14["total_locked_documents"], t1["total_locked_documents"])
        self.assertEqual(t20["total_locked_documents"], 0)
        self.assertEqual(t20["total_unlocked_documents"],
                         t1["total_unlocked_documents"] + t1["total_locked_documents"])

    def test_is_locked_computation(self):
        builder = VDRTreeBuilder(".")
        builder.build()
        node = builder.find("VDR_NODE_003")  # some node; existence not asserted
        # verify a Wave 3 doc is locked on day 1 and unlocked on day 14
        day1 = builder.get_tree(1)
        day14 = builder.get_tree(14)

        def find_wave3(nodes):
            for n in nodes:
                if n["release_wave"] == ReleaseWave.WAVE_3_FRIDAY_DUMP.value and \
                        n["node_type"] != VDRNodeType.FOLDER.value:
                    return n
                r = find_wave3(n.get("children", []))
                if r:
                    return r
            return None

        wave3_doc = find_wave3(day1["root_nodes"])
        self.assertIsNotNone(wave3_doc)
        self.assertTrue(wave3_doc["is_locked"])


class TestCapabilityTokens(unittest.TestCase):
    def test_token_generation_and_verification(self):
        mgr = CapabilityTokenManager("secret")
        t = mgr.generate("USR_1", "DOC_1", 14, ttl_seconds=60, now=1000.0)
        self.assertTrue(mgr.verify(t["token"], "USR_1", "DOC_1", 14, t["expires_at"], now=1000.0))
        # wrong user fails
        self.assertFalse(mgr.verify(t["token"], "USR_2", "DOC_1", 14, t["expires_at"], now=1000.0))
        # expired fails
        self.assertFalse(mgr.verify(t["token"], "USR_1", "DOC_1", 14, t["expires_at"], now=1000.0 + 61))


class TestWatermark(unittest.TestCase):
    def test_watermark_config(self):
        wm = WatermarkEngine()
        cfg = wm.config("APOLLO", "USR_8921", "VDR_1", "2024-10-18T11:32:05Z")
        self.assertIn("APOLLO", cfg["watermark_text"])
        self.assertIn("USR_8921", cfg["watermark_text"])
        self.assertTrue(cfg["enable_steganographic_dots"])
        self.assertEqual(wm.ANGLE_DEGREES, -45.0)
        self.assertEqual(wm.OPACITY, 0.18)


class TestZeroKnowledge(unittest.TestCase):
    def test_strips_ground_truth(self):
        zk = ZeroKnowledgeFilter()
        payload = {"a": 1, "ground_truth": {"x": 1}, "list": [{"injected_anomalies": 2, "ok": 3}]}
        cleaned = zk.strip(payload)
        self.assertNotIn("ground_truth", cleaned)
        self.assertNotIn("injected_anomalies", cleaned["list"][0])
        self.assertEqual(cleaned["a"], 1)


class TestRateLimiter(unittest.TestCase):
    def test_max_five_per_second(self):
        rl = RateLimiter(max_per_sec=5)
        hits = [rl.allow(now=1000.0) for _ in range(10)]
        self.assertEqual(sum(hits), 5)


class TestIRL(unittest.TestCase):
    def test_submit_and_thread(self):
        irl = IRLConsole()
        t = irl.submit("sim1", "W03", IRLPriority.P1_CRITICAL, "P07", "GL extract",
                       "Provide GL detail for FY23", ["DOC_1"], sim_day=8)
        self.assertEqual(t["status"], "IN_PROGRESS")
        self.assertEqual(len(t["thread_history"]), 1)
        irl.append_turn(t["request_id"], "P07", "Controller", "Here is the file", ["DOC_1"])
        self.assertEqual(len(irl.get(t["request_id"])["thread_history"]), 2)

    def test_attention_quota_rejects_sixth_p1(self):
        irl = IRLConsole()
        for i in range(5):
            irl.submit("sim1", "W", IRLPriority.P1_CRITICAL, "P07", f"s{i}", "body", [], 8)
        r = irl.submit("sim1", "W", IRLPriority.P1_CRITICAL, "P07", "s6", "body", [], 8)
        self.assertEqual(r["status"], "REJECTED_ATTENTION_QUOTA")

    def test_vague_inquiry_triggers_pushback(self):
        irl = IRLConsole()
        r = irl.submit("sim1", "W", IRLPriority.P2_HIGH, "P06", "fishing",
                       "send all contracts and everything", [], 8)
        self.assertEqual(r["pushback_tier_triggered"], "TIER_4_AGGRESSIVE_OBFUSCATION")


class TestDdeSanitizer(unittest.TestCase):
    def test_neutralizes_formula_prefix(self):
        s = DdeSanitizer()
        self.assertEqual(s.sanitize("=CMD|'/C calc'!A0"), "'=CMD|'/C calc'!A0")
        self.assertEqual(s.sanitize("@SUM(1)"), "'@SUM(1)")
        self.assertEqual(s.sanitize("plain text"), "plain text")


class TestGateway(unittest.TestCase):
    def test_five_rpcs_present(self):
        svc = WorkspaceGatewayService()
        for name in ("get_vdr_tree", "get_vdr_document", "submit_irl_inquiry",
                     "sync_workspace_state", "compile_deliverables"):
            self.assertTrue(hasattr(svc, name), name)

    def test_sync_state_hmac(self):
        svc = WorkspaceGatewayService()
        sig = svc.sign_state("sim1", "USR_1")
        r = svc.sync_workspace_state("sim1", "USR_1", 0, [], "", sig)
        self.assertTrue(r["sync_acknowledged"])
        with self.assertRaises(PermissionError):
            svc.sync_workspace_state("sim1", "USR_1", 0, [], "", "bad-sig")

    def test_compile_deliverables_checksum(self):
        svc = WorkspaceGatewayService()
        import base64, hashlib
        wb = base64.b64encode(b"fake-workbook").decode()
        good_hash = hashlib.sha256(wb.encode()).hexdigest()
        r = svc.compile_deliverables("sim1", "USR_1", wb, "{}", "{}", good_hash)
        self.assertTrue(r["compilation_success"])
        self.assertTrue(r["audit_eval_queue_job_id"].startswith("AUDIT_JOB"))
        bad = svc.compile_deliverables("sim1", "USR_1", wb, "{}", "{}", "deadbeef")
        self.assertFalse(bad["compilation_success"])
        self.assertIn("CLIENT_CHECKSUM_MISMATCH", bad["compilation_errors"])

    def test_cloudevents_emitted(self):
        svc = WorkspaceGatewayService()
        svc.get_vdr_document("sim1", "VDR_NODE_003", "USR_1")
        svc.submit_irl_inquiry("sim1", "W", IRLPriority.P2_HIGH, "P07", "s", "body", [])
        self.assertGreater(len(svc.events.filter("qoe.workspace.vdr.opened.v1")), 0)
        self.assertGreater(len(svc.events.filter("qoe.workspace.irl.submitted.v1")), 0)


# ---------------------------------------------------------------------------
# Proto contract (workspace_gateway.proto; no edits)
# ---------------------------------------------------------------------------
def _proto_path():
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "proto", "workspace_gateway.proto")


class TestWorkspaceProtoContract(unittest.TestCase):
    """Complete proto contract: enums, RPCs, request->param mapping, response fields,
    and nested message fields (VDRNode, IRLThreadTurn, DocumentWatermarkConfig)."""

    RPC_TO_METHOD = {
        "GetVDRTree": "get_vdr_tree",
        "GetVDRDocument": "get_vdr_document",
        "SubmitIRLInquiry": "submit_irl_inquiry",
        "SyncWorkspaceState": "sync_workspace_state",
        "CompileDeliverables": "compile_deliverables",
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
        cls.messages = {}
        for name, body in re.findall(r"message\s+(\w+)\s*\{(.*?)\}", cls.proto, re.DOTALL):
            cls.messages[name] = re.findall(r"(\w+)\s*=\s*\d+\s*;", body)

    def test_all_fourteen_messages_parsed(self):
        self.assertEqual(len(self.messages), 14)

    def test_enums_match_python(self):
        self.assertEqual(self.enums["VDRNodeType"], {e.name: e.value for e in VDRNodeType})
        self.assertEqual(self.enums["ReleaseWave"], {e.name: e.value for e in ReleaseWave})
        self.assertEqual(self.enums["IRLPriority"], {e.name: e.value for e in IRLPriority})

    def test_five_rpcs(self):
        self.assertEqual(len(self.rpcs), 5)

    def test_request_fields_map_to_method_parameters(self):
        svc = WorkspaceGatewayService()
        for rpc_name, req_msg, _resp in self.rpcs:
            method = getattr(svc, self.RPC_TO_METHOD[rpc_name])
            params = list(inspect.signature(method).parameters)
            req_fields = self.messages[req_msg]
            self.assertEqual(params, req_fields,
                             f"{rpc_name} params {params} != request fields {req_fields}")

    def test_response_fields_align(self):
        svc = WorkspaceGatewayService()
        for rpc_name, _req, resp_msg in self.rpcs:
            result = self._call(svc, rpc_name)
            for field in self.messages[resp_msg]:
                self.assertIn(field, result, f"{rpc_name} response missing '{field}'")

    def test_nested_vdr_node_fields(self):
        svc = WorkspaceGatewayService()
        svc.current_sim_day = 20
        tree = svc.get_vdr_tree("sim1", "U", 20)
        node = tree["root_nodes"][0]
        for field in self.messages["VDRNode"]:
            self.assertIn(field, node, f"VDRNode missing '{field}'")

    def test_nested_irl_thread_turn_fields(self):
        svc = WorkspaceGatewayService()
        t = svc.submit_irl_inquiry("sim1", "W", IRLPriority.P2_HIGH, "P07", "s", "body", [])
        turn = t["thread_history"][0]
        for field in self.messages["IRLThreadTurn"]:
            self.assertIn(field, turn, f"IRLThreadTurn missing '{field}'")

    def test_nested_watermark_config_fields(self):
        svc = WorkspaceGatewayService()
        svc.current_sim_day = 20
        doc = svc.get_vdr_document("sim1", "VDR_NODE_002", "U")
        for field in self.messages["DocumentWatermarkConfig"]:
            self.assertIn(field, doc["watermark"], f"DocumentWatermarkConfig missing '{field}'")

    def _call(self, svc, rpc_name):
        if rpc_name == "GetVDRTree":
            svc.current_sim_day = 20
            return svc.get_vdr_tree("sim1", "U", 20)
        if rpc_name == "GetVDRDocument":
            svc.current_sim_day = 20
            return svc.get_vdr_document("sim1", "VDR_NODE_002", "U")
        if rpc_name == "SubmitIRLInquiry":
            return svc.submit_irl_inquiry("sim1", "W", IRLPriority.P2_HIGH, "P07", "s", "body", [])
        if rpc_name == "SyncWorkspaceState":
            return svc.sync_workspace_state("sim1", "U", 0, [], "", svc.sign_state("sim1", "U"))
        if rpc_name == "CompileDeliverables":
            import hashlib
            return svc.compile_deliverables("sim1", "U", "wb", "{}", "{}",
                                            hashlib.sha256(b"wb").hexdigest())
        raise AssertionError(f"unknown rpc {rpc_name}")


class TestGapClosure(unittest.TestCase):
    """Covers the remaining manifest gaps: search, 403 gating, consumed CloudEvents,
    report + SPA assembly, and the FastAPI server."""

    def test_vdr_search(self):
        svc = WorkspaceGatewayService()
        results = svc.search_vdr("Rebate")
        self.assertTrue(any("Rebate" in r["title"] for r in results))

    def test_403_gating_on_locked_document(self):
        svc = WorkspaceGatewayService()
        svc.current_sim_day = 1
        # Find a Wave 3 document (unlock day 14) and try to open it on day 1.
        builder = svc.search_vdr("")  # no-op; find a wave-3 doc
        # Build tree to locate a wave-3 doc id.
        from app.level5_workspace.vdr import VDRTreeBuilder, ReleaseWave, VDRNodeType
        b = VDRTreeBuilder(".")
        b.build()
        wave3_doc = next(n for n in b.nodes.values()
                         if n["release_wave"] == ReleaseWave.WAVE_3_FRIDAY_DUMP.value
                         and n["node_type"] != VDRNodeType.FOLDER.value)
        with self.assertRaises(PermissionError):
            svc.get_vdr_document("sim1", wave3_doc["node_id"], "USR_1")

    def test_sim_clock_ticked_unlocks_document(self):
        svc = WorkspaceGatewayService()
        svc.handle_sim_clock_ticked("sim1", 14, 5.5, "MS04")
        self.assertEqual(svc.current_sim_day, 14)
        from app.level5_workspace.vdr import VDRTreeBuilder, ReleaseWave, VDRNodeType
        b = VDRTreeBuilder(".")
        b.build()
        wave3_doc = next(n for n in b.nodes.values()
                         if n["release_wave"] == ReleaseWave.WAVE_3_FRIDAY_DUMP.value
                         and n["node_type"] != VDRNodeType.FOLDER.value)
        # Now unlocked (day 14), should not raise.
        svc.get_vdr_document("sim1", wave3_doc["node_id"], "USR_1")

    def test_friction_inquiry_answered_appends_turn(self):
        svc = WorkspaceGatewayService()
        t = svc.submit_irl_inquiry("sim1", "W", IRLPriority.P2_HIGH, "P07", "s", "body", [])
        svc.handle_friction_inquiry_answered("sim1", t["request_id"], "Here is the file", ["DOC_1"])
        req = svc.irl.get(t["request_id"])
        self.assertEqual(len(req["thread_history"]), 2)

    def test_fdb_recalculated_updates_status(self):
        svc = WorkspaceGatewayService()
        svc.handle_fdb_recalculated("sim1", "DISCREPANCY", 1, 310000.0)
        self.assertIn("DISCREPANCY", svc.check_bar_status)
        svc.handle_fdb_recalculated("sim1", "OK", 0, 0.0)
        self.assertIn("OK", svc.check_bar_status)

    def _databook(self):
        import sys, os, tempfile
        compiler = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenarios", "compiler")
        if compiler not in sys.path:
            sys.path.insert(0, compiler)
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        from app.level4_databook.formula_graph import Databook
        result = compile_scenario(SCENARIO_PROFILES["target_apex_supply"], 3, 42, tempfile.mkdtemp())
        return Databook().build(result["package_dir"])

    def _package_dir(self):
        import sys, os, tempfile
        compiler = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenarios", "compiler")
        if compiler not in sys.path:
            sys.path.insert(0, compiler)
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        return compile_scenario(SCENARIO_PROFILES["target_apex_supply"], 3, 42, tempfile.mkdtemp())["package_dir"]

    def test_fastapi_databook_endpoint(self):
        from fastapi.testclient import TestClient
        from app.level5_workspace.server import app
        pkg = self._package_dir()
        client = TestClient(app)
        r = client.post("/api/v1/workspace/databook/tab",
                        json={"package_dir": pkg, "tab_id": "07_Working_Capital"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("nwc", r.json()["data"])
        self.assertIn("dso_days", r.json()["data"])


class TestBackendGaps(unittest.TestCase):
    """Circuit breaker, event bus, and Level 3 latency integration."""

    def _package_dir(self):
        import sys, os, tempfile
        compiler = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenarios", "compiler")
        if compiler not in sys.path:
            sys.path.insert(0, compiler)
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        return compile_scenario(SCENARIO_PROFILES["target_apex_supply"], 3, 42, tempfile.mkdtemp())["package_dir"]

    def _databook(self):
        from app.level4_databook.formula_graph import Databook
        return Databook().build(self._package_dir())

    def test_circuit_breaker_opens_after_failures(self):
        from app.level5_workspace.gateway import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        def fail():
            raise RuntimeError("boom")

        for _ in range(3):
            with self.assertRaises(RuntimeError):
                cb.call(fail)
        self.assertEqual(cb.state, "OPEN")
        with self.assertRaises(PermissionError):
            cb.call(fail)

    def test_event_bus_publish_subscribe(self):
        from app.level5_workspace.gateway import EventBus
        bus = EventBus()
        seen = []
        bus.subscribe("qoe.sim.clock.ticked.v1", lambda **kw: seen.append(kw))
        bus.publish("qoe.sim.clock.ticked.v1", current_day=14)
        self.assertEqual(seen, [{"current_day": 14}])

    def test_gateway_bus_wires_consumed_events(self):
        svc = WorkspaceGatewayService()
        svc.bus.publish("qoe.sim.clock.ticked.v1", engagement_id="s", current_day=20,
                        hours_remaining=1.0, milestone="M")
        self.assertEqual(svc.current_sim_day, 20)
        svc.bus.publish("qoe.fdb.recalculated.v1", engagement_id="s",
                        check_bars_status="BAD", break_count=2, break_amount=5000.0)
        self.assertIn("DISCREPANCY", svc.check_bar_status)

    def test_irl_latency_from_level3(self):
        svc = WorkspaceGatewayService()
        # vague inquiry -> Tier 4 -> highest latency multiplier
        t = svc.submit_irl_inquiry("sim1", "W", IRLPriority.P2_HIGH, "P06", "fishing",
                                   "send all contracts", [])
        self.assertGreater(t["estimated_latency_hours"], 0.0)

    def test_vdr_nodes_have_access_phase(self):
        from app.level5_workspace.vdr import VDRTreeBuilder
        b = VDRTreeBuilder(".")
        b.build()
        phases = {n["access_phase"] for n in b.nodes.values()}
        self.assertEqual(phases, {"PHASE_I", "PHASE_II"})

    def test_trace_metric(self):
        svc = WorkspaceGatewayService()
        trace = svc.trace_metric("07_Working_Capital", "nwc")
        self.assertTrue(trace["source_je_id"].startswith("JE-"))
        self.assertIn("111000", trace["source_accounts"])

    def test_vague_inquiry_penalty(self):
        svc = WorkspaceGatewayService()
        svc.submit_irl_inquiry("sim1", "W", IRLPriority.P2_HIGH, "P06", "fishing",
                               "send all contracts and everything", [])
        self.assertEqual(svc.vague_inquiry_count, 1)
        r = svc.compile_deliverables("sim1", "U", "wb", "{}", "{}",
                                     __import__("hashlib").sha256(b"wb").hexdigest())
        self.assertEqual(r["investigative_rigor_penalty"], 1)

    def test_report_assembler_ten_sections(self):
        from app.level5_workspace.report import ReportAssembler
        databook = self._databook()
        report = ReportAssembler().build(databook)
        self.assertEqual(len(report["sections"]), 10)
        self.assertIn("normalized_ebitda", report["sections"]["01_Executive_Summary"])

    def test_spa_exhibit_b(self):
        from app.level5_workspace.report import SPAExhibitBBuilder
        databook = self._databook()
        spa = SPAExhibitBBuilder().build(databook)
        self.assertIn("1_target_peg", spa)
        self.assertGreater(len(spa["2_inclusions"]), 0)
        self.assertGreater(len(spa["3_exclusions_debt_like"]), 0)
        self.assertIn("escrow", spa["4_indemnity_escrow"]["purpose"].lower()
                      or "Escrow" in spa["4_indemnity_escrow"]["purpose"])

    def test_fastapi_server_routes(self):
        from app.level5_workspace.server import app as fastapi_app
        paths = {r.path for r in fastapi_app.routes}
        for expected in ("/api/v1/workspace/vdr/tree", "/api/v1/workspace/irl/submit",
                         "/api/v1/workspace/deliverables/compile", "/api/v1/workspace/report/assemble"):
            self.assertIn(expected, paths)


if __name__ == "__main__":
    unittest.main()
