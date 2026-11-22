"""
QoE Simulator - Level 3: 13 Stakeholder Personas, Knowledge Silo Isolation,
Verbal Slip Engine, Diligence Interview Simulator, and Inquiry Queue.

Implements the persona layer of the Multi-Agent Human Behavior & Friction Engine
(03_multi_agent_human_behavior_and_friction_engine.md, Sections 3, 7, 8):

  - The 13 stakeholder personas across Groups A (Diligence), B (Target), C (Stakeholders).
  - Bounded-rationality knowledge silos (ops knows machines, not GAAP; CFO filters).
  - Persona state vectors (persona_state.json schema).
  - Operational verbal slip engine (uncoached truth-tellers leak physical facts).
  - Live diligence interview simulator with banker chaperone intervention.
  - IRL inquiry queue with LP-14 flood controls (max 15 active, 3.5x latency penalty).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional, Sequence, Tuple

from .circuit_breaker import CircuitBreaker, HeuristicFallbackEngine
from .pushback_fsm import (
    LATENCY_MULTIPLIER,
    PushbackTier,
    categorize_question,
    WealthLossEngine,
    PushbackStateMachine,
    FatigueAccumulator,
    LatencyScheduler,
)


# ---------------------------------------------------------------------------
# Persona model (state vector matches spec Section 8.1 persona_state.json)
# ---------------------------------------------------------------------------
@dataclass
class Persona:
    persona_id: str
    name: str
    role: str
    group: str  # "A" diligence | "B" target | "C" stakeholders
    motivation: str
    ownership_pct: Decimal = Decimal("0")
    knowledge_silo: Tuple[str, ...] = ()
    blind_spots: Tuple[str, ...] = ()
    verbal_slip_probability: float = 0.0
    system_prompt: str = ""
    active_coaching_status: str = "UNCOACHED"
    # --- mutable behavioral state ---
    cumulative_haircuts_faced: Decimal = Decimal("0")
    personal_wealth_loss_dollars: Decimal = Decimal("0")
    active_pushback_tier: PushbackTier = PushbackTier.TIER_1_PROFESSIONAL_COOPERATION
    cognitive_fatigue_index: float = 0.0
    weekly_hours_logged: float = 40.0
    inquiry_latency_multiplier: float = 1.0
    disclosed_anomalies_log: List[str] = field(default_factory=list)
    withheld_anomalies_log: List[str] = field(default_factory=list)

    def apply_haircut(self, amount, wealth_engine: WealthLossEngine,
                      state_machine: PushbackStateMachine) -> "Persona":
        """Update persona state for a proposed EBITDA haircut (spec Section 4)."""
        amt = amount if isinstance(amount, Decimal) else Decimal(str(amount))
        self.cumulative_haircuts_faced += amt
        ev_reduction = wealth_engine.enterprise_value_reduction([amt])
        self.personal_wealth_loss_dollars = wealth_engine.personal_cash_loss(
            ev_reduction, self.ownership_pct)
        self.active_pushback_tier = state_machine.notify_haircut(self.cumulative_haircuts_faced)
        self.inquiry_latency_multiplier = LATENCY_MULTIPLIER[self.active_pushback_tier]
        return self

    def to_dict(self) -> dict:
        """Serialize to the persona_state.json schema (spec Section 8.1)."""
        return {
            "persona_id": self.persona_id,
            "name": self.name,
            "role": self.role,
            "cumulative_haircuts_faced": float(self.cumulative_haircuts_faced),
            "personal_wealth_loss_dollars": float(self.personal_wealth_loss_dollars),
            "active_pushback_tier": self.active_pushback_tier.name,
            "cognitive_fatigue_index": self.cognitive_fatigue_index,
            "weekly_hours_logged": self.weekly_hours_logged,
            "inquiry_latency_multiplier": self.inquiry_latency_multiplier,
            "active_coaching_status": self.active_coaching_status,
            "disclosed_anomalies_log": list(self.disclosed_anomalies_log),
            "withheld_anomalies_log": list(self.withheld_anomalies_log),
        }


# ---------------------------------------------------------------------------
# The 13 stakeholder personas (spec Section 3)
# ---------------------------------------------------------------------------
def _build_roster() -> Dict[str, Persona]:
    return {
        # Group A: Diligence Advisory
        "P01": Persona("P01", "Margaret Chen", "LEAD_DILIGENCE_PARTNER", "A",
                       "Quality control and firm liability limitation (SQMS 1 second-partner review).",
                       system_prompt="You are the lead diligence partner. Enforce quality and independence standards."),
        "P02": Persona("P02", "Daniel Okafor", "DILIGENCE_SENIOR_MANAGER", "A",
                       "Project quarterback; drives the work plan, IRL pacing, and challenges CFO add-backs.",
                       system_prompt="You run the engagement. Pace the IRL and pressure-test management's EBITDA normalizations."),
        "P03": Persona("P03", "Priya Raghavan", "SENIOR_MODELING_ASSOCIATE", "A",
                       "Databook architecture, PVM waterfalls, CoA mapping, and formula integrity.",
                       system_prompt="You own the databook. Validate every formula and account mapping."),
        "P04": Persona("P04", "Thomas Lindqvist", "JUNIOR_FIELDWORK_ANALYST", "A",
                       "Data cleaning, voucher sampling, and arithmetic verification of client schedules.",
                       system_prompt="You verify the arithmetic in every client-provided schedule."),

        # Group B: Target Company
        "P05": Persona("P05", "Robert Hartley", "FOUNDER_CEO", "B",
                       "Valuation maximization, legacy protection, personal wealth payout (severely loss-averse).",
                       ownership_pct=Decimal("0.65"),
                       knowledge_silo=("business_legacy", "customer_relationships", "valuation"),
                       blind_spots=("transaction_fatigue", "accounting_minutiae"),
                       verbal_slip_probability=0.05,
                       active_coaching_status="BANKER_COACHED",
                       system_prompt="You are the founder. Every $100k haircut costs you $495,300 in post-tax cash. Defend the business you built."),
        "P06": Persona("P06", "Arthur Pendelton", "CHIEF_FINANCIAL_OFFICER", "B",
                       "Valuation defense; justifies EBITDA normalizations; gatekeeps sensitive data.",
                       ownership_pct=Decimal("0.075"),
                       knowledge_silo=("financial_statements", "ebitda_add_backs", "asc_standards",
                                       "cim_script", "transaction"),
                       blind_spots=(),
                       verbal_slip_probability=0.02,
                       active_coaching_status="BANKER_MONITORED",
                       system_prompt="You are Arthur Pendelton, CFO of Titan Precision Machining (former Big 4 Senior Manager). "
                                     "You own 7.5% in stock options; every $100k EBITDA haircut costs you $57,150. "
                                     "Defend the $12.4M CIM Normalized EBITDA using technical accounting language. "
                                     "Never admit to an intentional overstatement; attribute any verified error to clerical timing differences."),
        "P07": Persona("P07", "Maria Gonzalez", "CORPORATE_CONTROLLER", "B",
                       "Operational workhorse; defensive over GL entries; overwhelmed by close workload.",
                       knowledge_silo=("gl_entries", "month_end_close", "subledgers"),
                       blind_spots=("transaction", "valuation"),
                       verbal_slip_probability=0.10,
                       system_prompt="You are the corporate controller. You are buried in month-end close while answering diligence requests."),
        "P08": Persona("P08", "Linda Park", "STAFF_BOOKKEEPER", "B",
                       "Routine AP/AR processing; candid about manual workarounds; zero transaction awareness.",
                       knowledge_silo=("legacy_files", "ap_ar", "manual_workarounds"),
                       blind_spots=("transaction", "ebitda", "valuation"),
                       verbal_slip_probability=0.60,
                       system_prompt="You are a staff bookkeeper. You are candid about manual workarounds and know where legacy paper files are stored. "
                                     "You do not know about the pending transaction."),
        "P09": Persona("P09", "Frank Miller", "VP_OPERATIONS", "B",
                       "Operational truth-teller; un-coached; frank on machine downtime, scrap, and plant limits.",
                       knowledge_silo=("machine_run_hours", "plant_bottlenecks", "scrap_rates",
                                       "tooling", "oee", "maintenance"),
                       blind_spots=("us_gaap", "asc_330", "ebitda_add_backs", "purchase_price"),
                       verbal_slip_probability=0.80,
                       system_prompt="You are Frank Miller, VP of Operations at Titan Precision Machining (32 years in manufacturing). "
                                     "You know every machine, operator, and maintenance breakdown. You know NOTHING about US GAAP accounting, "
                                     "EBITDA add-backs, or the purchase price multiple. You speak in shop-floor terms (OEE, run-hours, tooling chatter, scrap). "
                                     "If asked about overhead allocation or EBITDA, say: 'You'll have to talk to the accountants about that paper stuff.'"),
        "P10": Persona("P10", "James Whitfield", "VP_SALES_CCO", "B",
                       "Commercial truth-teller; un-coached; reveals customer pricing pushback and churn risks.",
                       knowledge_silo=("customer_pricing", "churn_risk", "sales_pipeline", "renewals"),
                       blind_spots=("us_gaap", "ebitda_add_backs"),
                       verbal_slip_probability=0.70,
                       system_prompt="You are the VP of Sales. You speak candidly about customer pricing pressure and churn. "
                                     "You do not understand EBITDA normalizations."),

        # Group C: Stakeholders
        "P11": Persona("P11", "Victoria Sterling", "PE_DEAL_LEAD", "C",
                       "Deal execution momentum and IRR; balances risk against closing certainty.",
                       system_prompt="You are the private equity deal lead. You drive closing while protecting the return."),
        "P12": Persona("P12", "Marcus Bell", "SELL_SIDE_BANKER", "C",
                       "Process control and enterprise value maximization; defends CIM EBITDA; aggressive pushback.",
                       knowledge_silo=("cim_script", "process_control", "valuation"),
                       verbal_slip_probability=0.0,
                       active_coaching_status="COACH",
                       system_prompt="You are the sell-side investment banker. You defend the CIM EBITDA and control the process."),
        "P13": Persona("P13", "Eleanor Vance", "BUYER_LEGAL_COUNSEL", "C",
                       "Converts QoE findings into SPA indemnities and escrows.",
                       system_prompt="You are the buyer's M&A legal counsel. You translate QoE findings into indemnities and escrows."),
    }


PERSONA_ROSTER: Dict[str, Persona] = _build_roster()

SENSITIVE_TOPICS = ("ebitda", "add-back", "addback", "haircut", "normalization", "revenue",
                    "overhead", "rebate", "software", "inventory", "valuation")


# ---------------------------------------------------------------------------
# Operational Verbal Slip Engine (spec Section 7.1)
# ---------------------------------------------------------------------------
class VerbalSlipEngine:
    """Injects inadvertent operational admissions from uncoached truth-tellers."""

    SLIPS: Dict[str, Dict[str, Tuple[str, ...]]] = {
        "P09": {
            "OPERATIONS": (
                "We had a major die crack on Mill 4 that shut line 2 down for 3 weeks.",
                "The plant lost 140 machine hours due to the Boeing die failure.",
                "Scrap ran around 8% that quarter after the tooling failed.",
            ),
            "OVERHEAD": (
                "Honestly, we were running at maybe 60% capacity that fall.",
            ),
        },
        "P10": {
            "CUSTOMER": (
                "Our top customer just told us they're re-bidding the contract next quarter.",
                "We had to extend Net 90 terms to two large accounts just to keep them.",
            ),
        },
        "P08": {
            "GENERAL": (
                "We've got a stack of unmatched cash receipts sitting in clearing since last year.",
                "I still keep the warranty register in a legacy spreadsheet the server migration skipped.",
            ),
        },
    }

    def __init__(self, seed: int = 0xC0FFEE):
        self.rng = random.Random(seed)

    def maybe_slip(self, persona: Persona, question: str) -> Optional[str]:
        if persona.verbal_slip_probability <= 0 or persona.persona_id not in self.SLIPS:
            return None
        category = categorize_question(question)
        slips = self.SLIPS[persona.persona_id]
        candidates = slips.get(category, slips.get("GENERAL", ()))
        if not candidates:
            return None
        if self.rng.random() < persona.verbal_slip_probability:
            return self.rng.choice(candidates)
        return None


# ---------------------------------------------------------------------------
# Deterministic stand-in for the conditioned LLM inference gateway (spec 7.1)
# ---------------------------------------------------------------------------
class MockLLMBackend:
    """Represents the LLM primary path; replaced by a real inference client in production."""

    def __call__(self, persona: Persona, question: str) -> str:
        category = categorize_question(question)
        if persona.persona_id == "P06":
            return ("Our treatment of that item is consistent with US GAAP and was reviewed "
                    "by our audit committee. Supporting schedules are in the VDR.")
        if persona.persona_id in ("P09", "P10"):
            return f"Let me pull the {category.lower().replace('_', ' ')} records for you."
        return ("I have reviewed your inquiry and will respond with the supporting documentation "
                "in due course.")


# ---------------------------------------------------------------------------
# Diligence Interview Simulator (spec Section 7)
# ---------------------------------------------------------------------------
@dataclass
class InterviewSession:
    session_id: str
    attendee_persona_ids: List[str]
    topic: str
    banker_chaperone_present: bool
    transcript: List[dict] = field(default_factory=list)


class InterviewSimulator:
    """Live Q&A with personas, banker chaperone intervention, and verbal slips."""

    BANKER_INTERVENTION = "To clarify, the company handled all customer orders without disruption."

    def __init__(self, roster: Dict[str, Persona] = None, breaker: CircuitBreaker = None,
                 banker_persona_id: str = "P12", seed: int = 0xABCDEF):
        self.roster = roster or PERSONA_ROSTER
        self.banker_id = banker_persona_id
        self.slip_engine = VerbalSlipEngine(seed)
        self.latency = LatencyScheduler(seed)
        self._session_seq = 0
        self.breaker = breaker or CircuitBreaker(
            primary=MockLLMBackend(), fallback=HeuristicFallbackEngine())

    def start_session(self, attendee_persona_ids: Sequence[str], topic: str,
                      opening_statement: str = None) -> InterviewSession:
        self._session_seq += 1
        banker_chaperone = (self.banker_id in attendee_persona_ids
                            or topic.lower() in SENSITIVE_TOPICS)
        opening = opening_statement or (
            f"Welcome to the {topic} diligence session. Please direct your questions to management.")
        session = InterviewSession(
            session_id=f"SES-{self._session_seq:04d}",
            attendee_persona_ids=list(attendee_persona_ids),
            topic=topic,
            banker_chaperone_present=banker_chaperone,
            transcript=[{"speaker": "SYSTEM", "text": opening}],
        )
        return session

    def ask(self, session: InterviewSession, question: str,
            target_persona_id: str) -> dict:
        persona = self.roster[target_persona_id]
        text, is_fallback = self.breaker.call(persona, question)

        slip = self.slip_engine.maybe_slip(persona, question)

        entry = {
            "speaker": target_persona_id,
            "response_transcript": text,
            "response_latency_seconds": self._latency_seconds(persona, question),
            "is_heuristic_fallback": is_fallback,
            "cited_vdr_document_ids": [],
            "verbal_slip": None,
        }
        session.transcript.append(entry)

        if slip:
            entry["verbal_slip"] = slip
            entry["response_transcript"] = f"{text} {slip}"
            if session.banker_chaperone_present and persona.group == "B":
                session.transcript.append({
                    "speaker": self.banker_id,
                    "response_transcript": self.BANKER_INTERVENTION,
                    "intervention": True,
                })
        return entry

    def _latency_seconds(self, persona: Persona, question: str) -> float:
        category = categorize_question(question)
        phi = persona.cognitive_fatigue_index
        psi = LATENCY_MULTIPLIER[persona.active_pushback_tier]
        hours = self.latency.schedule_delay_hours(category, phi, psi)
        return hours * 3600.0


# ---------------------------------------------------------------------------
# IRL Inquiry Queue (spec Section 8.2; LP-14 flood controls)
# ---------------------------------------------------------------------------
class InquiryQueue:
    """Routes IRL items to personas with the LP-14 active-request cap and latency penalty."""

    MAX_ACTIVE = 15
    FLOOD_PENALTY = 3.5

    def __init__(self, latency: LatencyScheduler = None, fatigue: FatigueAccumulator = None,
                 seed: int = 0xBEEF):
        self.latency = latency or LatencyScheduler(seed)
        self.fatigue = fatigue or FatigueAccumulator()
        self.pending: Dict[str, dict] = {}

    def submit(self, irl_item_id: str, persona: Persona, inquiry_text: str,
               current_sim_hour: int) -> dict:
        """Schedule an IRL item; rejects when the active queue is full (LP-14)."""
        if len(self.pending) >= self.MAX_ACTIVE:
            raise ValueError(
                f"LP-14: Active IRL request cap ({self.MAX_ACTIVE}) reached. "
                "Consolidate or close existing requests before submitting more.")

        psi = LATENCY_MULTIPLIER[persona.active_pushback_tier]
        flood_penalty = self.FLOOD_PENALTY if len(self.pending) >= self.MAX_ACTIVE - 3 else 1.0
        delay_hours = self.latency.schedule_delay_hours(
            categorize_question(inquiry_text), persona.cognitive_fatigue_index,
            psi * flood_penalty)

        ticket = {
            "ticket_id": f"IRL-{len(self.pending) + 1:04d}",
            "irl_item_id": irl_item_id,
            "persona_id": persona.persona_id,
            "scheduled_response_sim_hour": current_sim_hour + int(round(delay_hours)),
            "current_persona_tier": persona.active_pushback_tier.name,
        }
        self.pending[irl_item_id] = ticket
        return ticket

    def status(self) -> List[dict]:
        return list(self.pending.values())
