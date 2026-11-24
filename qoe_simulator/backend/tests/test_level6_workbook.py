import unittest
from decimal import Decimal
from io import BytesIO
from zipfile import ZipFile
from xml.sax.saxutils import escape
from app.level6_audit.ast_audit import Parser, evaluate, constants, FormulaError
from app.level6_audit.ast_audit import WorkbookAudit
from app.level6_audit.rubric_scorer import evaluate_submission


def fixture(formula="B2", cached="10"):
    out=BytesIO()
    with ZipFile(out,"w") as z:
        z.writestr("xl/workbook.xml", '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'+''.join(f'<sheet name="S{i}" sheetId="{i}" r:id="r{i}"/>' for i in range(11))+'</sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",'<Relationships>'+''.join(f'<Relationship Id="r{i}" Target="worksheets/s{i}.xml"/>' for i in range(11))+'</Relationships>')
        for i in range(11):
            z.writestr(f"xl/worksheets/s{i}.xml", '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="str"><f>IF(B2=B3,"OK","FAIL")</f><v>OK</v></c></row><row r="2"><c r="B2"><v>10</v></c><c r="D2"><v>0</v></c><c r="C2"><f>'+escape(formula)+'</f><v>'+cached+'</v></c></row><row r="3"><c r="B3"><v>10</v></c></row></sheetData></worksheet>')
    return out.getvalue()


def policy():
    return {"required_sheets":[f"S{i}" for i in range(11)],"check_bars":[f"S{i}!A1" for i in range(11)],"calculation_cells":["S0!C2"]}


class WorkbookTests(unittest.TestCase):
    def test_references_and_rounding_are_not_hardcodes(self):
        self.assertEqual(constants(Parser('=ROUND($D$14,0)').parse()),[])
        self.assertEqual(constants(Parser('=A1+1E3').parse()),['1E+3'])
    def test_recalculates_cached_values(self):
        self.assertTrue(WorkbookAudit(fixture()).audit(policy())["passed"])
        result=WorkbookAudit(fixture(cached="9")).audit(policy())
        self.assertIn("RECALCULATION_MISMATCH",[x["violation_type"] for x in result["findings"]])
    def test_cycles_missing_references_and_hardcodes(self):
        for formula in ["C2", "Z99", "B2+1", "#REF!"]:
            with self.subTest(formula=formula): self.assertFalse(WorkbookAudit(fixture(formula)).audit(policy())["passed"])
    def test_calculation_cell_cannot_be_raw_input(self):
        p=policy();p["calculation_cells"]=["S0!B2"]
        self.assertFalse(WorkbookAudit(fixture()).audit(p)["passed"])
    def test_range_and_safe_arithmetic(self):
        self.assertEqual(evaluate(Parser('=SUM(A1:A3)').parse(),lambda s,c:Decimal(c[1:])),Decimal(6))
    def test_evidence_chain(self):
        scenario={"workbook_policy":policy(),"ledger":{"L":{"cell":"S0!B2","amount":"10","document_id":"D","document_path":"amount","document_value":"10"}},"documents":{"D":{"amount":"10"}},"anomalies":{"A":{"cell":"S0!C2","amount":"10","ledger_ids":["L"]}},"scope_gaps":{},"replacement_costs":[],"allocations":{},"reconciliations":[]}
        report={"sections":{"03_Quality_of_Earnings":{"anomalies":[{"anomaly_id":"A","cell":"S0!C2","amount":"10"}]}}}
        result=evaluate_submission(fixture(),report,{},scenario)
        self.assertFalse(any(x["quadrant"]==1 for x in result["findings"]))
        scenario["documents"]["D"]["amount"]="99"
        result=evaluate_submission(fixture(),report,{},scenario)
        self.assertTrue(any(x["violation_type"]=="UNVERIFIED_ANOMALY" for x in result["findings"]))
        self.assertFalse(result["passed_institutional_gate"])

    def test_duplicate_anomaly_claims_do_not_verify(self):
        from app.level6_audit.ast_audit import verify_submission_evidence
        workbook=WorkbookAudit(fixture())
        scenario={"ledger":{"L":{"cell":"S0!B2","amount":"10","document_id":"D","document_path":"amount","document_value":"10"}},
                  "documents":{"D":{"amount":"10"}},"anomalies":{"A":{"cell":"S0!C2","amount":"10","ledger_ids":["L"]}},
                  "replacement_costs":[],"allocations":{},"reconciliations":[]}
        claim={"anomaly_id":"A","cell":"S0!C2","amount":"10"}
        report={"sections":{"03_Quality_of_Earnings":{"anomalies":[claim,claim]}}}
        findings,verified=verify_submission_evidence(workbook,report,scenario)
        self.assertEqual(verified,[])
        self.assertIn("UNSUPPORTED_ANOMALY",[f["violation_type"] for f in findings])

    def test_complete_policy_replays_and_certifies(self):
        import math
        policy_data=policy()
        policy_data["pvm"]=[{"delta":"S0!C2","price":"S0!C2","volume":"S0!D2","mix":"S0!D2"}]
        ledger={str(i):{"amount":str(10 ** (i/1000*4))} for i in range(1000)}
        scenario={"workbook_policy":policy_data,"ledger":ledger,"documents":{},"anomalies":{},"scope_gaps":{},"replacement_costs":[],"allocations":{},"reconciliations":[{"report_path":"sections.01_Summary.amount","cell":"S0!C2"}],"professional_checks":[],"commercial_checks":[],"legal_checks":[],"behavior_checks":[]}
        report={"sections":{f"{i:02d}_Summary":{"amount":"10"} for i in range(1,11)}}
        first=evaluate_submission(fixture(),report,{},scenario)
        second=evaluate_submission(fixture(),report,{},scenario)
        self.assertEqual(first,second)
        self.assertTrue(first["passed_institutional_gate"],first)
        report["sections"]["01_Summary"]["amount"]="99"
        self.assertFalse(evaluate_submission(fixture(),report,{},scenario)["passed_institutional_gate"])

    def test_compiler_provenance_preserves_monthly_occurrences(self):
        from types import SimpleNamespace as N
        from app.level6_audit.ast_audit import build_scenario_evidence
        entries=[]; anomalies=[]
        for month in (1,2):
            entries.append(N(entry_id=f"JE{month}",sim_year=2024,sim_month=month,document_ref=f"D{month}",
                lines=[N(account_number="501000",category=N(value="COGS"),debit=Decimal(0),credit=Decimal(10))]))
            anomalies.append({"anomaly_id":"A","sim_year":2024,"sim_month":month,"document_ref":f"D{month}","target_gl_accounts":["501000"],"amount":"2.5"})
        result=build_scenario_evidence(entries,anomalies)
        self.assertEqual(len(result["anomaly_occurrences"]),2)
        self.assertEqual(result["anomaly_occurrences"]["A:2024:01:D1"]["ledger_ids"],["JE1-000"])
        self.assertEqual(result["anomaly_occurrences"]["A:2024:02:D2"]["ledger_ids"],["JE2-000"])
        self.assertFalse(result["ready_for_certification"])
        self.assertEqual(result,build_scenario_evidence(entries,anomalies))
        anomalies[0]["document_ref"]="unknown"
        with self.assertRaisesRegex(ValueError,"No matching ledger"): build_scenario_evidence(entries,anomalies)

    def test_databook_bindings_match_rendered_grid(self):
        from app.level4_databook.formula_graph import Databook, _databook_to_sheets
        book=Databook()
        book.tabs={tab:{"amount":Decimal("10"),"anomalies":[{"id":"A"}]} for tab in book.TAB_IDS}
        bindings=book.audit_cell_bindings()
        rendered=_databook_to_sheets(book)
        for tab in book.TAB_IDS:
            metrics=bindings["tabs"][tab]["metrics"]
            self.assertEqual(metrics["amount"]["cell"],f"{tab}!B2")
            self.assertFalse(metrics["amount"]["has_formula"])
            self.assertEqual(metrics["anomalies"]["representation"],"json_text")
            self.assertEqual(bindings["tabs"][tab]["check_bar_formula"],rendered[tab][0][1])
        self.assertEqual(bindings["missing_check_bars"],[])

    def test_xlsx_exports_the_rendered_anomaly_and_pvm_formulas(self):
        import os
        import tempfile
        from openpyxl import load_workbook
        from app.level4_databook.formula_graph import Databook, _databook_to_sheets
        from app.level4_databook.sandbox_worker import XLSXSerializer
        book=Databook()
        book.tabs={tab:{"amount":Decimal("10")} for tab in book.TAB_IDS}
        book.tabs["04_Revenue_PVM"]["waterfall"]={key:"0" for key in ("total_delta","price_effect","volume_effect","mix_effect")}
        book.tabs["04_Revenue_PVM"]["products"]=[{"product_id":"SAMPLE","base_units":10,"base_revenue":"100",
                                                    "current_units":10,"current_revenue":"100"}]
        book.tabs["02_EBITDA_Bridges"]["anomalies"]=[{"anomaly_id":"SR-B14","document_ref":"CAP-202401",
            "source_evidence":{"capitalized_labor":"100","maintenance_fraction":"0.65"}}]
        rendered=_databook_to_sheets(book)
        with tempfile.TemporaryDirectory() as directory:
            filename=os.path.join(directory,"audit.xlsx")
            XLSXSerializer().serialize(book,filename)
            wb=load_workbook(filename)
            for tab, rows in rendered.items():
                ws=wb[tab]
                self.assertEqual(ws["B1"].value,rows[0][1])
                self.assertEqual(ws["E1"].value,rows[0][4])
                for row_number, row in enumerate(rows[1:],2):
                    self.assertEqual(ws.cell(row_number,1).value,row[0])
                    self.assertEqual(ws.cell(row_number,2).value,row[1])
        self.assertTrue(rendered["02_EBITDA_Bridges"][-1][1].startswith("=ROUND("))

    def test_compiler_to_xlsx_to_grader_uses_trusted_occurrence_bindings(self):
        import sys
        import tempfile
        from pathlib import Path
        compiler=Path(__file__).resolve().parents[2]/"scenarios"/"compiler"
        sys.path.insert(0,str(compiler))
        from build_scenario import SCENARIO_PROFILES, compile_scenario
        from app.level4_databook.formula_graph import Databook
        from app.level4_databook.sandbox_worker import XLSXSerializer
        from app.level5_workspace.report import ReportAssembler, SPAExhibitBBuilder
        from app.level6_audit.rubric_scorer import load_scenario_policy, record_partner_review, store_partner_review, validate_scenario_policy
        with tempfile.TemporaryDirectory() as directory:
            package=Path(compile_scenario(SCENARIO_PROFILES["target_apex_supply"],3,42,directory)["package_dir"])
            book=Databook().build(str(package))
            xlsx=Path(directory)/"audit.xlsx"
            XLSXSerializer().serialize(book,str(xlsx))
            policy=load_scenario_policy(directory,"target_apex_supply","0x000000000000002a")
            report=ReportAssembler().build(book)
            spa=SPAExhibitBBuilder().build(book)
            report["sections"]["03_Quality_of_Earnings"]["anomalies"]=[
                {"anomaly_id":key,**value} for key,value in policy["anomalies"].items()]
            report["sections"]["10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities"]["caveats"]=[
                {"gap_id":key,"disclosure":"Records unavailable; indemnity required."} for key in policy["scope_gaps"]]
            spa["escrows"]=[{"gap_id":key,"amount":value["minimum_escrow"]}
                             for key,value in policy["scope_gaps"].items()]
            result=evaluate_submission(xlsx.read_bytes(),report,spa,policy)
            self.assertEqual(result["ast_report"]["check_bars_reconciled"],11)
            self.assertEqual(result["findings"],[])
            self.assertFalse(result["turing_gates"]["T01"])
            self.assertTrue(all(value for name,value in result["turing_gates"].items() if name!="T01"))
            self.assertEqual(result["incomplete_checks"],["expert_calibration"])
            self.assertFalse(result["passed_institutional_gate"])
            # A test-only review record exercises the trusted administrative transition.
            import hashlib
            import json
            baseline={key:value for key,value in policy.items() if key not in ("partner_review","professional_calibration")}
            digest=hashlib.sha256(json.dumps(baseline,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            review={"reviewer_id":"test-reviewer","reviewer_role":"transaction_advisory_partner",
                    "blind_comparison_id":"test-comparison","comparator_sha256":"1"*64,
                    "reviewed_at":"2026-11-24T00:00:00Z","verdict":"indistinguishable",
                    "baseline_policy_sha256":digest}
            from unittest.mock import patch
            with patch.dict("os.environ",{"QOE_REVIEW_SIGNING_KEY":"test-only-secret-key-with-32-characters"}):
                with self.assertRaises(ValueError):
                    record_partner_review(policy,dict(review,baseline_policy_sha256="0"*64))
                reviewed=record_partner_review(policy,review)
                with self.assertRaisesRegex(ValueError,"signature"):
                    validate_scenario_policy(dict(reviewed,partner_review=dict(reviewed["partner_review"],reviewer_id="tampered")))
            calibrated=evaluate_submission(xlsx.read_bytes(),report,spa,reviewed)
            self.assertTrue(calibrated["turing_gates"]["T01"])
            self.assertTrue(calibrated["passed_institutional_gate"])
            from openpyxl import load_workbook
            altered=load_workbook(xlsx)
            pvm=altered["04_Revenue_PVM"]
            pvm["F1"]=10
            pvm["B5"]=pvm["B5"].value+"+F1"
            altered.save(xlsx)
            shifted=evaluate_submission(xlsx.read_bytes(),report,spa,policy)
            self.assertIn("PVM_COMPONENT_MISMATCH",[finding["violation_type"] for finding in shifted["findings"]])
            XLSXSerializer().serialize(book,str(xlsx))
            altered=load_workbook(xlsx)
            altered["04_Revenue_PVM"]["C8"] = altered["04_Revenue_PVM"]["C8"].value + 10
            altered.save(xlsx)
            wrong_source=evaluate_submission(xlsx.read_bytes(),report,spa,policy)
            self.assertIn("PVM_SOURCE_MISMATCH",[finding["violation_type"] for finding in wrong_source["findings"]])
            XLSXSerializer().serialize(book,str(xlsx))
            report["sections"]["03_Quality_of_Earnings"]["anomalies"][0]["amount"]="0"
            rejected=evaluate_submission(xlsx.read_bytes(),report,spa,policy)
            self.assertIn("UNVERIFIED_ANOMALY",[finding["violation_type"] for finding in rejected["findings"]])
            altered=load_workbook(xlsx)
            altered["01_Summary"]["B1"]='="OK"'
            altered.save(xlsx)
            spoofed=evaluate_submission(xlsx.read_bytes(),report,spa,policy)
            self.assertIn("CHECK_BAR_FAILURE",[finding["violation_type"] for finding in spoofed["findings"]])
            with patch.dict("os.environ",{"QOE_REVIEW_SIGNING_KEY":"test-only-secret-key-with-32-characters"}):
                store_partner_review(package,review)
                self.assertEqual(load_scenario_policy(directory,"target_apex_supply","0x000000000000002a")["professional_calibration"],"expert_reviewed")
            policy_path=package/"audit_policy.json"
            policy_path.write_bytes(policy_path.read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError,"checksum mismatch"):
                load_scenario_policy(directory,"target_apex_supply","0x000000000000002a")
