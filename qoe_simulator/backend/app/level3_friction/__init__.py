"""
Level 3: Multi-Agent Human Behavior & Friction Engine (human-friction).

Public surface for the persona layer, pushback state machine, wealth loss engine,
fatigue/latency models, interview simulator, and circuit breaker.
"""

from .pushback_fsm import (
    PushbackTier,
    TIER_STANCE,
    LATENCY_MULTIPLIER,
    WealthLossEngine,
    PushbackStateMachine,
    FatigueAccumulator,
    LatencyScheduler,
    categorize_question,
)
from .circuit_breaker import (
    CircuitState,
    CircuitBreaker,
    HeuristicFallbackEngine,
)
from .personas import (
    Persona,
    PERSONA_ROSTER,
    VerbalSlipEngine,
    MockLLMBackend,
    InterviewSession,
    InterviewSimulator,
    InquiryQueue,
)

__all__ = [
    "PushbackTier",
    "TIER_STANCE",
    "LATENCY_MULTIPLIER",
    "WealthLossEngine",
    "PushbackStateMachine",
    "FatigueAccumulator",
    "LatencyScheduler",
    "categorize_question",
    "CircuitState",
    "CircuitBreaker",
    "HeuristicFallbackEngine",
    "Persona",
    "PERSONA_ROSTER",
    "VerbalSlipEngine",
    "MockLLMBackend",
    "InterviewSession",
    "InterviewSimulator",
    "InquiryQueue",
]
