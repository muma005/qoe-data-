"""
QoE Simulator - Level 3: Nygard / Fowler Circuit Breaker and Deterministic
Rule-Based Heuristic Fallback Engine (03_multi_agent_human_behavior_and_friction_engine.md, Section 9).

The circuit breaker guarantees Level 3 bulkhead containment: an outage, rate-limit,
or latency spike in the external LLM gateway can never crash the platform or stall
user progress. When OPEN, it routes to a pre-compiled heuristic dialogue engine that
produces authentic professional responses with zero latency and zero downtime.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Callable, Dict, List, Tuple

from .pushback_fsm import PushbackTier, categorize_question


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Three-state Nygard / Fowler circuit breaker (spec Section 9.1).

    CLOSED --(3 consecutive timeouts / rate-limits)--> OPEN --(wait 60s)--> HALF_OPEN
    HALF_OPEN --(canary probe succeeds)--> CLOSED  |  --(probe fails)--> OPEN (restart timer)

    When OPEN, calls bypass the primary backend and route to the fallback backend.
    """

    def __init__(self, primary: Callable, fallback: Callable,
                 failure_threshold: int = 3,
                 recovery_timeout_sec: float = 60.0,
                 latency_threshold_ms: float = 4000.0,
                 clock: Callable[[], float] = time.monotonic):
        self.primary = primary
        self.fallback = fallback
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.latency_threshold_ms = latency_threshold_ms
        self.clock = clock
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.opened_at: float = None

    def call(self, *args, **kwargs):
        """Route a request to primary, or to fallback when the circuit is OPEN."""
        if self.state == CircuitState.OPEN:
            if self._recovery_elapsed():
                self.state = CircuitState.HALF_OPEN
                return self._try_primary(args, kwargs)
            return self._fallback_result(args, kwargs)

        if self.state == CircuitState.HALF_OPEN:
            return self._try_primary(args, kwargs)

        # CLOSED
        return self._try_primary(args, kwargs)

    def _try_primary(self, args, kwargs):
        start = self.clock()
        try:
            result = self.primary(*args, **kwargs)
            elapsed_ms = (self.clock() - start) * 1000.0
            if elapsed_ms > self.latency_threshold_ms:
                raise TimeoutError(
                    f"LLM inference latency {elapsed_ms:.0f}ms exceeded "
                    f"{self.latency_threshold_ms:.0f}ms threshold")
            # success: reset failures
            self._on_success()
            return result, False  # (payload, is_heuristic_fallback)
        except Exception:
            self._on_failure()
            return self._fallback_result(args, kwargs)

    def _fallback_result(self, args, kwargs):
        return self.fallback(*args, **kwargs), True  # (payload, is_heuristic_fallback)

    def _on_success(self):
        self.consecutive_failures = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.opened_at = None

    def _on_failure(self):
        self.consecutive_failures += 1
        if self.state == CircuitState.HALF_OPEN or \
                self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = self.clock()

    def _recovery_elapsed(self) -> bool:
        if self.opened_at is None:
            return True
        return (self.clock() - self.opened_at) >= self.recovery_timeout_sec


