import hashlib
import json
import time
import unittest
from app.level6_audit.rubric_scorer import EvaluationJobs


class JobTests(unittest.TestCase):
    def test_failed_artifact_is_reported_without_hanging(self):
        jobs=EvaluationJobs(lambda scenario,seed:{},timeout=5)
        data=b"invalid workbook"
        checksum=hashlib.sha256(data+json.dumps({"report":{},"spa":{}},sort_keys=True,separators=(",",":")).encode()).hexdigest()
        queued=jobs.submit("e","s","1",data,{}, {},checksum)
        end=time.monotonic()+8
        while time.monotonic()<end:
            status=jobs.status(queued["job_id"])
            if status["status"] in ("COMPLETED","FAILED"): break
            time.sleep(.02)
        self.assertEqual(status["status"],"FAILED")
        self.assertIn("Missing trusted scenario",status["error"])
    def test_artifact_bytes_are_checksum_bound(self):
        jobs=EvaluationJobs(lambda scenario,seed:{})
        with self.assertRaises(ValueError): jobs.submit("e","s","1",b"changed",{},{},"bad")

    def test_store_survives_restart_and_marks_interruption(self):
        import tempfile
        from pathlib import Path
        from app.level6_audit.rubric_scorer import JobStore
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"jobs.db"
            store=JobStore(path)
            store.save({"job_id":"done","status":"COMPLETED","result":{"score":80}})
            store.save({"job_id":"lost","status":"PROCESSING"})
            recovered=EvaluationJobs(lambda s,k:{},store_path=path)
            self.assertEqual(recovered.status("done")["result"]["score"],80)
            self.assertEqual(recovered.status("lost")["status"],"FAILED")
            self.assertIn("INTERRUPTED",recovered.status("lost")["error"])

    def test_penalties_and_anomaly_ratio(self):
        from app.level6_audit.rubric_scorer import score_findings
        findings=[{"quadrant":2,"violation_type":"VIO_EMBEDDED_CONSTANT","rationale":"plug"}]
        self.assertEqual(score_findings(findings,1,2),[50,94,100,100])
        self.assertEqual(score_findings(findings*2,1,2),[50,94,100,100])

    def test_restart_replays_saved_inputs_without_loading_new_scenario(self):
        import tempfile
        from pathlib import Path
        from app.level6_audit.rubric_scorer import JobStore
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"jobs.db"
            store=JobStore(path)
            store.enqueue({"job_id":"replay","engagement_id":"e","status":"PROCESSING"},b"invalid",{},{},{})
            def forbidden(*args): raise AssertionError("Must use captured scenario")
            recovered=EvaluationJobs(forbidden,store_path=path)
            self.assertTrue(recovered.wait(10))
            status=recovered.status("replay")
            self.assertEqual(status["status"],"FAILED")
            self.assertIn("Missing trusted scenario",status["error"])
            self.assertEqual(store.load()["replay"]["status"],"FAILED")
            self.assertTrue(all(e["specversion"]=="1.0" for e in store.events()))

    def test_corrupt_saved_artifacts_are_not_replayed(self):
        import tempfile
        from pathlib import Path
        from app.level6_audit.rubric_scorer import JobStore
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"jobs.db"
            store=JobStore(path)
            store.enqueue({"job_id":"bad","engagement_id":"e","status":"QUEUED"},b"original",{},{},{})
            with store.connect() as db:
                db.execute("UPDATE submissions SET workbook=? WHERE id=?",(b"tampered","bad"))
            recovered=EvaluationJobs(lambda *args:{},store_path=path)
            self.assertEqual(recovered.status("bad")["status"],"FAILED")
            self.assertIn("integrity",recovered.status("bad")["error"])

    def test_standalone_ast_job_does_not_certify_or_run_benford(self):
        from tests.test_level6_workbook import fixture,policy
        jobs=EvaluationJobs(lambda s,k:{"workbook_policy":policy()})
        data=fixture()
        envelope=json.dumps({"report":{},"spa":{}},sort_keys=True,separators=(",",":")).encode()
        queued=jobs.submit("e","s","1",data,{},{},hashlib.sha256(data+envelope).hexdigest(),operation="ast")
        self.assertTrue(jobs.wait(10))
        result=jobs.status(queued["job_id"])
        self.assertEqual(result["status"],"COMPLETED",result)
        self.assertTrue(result["result"]["ast_report"]["passed"])
        self.assertFalse(result["result"]["passed_institutional_gate"])
        self.assertNotIn("qoe.audit.benford.completed.v1",[e["type"] for e in jobs.events])

    def test_concurrent_claim_has_one_owner_and_fences_stale_writes(self):
        import tempfile
        from pathlib import Path
        from concurrent.futures import ThreadPoolExecutor
        from app.level6_audit.rubric_scorer import JobStore
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"jobs.db"
            store=JobStore(path)
            store.save({"job_id":"j","status":"QUEUED"})
            def claim(owner): return owner,JobStore(path).claim("j",owner)
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes=list(pool.map(claim,["a","b"]))
            self.assertEqual(sum(ok for _,ok in outcomes),1)
            winner=next(owner for owner,ok in outcomes if ok)
            loser=next(owner for owner,ok in outcomes if not ok)
            with self.assertRaises(ValueError): store.save({"job_id":"j","status":"COMPLETED"},owner=loser)
            store.save({"job_id":"j","status":"COMPLETED"},owner=winner)
            self.assertFalse(store.claim("j","third"))

    def test_expired_lease_is_recovered_and_old_owner_fenced(self):
        import tempfile
        from pathlib import Path
        from app.level6_audit.rubric_scorer import JobStore
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"jobs.db"
            store=JobStore(path)
            record={"job_id":"expired","engagement_id":"e","status":"PROCESSING"}
            store.enqueue(record,b"invalid",{},{},{})
            self.assertTrue(store.claim("expired","old"))
            jobs=EvaluationJobs(lambda *args:{},store_path=path)
            self.assertTrue(jobs.wait(5))
            self.assertEqual(jobs.status("expired")["status"],"PROCESSING")
            with store.connect() as db:
                db.execute("UPDATE leases SET expires=0 WHERE id='expired'")
            jobs.recover_pending()
            self.assertTrue(jobs.wait(10))
            self.assertEqual(jobs.status("expired")["status"],"FAILED")
            with self.assertRaises(ValueError): store.save(record,owner="old")

    def test_periodic_recovery_and_shutdown(self):
        import threading
        jobs=EvaluationJobs(lambda *args:{})
        called=threading.Event()
        jobs.recover_pending=lambda:called.set()
        jobs.start_recovery(.01)
        first=jobs._recovery_thread
        jobs.start_recovery(.01)
        self.assertIs(jobs._recovery_thread,first)
        self.assertTrue(called.wait(2))
        self.assertTrue(jobs.stop_recovery())
        self.assertFalse(first.is_alive())

    def test_rubric_boundaries_and_unknown_rules(self):
        from decimal import Decimal
        from app.level6_audit.rubric_scorer import RubricScorer,score_findings
        for value,passed,honors in [("79.999",False,False),("80",True,False),("91.999",True,False),("92",True,True)]:
            result=RubricScorer.summarize([Decimal(value)]*4)
            self.assertEqual(result["passed_institutional_threshold"],passed)
            self.assertEqual(result["institutional_honors"],honors)
        with self.assertRaises(ValueError): score_findings([],2,1)
        with self.assertRaises(KeyError): score_findings([{"quadrant":2,"violation_type":"UNREGISTERED","rationale":"x"}],0,0)

    def test_grpc_roundtrip(self):
        import grpc
        from concurrent.futures import ThreadPoolExecutor
        from google.protobuf import message_factory
        from app.level6_audit.rubric_scorer import register_grpc_service
        jobs=EvaluationJobs(lambda *args:{"ledger":{"x":{"amount":"123"}}})
        server=grpc.server(ThreadPoolExecutor(max_workers=2))
        pool=register_grpc_service(server,jobs,lambda uri:b"invalid",lambda engagement:("s","1"))
        port=server.add_insecure_port("127.0.0.1:0")
        server.start()
        try:
            request_type=message_factory.GetMessageClass(pool.FindMessageTypeByName("qoe.audit.v1.ScanBenfordDistributionRequest"))
            response_type=message_factory.GetMessageClass(pool.FindMessageTypeByName("qoe.audit.v1.BenfordDistributionResult"))
            with grpc.insecure_channel(f"127.0.0.1:{port}") as channel:
                call=channel.unary_unary("/qoe.audit.v1.AuditEvaluationService/ScanBenfordDistribution",request_serializer=lambda x:x.SerializeToString(),response_deserializer=response_type.FromString)
                response=call(request_type(engagement_id="e"),timeout=5)
                self.assertEqual(response.total_transactions_scanned,1)
                self.assertEqual(response.engagement_id,"e")
        finally: server.stop(0).wait()

    def test_missing_scenario_mappings_rejected(self):
        from app.level6_audit.rubric_scorer import validate_scenario_policy
        with self.assertRaisesRegex(ValueError,"Missing scenario mappings"):
            validate_scenario_policy({"seed_hex_64":"1"})
