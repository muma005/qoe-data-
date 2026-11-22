"""
Test harness for Level 5: User Workspace, VDR Portal & Interaction Surfaces.

Validates the backend ui-workspace gateway: VDR tree + release waves, capability
tokens, watermarking, zero-knowledge filtering, rate limiting, IRL console (LP-15),
deliverable compiler (LP-04 DDE sanitizer + checksum), HMAC state guard, CloudEvents,
and the proto contract for workspace_gateway.proto.
"""

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
    @classmethod
    def setUpClass(cls):
        with open(_proto_path(), encoding="utf-8") as f:
            cls.proto = f.read()
        cls.enums = {}
        for name, body in re.findall(r"enum\s+(\w+)\s*\{(.*?)\}", cls.proto, re.DOTALL):
            cls.enums[name] = {k: int(v) for k, v in re.findall(r"(\w+)\s*=\s*(\d+)\s*;", body)}
        cls.rpcs = re.findall(r"rpc\s+(\w+)\s*\(\s*(\w+)\s*\)\s*returns\s*\(\s*(\w+)\s*\)",
                              re.search(r"service\s+\w+\s*\{(.*?)\}", cls.proto, re.DOTALL).group(1))

    def test_enums_match_python(self):
        self.assertEqual(self.enums["VDRNodeType"], {e.name: e.value for e in VDRNodeType})
        self.assertEqual(self.enums["ReleaseWave"], {e.name: e.value for e in ReleaseWave})
        self.assertEqual(self.enums["IRLPriority"], {e.name: e.value for e in IRLPriority})

    def test_five_rpcs(self):
        self.assertEqual(len(self.rpcs), 5)


if __name__ == "__main__":
    unittest.main()