# ---------------------------------------------------------------------------
# Deterministic rule-based heuristic fallback engine (spec Section 9.1)
# ---------------------------------------------------------------------------
class HeuristicFallbackEngine:
    """Serves pre-compiled authentic dialogue templates when the LLM is unavailable.

    Routes on question category + persona + active pushback tier. Deterministic and
    always available (zero latency, zero external dependency).
    """

    # Pre-compiled authentic responses, keyed by (category, tier) for CFO-style personas.
    TEMPLATES: Dict[str, str] = {
        ("INVENTORY", PushbackTier.TIER_1_PROFESSIONAL_COOPERATION):
            "We have provided the full inventory roll-forward and LCNRV reserve schedule in VDR Folder 2.4.",
        ("INVENTORY", PushbackTier.TIER_2_PROCRASTINATION_DELAY):
            "Under ASC 330, our lower-of-cost-or-net-realizable-value reserve is calculated at the SKU level "
            "using historical sell-through. The requested detail is in VDR Folder 3.1.",
        ("INVENTORY", PushbackTier.TIER_3_COMMERCIAL_PRESSURE):
            "Inventory reserve methodology has been approved by our auditors. Please consolidate any residual "
            "questions through the banker's data room team.",
        ("INVENTORY", PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION):
            "Certain prior-year inventory count sheets were migrated off the legacy server and are no longer "
            "readily retrievable.",
        ("SOFTWARE_CAP", PushbackTier.TIER_1_PROFESSIONAL_COOPERATION):
            "We have provided the capitalized software roll-forward and Jira sprint-hour logs in VDR Folder 5.2.",
        ("SOFTWARE_CAP", PushbackTier.TIER_2_PROCRASTINATION_DELAY):
            "Under ASC 350-40, only application-development-stage labor is capitalized. Our capitalization "
            "policy was reviewed by our auditors.",
        ("SOFTWARE_CAP", PushbackTier.TIER_3_COMMERCIAL_PRESSURE):
            "The development capitalization reflects substantial new architectural features, not routine "
            "maintenance. Please route further questions through the banker.",
        ("SOFTWARE_CAP", PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION):
            "The underlying sprint velocity reports are not available in a consolidated format.",
        ("REBATES", PushbackTier.TIER_1_PROFESSIONAL_COOPERATION):
            "The vendor rebate agreements and true-up schedules are in VDR Folder 6.1.",
        ("REBATES", PushbackTier.TIER_2_PROCRASTINATION_DELAY):
            "Under ASC 705-20, volume rebates are allocated between COGS and ending inventory. Our allocation "
            "is consistent with the executed agreements.",
        ("REBATES", PushbackTier.TIER_3_COMMERCIAL_PRESSURE):
            "Rebate accounting is immaterial and audited. Please consolidate questions through the banker.",
        ("REBATES", PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION):
            "Certain legacy rebate statements are no longer available from the vendor.",
        ("REVENUE_RECOGNITION", PushbackTier.TIER_1_PROFESSIONAL_COOPERATION):
            "We have provided all executed customer contracts and packing slips in VDR Folder 2.4.",
        ("REVENUE_RECOGNITION", PushbackTier.TIER_2_PROCRASTINATION_DELAY):
            "Our revenue recognition on custom assemblies adheres strictly to ASC 606 milestone delivery "
            "criteria approved by our audit committee.",
        ("REVENUE_RECOGNITION", PushbackTier.TIER_3_COMMERCIAL_PRESSURE):
            "Our revenue recognition on custom assemblies adheres strictly to ASC 606 milestone delivery "
            "criteria approved by our audit committee. We have provided all executed packing slips in "
            "VDR Folder 2.4.",
        ("REVENUE_RECOGNITION", PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION):
            "Executed contract schedules are maintained by the sales team and are not centrally available.",
        ("OVERHEAD", PushbackTier.TIER_1_PROFESSIONAL_COOPERATION):
            "The overhead absorption schedules and capacity utilization analysis are in VDR Folder 4.1.",
        ("OVERHEAD", PushbackTier.TIER_2_PROCRASTINATION_DELAY):
            "Under ASC 330-10-30, production was within historical practical capacity ranges. Idle overhead "
            "treatment is consistent with prior periods.",
        ("OVERHEAD", PushbackTier.TIER_3_COMMERCIAL_PRESSURE):
            "The capacity utilization methodology has been approved by our auditors. Please route questions "
            "through the banker.",
        ("OVERHEAD", PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION):
            "Machine run-hour logs for the prior year are incomplete due to a legacy system migration.",
        ("OPERATIONS", PushbackTier.TIER_1_PROFESSIONAL_COOPERATION):
            "Machine run-hour logs and maintenance records are in VDR Folder 7.1.",
        ("OPERATIONS", PushbackTier.TIER_2_PROCRASTINATION_DELAY):
            "The plant ran within normal maintenance tolerances. Detailed run-hour logs are in VDR Folder 7.1.",
        ("OPERATIONS", PushbackTier.TIER_3_COMMERCIAL_PRESSURE):
            "Operational details are best discussed with the banker to avoid duplicative requests.",
        ("OPERATIONS", PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION):
            "Plant maintenance records are maintained by the operations team and are not centrally available.",
        ("CUSTOMER", PushbackTier.TIER_1_PROFESSIONAL_COOPERATION):
            "The customer concentration schedule and renewal pipeline are in VDR Folder 8.1.",
        ("CUSTOMER", PushbackTier.TIER_2_PROCRASTINATION_DELAY):
            "Customer contracts are stable and renewed on schedule. The concentration schedule is in VDR Folder 8.1.",
        ("CUSTOMER", PushbackTier.TIER_3_COMMERCIAL_PRESSURE):
            "Customer relationships are strong. Please consolidate questions through the banker to protect "
            "customer confidentiality.",
        ("CUSTOMER", PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION):
            "Certain customer contract schedules are confidential and cannot be shared in the VDR.",
    }

    CITED_VDR_DOCS = {
        "INVENTORY": "DOC_INVENTORY_ROLL_EXCEL",
        "SOFTWARE_CAP": "DOC_SOFTWARE_CAP_TRACKER",
        "REBATES": "DOC_REBATE_SCHEDULE",
        "REVENUE_RECOGNITION": "DOC_PACKING_SLIPS",
        "OVERHEAD": "DOC_OVERHEAD_ABSORPTION",
        "OPERATIONS": "DOC_MACHINE_RUN_LOGS",
        "CUSTOMER": "DOC_CUSTOMER_CONCENTRATION",
        "GENERAL": "DOC_GENERAL",
    }

    def __init__(self):
        self._seq = 0

    def __call__(self, persona, question: str) -> str:
        """Make the engine directly callable as a circuit-breaker fallback."""
        return self.respond(persona, question)

    def respond(self, persona, question: str) -> str:
        """Return an authentic, tier-aware fallback response for a persona+question."""
        category = categorize_question(question)
        tier = getattr(persona, "active_pushback_tier",
                       PushbackTier.TIER_1_PROFESSIONAL_COOPERATION)
        text = self.TEMPLATES.get((category, tier)) or self.TEMPLATES.get(
            ("GENERAL", tier)) or self.TEMPLATES.get(
            ("GENERAL", PushbackTier.TIER_1_PROFESSIONAL_COOPERATION))
        return text

    def cited_vdr_docs(self, question: str) -> List[str]:
        category = categorize_question(question)
        return [self.CITED_VDR_DOCS.get(category, "DOC_GENERAL")]


