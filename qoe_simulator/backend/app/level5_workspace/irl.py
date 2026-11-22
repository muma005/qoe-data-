"""
QoE Simulator - Level 5: Information Request List (IRL) Console.

Implements spec Sections 4, 7.1 and LP-15:

  - Priority tagging (P1 Critical / P2 High / P3 Routine).
  - Multi-turn query threading (turn_id, sender, timestamp, text, attachments).
  - Tiered Executive Attention Quota (max 5 active P1 inquiries, LP-15).
  - Overly-broad-request detection -> Pushback Tier escalation + scoring penalty.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional


class IRLPriority(Enum):
    IRL_PRIORITY_UNSPECIFIED = 0
    P1_CRITICAL = 1
    P2_HIGH = 2
    P3_ROUTINE = 3


VAGUE_INQUIRY_MARKERS = (
    "all contracts", "all invoices", "send everything", "tell me what's wrong",
    "what's wrong with ebitda", "all documents", "everything",
)


class IRLConsole:
    """Living IRL with priority, latency, threading, and LP-15 attention quota."""

    MAX_ACTIVE_P1 = 5

    def __init__(self):
        self.requests: Dict[str, dict] = {}
        self._seq = 0

    @property
    def active_p1_count(self) -> int:
        return sum(1 for r in self.requests.values()
                   if r["priority"] == IRLPriority.P1_CRITICAL.value
                   and r["status"] in ("IN_PROGRESS", "PARTIALLY_ANSWERED", "PENDING"))

    def is_vague(self, inquiry_body: str) -> bool:
        return any(m in (inquiry_body or "").lower() for m in VAGUE_INQUIRY_MARKERS)

    def submit(self, engagement_id: str, workstream_code: str, priority: IRLPriority,
               target_persona_id: str, subject: str, inquiry_body: str,
               cited_vdr_doc_ids: List[str], sim_day: int,
               latency_hours: float = 0.0) -> Dict[str, object]:
        # LP-15: Executive Attention Quota (max 5 active P1)
        if priority == IRLPriority.P1_CRITICAL and self.active_p1_count >= self.MAX_ACTIVE_P1:
            return {
                "request_id": "",
                "status": "REJECTED_ATTENTION_QUOTA",
                "sim_day_submitted": sim_day,
                "estimated_latency_hours": latency_hours,
                "pushback_tier_triggered": "TIER_3_COMMERCIAL_PRESSURE",
                "thread_history": [],
            }

        # LP-15: overly-broad requests trigger pushback escalation + penalty
        pushback = "TIER_1_PROFESSIONAL_COOPERATION"
        if self.is_vague(inquiry_body):
            pushback = "TIER_4_AGGRESSIVE_OBFUSCATION"

        self._seq += 1
        request_id = f"IRL_REQ_{self._seq:04d}"
        turn = {
            "turn_id": 1,
            "sender_persona_id": "USER_ANALYST",
            "sender_display_name": "Diligence Analyst",
            "sent_at": f"2024-10-14T10:00:00Z",
            "message_text": inquiry_body,
            "attached_document_ids": list(cited_vdr_doc_ids),
        }
        self.requests[request_id] = {
            "request_id": request_id,
            "engagement_id": engagement_id,
            "workstream_code": workstream_code,
            "priority": priority.value,
            "target_persona_id": target_persona_id,
            "subject": subject,
            "status": "IN_PROGRESS",
            "sim_day_submitted": sim_day,
            "estimated_latency_hours": latency_hours,
            "pushback_tier_triggered": pushback,
            "thread_history": [turn],
        }
        return self.requests[request_id]

    def append_turn(self, request_id: str, sender_persona_id: str,
                    sender_display_name: str, message_text: str,
                    attached_document_ids: Optional[List[str]] = None) -> Optional[dict]:
        req = self.requests.get(request_id)
        if not req:
            return None
        turn = {
            "turn_id": len(req["thread_history"]) + 1,
            "sender_persona_id": sender_persona_id,
            "sender_display_name": sender_display_name,
            "sent_at": "2024-10-14T16:30:00Z",
            "message_text": message_text,
            "attached_document_ids": list(attached_document_ids or []),
        }
        req["thread_history"].append(turn)
        return turn

    def resolve(self, request_id: str, status: str) -> None:
        if request_id in self.requests:
            self.requests[request_id]["status"] = status

    def get(self, request_id: str) -> Optional[dict]:
        return self.requests.get(request_id)

    def all(self) -> List[dict]:
        return list(self.requests.values())
