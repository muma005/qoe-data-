"""
Brutal / stress / property / edge-case tests for Level 5 (ui-workspace).

Covers every subsystem at the limits: capability-token fuzzing, zero-knowledge
deep-nesting + idempotency, rate-limiter boundary, IRL quota + 50-turn threads,
DDE payload fuzzing, VDR unlock-day boundaries + search fuzzing, gateway 403/HMAC/
checksum/CloudEvents, circuit-breaker recovery, event-bus fan-out, watermark config,
report/SPA determinism, and Level 3 latency monotonicity.
"""

import os
import random
import sys
import tempfile
import time
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
    CircuitBreaker,
    DdeSanitizer,
    EventBus,
    WorkspaceGatewayService,
)


# ---------------------------------------------------------------------------
# Capability tokens — fuzzing
# ---------------------------------------------------------------------------
class TestBrutalTokens(unittest.TestCase):
    def test_1000_tokens_correct_verify_and_any_wrong_input_fails(self):
        mgr = CapabilityTokenManager("secret")
        rng = random.Random(0xBEEF)
        for _ in range(1000):
            user = f"U{rng.randint(0, 9999)}"
            doc = f"D{rng.randint(0, 9999)}"
            day = rng.randint(0, 60)
            t = mgr.generate(user, doc, day, ttl_seconds=60, now=1000.0)
            self.assertTrue(mgr.verify(t["token"], user, doc, day, t["expires_at"], now=1000.0))
            self.assertFalse(mgr.verify(t["token"], user + "x", doc, day, t["expires_at"], now=1000.0))
            self.assertFalse(mgr.verify(t["token"], user, doc + "x", day, t["expires_at"], now=1000.0))
            self.assertFalse(mgr.verify(t["token"], user, doc, day + 1, t["expires_at"], now=1000.0))
            self.assertFalse(mgr.verify(t["token"], user, doc, day, t["expires_at"], now=1000.0 + 61))

    def test_tampered_token_fails(self):
        mgr = CapabilityTokenManager("secret")
        t = mgr.generate("U", "D", 1, now=1000.0)
        tampered = t["token"][:-1] + ("0" if t["token"][-1] != "0" else "1")
        self.assertFalse(mgr.verify(tampered, "U", "D", 1, t["expires_at"], now=1000.0))


# ---------------------------------------------------------------------------
# Zero-knowledge filter — deep nesting + idempotency
# ---------------------------------------------------------------------------
class TestBrutalZeroKnowledge(unittest.TestCase):
    def test_deep_nesting_10_levels_all_stripped(self):
        zk = ZeroKnowledgeFilter()
        obj = {"ground_truth": {"x": 1}, "ok": 1}
        for _ in range(10):
            obj = {"nested": obj}
        cleaned = zk.strip(obj)
        for _ in range(10):
            cleaned = cleaned["nested"]
        self.assertNotIn("ground_truth", cleaned)
        self.assertEqual(cleaned["ok"], 1)

    def test_idempotency(self):
        zk = ZeroKnowledgeFilter()
        payload = {"a": 1, "injected_anomalies": [1, 2], "b": {"ebitda_impact": 5, "c": 3}}
        once = zk.strip(payload)
        twice = zk.strip(once)
        self.assertEqual(once, twice)

    def test_all_ground_truth_keys_stripped(self):
        zk = ZeroKnowledgeFilter()
        payload = {k: 1 for k in ("ground_truth", "injected_anomalies", "solution_key",
                                  "anomaly_ids", "ebitda_impact", "hidden_marker",
                                  "fraud_marker", "admin_ground_truth")}
        self.assertEqual(zk.strip(payload), {})


# ---------------------------------------------------------------------------
# Rate limiter — boundary + recovery
# ---------------------------------------------------------------------------
class TestBrutalRateLimiter(unittest.TestCase):
    def test_exact_boundary_and_window_slide(self):
        rl = RateLimiter(max_per_sec=5)
        self.assertTrue(all(rl.allow(now=1000.0) for _ in range(5)))
        self.assertFalse(rl.allow(now=1000.0))
        self.assertFalse(rl.allow(now=1000.99))
        self.assertTrue(rl.allow(now=1001.0))


