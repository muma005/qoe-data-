"""
QoE Simulator - Level 3: Pushback State Machine, Executive Wealth Loss Engine,
Cognitive Fatigue Accumulator, and Log-Normal Latency Scheduler.

Implements the behavioral-state core of the Multi-Agent Human Behavior & Friction
Engine (03_multi_agent_human_behavior_and_friction_engine.md):

  - PushbackTier enum (mirrors proto/human_friction.proto).
  - 4-tier pushback finite state machine (TransDigm v. Alcoa thresholds).
  - Executive personal wealth loss engine (valuation multiple x ownership x after-tax).
  - Leaky-integrator cognitive fatigue accumulator (Phi in [0,1]).
  - Log-normal inquiry latency scheduler (DelayHours = exp(mu + sigma*Z) * (1+Phi) * Psi).

This module is dependency-free (stdlib only); personas.py and circuit_breaker.py
build on top of it.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, Sequence, Tuple


# ---------------------------------------------------------------------------
# Pushback tier enum (authoritative names from proto/human_friction.proto)
# ---------------------------------------------------------------------------
class PushbackTier(Enum):
    TIER_UNSPECIFIED = 0
    TIER_1_PROFESSIONAL_COOPERATION = 1
    TIER_2_PROCRASTINATION_DELAY = 2
    TIER_3_COMMERCIAL_PRESSURE = 3
    TIER_4_AGGRESSIVE_OBFUSCATION = 4


# Spec Section 5 stance labels (the human-facing posture behind each tier).
TIER_STANCE: Dict[PushbackTier, str] = {
    PushbackTier.TIER_1_PROFESSIONAL_COOPERATION: "Professional Alignment",
    PushbackTier.TIER_2_PROCRASTINATION_DELAY: "Technical Defense",
    PushbackTier.TIER_3_COMMERCIAL_PRESSURE: "Commercial Pressure",
    PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION: "Active Obfuscation",
}

# Spec Section 6.2 pushback latency multipliers (Psi).
LATENCY_MULTIPLIER: Dict[PushbackTier, float] = {
    PushbackTier.TIER_1_PROFESSIONAL_COOPERATION: 1.0,
    PushbackTier.TIER_2_PROCRASTINATION_DELAY: 1.7,
    PushbackTier.TIER_3_COMMERCIAL_PRESSURE: 2.8,
    PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION: 4.5,
}

# Spec Section 5.1 tier threshold matrix (cumulative EBITDA haircuts).
TIER2_THRESHOLD = Decimal("100000.0000")
TIER3_THRESHOLD = Decimal("350000.0000")
TIER4_THRESHOLD = Decimal("800000.0000")

# Spec Section 5.1 manifestation summaries (what the user experiences).
TIER_MANIFESTATION: Dict[PushbackTier, str] = {
    PushbackTier.TIER_1_PROFESSIONAL_COOPERATION:
        "Full, rapid compliance; answers delivered < 24h; minor clerical errors acknowledged openly.",
    PushbackTier.TIER_2_PROCRASTINATION_DELAY:
        "CFO cites specific US GAAP / ASC standards; proposes compromise calculations; latency 48-72h.",
    PushbackTier.TIER_3_COMMERCIAL_PRESSURE:
        "Sell-side banker intercepts requests; accuses 'academic re-trading'; banker calls PE Deal Lead.",
    PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION:
        "'Lost' historical files; selective document leaks; withholding of schedules; delays > 120h.",
}


# ---------------------------------------------------------------------------
# Shared inquiry categorizer (used by the verbal-slip and fallback engines)
# ---------------------------------------------------------------------------
def categorize_question(question: str) -> str:
    """Classifies an inquiry into a diligence topic category (spec Section 9.1)."""
    q = (question or "").lower()
    if any(k in q for k in ("inventory", "obsolescence", "lcnrv", "e&o", "stock", "dio")):
        return "INVENTORY"
    if any(k in q for k in ("software", "capitaliz", "r&d", "development", "asc 350", "asc350")):
        return "SOFTWARE_CAP"
    if any(k in q for k in ("rebate", "asc 705", "asc705", "vendor", "volume")):
        return "REBATES"
    if any(k in q for k in ("revenue", "asc 606", "asc606", "deferred", "recognition", "milestone")):
        return "REVENUE_RECOGNITION"
    if any(k in q for k in ("overhead", "absorption", "asc 330", "asc330", "idle", "capacity")):
        return "OVERHEAD"
    if any(k in q for k in ("machine", "downtime", "scrap", "run-hour", "run hour", "oee", "line 2",
                            "maintenance", "tooling", "plant")):
        return "OPERATIONS"
    if any(k in q for k in ("customer", "concentration", "churn", "pricing", "renewal")):
        return "CUSTOMER"
    return "GENERAL"


# ---------------------------------------------------------------------------
# Executive Personal Wealth Loss Engine (spec Section 4)
# ---------------------------------------------------------------------------
class WealthLossEngine:
    """Models the personal post-tax cash loss an executive suffers per EBITDA haircut.

    DeltaPersonalCash = (DeltaEV - DeltaClosingDebt) * ownership_pct * (1 - cap_gains_tax)
    DeltaEV          = sum(haircuts) * ev_multiple
    """

    def __init__(self, ev_multiple: float = 10.0, cap_gains_tax: float = 0.238):
        self.ev_multiple = Decimal(str(ev_multiple))
        self.cap_gains_tax = Decimal(str(cap_gains_tax))
        self.after_tax_factor = Decimal("1") - self.cap_gains_tax

    @staticmethod
    def _d(value) -> Decimal:
        return value if isinstance(value, Decimal) else Decimal(str(value))

    def enterprise_value_reduction(self, haircut_amounts: Sequence) -> Decimal:
        total = sum((self._d(a) for a in haircut_amounts), Decimal("0"))
        return (total * self.ev_multiple).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def personal_cash_loss(self, ev_reduction, ownership_pct,
                           closing_debt_delta=Decimal("0")) -> Decimal:
        net = self._d(ev_reduction) - self._d(closing_debt_delta)
        ownership = self._d(ownership_pct)
        return (net * ownership * self.after_tax_factor).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# 4-Tier Pushback Finite State Machine (spec Section 5)
# ---------------------------------------------------------------------------
class PushbackStateMachine:
    """Escalates/de-escalates management stance by cumulative haircut materiality."""

    def __init__(self):
        self.tier = PushbackTier.TIER_1_PROFESSIONAL_COOPERATION

    def tier_for(self, cumulative_haircuts) -> PushbackTier:
        c = Decimal(str(cumulative_haircuts))
        if c >= TIER4_THRESHOLD:
            return PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION
        if c >= TIER3_THRESHOLD:
            return PushbackTier.TIER_3_COMMERCIAL_PRESSURE
        if c >= TIER2_THRESHOLD:
            return PushbackTier.TIER_2_PROCRASTINATION_DELAY
        return PushbackTier.TIER_1_PROFESSIONAL_COOPERATION

    def notify_haircut(self, cumulative_haircuts) -> PushbackTier:
        """Recompute tier from cumulative haircuts (escalates as materiality rises)."""
        self.tier = self.tier_for(cumulative_haircuts)
        return self.tier

    def resolve_concession(self) -> PushbackTier:
        """De-escalate one tier when adjustments are substantiated / buyer concedes."""
        if self.tier.value > PushbackTier.TIER_1_PROFESSIONAL_COOPERATION.value:
            self.tier = PushbackTier(self.tier.value - 1)
        return self.tier

    def latency_multiplier(self, tier: PushbackTier = None) -> float:
        return LATENCY_MULTIPLIER[tier if tier is not None else self.tier]

    def stance(self, tier: PushbackTier = None) -> str:
        return TIER_STANCE[tier if tier is not None else self.tier]

    def manifestation(self, tier: PushbackTier = None) -> str:
        return TIER_MANIFESTATION[tier if tier is not None else self.tier]


# ---------------------------------------------------------------------------
# Cognitive Fatigue Accumulator (spec Section 6.1)
# ---------------------------------------------------------------------------
class FatigueAccumulator:
    """Leaky-integrator cognitive fatigue index Phi(t) in [0.0, 1.0].

    Phi(t) = Phi(t-1) * 0.85 + (ActiveRequests*1.5 + MonthEndDutyHours) / 80
    """

    RECOVERY_DECAY = 0.85
    SEVERE_THRESHOLD = 0.70
    NORMAL_TYPO_RATE = 0.015
    SEVERE_TYPO_RATE = 0.048

    def __init__(self, initial: float = 0.0):
        self.phi = max(0.0, min(1.0, float(initial)))

    def step(self, active_requests: float, month_end_duty_hours: float) -> float:
        self.phi = (self.phi * self.RECOVERY_DECAY
                    + (active_requests * 1.5 + month_end_duty_hours) / 80.0)
        self.phi = max(0.0, min(1.0, self.phi))
        return self.phi

    def is_severe(self) -> bool:
        return self.phi > self.SEVERE_THRESHOLD

    def typo_error_rate(self) -> float:
        return self.SEVERE_TYPO_RATE if self.is_severe() else self.NORMAL_TYPO_RATE

    def response_style(self) -> str:
        return "truncated" if self.is_severe() else "detailed"


# ---------------------------------------------------------------------------
# Log-Normal Inquiry Latency Scheduler (spec Section 6.2)
# ---------------------------------------------------------------------------
class LatencyScheduler:
    """DelayHours = exp(mu + sigma*Z) * (1 + Phi(t)) * Psi_Pushback."""

    SIGMA = 0.45
    BASELINE_MU = {"routine": 3.1, "customer_concentration": 4.3}

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def schedule_delay_hours(self, category: str = "routine", phi: float = 0.0,
                             psi: float = 1.0) -> float:
        mu = self.BASELINE_MU.get(category, self.BASELINE_MU["routine"])
        z = self.rng.gauss(0.0, 1.0)
        raw = math.exp(mu + self.SIGMA * z)
        return raw * (1.0 + phi) * psi
