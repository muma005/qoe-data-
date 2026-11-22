"""
Test harness for Level 3: Multi-Agent Human Behavior & Friction Engine.

Validates the wealth-loss engine, 4-tier pushback state machine, fatigue/latency
models, 13-persona roster, interview simulator (verbal slips + banker intervention),
and the Nygard circuit breaker with heuristic fallback.
"""

import unittest
from dataclasses import replace
from decimal import Decimal

from app.level3_friction.pushback_fsm import (
    LATENCY_MULTIPLIER,
    FatigueAccumulator,
    LatencyScheduler,
    PushbackStateMachine,
    PushbackTier,
    WealthLossEngine,
    categorize_question,
)
from app.level3_friction.personas import (
    PERSONA_ROSTER,
    InquiryQueue,
    InterviewSimulator,
    Persona,
    VerbalSlipEngine,
)
from app.level3_friction.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    HeuristicFallbackEngine,
)


class TestWealthLossEngine(unittest.TestCase):
    def setUp(self):
        self.engine = WealthLossEngine(ev_multiple=10.0, cap_gains_tax=0.238)

    def test_enterprise_value_reduction(self):
        self.assertEqual(
            self.engine.enterprise_value_reduction([Decimal("100000")]),
            Decimal("1000000.00"),
        )

    def test_founder_personal_cash_loss_100k(self):
        # 100k haircut -> 1.0M EV reduction -> founder 65% -> $495,300 post-tax
        ev = self.engine.enterprise_value_reduction([Decimal("100000")])
        loss = self.engine.personal_cash_loss(ev, Decimal("0.65"))
        self.assertEqual(loss, Decimal("495300.00"))

    def test_cfo_personal_cash_loss_100k(self):
        # CFO 7.5% options -> $57,150 post-tax
        ev = self.engine.enterprise_value_reduction([Decimal("100000")])
        loss = self.engine.personal_cash_loss(ev, Decimal("0.075"))
        self.assertEqual(loss, Decimal("57150.00"))

    def test_founder_500k_haircut(self):
        ev = self.engine.enterprise_value_reduction([Decimal("500000")])
        loss = self.engine.personal_cash_loss(ev, Decimal("0.65"))
        self.assertEqual(loss, Decimal("2476500.00"))


class TestPushbackStateMachine(unittest.TestCase):
    def test_thresholds(self):
        sm = PushbackStateMachine()
        self.assertEqual(sm.tier_for(Decimal("99000")), PushbackTier.TIER_1_PROFESSIONAL_COOPERATION)
        self.assertEqual(sm.tier_for(Decimal("100000")), PushbackTier.TIER_2_PROCRASTINATION_DELAY)
        self.assertEqual(sm.tier_for(Decimal("350000")), PushbackTier.TIER_3_COMMERCIAL_PRESSURE)
        self.assertEqual(sm.tier_for(Decimal("800000")), PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION)

    def test_latency_multipliers(self):
        self.assertEqual(LATENCY_MULTIPLIER[PushbackTier.TIER_1_PROFESSIONAL_COOPERATION], 1.0)
        self.assertEqual(LATENCY_MULTIPLIER[PushbackTier.TIER_2_PROCRASTINATION_DELAY], 1.7)
        self.assertEqual(LATENCY_MULTIPLIER[PushbackTier.TIER_3_COMMERCIAL_PRESSURE], 2.8)
        self.assertEqual(LATENCY_MULTIPLIER[PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION], 4.5)

    def test_escalate_and_deescalate(self):
        sm = PushbackStateMachine()
        sm.notify_haircut(Decimal("400000"))
        self.assertEqual(sm.tier, PushbackTier.TIER_3_COMMERCIAL_PRESSURE)
        sm.resolve_concession()
        self.assertEqual(sm.tier, PushbackTier.TIER_2_PROCRASTINATION_DELAY)


class TestFatigueAndLatency(unittest.TestCase):
    def test_fatigue_accumulates_and_recovers(self):
        f = FatigueAccumulator(initial=0.0)
        # heavy month-end: 10 active requests, 50 duty hours
        f.step(active_requests=10, month_end_duty_hours=50)
        self.assertGreater(f.phi, 0.60)

    def test_severe_fatigue_typo_rate(self):
        f = FatigueAccumulator(initial=0.75)
        self.assertTrue(f.is_severe())
        self.assertEqual(f.typo_error_rate(), 0.048)
        f2 = FatigueAccumulator(initial=0.3)
        self.assertEqual(f2.typo_error_rate(), 0.015)

    def test_latency_scales_with_tier(self):
        sched = LatencyScheduler(seed=1)
        t1 = sched.schedule_delay_hours("routine", phi=0.0, psi=1.0)
        t4 = sched.schedule_delay_hours("routine", phi=0.0, psi=4.5)
        self.assertGreater(t4, t1)