# ---------------------------------------------------------------------------
# IRL — quota, 50-turn threads, vague detection
# ---------------------------------------------------------------------------
class TestBrutalIRL(unittest.TestCase):
    def test_quota_exact_five(self):
        irl = IRLConsole()
        for i in range(5):
            self.assertEqual(irl.submit("s", "W", IRLPriority.P1_CRITICAL, "P07", f"s{i}", "b", [], 1)["status"], "IN_PROGRESS")
        r = irl.submit("s", "W", IRLPriority.P1_CRITICAL, "P07", "s6", "b", [], 1)
        self.assertEqual(r["status"], "REJECTED_ATTENTION_QUOTA")

    def test_fifty_thread_turns(self):
        irl = IRLConsole()
        t = irl.submit("s", "W", IRLPriority.P2_HIGH, "P07", "s", "b", [], 1)
        for i in range(50):
            irl.append_turn(t["request_id"], "P06", "CFO", f"msg {i}")
        self.assertEqual(len(irl.get(t["request_id"])["thread_history"]), 51)

    def test_all_vague_markers(self):
        irl = IRLConsole()
        for m in ("all contracts", "all invoices", "send everything", "tell me what's wrong",
                  "what's wrong with ebitda", "all documents"):
            r = irl.submit("s", "W", IRLPriority.P2_HIGH, "P06", "f", m, [], 1)
            self.assertEqual(r["pushback_tier_triggered"], "TIER_4_AGGRESSIVE_OBFUSCATION", m)

    def test_specific_inquiry_not_vague(self):
        irl = IRLConsole()
        r = irl.submit("s", "W", IRLPriority.P2_HIGH, "P06", "f",
                       "Please provide GL account 409000 credit memo register for FY23", [], 1)
        self.assertEqual(r["pushback_tier_triggered"], "TIER_1_PROFESSIONAL_COOPERATION")


# ---------------------------------------------------------------------------
# DDE sanitizer — payload fuzzing
# ---------------------------------------------------------------------------
class TestBrutalDde(unittest.TestCase):
    def test_neutralizes_all_injection_prefixes(self):
        s = DdeSanitizer()
        payloads = ["=CMD|'/c calc'!A0", "+cmd|'/c calc'!A0", "-cmd|'/c calc'!A0",
                    "@SUM(1)", "=HYPERLINK(\"http://x\")", "=1+1", "=WEBSERVICE(...)"]
        for p in payloads:
            out = s.sanitize(p)
            self.assertTrue(out.startswith("'"), f"{p} not neutralized")

    def test_sanitize_all_deep(self):
        s = DdeSanitizer()
        payload = {"a": "=CMD", "b": [{"c": "@SUM"}], "d": {"e": "-evil"}}
        cleaned = s.sanitize_all(payload)
        self.assertEqual(cleaned["a"], "'=CMD")
        self.assertEqual(cleaned["b"][0]["c"], "'@SUM")
        self.assertEqual(cleaned["d"]["e"], "'-evil")


# ---------------------------------------------------------------------------
# VDR tree — unlock boundaries + search fuzzing
# ---------------------------------------------------------------------------
class TestBrutalVDR(unittest.TestCase):
    def test_24_leaf_documents_and_6_folders(self):
        b = VDRTreeBuilder(".")
        b.build()
        docs = [n for n in b.nodes.values() if n["node_type"] != VDRNodeType.FOLDER.value]
        folders = [n for n in b.nodes.values() if n["node_type"] == VDRNodeType.FOLDER.value]
        self.assertEqual(len(folders), 6)
        self.assertEqual(len(docs), 24)

    def test_unlock_boundary_exact(self):
        b = VDRTreeBuilder(".")
        b.build()
        wave2 = next(n for n in b.nodes.values()
                     if n["release_wave"] == ReleaseWave.WAVE_2_SUBLEDGERS.value
                     and n["node_type"] != VDRNodeType.FOLDER.value)
        self.assertEqual(wave2["unlock_sim_day"], 7)
        t6 = b.get_tree(6)
        t7 = b.get_tree(7)
        self.assertGreater(t6["total_locked_documents"], t7["total_locked_documents"])

    def test_search_case_insensitive_and_fuzz(self):
        b = VDRTreeBuilder(".")
        b.build()
        self.assertTrue(any("rebate" in n["title"].lower() for n in b.search("REBATE")))
        self.assertEqual(b.search(""), [])
        self.assertEqual(b.search("zzzzzz_nonexistent"), [])
        # every leaf doc is searchable by a unique substring of its title
        for n in b.nodes.values():
            if n["node_type"] != VDRNodeType.FOLDER.value:
                self.assertIn(n, b.search(n["title"][:6]))

    def test_access_phase_assignment(self):
        b = VDRTreeBuilder(".")
        b.build()
        for n in b.nodes.values():
            self.assertEqual(n["access_phase"],
                             "PHASE_I" if n["unlock_sim_day"] <= 13 else "PHASE_II")


# ---------------------------------------------------------------------------
# Watermark config
# ---------------------------------------------------------------------------
class TestBrutalWatermark(unittest.TestCase):
    def test_config_complete_and_deterministic(self):
        wm = WatermarkEngine()
        c1 = wm.config("APOLLO", "USR_1", "SES_1", "2024-10-18T11:32:05Z")
        c2 = wm.config("APOLLO", "USR_1", "SES_1", "2024-10-18T11:32:05Z")
        self.assertEqual(c1, c2)
        for key in ("watermark_text", "ip_address_hash", "session_uuid", "enable_steganographic_dots"):
            self.assertIn(key, c1)


