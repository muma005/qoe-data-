import hashlib
import json
import unittest
from app.level6_audit import AuditEvaluationService


class CertificationBoundaryTests(unittest.TestCase):
    def test_invented_and_duplicate_claims_cannot_certify_missing_workbook(self):
        service = AuditEvaluationService()
        report = json.dumps({"sections": {"03_Quality_of_Earnings": {
            "anomalies": [{"anomaly_id": x} for x in ["real", "real", "invented"]]}}})
        spa = json.dumps({"4_indemnity_escrow": {"amount": 0}})
        checksum = hashlib.sha256(json.dumps([report, spa, "missing.xlsx"], sort_keys=True).encode()).hexdigest()
        job = service.submit_engagement_for_grading("e", "u", "s", "1", "missing.xlsx", report, spa, checksum)
        result = service.process_job(job["job_id"], [], [], ["real", "missed"])
        self.assertEqual(result["detected_anomalies_count"], 1)
        self.assertEqual(result["missed_anomalies_count"], 1)
        self.assertFalse(result["passed_institutional_gate"])
        self.assertFalse(result["evaluation_complete"])
        self.assertEqual(result["formula_audit_results"]["check_bars_passed"], 0)
        self.assertNotIn("qoe.audit.eqcr.certified.v1", [e["type"] for e in service.events])

    def test_escrow_requires_positive_finite_amount_and_disclosure(self):
        report = {"sections": {"10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities": {"caveats": ["gap"]}}}
        for amount in [0, "0.00", -1, "NaN", "Infinity", None, "invalid"]:
            with self.subTest(amount=amount):
                self.assertEqual(AuditEvaluationService._scope_from({"4_indemnity_escrow": {"amount": amount}}, report), "caveated")
        self.assertEqual(AuditEvaluationService._scope_from({"4_indemnity_escrow": {"amount": "$500,000"}}, report), "escrow")


class ModuleOwnershipTests(unittest.TestCase):
    def test_only_four_implementation_modules(self):
        from pathlib import Path
        import app.level6_audit as package
        root=Path(package.__file__).parent
        self.assertEqual({p.name for p in root.glob("*.py")},
                         {"__init__.py","ast_audit.py","benford_scanner.py","eqrc_memo.py","rubric_scorer.py"})

    def test_specialists_do_not_import_grading_lifecycle(self):
        import ast
        from pathlib import Path
        import app.level6_audit as package
        root=Path(package.__file__).parent
        for name in ("ast_audit.py","benford_scanner.py","eqrc_memo.py"):
            tree=ast.parse((root/name).read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):
                    self.assertNotIn("rubric_scorer",node.module or "",name)

    def test_package_contains_exports_only(self):
        import ast
        from pathlib import Path
        import app.level6_audit as package
        tree=ast.parse(Path(package.__file__).read_text())
        self.assertFalse(any(isinstance(node,(ast.FunctionDef,ast.ClassDef)) for node in tree.body))


class ReadOnlyPolicyTests(unittest.TestCase):
    def test_postgres_provider_uses_read_only_transaction_and_integrity_digest(self):
        from app.level6_audit.rubric_scorer import load_postgres_scenario_policy
        policy={"seed_hex_64":"0x01","professional_calibration":"structural_only",
                "workbook_policy":{"required_sheets":[f"S{i}" for i in range(11)],
                "check_bars":[f"S{i}!B1" for i in range(11)],"calculation_cells":[],"pvm":[]},
                "ledger":{},"documents":{},"anomalies":{},"scope_gaps":{},"replacement_costs":[],
                "allocations":{},"reconciliations":[],"professional_checks":[],
                "commercial_checks":[],"legal_checks":[],"behavior_checks":[]}
        digest=hashlib.sha256(json.dumps(policy,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        class Cursor:
            def __init__(self,role="qoe_eval_readonly",digest=digest):
                self.sql=[];self.last="";self.role=role;self.digest=digest
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def execute(self,query,parameters=None):
                self.sql.append((query,parameters));self.last=query
            def fetchone(self):
                if "pg_roles" in self.last: return (self.role,"on",False,False,False,False)
                if "has_table_privilege" in self.last: return (False,False,False,False)
                return (policy,self.digest)
        class Connection:
            def __init__(self,cursor): self.selected=cursor
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def cursor(self): return self.selected
        cursor=Cursor()
        result=load_postgres_scenario_policy("postgresql://private","scenario","0x01",
                                             connect=lambda dsn,autocommit:Connection(cursor))
        self.assertEqual(result,policy)
        self.assertEqual(cursor.sql[0][0],"BEGIN READ ONLY")
        self.assertEqual(cursor.sql[-1][0],"ROLLBACK")
        query,params=next((sql,args) for sql,args in cursor.sql if "scenario_policies" in sql and "WHERE" in sql)
        self.assertIn("%s",query)
        self.assertEqual(params,("scenario","0x01"))
        for invalid in (Cursor(role="postgres"),Cursor(digest="0"*64)):
            with self.assertRaises(ValueError):
                load_postgres_scenario_policy("postgresql://private","scenario","0x01",
                                              connect=lambda dsn,autocommit:Connection(invalid))
