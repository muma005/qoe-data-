"""Adversarial regression cases for the production Level 6 grading path."""

import unittest
import base64
import hashlib
import json
import tempfile
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from app.level6_audit.ast_audit import WorkbookAudit, verify_submission_evidence
from app.level6_audit.benford_scanner import BenfordScanner
from app.level6_audit.rubric_scorer import create_router, evaluate_submission
from tests.test_level6_workbook import fixture, policy


def replace_sheet_xml(workbook, sheet, old, new):
    output = BytesIO()
    with ZipFile(BytesIO(workbook)) as source, ZipFile(output, "w") as destination:
        for member in source.infolist():
            content = source.read(member.filename)
            if member.filename == sheet:
                assert content.count(old) == 1
                content = content.replace(old, new)
            destination.writestr(member, content)
    return output.getvalue()


def evidence_scenario():
    return {
        "workbook_policy": policy(),
        "ledger": {"L": {"cell": "S0!B2", "amount": "10", "document_id": "D",
                         "document_path": "amount", "document_value": "10"}},
        "documents": {"D": {"amount": "10"}},
        "anomalies": {"A": {"cell": "S0!C2", "amount": "10", "ledger_ids": ["L"]}},
        "scope_gaps": {}, "replacement_costs": [], "allocations": {}, "reconciliations": [],
        "professional_checks": [], "commercial_checks": [], "legal_checks": [], "behavior_checks": [],
        "professional_calibration": "structural_only",
    }


