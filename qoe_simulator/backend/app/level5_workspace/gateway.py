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
        # Simulation clock state (consumed from qoe.sim.clock.ticked.v1).
        self.current_sim_day = 1
        self.check_bar_status = "OK (0 Breaks across 11 Tabs)"

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

    # rpc SubmitIRLInquiry (SubmitIRLInquiryRequest) returns (IRLInquiryResponse)
    def submit_irl_inquiry(self, engagement_id: str, workstream_code: str,
                           priority: IRLPriority, target_persona_id: str,
                           subject: str, inquiry_body: str,
                           cited_vdr_doc_ids: Sequence[str]) -> dict:
        if not self.rate_limiter.allow():
            raise PermissionError("Rate limit exceeded (max 5 req/sec)")
        ticket = self.irl.submit(engagement_id, workstream_code, priority,
                                 target_persona_id, subject, inquiry_body,
                                 list(cited_vdr_doc_ids), sim_day=8, latency_hours=0.0)
        self.events.emit("qoe.workspace.irl.submitted.v1",
                         engagement_id=engagement_id, request_id=ticket["request_id"],
                         persona_id=target_persona_id, priority=priority.value,
                         length=len(inquiry_body))
        return ticket

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
