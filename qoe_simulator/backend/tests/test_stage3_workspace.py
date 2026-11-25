"""Workspace handoff, access, and restart tests on a sealed VDR fixture."""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.level5_workspace import server
from app.level5_workspace.gateway import WorkspaceGatewayService
from vdr_fixture import create_vdr_fixture


class TestStage3Workspace(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="stage3-workspace-")
        self.addCleanup(self.temporary.cleanup)
        self.package = create_vdr_fixture(Path(self.temporary.name) / "package")
        self.store = str(Path(self.temporary.name) / "workspace.sqlite3")
        self.previous = server.svc
        server.svc = WorkspaceGatewayService(self.package, state_store_path=self.store)
        self.addCleanup(lambda: setattr(server, "svc", self.previous))
        self.client = TestClient(server.app)
        self.addCleanup(self.client.close)

    def test_vdr_clock_search_and_inquiry_citation(self):
        tree = self.client.post("/api/v1/workspace/vdr/tree", json={"current_sim_day": 20}).json()
        self.assertEqual(tree["current_sim_day"], 1)
        locked = server.svc.search_vdr("Supplier_Rebate_Terms")[0]
        self.assertTrue(locked["is_locked"])
        self.assertEqual(self.client.post("/api/v1/workspace/vdr/document",
                                          json={"document_id": locked["node_id"]}).status_code, 403)
        inquiry = {"engagement_id": "stage3", "subject": "Rebate terms",
                   "inquiry_body": "Please explain the rebate terms for the cited schedule.",
                   "cited_vdr_doc_ids": [locked["node_id"]]}
        self.assertEqual(self.client.post("/api/v1/workspace/irl/submit", json=inquiry).status_code, 403)
        self.assertEqual(self.client.post("/api/v1/workspace/irl/submit",
                          json=dict(inquiry, cited_vdr_doc_ids=["VDR_NODE_999"])).status_code, 404)
        server.svc.bus.publish("qoe.sim.clock.ticked.v1", engagement_id="stage3", current_day=14,
                               hours_remaining=0, milestone="Friday dump")
        self.assertFalse(server.svc.search_vdr("sUPPLIER_rebate_terms")[0]["is_locked"])
        self.assertEqual(self.client.post("/api/v1/workspace/vdr/document",
                                          json={"document_id": locked["node_id"]}).status_code, 200)
        posted = self.client.post("/api/v1/workspace/irl/submit", json=inquiry)
        self.assertEqual(posted.status_code, 200, posted.text)
        request_id = posted.json()["request_id"]
        self.assertEqual(self.client.get(f"/api/v1/workspace/irl/{request_id}",
                                         params={"engagement_id": "stage3"}).json()["thread_history"][0]
                         ["attached_document_ids"], [locked["node_id"]])
        self.assertEqual(self.client.get(f"/api/v1/workspace/irl/{request_id}",
                                         params={"engagement_id": "other"}).status_code, 404)
        restarted = WorkspaceGatewayService(self.package, state_store_path=self.store)
        self.assertEqual(restarted.get_irl_inquiry("stage3", request_id)["subject"], "Rebate terms")

    def test_signed_state_sync_can_be_retrieved_after_restart(self):
        signature = server.svc.sign_state("stage3", "analyst")
        payload = {"engagement_id": "stage3", "user_id": "analyst", "active_tab_index": 4,
                   "active_vdr_doc_id": "VDR_NODE_007", "tab_states": [{"tab_id": "05_Gross_Margin",
                   "active_cell": "B4", "scroll_row": 3, "scroll_col": 1, "check_bar_passed": True}],
                   "hmac_signature": signature}
        response = self.client.post("/api/v1/workspace/state/sync", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["server_sim_day"], 1)
        self.assertEqual(self.client.post("/api/v1/workspace/state/get", json=payload).json()
                         ["tab_states"], payload["tab_states"])
        self.assertEqual(self.client.post("/api/v1/workspace/state/get",
                                          json=dict(payload, hmac_signature="bad")).status_code, 403)
        restarted = WorkspaceGatewayService(self.package, state_store_path=self.store)
        self.assertEqual(restarted.get_workspace_state("stage3", "analyst", signature)
                         ["active_tab_index"], 4)
        with self.assertRaises(KeyError):
            restarted.get_workspace_state("stage3", "other", restarted.sign_state("stage3", "other"))


if __name__ == "__main__":
    unittest.main()
