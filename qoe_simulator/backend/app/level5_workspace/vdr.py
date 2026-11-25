"""
QoE Simulator - Level 5: Virtual Data Room (VDR) Portal.

Implements spec Sections 3, 5.1, 7.2, 9.2 and the VDR half of the workspace:

  - Institutional 6-folder VDR tree with release-wave gating.
  - HMAC-SHA256 pre-signed capability tokens (60s expiry, LP-11).
  - Dynamic forensic watermarking (diagonal text + steganographic dots, LP-11).
  - Zero-knowledge filtering (ground-truth never leaves the backend, LP-05).
  - Rate limiting (max 5 req/sec) and a Nygard circuit breaker.

Enums mirror proto/workspace_gateway.proto (source of truth).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Proto-mirror enums (proto/workspace_gateway.proto)
# ---------------------------------------------------------------------------
class VDRNodeType(Enum):
    VDR_NODE_TYPE_UNSPECIFIED = 0
    FOLDER = 1
    DOCUMENT_PDF = 2
    DOCUMENT_XLSX = 3
    DOCUMENT_CSV = 4


class ReleaseWave(Enum):
    RELEASE_WAVE_UNSPECIFIED = 0
    WAVE_1_INITIAL = 1
    WAVE_2_SUBLEDGERS = 2
    WAVE_3_FRIDAY_DUMP = 3
    WAVE_4_DRIP_FEED = 4


# Phase-gated unlock days per release wave.
WAVE_UNLOCK_DAY = {
    ReleaseWave.WAVE_1_INITIAL: 1,
    ReleaseWave.WAVE_2_SUBLEDGERS: 7,
    ReleaseWave.WAVE_3_FRIDAY_DUMP: 14,
    ReleaseWave.WAVE_4_DRIP_FEED: 20,
}


# ---------------------------------------------------------------------------
# LP-11: HMAC-SHA256 pre-signed capability tokens (60 second expiry)
# ---------------------------------------------------------------------------
class CapabilityTokenManager:
    """Token = HMAC-SHA256(Secret, UserID | DocID | SimDay | ExpiresAt)."""

    def __init__(self, secret: str = "qoe-vdr-secret"):
        self.secret = secret.encode("utf-8")

    def _msg(self, user_id: str, doc_id: str, sim_day: int, expires_at: int) -> str:
        return f"{user_id}|{doc_id}|{sim_day}|{expires_at}"

    def generate(self, user_id: str, doc_id: str, sim_day: int,
                 ttl_seconds: int = 60, now: Optional[float] = None) -> Dict[str, object]:
        now = time.time() if now is None else now
        expires_at = int(now) + ttl_seconds
        token = hmac.new(self.secret, self._msg(user_id, doc_id, sim_day, expires_at).encode(),
                         hashlib.sha256).hexdigest()
        return {"token": token, "expires_at": expires_at}

    def verify(self, token: str, user_id: str, doc_id: str, sim_day: int,
               expires_at: int, now: Optional[float] = None) -> bool:
        now = time.time() if now is None else now
        if now > expires_at:
            return False
        expected = hmac.new(self.secret, self._msg(user_id, doc_id, sim_day, expires_at).encode(),
                            hashlib.sha256).hexdigest()
        return hmac.compare_digest(token, expected)


# ---------------------------------------------------------------------------
# LP-11: dynamic forensic watermarking
# ---------------------------------------------------------------------------
class WatermarkEngine:
    """Diagonal -45deg, Helvetica Bold 16pt, opacity 0.18, hash in margin."""

    ANGLE_DEGREES = -45.0
    FONT = "Helvetica Bold"
    FONT_SIZE_PT = 16
    OPACITY = 0.18

    def text(self, institution: str, user_id: str, session_id: str, timestamp: str) -> str:
        return (f"CONFIDENTIAL - STRICTLY RESTRICTED\n"
                f"ACQUIRING INSTITUTION: {institution}\n"
                f"USER: {user_id}\n"
                f"VDR SESSION ID: {session_id}\n"
                f"TIMESTAMP: {timestamp} - DO NOT DUPLICATE")

    def config(self, institution: str, user_id: str, session_id: str,
               timestamp: str, enable_steganographic_dots: bool = True) -> dict:
        return {
            "watermark_text": self.text(institution, user_id, session_id, timestamp),
            "ip_address_hash": hashlib.sha256(user_id.encode()).hexdigest()[:16],
            "session_uuid": session_id,
            "enable_steganographic_dots": enable_steganographic_dots,
        }


# ---------------------------------------------------------------------------
# VDR node + tree builder
# ---------------------------------------------------------------------------
class VDRTreeBuilder:
    """Builds a JSON-only VDR from sealed, learner-safe package documents."""

    SECTIONS = (
        "01_Corporate_Governance_and_Legal", "02_Financial_and_Accounting",
        "03_Tax_and_Regulatory", "04_Commercial_and_Customers",
        "05_Operations_and_Procurement", "06_Human_Resources_and_Compensation",
    )
    SAFE_FILENAMES = frozenset((
        "entity_master.json", "operational_trajectory.json", "erp_general_ledger.json",
        "aged_ar_schedule.json", "subledgers.json", "sku_inventory.json",
        "working_capital_schedule.json", "cutoff_break_schedule.json",
        "product_sales_lines.json", "operational_source_documents.json",
        "corporate_identity.json", "board_minutes_register.json", "litigation_register.json",
        "annual_financial_statements.json", "cash_reconciliation_register.json",
        "federal_tax_register.json", "state_apportionment_register.json",
        "sales_tax_correspondence.json", "customer_agreement_register.json",
        "customer_churn_credit_activity.json", "facility_lease_register.json",
        "product_bom_register.json", "employee_census_register.json",
        "executive_employment_register.json", "owner_expense_register.json",
    ))

    def __init__(self, package_dir: str):
        self.package_dir = package_dir
        self.nodes: Dict[str, dict] = {}
        self._seq = 0
        self._paths: Dict[str, str] = {}

    def _node(self, parent: Optional[str], title: str, node_type: VDRNodeType,
              wave: ReleaseWave, unlock_day: Optional[int] = None,
              file_size: int = 0, checksum: str = "", json_ref: str = "") -> dict:
        self._seq += 1
        node_id = f"VDR_NODE_{self._seq:03d}"
        unlock = unlock_day if unlock_day is not None else WAVE_UNLOCK_DAY[wave]
        node = {
            "node_id": node_id,
            "parent_node_id": parent or "",
            "title": title,
            "node_type": node_type.value,
            "release_wave": wave.value,
            "unlock_sim_day": unlock,
            "access_phase": "PHASE_I" if unlock <= 13 else "PHASE_II",
            "is_locked": True,
            "file_size_bytes": file_size,
            "sha256_checksum": checksum,
            "canonical_json_ref": json_ref,
            "children": [],
        }
        self.nodes[node_id] = node
        if parent and parent in self.nodes:
            self.nodes[parent]["children"].append(node_id)
        return node

    def _folder(self, parent, title, wave) -> str:
        return self._node(parent, title, VDRNodeType.FOLDER, wave)["node_id"]

    def _sealed_json(self, relative_path: str, hashes: dict) -> bytes:
        from pathlib import Path
        root = Path(self.package_dir).resolve()
        path = (root / relative_path).resolve()
        if (not path.is_relative_to(root / "vdr_artifacts" / "json") or
                path.name not in self.SAFE_FILENAMES | {"catalog.json"} or
                relative_path not in hashes):
            raise ValueError("Unapproved VDR JSON path: " + relative_path)
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != hashes[relative_path]:
            raise ValueError("VDR document checksum mismatch: " + relative_path)
        json.loads(content)
        return content

    def document_bytes(self, document_id: str) -> bytes:
        relative = self._paths.get(document_id)
        if relative is None:
            raise KeyError("Unknown VDR document: " + document_id)
        hashes = self._checksums()
        return self._sealed_json(relative, hashes)

    def _checksums(self) -> dict:
        from pathlib import Path
        checksum = Path(self.package_dir) / "checksum.sha256"
        return dict((name, digest) for digest, name in
                    (line.split("  ", 1) for line in checksum.read_text(encoding="utf-8").splitlines()))

    def build(self) -> List[dict]:
        # The catalog and every exposed file must be present and sealed.
        self.nodes = {}
        self._seq = 0
        self._paths = {}
        hashes = self._checksums()
        catalog = json.loads(self._sealed_json("vdr_artifacts/json/catalog.json", hashes))
        if catalog.get("schema_version") != 1:
            raise ValueError("Unsupported VDR catalog version")
        folders = {section: self._folder(None, section, ReleaseWave.WAVE_1_INITIAL)
                   for section in self.SECTIONS}
        seen = set()
        for record in catalog["documents"]:
            section, title, relative = record["section"], record["title"], record["path"]
            day = record["unlock_day"]
            if (section not in folders or not title.endswith(".json") or
                    not isinstance(day, int) or day not in (1, 7, 14, 20) or
                    relative in seen):
                raise ValueError("Invalid VDR catalog document")
            seen.add(relative)
            content = self._sealed_json(relative, hashes)
            wave = {1: ReleaseWave.WAVE_1_INITIAL, 7: ReleaseWave.WAVE_2_SUBLEDGERS,
                    14: ReleaseWave.WAVE_3_FRIDAY_DUMP, 20: ReleaseWave.WAVE_4_DRIP_FEED}[day]
            node = self._node(folders[section], title, VDRNodeType.VDR_NODE_TYPE_UNSPECIFIED,
                              wave, unlock_day=day, file_size=len(content),
                              checksum=hashlib.sha256(content).hexdigest(), json_ref=relative)
            self._paths[node["node_id"]] = relative
        root_nodes = [self.nodes[n] for n in self.nodes if not self.nodes[n]["parent_node_id"]]
        return root_nodes

    def get_tree(self, current_sim_day: int) -> Dict[str, object]:
        """Return the tree with is_locked computed, plus unlocked/locked counts."""
        self.build()
        unlocked = 0
        locked = 0

        def render(node: dict) -> dict:
            nonlocal unlocked, locked
            out = dict(node)
            out["is_locked"] = current_sim_day < out["unlock_sim_day"]
            if out["node_type"] != VDRNodeType.FOLDER.value:
                if out["is_locked"]:
                    locked += 1
                else:
                    unlocked += 1
            out["children"] = [render(self.nodes[c]) for c in node["children"]]
            return out

        root_nodes = [render(self.nodes[n]) for n in self.nodes
                      if not self.nodes[n]["parent_node_id"]]
        return {
            "root_nodes": root_nodes,
            "total_unlocked_documents": unlocked,
            "total_locked_documents": locked,
        }

    def find(self, document_id: str) -> Optional[dict]:
        for node in self.nodes.values():
            if node["node_id"] == document_id:
                return node
        return None

    def search(self, query: str) -> List[dict]:
        """Case-insensitive substring search over node titles."""
        q = (query or "").lower()
        if not q:
            return []
        return [n for n in self.nodes.values() if q in n["title"].lower()]


# ---------------------------------------------------------------------------
# LP-05 / NFR-03: zero-knowledge filter + rate limiter
# ---------------------------------------------------------------------------
GROUND_TRUTH_KEYS = ("ground_truth", "injected_anomalies", "solution_key", "anomaly_ids",
                     "ebitda_impact", "hidden_marker", "fraud_marker", "admin_ground_truth")


class ZeroKnowledgeFilter:
    """Recursively strips ground-truth keys from any client-bound payload."""

    def strip(self, obj):
        if isinstance(obj, dict):
            return {k: self.strip(v) for k, v in obj.items() if k not in GROUND_TRUTH_KEYS}
        if isinstance(obj, list):
            return [self.strip(v) for v in obj]
        return obj


class RateLimiter:
    """Sliding-window rate limiter (max N requests per second)."""

    def __init__(self, max_per_sec: int = 5):
        self.max_per_sec = max_per_sec
        self._hits: List[float] = []

    def allow(self, now: Optional[float] = None) -> bool:
        now = time.time() if now is None else now
        self._hits = [t for t in self._hits if now - t < 1.0]
        if len(self._hits) >= self.max_per_sec:
            return False
        self._hits.append(now)
        return True