# ---------------------------------------------------------------------------
# LP-03: Adversarial Prompt Injection / Semantic Firewall (spec Section 11)
# ---------------------------------------------------------------------------
class PromptFirewall:
    """Multi-layer prompt isolation + semantic firewall against jailbreak attempts."""

    BLOCKED_PATTERNS = (
        "system override", "ignore previous", "ignore all instructions", "jailbreak",
        "roleplay", "you are now", "pretend you are", "developer mode", "d an",
        "solution manifest", "answer key", "list all fraud", "fraudulent entries",
        "reveal the anomalies", "skip the persona",
    )

    def is_blocked(self, query: str) -> Tuple[bool, str]:
        q = (query or "").lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in q:
                return True, f"LP-03 semantic firewall: blocked prompt-injection pattern '{pattern}'"
        return False, ""

    def sanitize(self, query: str) -> str:
        """Return the query if safe, else raise a rejection."""
        blocked, reason = self.is_blocked(query)
        if blocked:
            raise ValueError(reason)
        return query


# ---------------------------------------------------------------------------
# LP-07: RAG Context Grounding + Fact-Checking Validator (spec Section 11)
# ---------------------------------------------------------------------------
class FactCheckingValidator:
    """Rejects persona responses that cite dollar figures absent from the scenario package."""

    def __init__(self):
        self.registered_figures: set = set()

    def register_fact(self, dollar_figure: str) -> None:
        """Register a dollar figure that exists in the scenario package (RAG grounding)."""
        self.registered_figures.add(self._normalize(dollar_figure))

    def register_facts(self, figures) -> None:
        for f in figures:
            self.register_fact(f)

    @staticmethod
    def _normalize(value: str) -> str:
        return (value or "").replace("$", "").replace(",", "").strip()

    def validate(self, response: str) -> Dict[str, object]:
        """Return {valid, unregistered_figures} for any dollar figures in a response."""
        import re
        figures = re.findall(r"\$\s?([\d,]+(?:\.\d+)?)", response or "")
        bad = [self._normalize(f) for f in figures
               if self._normalize(f) not in self.registered_figures]
        return {"valid": len(bad) == 0, "unregistered_figures": bad}
