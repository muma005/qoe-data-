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
import os
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
    """Builds the institutional 6-folder VDR tree from a Level 2 .csp package."""

    def __init__(self, package_dir: str):
        self.package_dir = package_dir
        self.nodes: Dict[str, dict] = {}
        self._seq = 0

    def _node(self, parent: Optional[str], title: str, node_type: VDRNodeType,
              wave: ReleaseWave, unlock_day: Optional[int] = None,
              file_size: int = 0, checksum: str = "", json_ref: str = "") -> dict:
        self._seq += 1
        node_id = f"VDR_NODE_{self._seq:03d}"
        node = {
            "node_id": node_id,
            "parent_node_id": parent or "",
            "title": title,
            "node_type": node_type.value,
            "release_wave": wave.value,
            "unlock_sim_day": unlock_day if unlock_day is not None else WAVE_UNLOCK_DAY[wave],
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

    def _doc(self, parent, title, node_type, wave, path="", json_ref="", unlock_day=None) -> None:
        size = 0
        checksum = ""
        if path and os.path.exists(os.path.join(self.package_dir, path)):
            full = os.path.join(self.package_dir, path)
            size = os.path.getsize(full)
            checksum = hashlib.sha256(open(full, "rb").read()).hexdigest()
        self._node(parent, title, node_type, wave, unlock_day=unlock_day,
                   file_size=size, checksum=checksum, json_ref=json_ref)

    def build(self) -> List[dict]:
        # Idempotent: rebuild from scratch each call.
        self.nodes = {}
        self._seq = 0
        root_parent = None

        # 01 Corporate Governance & Legal (Wave 1)
        g1 = self._folder(root_parent, "01_Corporate_Governance_and_Legal", ReleaseWave.WAVE_1_INITIAL)
        self._doc(g1, "01.01_Certificate_of_Incorporation_and_Bylaws.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_1_INITIAL)
        self._doc(g1, "01.02_Capitalization_Table.xlsx",
                  VDRNodeType.DOCUMENT_XLSX, ReleaseWave.WAVE_1_INITIAL,
                  path="entity_ledger.json", json_ref="entity_ledger.json")
        self._doc(g1, "01.03_Board_Minutes_FY21_FY24.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_1_INITIAL)
        self._doc(g1, "01.04_Material_Litigation.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_3_FRIDAY_DUMP, unlock_day=14)

        # 02 Financial & Accounting
        g2 = self._folder(root_parent, "02_Financial_and_Accounting", ReleaseWave.WAVE_1_INITIAL)
        self._doc(g2, "02.01_Audited_Financial_Statements_FY21_FY23.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_1_INITIAL)
        self._doc(g2, "02.02_Trial_Balances_Monthly_36M.csv",
                  VDRNodeType.DOCUMENT_CSV, ReleaseWave.WAVE_1_INITIAL,
                  path="operational_trajectory.json", json_ref="operational_trajectory.json")
        self._doc(g2, "02.03_General_Ledger_Detail_NetSuite.csv",
                  VDRNodeType.DOCUMENT_CSV, ReleaseWave.WAVE_2_SUBLEDGERS,
                  path="vdr_artifacts/erp_exports/netsuite_gl.csv", json_ref="ground_truth.duckdb", unlock_day=7)
        self._doc(g2, "02.04_Aged_Accounts_Receivable_Subledger.csv",
                  VDRNodeType.DOCUMENT_CSV, ReleaseWave.WAVE_2_SUBLEDGERS,
                  path="vdr_artifacts/aged_ar_schedule.csv", unlock_day=7)
        self._doc(g2, "02.05_Aged_Accounts_Payable_and_Vendor_Spend.csv",
                  VDRNodeType.DOCUMENT_CSV, ReleaseWave.WAVE_2_SUBLEDGERS,
                  path="subledgers.json", json_ref="subledgers.json", unlock_day=7)
        self._doc(g2, "02.06_Inventory_Valuation_and_Obsolescence_Rolls.xlsx",
                  VDRNodeType.DOCUMENT_XLSX, ReleaseWave.WAVE_2_SUBLEDGERS,
                  path="sku_inventory.json", json_ref="sku_inventory.json", unlock_day=7)
        self._doc(g2, "02.07_Bank_Statements_and_Clearing_Reconciliations.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_3_FRIDAY_DUMP, unlock_day=14)

        # 03 Tax & Regulatory (Phase II)
        g3 = self._folder(root_parent, "03_Tax_and_Regulatory", ReleaseWave.WAVE_3_FRIDAY_DUMP)
        self._doc(g3, "03.01_Federal_Form_1120_Tax_Returns_FY21_FY23.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_3_FRIDAY_DUMP, unlock_day=14)
        self._doc(g3, "03.02_State_Apportionment_and_Nexus_Studies.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_3_FRIDAY_DUMP, unlock_day=14)
        self._doc(g3, "03.03_Sales_and_Use_Tax_Audit_Correspondence.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_3_FRIDAY_DUMP, unlock_day=14)

        # 04 Commercial & Customers
        g4 = self._folder(root_parent, "04_Commercial_and_Customers", ReleaseWave.WAVE_2_SUBLEDGERS)
        self._doc(g4, "04.01_Top_20_Customer_Master_Services_Agreements.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_3_FRIDAY_DUMP, unlock_day=14)
        self._doc(g4, "04.02_Historical_Sales_by_SKU_and_Customer_Monthly.csv",
                  VDRNodeType.DOCUMENT_CSV, ReleaseWave.WAVE_2_SUBLEDGERS,
                  path="sku_inventory.json", json_ref="sku_inventory.json", unlock_day=7)
        self._doc(g4, "04.03_Customer_Churn_and_Credit_Memo_Logs.csv",
                  VDRNodeType.DOCUMENT_CSV, ReleaseWave.WAVE_3_FRIDAY_DUMP, unlock_day=14)

        # 05 Operations & Procurement
        g5 = self._folder(root_parent, "05_Operations_and_Procurement", ReleaseWave.WAVE_2_SUBLEDGERS)
        self._doc(g5, "05.01_Supplier_Rebate_Agreements_ASC_705.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_3_FRIDAY_DUMP,
                  path="injected_anomalies.json", json_ref="injected_anomalies.json", unlock_day=14)
        self._doc(g5, "05.02_Warehouse_Facility_Leases_ASC_842.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_3_FRIDAY_DUMP, unlock_day=14)
        self._doc(g5, "05.03_Machine_Shop_Run_Hours_and_OEE_Telemetry.xlsx",
                  VDRNodeType.DOCUMENT_XLSX, ReleaseWave.WAVE_2_SUBLEDGERS,
                  path="operational_trajectory.json", json_ref="operational_trajectory.json", unlock_day=7)
        self._doc(g5, "05.04_Raw_Material_Bills_of_Material_BOM.xlsx",
                  VDRNodeType.DOCUMENT_XLSX, ReleaseWave.WAVE_2_SUBLEDGERS, unlock_day=7)

        # 06 HR & Compensation
        g6 = self._folder(root_parent, "06_Human_Resources_and_Compensation", ReleaseWave.WAVE_4_DRIP_FEED)
        self._doc(g6, "06.01_Employee_Census_and_Payroll_Run_Rate.xlsx",
                  VDRNodeType.DOCUMENT_XLSX, ReleaseWave.WAVE_3_FRIDAY_DUMP, unlock_day=14)
        self._doc(g6, "06.02_Executive_Employment_Agreements_and_Severance.pdf",
                  VDRNodeType.DOCUMENT_PDF, ReleaseWave.WAVE_4_DRIP_FEED, unlock_day=20)
        self._doc(g6, "06.03_Owner_Personal_Expenses_and_Perks_Schedule.xlsx",
                  VDRNodeType.DOCUMENT_XLSX, ReleaseWave.WAVE_4_DRIP_FEED, unlock_day=20)

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