# ---------------------------------------------------------------------------
# Gateway — 403, HMAC, checksum, CloudEvents, circuit breaker, event bus
# ---------------------------------------------------------------------------
class TestBrutalGateway(unittest.TestCase):
    def test_403_at_exact_boundary(self):
        svc = WorkspaceGatewayService()
        from app.level5_workspace.vdr import VDRTreeBuilder, ReleaseWave, VDRNodeType
        b = VDRTreeBuilder("."); b.build()
        wave3 = next(n for n in b.nodes.values()
                     if n["release_wave"] == ReleaseWave.WAVE_3_FRIDAY_DUMP.value
                     and n["node_type"] != VDRNodeType.FOLDER.value)
        svc.current_sim_day = wave3["unlock_sim_day"] - 1
        with self.assertRaises(PermissionError):
            svc.get_vdr_document("s", wave3["node_id"], "U")
        svc.current_sim_day = wave3["unlock_sim_day"]
        svc.get_vdr_document("s", wave3["node_id"], "U")  # no raise

    def test_hmac_tamper_detected(self):
        svc = WorkspaceGatewayService()
        sig = svc.sign_state("sim1", "U")
        # flip a character
        bad = sig[:-1] + ("0" if sig[-1] != "0" else "1")
        with self.assertRaises(PermissionError):
            svc.sync_workspace_state("sim1", "U", 0, [], "", bad)

    def test_checksum_mismatch_detected(self):
        svc = WorkspaceGatewayService()
        r = svc.compile_deliverables("sim1", "U", "wb", "{}", "{}", "deadbeef")
        self.assertFalse(r["compilation_success"])

    def test_cloudevent_counts(self):
        svc = WorkspaceGatewayService()
        svc.current_sim_day = 20
        for i in range(10):
            svc.get_vdr_document("s", f"VDR_NODE_{i+2:03d}", "U") if i < 24 else None
        svc.submit_irl_inquiry("s", "W", IRLPriority.P2_HIGH, "P07", "s", "body", [])
        self.assertGreater(len(svc.events.filter("qoe.workspace.vdr.opened.v1")), 0)
        self.assertGreater(len(svc.events.filter("qoe.workspace.irl.submitted.v1")), 0)

    def test_event_bus_fanout_and_ordering(self):
        bus = EventBus()
        seen = []
        bus.subscribe("e", lambda **kw: seen.append(("a", kw)))
        bus.subscribe("e", lambda **kw: seen.append(("b", kw)))
        bus.publish("e", x=1)
        self.assertEqual(len(seen), 2)
        self.assertEqual([s[0] for s in seen], ["a", "b"])

    def test_circuit_breaker_recovery(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.05)
        for _ in range(2):
            with self.assertRaises(RuntimeError):
                cb.call(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        self.assertEqual(cb.state, "OPEN")
        with self.assertRaises(PermissionError):
            cb.call(lambda: 1)
        time.sleep(0.08)
        # HALF_OPEN -> success -> CLOSED
        self.assertEqual(cb.call(lambda: 42), 42)
        self.assertEqual(cb.state, "CLOSED")


# ---------------------------------------------------------------------------
# Report / SPA determinism + Level 3 latency monotonicity
# ---------------------------------------------------------------------------
class TestBrutalDeliverables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scenarios", "compiler")
        if compiler not in sys.path:
            sys.path.insert(0, compiler)
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        from app.level4_databook.formula_graph import Databook
        cls.pkg = compile_scenario(SCENARIO_PROFILES["target_apex_supply"], 3, 42, tempfile.mkdtemp())
        cls.databook = Databook().build(cls.pkg["package_dir"])

    def test_report_deterministic(self):
        from app.level5_workspace.report import ReportAssembler
        r1 = ReportAssembler().build(self.databook)
        r2 = ReportAssembler().build(self.databook)
        self.assertEqual(r1, r2)

    def test_report_ten_sections(self):
        from app.level5_workspace.report import ReportAssembler
        self.assertEqual(len(ReportAssembler().build(self.databook)["sections"]), 10)

    def test_spa_complete(self):
        from app.level5_workspace.report import SPAExhibitBBuilder
        spa = SPAExhibitBBuilder().build(self.databook)
        for key in ("1_target_peg", "2_inclusions", "3_exclusions_debt_like", "4_indemnity_escrow"):
            self.assertIn(key, spa)

    def test_latency_monotonic_by_pushback_tier(self):
        svc = WorkspaceGatewayService()
        vague = svc.submit_irl_inquiry("s", "W", IRLPriority.P2_HIGH, "P06", "f",
                                       "send all contracts", [])
        specific = svc.submit_irl_inquiry("s", "W", IRLPriority.P2_HIGH, "P06", "f",
                                          "GL account 409000 register", [])
        # Tier 4 latency must exceed Tier 1 latency.
        self.assertGreater(vague["estimated_latency_hours"],
                           specific["estimated_latency_hours"])


if __name__ == "__main__":
    unittest.main()
