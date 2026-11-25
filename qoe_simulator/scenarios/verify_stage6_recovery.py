"""Fault and recovery verification against isolated Apex package and job stores."""

import argparse
import base64
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def envelope(report, spa):
    return json.dumps({"report": report, "spa": spa}, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def wait_terminal(jobs, job_id, seconds=35):
    deadline = time.monotonic() + seconds
    states = []
    while time.monotonic() < deadline:
        status = jobs.status(job_id)
        if not states or states[-1] != status["status"]:
            states.append(status["status"])
        if status["status"] in ("COMPLETED", "FAILED"):
            return status, states
        time.sleep(.05)
    raise AssertionError(f"Job {job_id} did not settle within {seconds}s; states {states}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("package", "handoff", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    package, handoff, output = args.package.resolve(strict=True), args.handoff.resolve(strict=True), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    os.environ["QOE_SCENARIO_PACKAGE_DIR"] = str(package)
    os.environ["QOE_WORKSPACE_STATE_DB"] = str(output / "workspace.sqlite3")
    os.environ["QOE_AUDIT_JOB_STORE"] = str(output / "http_jobs.sqlite3")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

    import grpc
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from google.protobuf import message_factory
    from app.level0_physics.package_integrity import verify_package_integrity
    from app.level4_databook.formula_graph import Databook
    from app.level5_workspace import server as workspace
    from app.level6_audit.rubric_scorer import (EvaluationJobs, JobStore, create_router,
                                                load_scenario_policy)

    scenario, seed, engagement = "target_apex_supply", "0x4a9f82c1e703bd55", "STAGE6_APEX_20261125"
    source_hash = sha((package / "checksum.sha256").read_bytes())
    sealed_count = verify_package_integrity(package)
    workbook = (handoff / "apex_databook.xlsx").read_bytes()
    report = json.loads((handoff / "apex_report.json").read_text(encoding="utf-8"))
    spa = json.loads((handoff / "apex_spa_exhibit_b.json").read_text(encoding="utf-8"))
    trusted_policy = load_scenario_policy(package.parent, scenario, seed)
    assert trusted_policy["professional_calibration"] == "structural_only"
    original = re.search(r"real job `([0-9a-f]{32})`",
                         (handoff / "STAGE4_DELIVERABLE_HANDOFF.md").read_text(encoding="utf-8")).group(1)
    original_store = JobStore(handoff / "jobs.sqlite3")
    original_record = original_store.get(original)
    assert original_record["status"] == "COMPLETED"
    original_events = [e for e in original_store.events() if e["subject"] == original]
    checks = []
    def record(name, request, observed, evidence):
        checks.append((name, request, observed, evidence))

    encoded = base64.b64encode(workbook).decode("ascii")
    body = {"engagement_id": engagement, "user_id": "USR_STAGE6_ANALYST",
            "scenario_id": scenario, "seed_hex_64": seed,
            "fdb_workbook_bytes_base64": encoded,
            "qoe_report_memo_json": json.dumps(report, sort_keys=True),
            "spa_exhibit_b_schedule_json": json.dumps(spa, sort_keys=True),
            "client_checksum_sha256": sha(encoded.encode())}
    with TestClient(workspace.app) as client:
        bad = client.post("/api/v1/workspace/deliverables/compile",
                          json={**body, "client_checksum_sha256": "0" * 64})
        assert bad.status_code == 200 and bad.json()["compilation_success"] is False
        assert bad.json()["compilation_errors"] == ["CLIENT_CHECKSUM_MISMATCH"]
        assert bad.json()["audit_eval_queue_job_id"] == ""
        assert workspace.svc.events.events[-1]["compilation_success"] is False
        assert workspace.audit_jobs.store.load() == {}
        record("Workspace checksum", "POST /workspace/deliverables/compile, wrong base64 checksum", "REJECTED",
               "HTTP 200 failure body; CLIENT_CHECKSUM_MISMATCH; zero jobs; no success event")

        wrong = client.post("/api/v1/workspace/deliverables/compile",
                            json={**body, "seed_hex_64": "0x0000000000000001"})
        assert wrong.status_code == 200 and wrong.json()["compilation_success"] is False
        assert wrong.json()["compilation_errors"] == ["AUDIT_SUBMISSION_FAILED"]
        assert wrong.json()["audit_eval_queue_job_id"] == ""
        assert "seed mismatch" in wrong.json()["audit_submission_error"].lower()
        assert workspace.svc.events.events[-1]["compilation_success"] is False
        assert workspace.audit_jobs.store.load() == {}
        record("Workspace wrong seed", "POST /workspace/deliverables/compile, changed seed", "REJECTED",
               "HTTP 200 failure body; AUDIT_SUBMISSION_FAILED; seed mismatch; zero jobs")

        audit_body = {"engagement_id": engagement, "scenario_id": scenario, "seed_hex_64": seed,
                      "workbook_base64": encoded, "report": report, "spa": spa,
                      "checksum_sha256": sha(workbook + envelope(report, spa))}
        bad_audit = client.post("/api/v1/audit/submit",
                                json={**audit_body, "checksum_sha256": "0" * 64})
        bad_seed = client.post("/api/v1/audit/submit",
                               json={**audit_body, "seed_hex_64": "0x0000000000000001"})
        assert bad_audit.status_code == 400 and "checksum mismatch" in bad_audit.text.lower()
        assert bad_seed.status_code == 400 and "seed mismatch" in bad_seed.text.lower()
        assert workspace.audit_jobs.store.load() == {}
        record("Audit HTTP checksum and seed", "POST /audit/submit twice with incorrect inputs", "REJECTED",
               "both HTTP 400; no job persisted")

    grpc_jobs = EvaluationJobs(lambda s, k: load_scenario_policy(package.parent, s, k),
                               store_path=output / "grpc_jobs.sqlite3")
    executor = ThreadPoolExecutor(max_workers=3)
    grpc_server = grpc.server(executor)
    from app.level6_audit.rubric_scorer import register_grpc_service
    pool = register_grpc_service(grpc_server, grpc_jobs,
                                 lambda uri: workbook if uri == "artifact://apex.xlsx" else (_ for _ in ()).throw(KeyError(uri)),
                                 lambda e: (scenario, seed))
    port = grpc_server.add_insecure_port("127.0.0.1:0")
    assert port > 0
    grpc_server.start()
    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    def rpc(**values):
        request_type = message_factory.GetMessageClass(pool.FindMessageTypeByName(
            "qoe.audit.v1.SubmitEngagementForGradingRequest"))
        response_type = message_factory.GetMessageClass(pool.FindMessageTypeByName(
            "qoe.audit.v1.GradingJobQueuedResponse"))
        method = channel.unary_unary("/qoe.audit.v1.AuditEvaluationService/SubmitEngagementForGrading",
                                      request_serializer=lambda x: x.SerializeToString(),
                                      response_deserializer=response_type.FromString)
        return method(request_type(**values), timeout=10)
    proto_body = {"engagement_id": engagement, "scenario_id": scenario, "seed_hex_64": seed,
                  "fdb_xlsx_blob_uri": "artifact://apex.xlsx", "report_memo_json": json.dumps(report),
                  "spa_exhibit_b_json": json.dumps(spa),
                  "submission_checksum_sha256": sha(workbook + envelope(report, spa))}
    try:
        for label, changes, code in (("checksum", {"submission_checksum_sha256": "0" * 64}, grpc.StatusCode.INVALID_ARGUMENT),
                                     ("seed", {"seed_hex_64": "0x0000000000000001"}, grpc.StatusCode.INVALID_ARGUMENT),
                                     ("missing workbook URI", {"fdb_xlsx_blob_uri": "artifact://missing"}, grpc.StatusCode.NOT_FOUND)):
            try:
                rpc(**{**proto_body, **changes})
                raise AssertionError(f"gRPC accepted {label}")
            except grpc.RpcError as error:
                assert error.code() == code, (label, error.code(), error.details())
            assert grpc_jobs.store.load() == {}
            record("Protobuf " + label, "SubmitEngagementForGrading with " + label, code.name,
                   "typed rejection; no job persisted")
    finally:
        channel.close()
        grpc_server.stop(0).wait()
        executor.shutdown(wait=True)

    copied = output / "missing_package" / scenario
    shutil.copytree(package, copied)
    missing = copied / "ground_truth.duckdb"
    missing.unlink()
    try:
        Databook().build(str(copied))
        raise AssertionError("Missing ledger accepted")
    except FileNotFoundError as error:
        assert "ground_truth.duckdb" in str(error)
    assert not missing.exists()
    try:
        load_scenario_policy(copied.parent, scenario, seed)
        raise AssertionError("Missing package file accepted")
    except FileNotFoundError as error:
        assert "ground_truth.duckdb" in str(error)
    record("Missing sealed package file", "Disposable copy without ground_truth.duckdb", "REJECTED",
           "Databook and policy loader reject; no empty replacement database")

    provider = lambda s, k: load_scenario_policy(package.parent, s, k)
    damaged_jobs = EvaluationJobs(provider, timeout=20, store_path=output / "damaged_jobs.sqlite3")
    damaged = b"corrupted XLSX bytes, with a correct submission checksum"
    queued = damaged_jobs.submit(engagement, scenario, seed, damaged, report, spa,
                                 sha(damaged + envelope(report, spa)))
    failed, transitions = wait_terminal(damaged_jobs, queued["job_id"])
    assert failed["status"] == "FAILED" and failed.get("error")
    assert damaged_jobs.wait(25)
    assert not any(e["type"] == "qoe.audit.eqcr.certified.v1" for e in damaged_jobs.store.events())
    damaged_app = FastAPI()
    damaged_router, _ = create_router(package.parent, store_path=output / "damaged_jobs.sqlite3")
    damaged_app.include_router(damaged_router)
    with TestClient(damaged_app) as client:
        response = client.get(f"/api/v1/audit/jobs/{queued['job_id']}/memo")
        assert response.status_code == 409
    record("Damaged workbook", "Audit submit with bad XLSX and valid recomputed checksum", "FAILED",
           f"job `{queued['job_id']}` states {transitions}; error `{failed['error']}`; memo 409; no certification")

    record_data = {"engagement_id": engagement, "status": "QUEUED",
                   "queued_at": datetime.now(timezone.utc).isoformat()}
    captured_policy = dict(trusted_policy, _operation="grade")
    replay_id = "stage6_queued_replay"
    replay_store = JobStore(output / "replay_jobs.sqlite3")
    replay_store.enqueue(dict(record_data, job_id=replay_id), workbook, report, spa, captured_policy)
    def forbidden(*_):
        raise AssertionError("Recovery must use stored policy")
    replay_jobs = EvaluationJobs(forbidden, timeout=20, store_path=output / "replay_jobs.sqlite3")
    replayed, replay_states = wait_terminal(replay_jobs, replay_id)
    assert replay_jobs.wait(25) and replayed["status"] == "COMPLETED", replayed.get("error")
    assert replay_store.submission(replay_id)[:3] == (workbook, report, spa)
    assert replayed["result"]["partner_review_packet"]["status"] == "PENDING"
    events = [e["type"] for e in replay_store.events() if e["subject"] == replay_id]
    assert events.count("qoe.audit.job.started.v1") == 1
    assert "qoe.audit.eqcr.certified.v1" not in events
    record("Queued restart", "Persisted valid QUEUED job; new EvaluationJobs service", "COMPLETED",
           f"job `{replay_id}` states {replay_states}; stored artifacts used; one start event; review PENDING")

    absent_id = "stage6_missing_payload"
    absent_store = JobStore(output / "missing_input_jobs.sqlite3")
    absent_store.save(dict(record_data, job_id=absent_id))
    absent_jobs = EvaluationJobs(forbidden, store_path=output / "missing_input_jobs.sqlite3")
    absent = absent_jobs.status(absent_id)
    assert absent["status"] == "FAILED" and "EVALUATION_INTERRUPTED" in absent["error"]
    record("Missing persisted payload", "QUEUED record with absent submissions row; restart", "FAILED",
           f"{absent['error']}")

    tampered_id = "stage6_tampered_payload"
    tampered_store = JobStore(output / "tampered_input_jobs.sqlite3")
    tampered_store.enqueue(dict(record_data, job_id=tampered_id), workbook, report, spa, captured_policy)
    with tampered_store.connect() as db:
        db.execute("UPDATE submissions SET workbook=? WHERE id=?", (b"changed", tampered_id))
    tampered_jobs = EvaluationJobs(forbidden, store_path=output / "tampered_input_jobs.sqlite3")
    tampered = tampered_jobs.status(tampered_id)
    assert tampered["status"] == "FAILED" and "integrity" in tampered["error"].lower()
    record("Tampered persisted payload", "Alter workbook blob without changing stored checksum; restart", "FAILED",
           f"{tampered['error']}")

    competing_id = "stage6_competing_claim"
    competing_store = JobStore(output / "competing_jobs.sqlite3")
    competing_store.enqueue(dict(record_data, job_id=competing_id), workbook, report, spa, captured_policy)
    first = EvaluationJobs(forbidden, timeout=20, store_path=output / "competing_jobs.sqlite3")
    second = EvaluationJobs(forbidden, timeout=20, store_path=output / "competing_jobs.sqlite3")
    assert first.wait(30) and second.wait(30)
    competing = competing_store.get(competing_id)
    assert competing["status"] == "COMPLETED", competing.get("error")
    starts = [e for e in competing_store.events() if e["subject"] == competing_id
              and e["type"] == "qoe.audit.job.started.v1"]
    assert len(starts) == 1
    with competing_store.connect() as db:
        owner = db.execute("SELECT owner FROM leases WHERE id=?", (competing_id,)).fetchone()[0]
    loser = second.owner if owner == first.owner else first.owner
    try:
        competing_store.save(competing, owner=loser)
        raise AssertionError("Stale owner modified completed job")
    except ValueError as error:
        assert "lease lost" in str(error).lower()
    record("Competing owners", "Two services open same QUEUED job; stale write", "PASS",
           f"one start event; terminal COMPLETED; owner `{owner}`; other owner fenced")

    interrupted_dir = output / "interrupted"
    interrupted_dir.mkdir()
    marker = interrupted_dir / "processing.json"
    interrupted_path = interrupted_dir / "jobs.sqlite3"
    helper = Path(__file__).with_name("stage6_interrupted_submitter.py")
    command = [sys.executable, str(helper), "--package", str(package), "--handoff", str(handoff),
               "--store", str(interrupted_path), "--marker", str(marker)]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 20
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.02)
        assert marker.exists(), f"Helper failed before PROCESSING: {process.communicate(timeout=2)[1].decode(errors='replace')}"
        mark = json.loads(marker.read_text(encoding="utf-8"))
        assert mark["pid"] == process.pid and mark["status"] == "PROCESSING"
        process.terminate()
        process.communicate(timeout=5)
        stopped = JobStore(interrupted_path).get(mark["job_id"])
        assert stopped["status"] == "PROCESSING", stopped
        assert not any(e["type"] == "qoe.audit.eqcr.certified.v1" for e in JobStore(interrupted_path).events())
        recovered_jobs = EvaluationJobs(forbidden, timeout=20, store_path=interrupted_path)
        assert recovered_jobs.wait(5)
        assert recovered_jobs.status(mark["job_id"])["status"] == "PROCESSING"
        recovered_jobs.start_recovery(interval=1)
        started = time.monotonic()
        recovered, states = wait_terminal(recovered_jobs, mark["job_id"], seconds=90)
        assert recovered_jobs.stop_recovery() and recovered_jobs.wait(25)
        assert recovered["status"] == "COMPLETED", recovered.get("error")
        assert JobStore(interrupted_path).submission(mark["job_id"])[:3] == (workbook, report, spa)
        job_events = [e["type"] for e in JobStore(interrupted_path).events() if e["subject"] == mark["job_id"]]
        assert job_events.count("qoe.audit.job.started.v1") == 2
        assert "qoe.audit.eqcr.certified.v1" not in job_events
        record("Interrupted processing service", "Terminate isolated PID after PROCESSING; restart; natural lease expiry", "COMPLETED",
               f"PID {mark['pid']}; job `{mark['job_id']}`; restart states {states}; "
               f"recovered in {time.monotonic()-started:.1f}s; two starts (original and replay), no certification")
    finally:
        if process.poll() is None:
            process.terminate()
            process.communicate(timeout=5)

    assert sha((package / "checksum.sha256").read_bytes()) == source_hash
    assert verify_package_integrity(package) == sealed_count
    assert original_store.get(original) == original_record
    assert [e for e in original_store.events() if e["subject"] == original] == original_events
    record("Original controls", "Rehash sealed package; compare original Stage 4 job and events", "PASS",
           f"{sealed_count} files and original completed job unchanged")

    revision = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, cwd=Path(__file__).resolve().parents[2]).stdout.strip()
    lines = ["# Stage 6: Apex recovery and rejection verification", "",
             f"Source package: `{package}`. Scenario `{scenario}`, seed `{seed}`. Original Stage 4 job `{original}`.",
             f"Code revision `{revision}` plus uncommitted changes; Python `{platform.python_version()}`.",
             f"Command: `python qoe_simulator/scenarios/verify_stage6_recovery.py --package '{package}' --handoff '{handoff}' --output '{output}'`.",
             f"All mutations and job stores were isolated under `{output}`. Sealed package checksum SHA-256 `{source_hash}`.", "",
             "## Observed faults and recovery", "", "| Check | Request or fault | Result | Evidence |", "| --- | --- | --- | --- |"]
    lines += [f"| {name} | `{request}` | {observed} | {evidence} |" for name, request, observed, evidence in checks]
    lines += ["", "## Boundaries", "",
              "- The workspace returns HTTP 200 with a failure body for rejected deliverables. Both fields and absence of a job were checked.",
              "- The damaged workbook used a valid newly computed checksum, reaching the worker rather than merely failing the checksum test.",
              "- The interrupted child was terminated by its captured PID after the job entered PROCESSING. Its live lease prevented immediate duplicate replay; the new service recovered after natural expiry.",
              "- The grade gate stayed closed because professional calibration remains pending. This is functional recovery evidence, not a QoE conclusion.",
              "- Proto and sealed Apex package were unchanged.", ""]
    report_path = output / "STAGE6_RECOVERY_REJECTION.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"PASS: {len(checks)} checks; report {report_path}")


if __name__ == "__main__":
    main()
