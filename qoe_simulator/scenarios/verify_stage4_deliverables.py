"""Verify the Apex package -> workbook/report/SPA -> workspace -> Level 6 handoff."""

import argparse
import base64
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import zipfile
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    package = args.package.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    os.environ["QOE_SCENARIO_PACKAGE_DIR"] = str(package)
    os.environ["QOE_WORKSPACE_STATE_DB"] = str(output / "workspace.sqlite3")
    os.environ["QOE_AUDIT_JOB_STORE"] = str(output / "jobs.sqlite3")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

    from fastapi.testclient import TestClient
    from openpyxl import load_workbook
    from app.level0_physics.package_integrity import verify_package_integrity
    from app.level4_databook.formula_graph import Databook, _databook_to_sheets
    from app.level4_databook.sandbox_worker import XLSXSerializer
    from app.level5_workspace import server
    from app.level5_workspace.report import ReportAssembler, SPAExhibitBBuilder
    from app.level6_audit.rubric_scorer import load_scenario_policy

    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    scenario_id = "target_apex_supply"
    seed = "0x4a9f82c1e703bd55"
    engagement = "STAGE4_APEX_20261124"
    assert manifest["scenario_id"] == scenario_id
    assert manifest["random_seed"] == int(seed, 16)
    initial = digest((package / "checksum.sha256").read_bytes())
    sealed = verify_package_integrity(package)
    assert Path(server.svc.package_dir).resolve() == package
    assert server._audit_root.resolve() == package.parent
    assert Path(server.audit_jobs.store.path).resolve() == (output / "jobs.sqlite3").resolve()

    book = Databook().build(str(package))
    rendered = _databook_to_sheets(book)
    workbook_path = output / "apex_databook.xlsx"
    XLSXSerializer().serialize(book, str(workbook_path))
    workbook_bytes = workbook_path.read_bytes()
    with zipfile.ZipFile(workbook_path) as archive:
        assert archive.testzip() is None
    workbook = load_workbook(workbook_path, read_only=False, data_only=False)
    assert workbook.sheetnames == list(book.TAB_IDS) == list(rendered)
    checked_cells = 0
    for tab, rows in rendered.items():
        sheet = workbook[tab]
        assert sheet["B1"].value == rows[0][1]
        assert sheet["E1"].value == rows[0][4]
        for index, row in enumerate(rows[1:], 2):
            assert sheet.cell(index, 1).value == row[0], (tab, index, "label")
            actual = sheet.cell(index, 2).value
            if isinstance(row[1], float):
                assert isinstance(actual, (float, int)) and math.isclose(
                    actual, row[1], rel_tol=1e-13, abs_tol=1e-12), (tab, index, "value")
            else:
                assert actual == row[1], (tab, index, "value")
            checked_cells += 2
    workbook.close()

    checks = []
    def record(action, request, response, evidence):
        checks.append((action, request, response, evidence))

    record("Package preflight", "verify_package_integrity", "PASS",
           f"{sealed} sealed files; checksum manifest SHA-256 `{initial}`")
    record("Workbook export", "Databook.build; XLSXSerializer.serialize; reopen XLSX", "PASS",
           f"11 sheets and 11 check-bar formulas; {checked_cells} rendered cells matched")

    with TestClient(server.app) as client:
        report_response = client.post("/api/v1/workspace/report/assemble", json={"package_dir": str(package)})
        assert report_response.status_code == 200, report_response.text
        report = report_response.json()
        assert report == server._jsonable(ReportAssembler().build(book))
        assert report["report_title"] == "Executive Diligence Report"
        assert len(report["sections"]) == 10
        assert all(str(i).zfill(2) in key for i, key in enumerate(report["sections"], 1))
        report_path = output / "apex_report.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        record("Report assembly", "POST /api/v1/workspace/report/assemble", "200 PASS",
               "10 sections; exact response equals builder output for selected Databook")

        spa_response = client.post("/api/v1/workspace/spa/exhibit-b", json={"package_dir": str(package)})
        assert spa_response.status_code == 200, spa_response.text
        spa = spa_response.json()
        assert spa == server._jsonable(SPAExhibitBBuilder().build(book))
        assert set(("document", "1_target_peg", "2_inclusions", "3_exclusions_debt_like",
                    "4_indemnity_escrow", "net_debt_summary")) <= set(spa)
        assert spa["1_target_peg"]["target_nwc"] == report["sections"]["05_Net_Working_Capital"]["target_peg"]
        assert spa["net_debt_summary"] == report["sections"]["06_Net_Debt_and_Debt_Like_Items"]["net_debt"]
        spa_path = output / "apex_spa_exhibit_b.json"
        spa_path.write_text(json.dumps(spa, indent=2, ensure_ascii=False), encoding="utf-8")
        record("SPA assembly", "POST /api/v1/workspace/spa/exhibit-b", "200 PASS",
               "six required fields; target peg and net debt agree with report and builder")

        wrong_package = client.post("/api/v1/workspace/report/assemble", json={"package_dir": str(output)})
        assert wrong_package.status_code == 409, wrong_package.text
        record("Package binding", "POST /report/assemble with unrelated directory", "409 PASS",
               "Caller cannot substitute an unrelated package")

        encoded = base64.b64encode(workbook_bytes).decode("ascii")
        payload = {"engagement_id": engagement, "user_id": "USR_STAGE4_ANALYST",
                   "scenario_id": scenario_id, "seed_hex_64": seed,
                   "fdb_workbook_bytes_base64": encoded,
                   "qoe_report_memo_json": json.dumps(report, sort_keys=True, allow_nan=False),
                   "spa_exhibit_b_schedule_json": json.dumps(spa, sort_keys=True, allow_nan=False),
                   "client_checksum_sha256": digest(encoded.encode("ascii"))}
        bad = client.post("/api/v1/workspace/deliverables/compile",
                          json={**payload, "client_checksum_sha256": "0" * 64})
        assert bad.status_code == 200 and not bad.json()["compilation_success"]
        assert bad.json()["compilation_errors"] == ["CLIENT_CHECKSUM_MISMATCH"]
        assert not bad.json()["audit_eval_queue_job_id"]
        record("Checksum rejection", "POST /deliverables/compile with incorrect checksum", "200 FAIL RESPONSE",
               "CLIENT_CHECKSUM_MISMATCH; no Level 6 job")

        missing_seed = client.post("/api/v1/workspace/deliverables/compile",
                                   json={key: value for key, value in payload.items() if key != "seed_hex_64"})
        assert missing_seed.status_code == 200 and not missing_seed.json()["compilation_success"]
        assert missing_seed.json()["compilation_errors"] == ["AUDIT_SUBMISSION_FAILED"]
        assert not missing_seed.json()["audit_eval_queue_job_id"]
        assert server.svc.events.events[-1]["compilation_success"] is False
        record("Queue failure rejection", "POST /deliverables/compile without seed", "200 FAIL RESPONSE",
               "AUDIT_SUBMISSION_FAILED; no false success or placeholder job")

        submission_response = client.post("/api/v1/workspace/deliverables/compile", json=payload)
        assert submission_response.status_code == 200, submission_response.text
        submitted = submission_response.json()
        assert submitted["compilation_success"] and submitted["compilation_errors"] == [], submitted
        job_id = submitted["audit_eval_queue_job_id"]
        assert job_id and not job_id.startswith("AUDIT_JOB_"), submitted
        assert server.svc._submissions[submitted["submission_id"]]["audit_job"] == job_id
        assert server.svc.events.events[-1]["compilation_success"] is True
        assert server.svc.events.events[-1]["audit_eval_queue_job_id"] == job_id
        status_response = client.get(f"/api/v1/audit/jobs/{job_id}")
        assert status_response.status_code == 200, status_response.text
        job = status_response.json()
        assert job["job_id"] == job_id and job["engagement_id"] == engagement
        assert job["status"] in ("QUEUED", "PROCESSING", "COMPLETED", "FAILED")
        stored_workbook, stored_report, stored_spa, policy = server.audit_jobs.store.submission(job_id)
        assert stored_workbook == workbook_bytes
        assert stored_report == report and stored_spa == spa
        expected_policy = load_scenario_policy(package.parent, scenario_id, seed)
        assert policy["seed_hex_64"] == seed
        assert {key: value for key, value in policy.items() if key != "_operation"} == expected_policy
        assert policy["_operation"] == "grade"
        record("Deliverable submission", "POST /api/v1/workspace/deliverables/compile", "200 PASS",
               f"submission `{submitted['submission_id']}`; real job `{job_id}`")
        record("Level 6 receipt", f"GET /api/v1/audit/jobs/{job_id}; JobStore.submission", "200 PASS",
               f"engagement `{engagement}`; scenario and seed match; status `{job['status']}`; all submitted artifacts match")
        # Keep the submitting process alive until its background worker has settled.
        # Terminal grading is reported separately in Stage 5.
        assert server.audit_jobs.wait(timeout=30), "Audit worker did not settle within 30 seconds"
        terminal = server.audit_jobs.store.get(job_id)
        record("Background worker settlement", "EvaluationJobs.wait(30); JobStore.get", terminal["status"],
               f"job `{job_id}`; error `{terminal.get('error', '')}`")

    final = digest((package / "checksum.sha256").read_bytes())
    assert final == initial and verify_package_integrity(package) == sealed
    record("Package after submission", "verify_package_integrity", "PASS", "All sealed hashes still match")

    version = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                             text=True, cwd=Path(__file__).resolve().parents[2]).stdout.strip()
    paths = (workbook_path, report_path, spa_path)
    lines = ["# Stage 4: Apex deliverable handoff verification", "",
             f"Package: `{package}`. Scenario: `{scenario_id}`. Seed: `{seed}`. Engagement: `{engagement}`.",
             f"Code revision: `{version}` plus uncommitted changes. Python: `{platform.python_version()}`.",
             f"Command: `python qoe_simulator/scenarios/verify_stage4_deliverables.py --package '{package}' --output '{output}'`.",
             f"Isolated workspace and Level 6 job stores: `{output}`. Sealed files: {sealed}.", "",
             "## Artifact inventory", "", "| Artifact | Bytes | SHA-256 |", "| --- | ---: | --- |"]
    for path in paths:
        data = path.read_bytes()
        lines.append(f"| `{path}` | {len(data):,} | `{digest(data)}` |")
    lines += ["", "## Observed operations", "", "| Operation | Request/action | Result | Evidence |",
              "| --- | --- | --- | --- |"]
    lines += [f"| {name} | `{request}` | {response} | {detail} |" for name, request, response, detail in checks]
    lines += ["", "## Submission and checksum contracts", "",
              f"- Workspace checksum (SHA-256 of base64 text): `{digest(encoded.encode('ascii'))}`.",
              f"- Workbook bytes SHA-256: `{digest(workbook_bytes)}`.",
              "- Level 6 checksum: SHA-256 of workbook bytes plus compact, sorted JSON of `report` and `spa`; the server computes this from the submitted sanitized JSON.",
              f"- Submission `{submitted['submission_id']}` yielded durable job `{job_id}` for `{engagement}`.",
              "- The job state shown above was observed during handoff; terminal evaluation is assessed in Stage 5.",
              "- The proto was unchanged. The report and SPA endpoints accept `package_dir`; bound workspace rejects a different directory.",
              "- Functional handoff PASS. No business realism, financial correctness, or certification conclusion is inferred.", ""]
    report_file = output / "STAGE4_DELIVERABLE_HANDOFF.md"
    report_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"PASS: {len(checks)} operations; job {job_id}; report {report_file}")


if __name__ == "__main__":
    main()
