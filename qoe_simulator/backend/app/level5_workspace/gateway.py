"""
QoE Simulator - Level 5: Workspace Gateway Service (ui-workspace).

Implements the 5 proto RPCs (GetVDRTree, GetVDRDocument, SubmitIRLInquiry,
SyncWorkspaceState, CompileDeliverables), HMAC-SHA256 state guarding (NFR-04),
the deliverable compiler (packager + DDE sanitizer, LP-04), and the 6 CloudEvents
(spec Section 10.2).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from typing import Dict, List, Optional, Sequence

from .vdr import (
    CapabilityTokenManager,
    RateLimiter,
    VDRTreeBuilder,
    WatermarkEngine,
    ZeroKnowledgeFilter,
)
from .irl import IRLConsole, IRLPriority


# Databook metric -> source GL account numbers (for the formula tracer).
METRIC_ACCOUNT_MAP = {
    "revenue": ["401000", "402000"],
    "total_revenue": ["401000", "402000"],
    "cogs": ["501000", "502000", "503000", "504000"],
    "total_cogs": ["501000", "502000", "503000", "504000"],
    "opex": ["601000", "604000", "605000"],
    "total_opex": ["601000", "604000", "605000"],
    "ebitda": ["401000", "402000", "501000", "601000"],
    "normalized_ebitda": ["401000", "402000", "501000", "601000"],
    "ar": ["111000"],
    "ap": ["201000"],
    "inventory": ["141000", "142000", "143000", "144000"],
    "nwc": ["111000", "141000", "201000"],
    "materials": ["501000"],
    "labor": ["502000"],
    "overhead": ["503000", "504000"],
    "net_debt": ["101000", "201000", "211000"],
}


class DdeSanitizer:
    """LP-04: neutralizes formula/DDE command-injection in deliverable strings."""

    DANGEROUS_PREFIXES = ("=", "+", "-", "@")

    def sanitize(self, value: str) -> str:
        v = str(value)
        # Neutralize DDE / formula injection by prefixing dangerous leading chars.
        if v.lstrip().startswith(self.DANGEROUS_PREFIXES):
            return "'" + v
        return v

    def sanitize_all(self, obj):
        if isinstance(obj, dict):
            return {k: self.sanitize_all(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.sanitize_all(v) for v in obj]
        if isinstance(obj, str):
            return self.sanitize(obj)
        return obj


class CloudEventEmitter:
    """Level 5 CloudEvents (3 emitted, 3 consumed — consumed ones are handlers)."""

    def __init__(self):
        self.events: List[dict] = []

    def emit(self, event_type: str, **payload) -> dict:
        event = {"type": event_type, **payload}
        self.events.append(event)
        return event

    def filter(self, event_type: str) -> List[dict]:
        return [e for e in self.events if e["type"] == event_type]


class EventBus:
    """Minimal pub/sub so Levels 1/3/4 can push consumed CloudEvents into Level 5."""

    def __init__(self):
        self._subscribers: Dict[str, List] = {}

    def subscribe(self, event_type: str, handler) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, **payload) -> None:
        for handler in self._subscribers.get(event_type, []):
            handler(**payload)


class CircuitBreaker:
    """Nygard breaker for the gateway's VDR stream (spec Section 9)."""

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED"
        self.opened_at: Optional[float] = None

    def call(self, fn, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.opened_at >= self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise PermissionError("Circuit breaker OPEN (VDR stream unavailable)")
        try:
            result = fn(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                self.opened_at = time.time()
            raise


class WorkspaceGatewayService:
    """Proto-shaped facade mirroring proto/workspace_gateway.proto."""

    def __init__(self, package_dir: str = None, secret: str = "qoe-vdr-secret"):
        self.package_dir = package_dir
        self.tokens = CapabilityTokenManager(secret)
        self.watermark = WatermarkEngine()
        self.zero_knowledge = ZeroKnowledgeFilter()
        self.rate_limiter = RateLimiter(max_per_sec=5)
        self.irl = IRLConsole()
        self.sanitizer = DdeSanitizer()
        self.events = CloudEventEmitter()
        self._submissions: Dict[str, dict] = {}
        self._seq = 0
        self.circuit_breaker = CircuitBreaker()
        # Simulation clock state (consumed from qoe.sim.clock.ticked.v1).
        self.current_sim_day = 1
        self.check_bar_status = "OK (0 Breaks across 11 Tabs)"
        self.vague_inquiry_count = 0  # LP-15 Investigative-Rigor penalty counter
        # Live event bus: subscribe to the 3 consumed CloudEvents.
        self.bus = EventBus()
        self.bus.subscribe("qoe.sim.clock.ticked.v1", self.handle_sim_clock_ticked)
        self.bus.subscribe("qoe.friction.inquiry.answered.v1", self.handle_friction_inquiry_answered)
        self.bus.subscribe("qoe.fdb.recalculated.v1", self.handle_fdb_recalculated)

    # rpc GetVDRTree (GetVDRTreeRequest) returns (VDRTreeResponse)
    def get_vdr_tree(self, engagement_id: str, user_id: str,
                     current_sim_day: int) -> dict:
        builder = VDRTreeBuilder(self.package_dir) if self.package_dir else VDRTreeBuilder(".")
        tree = builder.get_tree(current_sim_day)
        # Zero-knowledge: strip any ground-truth keys before returning.
        tree = self.zero_knowledge.strip(tree)
        return {
            "engagement_id": engagement_id,
            "current_sim_day": current_sim_day,
            "root_nodes": tree["root_nodes"],
            "total_unlocked_documents": tree["total_unlocked_documents"],
            "total_locked_documents": tree["total_locked_documents"],
        }

    # rpc GetVDRDocument (GetVDRDocumentRequest) returns (VDRDocumentResponse)
    def get_vdr_document(self, engagement_id: str, document_id: str,
                         user_id: str) -> dict:
        builder = VDRTreeBuilder(self.package_dir) if self.package_dir else VDRTreeBuilder(".")
        builder.build()
        node = builder.find(document_id)
        if node is None:
            raise KeyError(f"Unknown document {document_id}")

        # LP-11: enforce sim-day gating -> 403 FORBIDDEN if not yet unlocked.
        if self.current_sim_day < node["unlock_sim_day"]:
            raise PermissionError(
                f"403 FORBIDDEN: {document_id} unlocks on sim day {node['unlock_sim_day']} "
                f"(current day {self.current_sim_day})")

        signed = self.tokens.generate(user_id, document_id, self.current_sim_day, ttl_seconds=60)
        session_id = f"VDR_{engagement_id}_{int(time.time())}"
        watermark = self.watermark.config("APOLLO PRIVATE EQUITY DEAL TEAM", user_id,
                                          session_id, "2024-10-18T11:32:05Z")

        # Emit vdr.opened CloudEvent
        self.events.emit("qoe.workspace.vdr.opened.v1",
                         engagement_id=engagement_id, user_id=user_id,
                         document_id=document_id, sim_day=self.current_sim_day, latency_ms=0.0)

        return {
            "document_id": document_id,
            "file_name": node["title"],
            "mime_type": "application/pdf" if node["node_type"] == 2 else "text/csv",
            "download_signed_url": f"/api/v1/vdr/docs/{document_id}?token={signed['token']}",
            "expires_at": signed["expires_at"],
            "watermark": watermark,
            "canonical_json_payload": json.dumps({"node_id": document_id, "title": node["title"]}),
        }

    # VDR search (spec Section 3)
    def search_vdr(self, query: str) -> List[dict]:
        builder = VDRTreeBuilder(self.package_dir) if self.package_dir else VDRTreeBuilder(".")
        builder.build()
        return builder.search(query)

    def _compute_latency(self, pushback_tier_str: str) -> float:
        """Route latency through the Level 3 LatencyScheduler + PushbackTier."""
        from app.level3_friction.pushback_fsm import (
            LATENCY_MULTIPLIER,
            PushbackTier,
            LatencyScheduler,
        )
        tier = PushbackTier.TIER_1_PROFESSIONAL_COOPERATION
        if pushback_tier_str.startswith("TIER_4"):
            tier = PushbackTier.TIER_4_AGGRESSIVE_OBFUSCATION
        elif pushback_tier_str.startswith("TIER_3"):
            tier = PushbackTier.TIER_3_COMMERCIAL_PRESSURE
        elif pushback_tier_str.startswith("TIER_2"):
            tier = PushbackTier.TIER_2_PROCRASTINATION_DELAY
        psi = LATENCY_MULTIPLIER[tier]
        return LatencyScheduler(seed=42).schedule_delay_hours("routine", 0.0, psi)

    # rpc SubmitIRLInquiry (SubmitIRLInquiryRequest) returns (IRLInquiryResponse)
    def submit_irl_inquiry(self, engagement_id: str, workstream_code: str,
                           priority: IRLPriority, target_persona_id: str,
                           subject: str, inquiry_body: str,
                           cited_vdr_doc_ids: Sequence[str]) -> dict:
        if not self.rate_limiter.allow():
            raise PermissionError("Rate limit exceeded (max 5 req/sec)")
        ticket = self.irl.submit(engagement_id, workstream_code, priority,
                                 target_persona_id, subject, inquiry_body,
                                 list(cited_vdr_doc_ids), sim_day=self.current_sim_day,
                                 latency_hours=0.0)
        ticket["estimated_latency_hours"] = self._compute_latency(
            ticket["pushback_tier_triggered"])
        # LP-15: unfocused/vague inquiries deduct from Investigative Rigor.
        if ticket["pushback_tier_triggered"].startswith("TIER_4"):
            self.vague_inquiry_count += 1
        self.events.emit("qoe.workspace.irl.submitted.v1",
                         engagement_id=engagement_id, request_id=ticket["request_id"],
                         persona_id=target_persona_id, priority=priority.value,
                         length=len(inquiry_body))
        return ticket

    # Evidentiary formula tracer (spec Section 5.2): metric -> source GL + VDR hash.
    def trace_metric(self, tab_id: str, metric: str) -> dict:
        builder = VDRTreeBuilder(self.package_dir) if self.package_dir else VDRTreeBuilder(".")
        builder.build()
        gl_node = next((n for n in builder.nodes.values()
                        if "General_Ledger" in n["title"]), None)
        return {
            "tab_id": tab_id,
            "metric": metric,
            "source_accounts": METRIC_ACCOUNT_MAP.get(metric, ["100000"]),
            "source_je_id": f"JE-{hashlib.sha256(f'{tab_id}:{metric}'.encode()).hexdigest()[:12]}",
            "vdr_document_id": gl_node["node_id"] if gl_node else "",
            "vdr_file_hash": gl_node["sha256_checksum"] if gl_node else "",
        }

    # rpc SyncWorkspaceState (WorkspaceStateSyncRequest) returns (WorkspaceStateSyncResponse)
    def sync_workspace_state(self, engagement_id: str, user_id: str, active_tab_index: int,
                             tab_states: Sequence[dict], active_vdr_doc_id: str,
                             hmac_signature: str) -> dict:
        # NFR-04: verify the HMAC signature of the local state before accepting.
        self._verify_hmac(engagement_id, user_id, hmac_signature)
        return {
            "sync_acknowledged": True,
            "server_timestamp": int(time.time()),
            "server_sim_day": 14,
            "check_bar_aggregate_status": "OK (0 Breaks across 11 Tabs)",
        }

    # rpc CompileDeliverables (SubmitDeliverablePackageRequest) returns (DeliverableCompilationResponse)
    def compile_deliverables(self, engagement_id: str, user_id: str,
                             fdb_workbook_bytes_base64: str, qoe_report_memo_json: str,
                             spa_exhibit_b_schedule_json: str,
                             client_checksum_sha256: str) -> dict:
        self._seq += 1
        submission_id = f"SUB_{self._seq:06d}"

        # LP-04: DDE/formula sanitization of the memo and schedule.
        memo = self.sanitizer.sanitize_all(json.loads(qoe_report_memo_json or "{}"))
        spa = self.sanitizer.sanitize_all(json.loads(spa_exhibit_b_schedule_json or "{}"))

        # Packager: validate checksum over the workbook bytes.
        checksum = hashlib.sha256(fdb_workbook_bytes_base64.encode()).hexdigest()
        errors = []
        if checksum != client_checksum_sha256:
            errors.append("CLIENT_CHECKSUM_MISMATCH")

        success = len(errors) == 0
        audit_job = f"AUDIT_JOB_{submission_id}" if success else ""
        self._submissions[submission_id] = {
            "submission_id": submission_id, "success": success, "errors": errors,
            "memo": memo, "spa": spa, "audit_job": audit_job,
            "investigative_rigor_penalty": self.vague_inquiry_count,
        }
        self.events.emit("qoe.workspace.deliverable.compiled.v1",
                         engagement_id=engagement_id, submission_id=submission_id,
                         fdb_hash=checksum, report_hash=hashlib.sha256(
                             json.dumps(memo).encode()).hexdigest())
        return {
            "submission_id": submission_id,
            "compilation_success": success,
            "compilation_errors": errors,
            "submitted_at": int(time.time()),
            "audit_eval_queue_job_id": audit_job,
            "investigative_rigor_penalty": self.vague_inquiry_count,
        }

    # -- HMAC state guard (NFR-04) -------------------------------------------
    def sign_state(self, engagement_id: str, user_id: str) -> str:
        msg = f"{engagement_id}|{user_id}".encode()
        return hmac.new(b"qoe-state-secret", msg, hashlib.sha256).hexdigest()

    def _verify_hmac(self, engagement_id: str, user_id: str, signature: str) -> None:
        expected = self.sign_state(engagement_id, user_id)
        if not hmac.compare_digest(expected, signature):
            raise PermissionError("HMAC-SHA256 state signature verification failed")

    # -- Consumed CloudEvents (spec Section 10.2) ----------------------------
    def handle_sim_clock_ticked(self, engagement_id: str, current_day: int,
                                hours_remaining: float, milestone: str) -> None:
        """qoe.sim.clock.ticked.v1: advance the sim day, unlocking release waves."""
        self.current_sim_day = current_day

    def handle_friction_inquiry_answered(self, engagement_id: str, request_id: str,
                                         answer_text: str,
                                         documents_attached: Sequence[str]) -> None:
        """qoe.friction.inquiry.answered.v1: inject a persona answer into the IRL thread."""
        self.irl.append_turn(request_id, "TARGET_CFO", "Target CFO", answer_text,
                             list(documents_attached))

    def handle_fdb_recalculated(self, engagement_id: str, check_bars_status: str,
                                break_count: int, break_amount: float) -> None:
        """qoe.fdb.recalculated.v1: pin the green/red check-bar status."""
        if break_count > 0:
            self.check_bar_status = f"DISCREPANCY: ${break_amount:,.0f} ({break_count} breaks)"
        else:
            self.check_bar_status = check_bars_status or "OK (0 Breaks across 11 Tabs)"
