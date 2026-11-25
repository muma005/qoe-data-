"""Verify the Apex Level 6 job, result, memo, and all five protobuf RPCs."""

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(report, spa):
    return json.dumps({"report": report, "spa": spa}, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    handoff, package, output = args.handoff.resolve(strict=True), args.package.resolve(strict=True), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    os.environ["QOE_SCENARIO_PACKAGE_DIR"] = str(package)
    os.environ["QOE_WORKSPACE_STATE_DB"] = str(output / "workspace.sqlite3")
    os.environ["QOE_AUDIT_JOB_STORE"] = str(handoff / "jobs.sqlite3")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

    import grpc
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from google.protobuf import message_factory
    from app.level0_physics.package_integrity import verify_package_integrity
    from app.level6_audit.rubric_scorer import (EvaluationJobs, JobStore, PENALTIES,
                                                create_router, load_scenario_policy, register_grpc_service)
    from app.level5_workspace import server as workspace

    scenario_id, seed, engagement = "target_apex_supply", "0x4a9f82c1e703bd55", "STAGE4_APEX_20261124"
    stage4_report = (handoff / "STAGE4_DELIVERABLE_HANDOFF.md").read_text(encoding="utf-8")
    match = re.search(r"real job `([0-9a-f]{32})`", stage4_report)
    assert match, "Stage 4 job ID absent"
    original_id = match.group(1)
    initial_checksum = sha((package / "checksum.sha256").read_bytes())
    sealed = verify_package_integrity(package)
    workbook = (handoff / "apex_databook.xlsx").read_bytes()
    report = json.loads((handoff / "apex_report.json").read_text(encoding="utf-8"))
    spa = json.loads((handoff / "apex_spa_exhibit_b.json").read_text(encoding="utf-8"))
    original_store = JobStore(handoff / "jobs.sqlite3")
    original = original_store.get(original_id)
    assert original["status"] == "COMPLETED" and original["engagement_id"] == engagement
    saved_workbook, saved_report, saved_spa, saved_policy = original_store.submission(original_id)
    assert (saved_workbook, saved_report, saved_spa) == (workbook, report, spa)
    trusted_policy = load_scenario_policy(package.parent, scenario_id, seed)
    assert saved_policy["seed_hex_64"] == seed
    assert {k: v for k, v in saved_policy.items() if k != "_operation"} == trusted_policy

    result = original["result"]
    audit, packet, memo = result["ast_report"], result["partner_review_packet"], result["eqcr_memo"]
    assert result["rubric_version"] and audit["total_cells_scanned"] > 0
    assert audit["check_bars_reconciled"] == len(trusted_policy["workbook_policy"]["check_bars"]) == 11
    assert audit["formulas_verified_reproducible"] <= audit["total_cells_scanned"]
    assert all(f["quadrant"] in (1, 2, 3, 4) and f["violation_type"] in (set(PENALTIES) | {"UNVERIFIED_ANOMALY"})
               and f["rationale"] for f in result["findings"])
    weighted = result["quadrant_scores"]["weighted_quadrant_scores"]
    assert abs(sum(weighted.values()) - result["composite_score"]) <= .03
    assert result["quadrant_scores"]["composite_score"] == result["composite_score"]
    assert result["turing_test_pass"] == all(result["turing_gates"].values())
    assert result["passed_institutional_gate"] == (result["composite_score"] >= 80
        and all(result["turing_gates"].values()) and not result["incomplete_checks"])
    assert result["evaluation_complete"] == (not result["incomplete_checks"])
    assert trusted_policy["professional_calibration"] == "structural_only"
    assert "expert_calibration" in result["incomplete_checks"]
    assert packet["status"] == "PENDING" and not result["passed_institutional_gate"]
    assert memo["engagement_id"] == engagement and engagement in memo["memo_markdown_text"]
    assert "BLIND PARTNER REVIEW: PENDING" in memo["memo_markdown_text"]
    assert packet["workbook_sha256"] == sha(workbook)
    assert packet["report_sha256"] == sha(json.dumps(report, sort_keys=True, separators=(",", ":")).encode())
    assert packet["spa_sha256"] == sha(json.dumps(spa, sort_keys=True, separators=(",", ":")).encode())
    original_events = [e for e in original_store.events() if e["subject"] == original_id]
    assert any(e["type"] == "qoe.audit.ast.completed.v1" for e in original_events)
    assert any(e["type"] == "qoe.audit.benford.completed.v1" for e in original_events)
    assert not any(e["type"] == "qoe.audit.eqcr.certified.v1" for e in original_events)

    rows = []
    def record(name, request, status, detail):
        rows.append((name, request, status, detail))
    record("Stored handoff", "JobStore.get; JobStore.submission", "PASS",
           f"job `{original_id}` COMPLETED; all three artifacts and trusted Apex policy match")
    record("Result consistency", "Stored result and event records", "PASS",
           f"{audit['total_cells_scanned']} cells scanned, {audit['check_bars_reconciled']} check bars, "
           f"{len(result['findings'])} findings; score {result['composite_score']}; no certification event")
    record("Professional boundary", "Policy, incomplete checks, memo, review packet", "PASS",
           "structural_only; expert_calibration incomplete; review PENDING; no certification")

    with TestClient(workspace.app) as client:
        status_http = client.get(f"/api/v1/audit/jobs/{original_id}")
        memo_http = client.get(f"/api/v1/audit/jobs/{original_id}/memo")
        missing_http = client.get("/api/v1/audit/jobs/not-a-job")
        assert status_http.status_code == 200 and status_http.json() == original
        assert memo_http.status_code == 200 and memo_http.json() == memo
        assert missing_http.status_code == 404
        record("HTTP result and memo", "GET /audit/jobs/{id}; GET /audit/jobs/{id}/memo; unknown ID", "PASS",
               "exact durable result and memo; unknown ID 404")

    def provider(s, k):
        return load_scenario_policy(package.parent, s, k)
    jobs = EvaluationJobs(provider, timeout=20, store_path=output / "jobs.sqlite3")
    executor = ThreadPoolExecutor(max_workers=5)
    grpc_server = grpc.server(executor)
    artifact_uri = "artifact://stage4/apex_databook.xlsx"
    def read_artifact(uri):
        if uri != artifact_uri:
            raise KeyError(uri)
        return (handoff / "apex_databook.xlsx").read_bytes()
    def resolve_engagement(value):
        if value != engagement:
            raise KeyError(value)
        return scenario_id, seed
    pool = register_grpc_service(grpc_server, jobs, read_artifact, resolve_engagement)
    port = grpc_server.add_insecure_port("127.0.0.1:0")
    assert port > 0
    grpc_server.start()
    channel = grpc.insecure_channel(f"127.0.0.1:{port}")

    def rpc(method, request_type, response_type, **values):
        request = message_factory.GetMessageClass(pool.FindMessageTypeByName("qoe.audit.v1." + request_type))(**values)
        response = message_factory.GetMessageClass(pool.FindMessageTypeByName("qoe.audit.v1." + response_type))
        call = channel.unary_unary("/qoe.audit.v1.AuditEvaluationService/" + method,
                                   request_serializer=lambda x: x.SerializeToString(),
                                   response_deserializer=response.FromString)
        return call(request, timeout=25)

    try:
        queued = rpc("SubmitEngagementForGrading", "SubmitEngagementForGradingRequest", "GradingJobQueuedResponse",
                     engagement_id=engagement, user_id="USR_STAGE5_ANALYST", scenario_id=scenario_id,
                     seed_hex_64=seed, fdb_xlsx_blob_uri=artifact_uri,
                     report_memo_json=json.dumps(report, sort_keys=True), spa_exhibit_b_json=json.dumps(spa, sort_keys=True),
                     submission_checksum_sha256=sha(workbook + canonical(report, spa)))
        assert queued.job_id and queued.job_id != original_id
        assert queued.engagement_id == engagement and queued.status == "QUEUED" and queued.HasField("queued_at")
        observed_statuses = [queued.status]
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            polled = rpc("GetGradingStatus", "GradingJobStatusRequest", "GradingJobStatusResponse",
                         job_id=queued.job_id)
            if polled.status != observed_statuses[-1]:
                observed_statuses.append(polled.status)
            if polled.status in ("COMPLETED", "FAILED"):
                break
            time.sleep(.05)
        else:
            raise AssertionError("Protobuf grading job did not reach a terminal state in 30 seconds")
        assert jobs.wait(30), "Protobuf grading job did not settle"
        grpc_job = jobs.status(queued.job_id)
        assert grpc_job["status"] == "COMPLETED", grpc_job.get("error")
        assert jobs.store.submission(queued.job_id)[:3] == (workbook, report, spa)
        record("SubmitEngagementForGrading", "gRPC, actual Stage 4 artifacts and checksum", "PASS",
               f"new durable job `{queued.job_id}`; terminal `{grpc_job['status']}`")

        status = rpc("GetGradingStatus", "GradingJobStatusRequest", "GradingJobStatusResponse", job_id=queued.job_id)
        assert status.job_id == queued.job_id and status.status == "COMPLETED" and status.HasField("completed_at")
        assert status.ast_report.engagement_id == engagement
        assert status.ast_report.total_cells_scanned == grpc_job["result"]["ast_report"]["total_cells_scanned"]
        assert status.ast_report.check_bars_reconciled == 11
        assert status.HasField("scores") and status.HasField("benford_result") and status.HasField("eqcr_memo")
        assert status.benford_result.engagement_id == engagement
        assert status.scores.composite_score == grpc_job["result"]["composite_score"]
        assert not status.scores.passed_institutional_threshold
        record("GetGradingStatus", "gRPC completed grading job", "PASS",
               f"polled statuses `{observed_statuses}`; typed AST, scores, Benford, memo and timestamp agree with durable job")

        grpc_memo = rpc("GenerateEQCRMemo", "GenerateEQCRMemoRequest", "EQCRMemoResponse",
                        job_id=queued.job_id, engagement_id=engagement)
        assert grpc_memo.engagement_id == engagement and engagement in grpc_memo.memo_markdown_text
        assert grpc_memo.scores.composite_score == status.scores.composite_score
        assert "BLIND PARTNER REVIEW: PENDING" in grpc_memo.memo_markdown_text
        record("GenerateEQCRMemo", "gRPC completed grading job and matching engagement", "PASS",
               "attributed memo, matching scores, pending professional review")

        before = set(jobs.store.load())
        ast = rpc("RunASTFormulaAudit", "RunASTFormulaAuditRequest", "ASTAuditReport",
                  engagement_id=engagement, fdb_xlsx_blob_uri=artifact_uri)
        assert jobs.wait(30), "Formula-only job did not settle"
        new_jobs = set(jobs.store.load()) - before
        assert len(new_jobs) == 1
        ast_id = new_jobs.pop()
        ast_job = jobs.status(ast_id)
        assert ast.engagement_id == engagement and ast.check_bars_reconciled == 11
        assert ast.total_cells_scanned > 0 and ast_job["status"] == "COMPLETED"
        assert ast_job["result"]["operation"] == "ast" and not ast_job["result"]["passed_institutional_gate"]
        assert "eqcr_memo" not in ast_job["result"] and "benford_result" not in ast_job["result"]
        assert not any(e["subject"] == ast_id and e["type"] == "qoe.audit.eqcr.certified.v1" for e in jobs.store.events())
        record("RunASTFormulaAudit", "gRPC Stage 4 XLSX URI", "PASS",
               f"formula-only job `{ast_id}`; no memo, Benford result, or certification")

        scan = rpc("ScanBenfordDistribution", "ScanBenfordDistributionRequest", "BenfordDistributionResult",
                   engagement_id=engagement, ledger_table_name="proj_gl")
        expected_count = sum(float(v["amount"]) != 0 for v in trusted_policy["ledger"].values())
        assert scan.engagement_id == engagement and scan.total_transactions_scanned == expected_count
        assert len(scan.first_digit_distribution) == 9 and len(scan.second_digit_distribution) == 10
        categories = {v.get("account_category") for v in trusted_policy["ledger"].values() if v.get("account_category")}
        category = sorted(categories)[0] if categories else "NONEXISTENT_CATEGORY"
        filtered = rpc("ScanBenfordDistribution", "ScanBenfordDistributionRequest", "BenfordDistributionResult",
                       engagement_id=engagement, ledger_table_name="proj_gl", account_category_filter=category)
        expected_filtered = sum(float(v["amount"]) != 0 and v.get("account_category") == category
                                for v in trusted_policy["ledger"].values())
        assert filtered.total_transactions_scanned == expected_filtered
        record("ScanBenfordDistribution", "gRPC proj_gl, full ledger and category filter", "PASS",
               f"full {expected_count} nonzero transactions, filtered {expected_filtered} for `{category}`; 9/10 digit bins")

        def rejected(method, request_type, response_type, code, **values):
            try:
                rpc(method, request_type, response_type, **values)
            except grpc.RpcError as error:
                assert error.code() == code, (method, error.code(), error.details())
                return
            raise AssertionError(f"{method} accepted invalid request")

        rejected("SubmitEngagementForGrading", "SubmitEngagementForGradingRequest", "GradingJobQueuedResponse",
                 grpc.StatusCode.INVALID_ARGUMENT, engagement_id=engagement, scenario_id=scenario_id,
                 seed_hex_64=seed, fdb_xlsx_blob_uri=artifact_uri, report_memo_json="{}",
                 spa_exhibit_b_json="{}", submission_checksum_sha256="0" * 64)
        rejected("GetGradingStatus", "GradingJobStatusRequest", "GradingJobStatusResponse",
                 grpc.StatusCode.NOT_FOUND, job_id="unknown-stage5-job")
        rejected("ScanBenfordDistribution", "ScanBenfordDistributionRequest", "BenfordDistributionResult",
                 grpc.StatusCode.INVALID_ARGUMENT, engagement_id=engagement, ledger_table_name="unsupported")
        rejected("GenerateEQCRMemo", "GenerateEQCRMemoRequest", "EQCRMemoResponse",
                 grpc.StatusCode.PERMISSION_DENIED, engagement_id="wrong-engagement", job_id=queued.job_id)
        rejected("GenerateEQCRMemo", "GenerateEQCRMemoRequest", "EQCRMemoResponse",
                 grpc.StatusCode.FAILED_PRECONDITION, engagement_id=engagement, job_id=ast_id)
        record("RPC rejection contracts", "wrong checksum, unknown job, unsupported table, wrong engagement, formula-only memo", "PASS",
               "INVALID_ARGUMENT, NOT_FOUND, INVALID_ARGUMENT, PERMISSION_DENIED, FAILED_PRECONDITION")
    finally:
        channel.close()
        grpc_server.stop(0).wait()
        assert jobs.wait(30), "Worker still active after gRPC shutdown"
        executor.shutdown(wait=True)

    isolated_http = FastAPI()
    audit_router, _ = create_router(package.parent, store_path=output / "jobs.sqlite3")
    isolated_http.include_router(audit_router)
    with TestClient(isolated_http) as client:
        ast_status = client.get(f"/api/v1/audit/jobs/{ast_id}")
        ast_memo = client.get(f"/api/v1/audit/jobs/{ast_id}/memo")
        assert ast_status.status_code == 200 and ast_status.json()["status"] == "COMPLETED"
        assert ast_memo.status_code == 409
        record("HTTP formula-only boundary", "GET /audit/jobs/{formula_job}/memo", "409 PASS",
               "completed AST-only job has no grading memo")

    # A second transport instance reads the workspace-submitted job's own store.
    original_jobs = EvaluationJobs(provider, timeout=20, store_path=handoff / "jobs.sqlite3")
    original_executor = ThreadPoolExecutor(max_workers=2)
    original_server = grpc.server(original_executor)
    original_pool = register_grpc_service(original_server, original_jobs, read_artifact, resolve_engagement)
    original_port = original_server.add_insecure_port("127.0.0.1:0")
    assert original_port > 0
    original_server.start()
    original_channel = grpc.insecure_channel(f"127.0.0.1:{original_port}")
    def original_rpc(method, request_type, response_type, **values):
        request = message_factory.GetMessageClass(original_pool.FindMessageTypeByName(
            "qoe.audit.v1." + request_type))(**values)
        response = message_factory.GetMessageClass(original_pool.FindMessageTypeByName(
            "qoe.audit.v1." + response_type))
        call = original_channel.unary_unary("/qoe.audit.v1.AuditEvaluationService/" + method,
                                            request_serializer=lambda x: x.SerializeToString(),
                                            response_deserializer=response.FromString)
        return call(request, timeout=10)
    try:
        original_status = original_rpc("GetGradingStatus", "GradingJobStatusRequest",
                                       "GradingJobStatusResponse", job_id=original_id)
        original_memo = original_rpc("GenerateEQCRMemo", "GenerateEQCRMemoRequest",
                                     "EQCRMemoResponse", job_id=original_id, engagement_id=engagement)
        assert original_status.status == "COMPLETED" and original_status.job_id == original_id
        assert original_status.ast_report.total_cells_scanned == audit["total_cells_scanned"]
        assert original_status.scores.composite_score == result["composite_score"]
        assert original_memo.engagement_id == engagement and original_memo.memo_markdown_text == memo["memo_markdown_text"]
        record("Original job protobuf retrieval", "gRPC GetGradingStatus and GenerateEQCRMemo on workspace job", "PASS",
               f"original job `{original_id}`; score, AST and attributed memo match HTTP and stored result")
    finally:
        original_channel.close()
        original_server.stop(0).wait()
        original_executor.shutdown(wait=True)

    assert sha((package / "checksum.sha256").read_bytes()) == initial_checksum
    assert verify_package_integrity(package) == sealed
    record("Sealed package", "Recheck all package hashes", "PASS", f"{sealed} sealed files unchanged")
    version = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                             text=True, cwd=Path(__file__).resolve().parents[2]).stdout.strip()
    lines = ["# Stage 5: Apex Level 6 lifecycle verification", "",
             f"Source package: `{package}`; seed `{seed}`; engagement `{engagement}`.",
             f"Stage 4 handoff: `{handoff}`; original job `{original_id}`.",
             f"Code revision `{version}` plus uncommitted changes; Python `{platform.python_version()}`.",
             f"Command: `python qoe_simulator/scenarios/verify_stage5_lifecycle.py --handoff '{handoff}' --package '{package}' --output '{output}'`.",
             f"Isolated new RPC jobs: `{output / 'jobs.sqlite3'}`. Proto unchanged.", "",
             "## Observed checks", "", "| Check | Request/action | Result | Evidence |", "| --- | --- | --- | --- |"]
    lines += [f"| {name} | `{request}` | {status} | {detail} |" for name, request, status, detail in rows]
    lines += ["", "## Actual result from Stage 4 job", "",
              f"- Formula scan: {audit['total_cells_scanned']} cells, {audit['formulas_verified_reproducible']} reproducible formulas, {audit['check_bars_reconciled']} check bars.",
              f"- Findings: {len(result['findings'])}; codes: {', '.join(f['violation_type'] for f in result['findings'])}.",
              f"- Composite score: {result['composite_score']}; gates: `{json.dumps(result['turing_gates'], sort_keys=True)}`.",
              f"- Incomplete checks: `{json.dumps(result['incomplete_checks'])}`; institutional gate: `{result['passed_institutional_gate']}`.",
              "- Professional review: PENDING. A generated memo is an automated result, not partner sign-off.",
              "- Grading status proto has only job_id; its contract cannot enforce engagement-specific lookup.",
              "- The sealed policy contains no ledger account_category values; category-filter request therefore returned zero rows.",
              "- Functional lifecycle and RPC transport PASS. No claim about realism or validity of business conclusions.", ""]
    path = output / "STAGE5_LEVEL6_LIFECYCLE.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"PASS: {len(rows)} checks; original {original_id}; new {queued.job_id}; report {path}")


if __name__ == "__main__":
    main()