class AdversarialGradingTests(unittest.TestCase):
    def test_formula_disguised_as_trusted_ledger_input_is_rejected(self):
        forged = replace_sheet_xml(
            fixture(), "xl/worksheets/s0.xml",
            b'<c r="B2"><v>10</v></c>', b'<c r="B2"><f>B3</f><v>10</v></c>',
        )
        scenario = evidence_scenario()
        report = {"sections": {"03_Quality_of_Earnings": {"anomalies": [
            {"anomaly_id": "A", "cell": "S0!C2", "amount": "10"}]}}}
        result = evaluate_submission(forged, report, {}, scenario)
        self.assertIn("LEDGER_INPUT_MISMATCH", {f["violation_type"] for f in result["findings"]})
        self.assertFalse(result["passed_institutional_gate"])

    def test_duplicated_escrow_cannot_satisfy_scope_protection(self):
        scenario = evidence_scenario()
        scenario["scope_gaps"] = {"G": {"minimum_escrow": "100"}}
        report = {"sections": {"10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities": {
            "caveats": [{"gap_id": "G", "disclosure": "Source records missing"}]}}}
        spa = {"escrows": [{"gap_id": "G", "amount": "1"}, {"gap_id": "G", "amount": "100"}]}
        result = evaluate_submission(fixture(), report, spa, scenario)
        self.assertIn("SCOPE_PROTECTION", {f["violation_type"] for f in result["findings"]})
        self.assertFalse(result["turing_gates"]["T05"])

    def test_duplicated_disclosure_cannot_satisfy_scope_protection(self):
        scenario = evidence_scenario()
        scenario["scope_gaps"] = {"G": {"minimum_escrow": "100"}}
        caveat = {"gap_id": "G", "disclosure": "Missing source records"}
        report = {"sections": {"10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities": {
            "caveats": [caveat, caveat]}}}
        result = evaluate_submission(fixture(), report, {"escrows": [
            {"gap_id": "G", "amount": "100"}]}, scenario)
        self.assertIn("SCOPE_PROTECTION", {f["violation_type"] for f in result["findings"]})

    def test_independent_business_checks_detect_individual_manipulations(self):
        report = {"sections": {"01_Summary": {"amount": "10"}}}
        cases = [
            ({"replacement_costs": [{"gross_cell": "S0!B2", "net_cell": "S0!C2",
                                     "replacement_cost": "2"}]}, "REPLACEMENT_COST"),
            ({"allocations": {"exposure": ["S0!B2", "S0!C2"]}}, "DOUBLE_DIPPING"),
            ({"reconciliations": [{"report_path": "sections.01_Summary.amount",
                                    "cell": "S0!D2"}]}, "CROSS_SCHEDULE_MISMATCH"),
            ({"workbook_policy": dict(policy(), pvm=[{
                "delta": "S0!C2", "price": "S0!D2", "volume": "S0!D2",
                "mix": "S0!D2"}])}, "PVM_NON_ADDITIVE"),
        ]
        for changes, expected in cases:
            with self.subTest(expected=expected):
                scenario = evidence_scenario()
                scenario.update(changes)
                result = evaluate_submission(fixture(), report, {}, scenario)
                self.assertIn(expected, {f["violation_type"] for f in result["findings"]})
                self.assertFalse(result["passed_institutional_gate"])

    def test_malformed_or_nonfinite_inputs_fail_closed(self):
        scanner = BenfordScanner()
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                scanner.scan(["123", value])
        scenario = evidence_scenario()
        scenario["scope_gaps"] = {"G": {"minimum_escrow": "100"}}
        report = {"sections": {"10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities": {
            "caveats": [{"gap_id": "G", "disclosure": "Missing records"}]}}}
        for escrows in ([None, {"gap_id": "G", "amount": "100"}],
                        [{"gap_id": "G", "amount": "NaN"}]):
            with self.subTest(escrows=escrows):
                outcome = evaluate_submission(fixture(), report, {"escrows": escrows}, scenario)
                self.assertFalse(outcome["turing_gates"]["T05"])

    def test_claim_requires_each_link_in_source_chain(self):
        scenario = evidence_scenario()
        report = {"sections": {"03_Quality_of_Earnings": {"anomalies": [
            {"anomaly_id": "A", "cell": "S0!C2", "amount": "10"}]}}}
        workbook = WorkbookAudit(fixture())
        workbook.audit(policy())
        findings, verified = verify_submission_evidence(workbook, report, scenario)
        self.assertEqual(findings, [])
        self.assertEqual(verified, ["A"])
        scenario["documents"]["D"]["amount"] = "11"
        findings, verified = verify_submission_evidence(workbook, report, scenario)
        self.assertEqual(verified, [])
        self.assertIn("UNVERIFIED_ANOMALY", {f["violation_type"] for f in findings})

    def test_http_formula_route_binds_bytes_and_never_issues_certification(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        workbook = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "packages"
            target = root / "s"
            target.mkdir(parents=True)
            scenario = evidence_scenario()
            scenario["seed_hex_64"] = "0x01"
            (target / "audit_policy.json").write_text(json.dumps(scenario), encoding="utf-8")
            (target / "manifest.json").write_text(
                json.dumps({"scenario_id": "s", "random_seed": 1}), encoding="utf-8")
            (target / "checksum.sha256").write_text("".join(
                f"{hashlib.sha256((target / name).read_bytes()).hexdigest()}  {name}\n"
                for name in ("audit_policy.json", "manifest.json")), encoding="utf-8")
            router, jobs = create_router(root)
            app = FastAPI()
            app.include_router(router)
            request = {"engagement_id": "e", "scenario_id": "s", "seed_hex_64": "0x01",
                       "workbook_base64": base64.b64encode(workbook).decode(),
                       "checksum_sha256": hashlib.sha256(workbook).hexdigest()}
            with TestClient(app) as client:
                self.assertEqual(client.post("/api/v1/audit/formulas", json=dict(
                    request, checksum_sha256="0" * 64)).status_code, 400)
                self.assertEqual(client.post("/api/v1/audit/formulas", json=dict(
                    request, seed_hex_64="wrong")).status_code, 400)
                response = client.post("/api/v1/audit/formulas", json=request)
                self.assertEqual(response.status_code, 200, response.text)
                job_id = response.json()["job_id"]
                self.assertTrue(jobs.wait(10))
                status = client.get(f"/api/v1/audit/jobs/{job_id}")
                self.assertEqual(status.json()["status"], "COMPLETED", status.text)
                self.assertTrue(status.json()["result"]["ast_report"]["passed"])
                self.assertFalse(status.json()["result"]["passed_institutional_gate"])
                self.assertEqual(client.get(f"/api/v1/audit/jobs/{job_id}/memo").status_code, 409)
                self.assertEqual(client.get("/api/v1/audit/jobs/unknown").status_code, 404)
                self.assertEqual(client.post("/api/v1/audit/benford", json={
                    "scenario_id": "s", "seed_hex_64": "0x01"}).json()["total_transactions_scanned"], 1)
