"""
QoE Simulator - Level 5: FastAPI HTTP server for the ui-workspace gateway.

Exposes the 5 proto RPCs as REST endpoints, plus VDR search and the
10-section report / SPA Exhibit B assembly. Run with:
    uvicorn app.level5_workspace.server:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .gateway import WorkspaceGatewayService
from .irl import IRLPriority
from .report import ReportAssembler, SPAExhibitBBuilder

app = FastAPI(title="QoE Workspace Gateway", version="1.0.0")
svc = WorkspaceGatewayService()


def _load_databook(package_dir: str):
    """Build the Level 4 Databook from a .csp package dir (lazy import)."""
    from app.level4_databook.formula_graph import Databook
    return Databook().build(package_dir)


def _jsonable(obj):
    from decimal import Decimal
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    return obj


# -- VDR -------------------------------------------------------------------
@app.post("/api/v1/workspace/vdr/tree")
def vdr_tree(req: dict):
    return svc.get_vdr_tree(req.get("engagement_id", "sim1"), req.get("user_id", "USR_1"),
                            req.get("current_sim_day", svc.current_sim_day))


@app.post("/api/v1/workspace/vdr/document")
def vdr_document(req: dict):
    try:
        return svc.get_vdr_document(req.get("engagement_id", "sim1"),
                                    req["document_id"], req.get("user_id", "USR_1"))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/v1/workspace/vdr/search")
def vdr_search(req: dict):
    return {"results": svc.search_vdr(req.get("query", ""))}


# -- IRL -------------------------------------------------------------------
@app.post("/api/v1/workspace/irl/submit")
def irl_submit(req: dict):
    priority = IRLPriority(req.get("priority", 2))
    return svc.submit_irl_inquiry(
        req.get("engagement_id", "sim1"), req.get("workstream_code", "W00"), priority,
        req.get("target_persona_id", "P07"), req.get("subject", ""),
        req.get("inquiry_body", ""), req.get("cited_vdr_doc_ids", []))


# -- State -----------------------------------------------------------------
@app.post("/api/v1/workspace/state/sync")
def state_sync(req: dict):
    try:
        return svc.sync_workspace_state(
            req.get("engagement_id", "sim1"), req.get("user_id", "USR_1"),
            req.get("active_tab_index", 0), req.get("tab_states", []),
            req.get("active_vdr_doc_id", ""), req.get("hmac_signature", ""))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# -- Deliverables ----------------------------------------------------------
@app.post("/api/v1/workspace/deliverables/compile")
def deliverables_compile(req: dict):
    result = svc.compile_deliverables(
        req.get("engagement_id", "sim1"), req.get("user_id", "USR_1"),
        req.get("fdb_workbook_bytes_base64", ""), req.get("qoe_report_memo_json", "{}"),
        req.get("spa_exhibit_b_schedule_json", "{}"), req.get("client_checksum_sha256", ""))
    if result["compilation_success"]:
        import base64, hashlib, json
        try:
            workbook = base64.b64decode(req["fdb_workbook_bytes_base64"], validate=True)
            report = json.loads(req.get("qoe_report_memo_json", "{}"))
            spa = json.loads(req.get("spa_exhibit_b_schedule_json", "{}"))
            payload = json.dumps({"report": report, "spa": spa}, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
            queued = audit_jobs.submit(req.get("engagement_id", "sim1"), req["scenario_id"],
                req["seed_hex_64"], workbook, report, spa, hashlib.sha256(workbook + payload).hexdigest())
            result["audit_eval_queue_job_id"] = queued["job_id"]
        except (ValueError, KeyError, OSError) as error:
            result["audit_eval_queue_job_id"] = ""
            result["audit_submission_error"] = str(error)
    return result



# -- Report / SPA ----------------------------------------------------------
@app.post("/api/v1/workspace/report/assemble")
def report_assemble(req: dict):
    databook = _load_databook(req["package_dir"])
    return ReportAssembler().build(databook)


@app.post("/api/v1/workspace/spa/exhibit-b")
def spa_exhibit_b(req: dict):
    databook = _load_databook(req["package_dir"])
    return SPAExhibitBBuilder().build(databook)


# -- Databook tabs (feeds the center-pane grid) ----------------------------
@app.post("/api/v1/workspace/databook/tabs")
def databook_tabs(req: dict):
    databook = _load_databook(req["package_dir"])
    return {"tabs": list(databook.tabs.keys())}


@app.post("/api/v1/workspace/databook/tab")
def databook_tab(req: dict):
    databook = _load_databook(req["package_dir"])
    tab_id = req.get("tab_id")
    if tab_id not in databook.tabs:
        raise HTTPException(status_code=404, detail=f"unknown tab {tab_id}")
    return {"tab_id": tab_id, "data": _jsonable(databook.tabs[tab_id])}


@app.post("/api/v1/workspace/databook/trace")
def databook_trace(req: dict):
    return svc.trace_metric(req.get("tab_id", ""), req.get("metric", ""))


# The audit subsystem reads only server-owned policies from scenario packages.
from pathlib import Path as _Path
from app.level6_audit.rubric_scorer import create_router as _create_audit_router
_audit_router, audit_jobs = _create_audit_router(
    _Path(__file__).resolve().parents[3] / "scenarios" / "packages")
app.include_router(_audit_router)