class TestPersonas(unittest.TestCase):
    def test_thirteen_personas_three_groups(self):
        self.assertEqual(len(PERSONA_ROSTER), 13)
        groups = {p.group for p in PERSONA_ROSTER.values()}
        self.assertEqual(groups, {"A", "B", "C"})

    def test_knowledge_silo_isolation(self):
        vp_ops = PERSONA_ROSTER["P09"]
        self.assertIn("machine_run_hours", vp_ops.knowledge_silo)
        self.assertIn("us_gaap", vp_ops.blind_spots)  # ops does not know GAAP

        cfo = PERSONA_ROSTER["P06"]
        self.assertIn("ebitda_add_backs", cfo.knowledge_silo)
        self.assertEqual(cfo.active_coaching_status, "BANKER_MONITORED")

        bookkeeper = PERSONA_ROSTER["P08"]
        self.assertIn("transaction", bookkeeper.blind_spots)

    def test_ownership(self):
        self.assertEqual(PERSONA_ROSTER["P05"].ownership_pct, Decimal("0.65"))
        self.assertEqual(PERSONA_ROSTER["P06"].ownership_pct, Decimal("0.075"))

    def test_persona_state_schema(self):
        cfo = PERSONA_ROSTER["P06"]
        d = cfo.to_dict()
        for key in ("persona_id", "name", "role", "cumulative_haircuts_faced",
                    "personal_wealth_loss_dollars", "active_pushback_tier",
                    "cognitive_fatigue_index", "weekly_hours_logged",
                    "inquiry_latency_multiplier", "active_coaching_status",
                    "disclosed_anomalies_log", "withheld_anomalies_log"):
            self.assertIn(key, d)

    def test_apply_haircut_updates_state(self):
        founder = replace(PERSONA_ROSTER["P05"])
        sm = PushbackStateMachine()
        founder.apply_haircut(Decimal("500000"), WealthLossEngine(), sm)
        self.assertEqual(founder.personal_wealth_loss_dollars, Decimal("2476500.00"))
        self.assertEqual(founder.active_pushback_tier, PushbackTier.TIER_3_COMMERCIAL_PRESSURE)


class TestInterviewSimulator(unittest.TestCase):
    def test_verbal_slip_and_banker_intervention(self):
        sim = InterviewSimulator(seed=7)
        session = sim.start_session(["P09", "P12"], "Operations & Supply Chain")
        entry = sim.ask(session, "How did line 2 perform in Q3?", "P09")
        self.assertEqual(entry["speaker"], "P09")
        # Banker chaperone present + target persona -> intervention line appended
        speakers = [e["speaker"] for e in session.transcript]
        self.assertIn("P12", speakers)

    def test_interview_heuristic_fallback_flag(self):
        def failing(persona, question):
            raise RuntimeError("LLM 503")
        fallback = HeuristicFallbackEngine()
        breaker = CircuitBreaker(primary=failing, fallback=fallback)
        sim = InterviewSimulator(breaker=breaker)
        session = sim.start_session(["P06"], "Revenue Recognition")
        entry = sim.ask(session, "Explain your ASC 606 revenue recognition policy", "P06")
        self.assertTrue(entry["is_heuristic_fallback"])


class TestCircuitBreaker(unittest.TestCase):
    def test_trips_open_after_three_failures(self):
        def failing(persona, question):
            raise RuntimeError("LLM 429")
        fallback = HeuristicFallbackEngine()
        breaker = CircuitBreaker(primary=failing, fallback=fallback, failure_threshold=3)
        cfo = replace(PERSONA_ROSTER["P06"],
                      active_pushback_tier=PushbackTier.TIER_2_PROCRASTINATION_DELAY)
        for _ in range(3):
            text, is_fb = breaker.call(cfo, "inventory reserve question")
        self.assertEqual(breaker.state, CircuitState.OPEN)
        text, is_fb = breaker.call(cfo, "inventory reserve question")
        self.assertTrue(is_fb)
        self.assertIn("ASC 330", text)

    def test_heuristic_fallback_cfo_tier3(self):
        cfo = replace(PERSONA_ROSTER["P06"],
                      active_pushback_tier=PushbackTier.TIER_3_COMMERCIAL_PRESSURE)
        fallback = HeuristicFallbackEngine()
        text = fallback.respond(cfo, "Explain revenue recognition on custom assemblies")
        self.assertIn("ASC 606", text)
        self.assertIn("packing slips", text)

    def test_categorize_question(self):
        self.assertEqual(categorize_question("inventory obsolescence reserve"), "INVENTORY")
        self.assertEqual(categorize_question("software capitalization ASC 350"), "SOFTWARE_CAP")
        self.assertEqual(categorize_question("vendor volume rebate"), "REBATES")
        self.assertEqual(categorize_question("machine run hours and scrap"), "OPERATIONS")


class TestInquiryQueue(unittest.TestCase):
    def test_flood_cap_lp14(self):
        q = InquiryQueue()
        persona = PERSONA_ROSTER["P07"]
        for i in range(InquiryQueue.MAX_ACTIVE):
            q.submit(f"ITEM-{i}", persona, "routine voucher question", 100)
        with self.assertRaises(ValueError):
            q.submit("ITEM-OVER", persona, "another question", 100)


if __name__ == "__main__":
    unittest.main()
