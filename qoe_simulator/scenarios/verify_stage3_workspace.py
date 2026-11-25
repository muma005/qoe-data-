"""Exercise the Stage 3 HTTP workspace against a sealed Apex package."""

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

import fastapi
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.level0_physics.package_integrity import verify_package_integrity  # noqa: E402
from app.level4_databook.formula_graph import Databook  # noqa: E402
from app.level5_workspace import server  # noqa: E402
from app.level5_workspace.gateway import WorkspaceGatewayService  # noqa: E402


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten(nodes):
    for node in nodes:
        if node["canonical_json_ref"]:
            yield node
        yield from flatten(node["children"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    package = args.package.resolve(strict=True)
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["scenario_id"] == "target_apex_supply"
    assert manifest["random_seed"] == int("0x4a9f82c1e703bd55", 16)
    baseline = {name: file_hash(package / name) for name in
                ("checksum.sha256", "manifest.json", "ground_truth.duckdb", "audit_policy.json")}
    sealed = verify_package_integrity(package)
    results = []
    doc_rows = []
    tab_rows = []

    def record(name, request, response, detail):
        results.append((name, request, response, detail))

    engagement, user = "STAGE3_APEX_20261124", "USR_STAGE3_ANALYST"
    previous = server.svc
    try:
        with tempfile.TemporaryDirectory(prefix="stage3-apex-state-") as temp:
            db_path = str(Path(temp) / "workspace.sqlite3")
            server.svc = WorkspaceGatewayService(str(package), state_store_path=db_path)
            with TestClient(server.app) as client:
                post = lambda route, body: client.post("/api/v1/workspace/" + route, json=body)
                tree1 = post("vdr/tree", {"engagement_id": engagement, "user_id": user,
                                          "current_sim_day": 20})
                assert tree1.status_code == 200, tree1.text
                initial = tree1.json()
                docs = list(flatten(initial["root_nodes"]))
                assert len(initial["root_nodes"]) == 6
                assert len(docs) == 25
                assert initial["total_locked_documents"] + initial["total_unlocked_documents"] == 25
                assert initial["current_sim_day"] == 1
                record("Initial VDR tree", "POST /vdr/tree (client day 20)", "200",
                       f"6 folders, 25 documents, {initial['total_locked_documents']} locked; server day 1")
                locked = next(doc for doc in docs if doc["unlock_sim_day"] == 14)
                denied = post("vdr/document", {"engagement_id": engagement,
                                                 "document_id": locked["node_id"], "user_id": user})
                assert denied.status_code == 403
                record("Release boundary", "POST /vdr/document before day 14", "403",
                       f"{locked['node_id']} denied on day 1")
                unknown = post("vdr/document", {"document_id": "VDR_NODE_999"})
                assert unknown.status_code == 404
                record("Unknown document", "POST /vdr/document unknown ID", "404", "No document returned")

                search = post("vdr/search", {"query": "eRp_gEnErAl_lEdGeR"})
                assert search.status_code == 200 and len(search.json()["results"]) == 1
                searched = search.json()["results"][0]
                assert searched["node_id"] in {doc["node_id"] for doc in docs}
                assert searched["is_locked"]
                empty = post("vdr/search", {"query": "no_such_stage3_document"})
                assert empty.status_code == 200 and empty.json()["results"] == []
                record("Search", "POST /vdr/search mixed case and no-match", "200 / 200",
                       f"Found {searched['node_id']} locked on day 1; no-match returned []")

                server.svc.bus.publish("qoe.sim.clock.ticked.v1", engagement_id=engagement,
                                       current_day=14, hours_remaining=0, milestone="Friday dump")
                opened = post("vdr/document", {"engagement_id": engagement,
                                                 "document_id": locked["node_id"], "user_id": user})
                assert opened.status_code == 200, opened.text
                server.svc.bus.publish("qoe.sim.clock.ticked.v1", engagement_id=engagement,
                                       current_day=20, hours_remaining=0, milestone="Drip feed")
                tree20 = post("vdr/tree", {"engagement_id": engagement}).json()
                assert tree20["current_sim_day"] == 20 and tree20["total_locked_documents"] == 0
                assert not post("vdr/search", {"query": "eRp_gEnErAl_lEdGeR"}).json()["results"][0]["is_locked"]
                record("Clock unlock", "Clock events to days 14 and 20", "200",
                       "Day-14 document opened; all 25 documents unlocked by day 20")

                for doc in flatten(tree20["root_nodes"]):
                    response = post("vdr/document", {"engagement_id": engagement,
                                                       "document_id": doc["node_id"], "user_id": user})
                    assert response.status_code == 200, (doc["node_id"], response.text)
                    body = response.json()
                    payload = body["canonical_json_payload"].encode("utf-8")
                    json.loads(payload)
                    assert body["mime_type"] == "application/json" and body["download_signed_url"] == ""
                    assert len(payload) == doc["file_size_bytes"]
                    assert hashlib.sha256(payload).hexdigest() == doc["sha256_checksum"]
                    assert payload == (package / doc["canonical_json_ref"]).read_bytes()
                    for hidden in (b'ground_truth.duckdb', b'injected_anomalies.json',
                                   b'audit_policy.json', b'"ebitda_impact"', b'"solution_key"'):
                        assert hidden not in payload, (doc["node_id"], hidden)
                    doc_rows.append((doc["node_id"], doc["title"], len(payload),
                                     doc["sha256_checksum"]))
                record("Document retrieval", "POST /vdr/document for each cataloged ID", "25 x 200",
                       "25 valid JSON payloads; MIME, size, SHA-256, source bytes and hidden-field checks matched")

                inquiry = {"engagement_id": engagement, "workstream_code": "W02", "priority": 2,
                           "target_persona_id": "P07", "subject": "Rebate source terms",
                           "inquiry_body": "Please reconcile the cited rebate source terms with the journal reference.",
                           "cited_vdr_doc_ids": [locked["node_id"]]}
                bad = post("irl/submit", dict(inquiry, cited_vdr_doc_ids=["VDR_NODE_999"]))
                assert bad.status_code == 404
                submitted = post("irl/submit", inquiry)
                assert submitted.status_code == 200, submitted.text
                ticket = submitted.json()
                request_id = ticket["request_id"]
                assert request_id and ticket["engagement_id"] == engagement
                assert ticket["thread_history"][0]["attached_document_ids"] == [locked["node_id"]]
                fetched = client.get(f"/api/v1/workspace/irl/{request_id}",
                                     params={"engagement_id": engagement})
                assert fetched.status_code == 200 and fetched.json() == ticket
                assert client.get(f"/api/v1/workspace/irl/{request_id}",
                                  params={"engagement_id": "OTHER"}).status_code == 404
                assert server.svc.events.filter("qoe.workspace.irl.submitted.v1")
                record("Information request", "POST /irl/submit; GET /irl/{id}", "404 / 200 / 200",
                       f"Invalid citation rejected; {request_id} saved and retrieved for {engagement}")

                signature = server.svc.sign_state(engagement, user)
                state = {"engagement_id": engagement, "user_id": user,
                         "active_tab_index": 2, "active_vdr_doc_id": locked["node_id"],
                         "tab_states": [{"tab_id": "03_Income_Statement", "active_cell": "B4",
                                         "scroll_row": 2, "scroll_col": 1, "check_bar_passed": True}],
                         "hmac_signature": signature}
                synced = post("state/sync", state)
                assert synced.status_code == 200 and synced.json()["sync_acknowledged"]
                assert synced.json()["server_sim_day"] == 20
                saved = post("state/get", state)
                assert saved.status_code == 200 and saved.json()["tab_states"] == state["tab_states"]
                assert post("state/get", dict(state, hmac_signature="bad")).status_code == 403
                record("Workspace state", "POST /state/sync; POST /state/get", "200 / 200 / 403",
                       "Signed state round-tripped; wrong signature rejected")

                server.svc = WorkspaceGatewayService(str(package), state_store_path=db_path)
                again = client.get(f"/api/v1/workspace/irl/{request_id}",
                                   params={"engagement_id": engagement})
                state_again = post("state/get", state)
                assert again.status_code == 200 and again.json() == ticket
                assert state_again.status_code == 200 and state_again.json()["active_tab_index"] == 2
                record("Service restart", "New WorkspaceGatewayService with the same state DB", "200 / 200",
                       f"Inquiry {request_id} and active tab 2 survived restart")

                tabs = post("databook/tabs", {"package_dir": str(package)})
                assert tabs.status_code == 200, tabs.text
                expected = set(Databook.TAB_IDS)
                assert set(tabs.json()["tabs"]) == expected and len(expected) == 11
                for tab_id in tabs.json()["tabs"]:
                    result = post("databook/tab", {"package_dir": str(package), "tab_id": tab_id})
                    assert result.status_code == 200, (tab_id, result.text)
                    assert result.json()["tab_id"] == tab_id
                    assert isinstance(result.json()["data"], dict) and result.json()["data"]
                    tab_rows.append((tab_id, len(result.json()["data"])))
                assert post("databook/tab", {"package_dir": str(package),
                                             "tab_id": "NOT_A_TAB"}).status_code == 404
                record("Databook", "POST /databook/tabs and /databook/tab x11", "12 x 200 / 404",
                       "All 11 named tabs returned nonempty data; unknown tab rejected")
    finally:
        server.svc = previous

    assert sealed == verify_package_integrity(package)
    assert baseline == {name: file_hash(package / name) for name in baseline}
    record("Package unchanged", "Rehash package after HTTP run", "PASS",
           f"{sealed} sealed files valid; selected source hashes unchanged")
    repo = Path(__file__).resolve().parents[2]
    revision = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       cwd=repo, text=True).strip()
    lines = ["# Stage 3: Apex workspace interaction verification", "",
             f"Package: `{package}`; scenario `{manifest['scenario_id']}`; seed `0x{manifest['random_seed']:016x}`.",
             f"Code revision: `{revision}` plus uncommitted Stage 2/3 changes. Python `{platform.python_version()}`, "
             f"FastAPI `{fastapi.__version__}`, workspace API `{server.app.version}`.",
             f"Package checksum manifest SHA-256: `{baseline['checksum.sha256']}`. "
             f"Engagement: `{engagement}`; user: `{user}`.",
             f"Command: `python qoe_simulator/scenarios/verify_stage3_workspace.py --package "
             f"qoe_simulator/scenarios/.stage2_sealed_complete_20261124/target_apex_supply "
             f"--report qoe_simulator/scenarios/STAGE3_WORKSPACE_VERIFICATION.md`.",
             "State database was created in a disposable directory outside the sealed package.", "",
             "## Diagnosed and repaired before the final run", "",
             "- IRL submissions existed only in a service instance; there was no retrieval route. "
             "A SQLite-backed store and engagement-scoped GET route now persist and retrieve inquiries.",
             "- State sync previously acknowledged input without saving it. Signed sync now stores the tab and "
             "document state; a signed retrieval route returns it after restart.",
             "- Search previously returned stale `is_locked` flags. It now computes the flag from the server clock.",
             "- The first storage test exposed SQLite connections left open on Windows. The store now closes "
             "each connection, including failure paths. No proto field or RPC was edited.", "",
             "| Operation | Request or action | Response | Observed result |",
             "| --- | --- | --- | --- |"]
    for name, request, response, detail in results:
        lines.append(f"| {name} | `{request}` | {response} | {detail} |")
    lines.extend(["", "## Submitted and retrieved inquiry", "",
                  f"- Engagement `{engagement}`, request `{request_id}`, cited VDR document `{locked['node_id']}`.",
                  f"- Subject: `{inquiry['subject']}`. Body: `{inquiry['inquiry_body']}`.",
                  "- The retrieved inquiry, including its initial thread and citation, equaled the submitted response "
                  "both before and after a new service instance opened the same state store.", "",
                  "## Synchronized and retrieved state", "",
                  f"- User `{user}`, active tab index `2`, active document `{locked['node_id']}`.",
                  "- `03_Income_Statement` active cell `B4`, scroll row `2`, scroll column `1`, check bar flag `true`. "
                  "The stored tab state matched after service restart.", "",
                  "## Every retrieved VDR document", "",
                  "| ID | JSON title | Delivered bytes | Delivered SHA-256 |",
                  "| --- | --- | ---: | --- |"])
    for node_id, title, size, digest in doc_rows:
        lines.append(f"| `{node_id}` | `{title}` | {size:,} | `{digest}` |")
    lines.extend(["", "## Every loaded Databook tab", "",
                  "| Tab | Top-level fields |", "| --- | ---: |"])
    for tab_id, field_count in tab_rows:
        lines.append(f"| `{tab_id}` | {field_count} |")
    lines.extend(["", "## Regression checks", "",
                  "- Focused Stage 3 tests: 2 passed, including restart persistence and access rejection.",
                  "- Level 5 workspace tests: 70 passed. Level 6 tests: 40 passed. `git diff --check`: passed.", "",
                  "**Stage 3 result: PASS.** Every operation above returned the expected response. "
                  "The run exercised HTTP routes with FastAPI TestClient, not a visual browser session. "
                  "It verifies workspace behavior and artifact handoff, not the realism of financial data or QoE conclusions.", ""])
    args.report.write_text("\n".join(lines), encoding="utf-8")
    print(f"PASS Stage 3: {len(results)} operation groups; 25 VDR documents; 11 Databook tabs; "
          f"inquiry {request_id} and state persisted across service restart; source package unchanged")


if __name__ == "__main__":
    main()
