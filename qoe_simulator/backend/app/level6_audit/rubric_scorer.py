"""Assessment policy, grading lifecycle, persistence, and service adapters."""
from __future__ import annotations
from .ast_audit import ASTAuditor, AuditSeverity, CellAuditFinding, find_hardcodes, WorkbookAudit, money, path_value, verify_submission_evidence
from .benford_scanner import BenfordScanner
from .eqrc_memo import EQCRMemoGenerator


# ========================================================================
# Rubric inputs and policy
# ========================================================================

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict

PASS_THRESHOLD = Decimal("80.0")
HONORS_THRESHOLD = Decimal("92.0")

# Scope-limitation decision tree (spec Section 5), on a 0-100 legal-protection scale.
SCOPE_SCORES = {
    "escrow": Decimal("100.0"),   # identified + caveated + escrow -> distinction
    "caveated": Decimal("70.0"),  # formal caveat, no escrow -> moderate
    "identified": Decimal("40.0"),  # mentioned in email only -> partial
    "missed": Decimal("0.0"),     # false-certainty illusion -> fail
}


@dataclass
class EvaluationInputs:
    detected_anomalies: int = 0
    missed_anomalies: int = 0
    hardcode_count: int = 0
    check_bars_passed: int = 11
    check_bars_total: int = 11
    replacement_cost_net: bool = True   # True = netted (correct), False = gross (penalized)
    double_dipping_count: int = 0
    scope_limitation: str = "missed"    # missed | identified | caveated | escrow


class RubricScorer:
    """Deterministic 4-quadrant scorer (LP-09: no stochastic drift)."""

    def score(self, inputs: EvaluationInputs) -> Dict[str, float]:
        # Q1 Investigative Rigor (0-100): anomaly detection rate.
        total_anomalies = inputs.detected_anomalies + inputs.missed_anomalies
        q1 = (Decimal("100") * Decimal(inputs.detected_anomalies) / Decimal(total_anomalies)
              if total_anomalies > 0 else Decimal("0"))

        # Q2 Modeling Hygiene (0-100): deduct per hardcode and per check-bar failure.
        q2 = Decimal("100") - Decimal("6.0") * Decimal(inputs.hardcode_count)
        if inputs.check_bars_total > 0 and inputs.check_bars_passed < inputs.check_bars_total:
            q2 -= Decimal("20.0")
        q2 = max(q2, Decimal("0"))

        # Q3 Commercial Judgment (0-100): deduct double-dipping + gross replacement cost.
        q3 = Decimal("100") - Decimal("16.0") * Decimal(inputs.double_dipping_count)
        if not inputs.replacement_cost_net:
            q3 -= Decimal("20.0")
        q3 = max(q3, Decimal("0"))

        # Q4 Legal Protection (0-100): scope-limitation decision tree.
        q4 = SCOPE_SCORES.get(inputs.scope_limitation, Decimal("0"))

        return self.summarize([q1, q2, q3, q4])

    @staticmethod
    def weighted_total(raw):
        weights = (Decimal("0.30"), Decimal("0.25"), Decimal("0.25"), Decimal("0.20"))
        return sum((weight * value for weight, value in zip(weights, raw)), Decimal(0))

    @staticmethod
    def summarize(raw):
        """One weighting and threshold implementation for all scoring inputs."""
        weights = (Decimal("0.30"), Decimal("0.25"), Decimal("0.25"), Decimal("0.20"))
        names = ("investigative_rigor", "modeling_hygiene", "commercial_judgment", "legal_protection")
        composite = RubricScorer.weighted_total(raw)
        result = {f"q{i}_{name}": float(value.quantize(Decimal("0.01")))
                  for i, (name, value) in enumerate(zip(names, raw), 1)}
        result["weighted_quadrant_scores"] = {
            f"q{i}_{name}": float((value * weight).quantize(Decimal("0.01")))
            for i, (name, value, weight) in enumerate(zip(names, raw, weights), 1)
        }
        result.update(composite_score=float(composite.quantize(Decimal("0.01"))),
                      passed_institutional_threshold=composite >= PASS_THRESHOLD,
                      institutional_honors=composite >= HONORS_THRESHOLD)
        return result

    def grade_letter(self, composite: float) -> str:
        if composite >= 92.0:
            return "DISTINCTION — INSTITUTIONAL HONORS"
        if composite >= 80.0:
            return "PASS WITH MERIT"
        if composite >= 60.0:
            return "CONDITIONAL PASS"
        return "FAIL"


# ========================================================================
# Versioned finding penalties
# ========================================================================

from decimal import Decimal

RUBRIC_VERSION = "level6-1.0"
PENALTIES = {
    "VIO_EMBEDDED_CONSTANT": 6, # 1.5 weighted points, design section 8
    "RAW_HARDCODE": 25, "FORMULA_ERROR": 25,
    "CHECK_BAR_FAILURE": 20, "CHECK_BAR_COVERAGE": 20,
    "REPLACEMENT_COST": 20, "DOUBLE_DIPPING": 16,
    "SCOPE_PROTECTION": 25, "UNSUPPORTED_ANOMALY": 10,
    "INVALID_POLICY":25, "MISSING_SHEET":25, "MISSING_CACHE":25,
    "RECALCULATION_MISMATCH":25, "MISSING_CALCULATION":25,
    "PVM_NON_ADDITIVE":25, "PVM_COMPONENT_MISMATCH":25, "PVM_SOURCE_MISMATCH":25,
    "PVM_ERROR":25, "ROUNDING_REQUIRED":25,
    "LEDGER_INPUT_MISMATCH":25, "LEDGER_INPUT_MISSING":25,
    "ALLOCATION_UNVERIFIED":25, "CROSS_SCHEDULE_MISMATCH":25,
    "CROSS_SCHEDULE_MISSING":25, "CRITERION_FAILED":25,
}


def score_findings(findings, verified_count, expected_count):
    if type(verified_count) is not int or type(expected_count) is not int or not 0 <= verified_count <= expected_count:
        raise ValueError("Invalid verified anomaly counts")
    raw = [Decimal(100) for _ in range(4)]
    if expected_count:
        raw[0] = Decimal(100) * Decimal(verified_count) / Decimal(expected_count)
    seen = set()
    for finding in findings:
        code = finding["violation_type"]
        if finding["quadrant"] not in (1,2,3,4): raise ValueError("Invalid quadrant")
        if code == "UNVERIFIED_ANOMALY":
            continue  # Already reflected in the verified detection ratio.
        identity = (finding["quadrant"], code, finding.get("cell_coordinate", ""), finding["rationale"])
        if identity in seen:
            continue
        seen.add(identity)
        raw[finding["quadrant"] - 1] -= Decimal(PENALTIES[code])
    return [max(Decimal(0), min(Decimal(100), value)) for value in raw]


# ========================================================================
# Evaluation coordination and certification
# ========================================================================

def evaluate_submission(workbook_bytes,report,spa,scenario):
    required=("workbook_policy","ledger","documents","anomalies","scope_gaps","replacement_costs","allocations","reconciliations")
    for key in required:
        if key not in scenario: raise ValueError("Missing trusted scenario field: "+key)
    workbook=WorkbookAudit(workbook_bytes)
    audit=workbook.audit(scenario["workbook_policy"])
    findings=[dict(f,quadrant=2) for f in audit["findings"]]
    incomplete=[]
    for key in ("professional_checks", "commercial_checks", "legal_checks", "behavior_checks"):
        if key not in scenario: incomplete.append(key)
    if not scenario["reconciliations"]: incomplete.append("cross_schedule_policy")
    if not scenario["workbook_policy"].get("pvm"): incomplete.append("pvm_policy")
    if scenario.get("professional_calibration") == "structural_only": incomplete.append("expert_calibration")
    def defect(q,code,detail): findings.append({"quadrant":q,"violation_type":code,"rationale":detail})
    for group,quadrant in (("professional_checks",1),("commercial_checks",3),("legal_checks",4),("behavior_checks",4)):
        for rule in scenario.get(group,[]):
            try:
                source={"report":report,"spa":spa}[rule["source"]]
                actual=path_value(source,rule["path"])
                if "expected" in rule and actual!=rule["expected"]: raise ValueError("Value does not match trusted criterion")
                if "minimum" in rule and money(actual)<money(rule["minimum"]): raise ValueError("Below supported range")
                if "maximum" in rule and money(actual)>money(rule["maximum"]): raise ValueError("Above supported range")
                if rule.get("required") and not actual: raise ValueError("Required evidence absent")
            except (KeyError,ValueError,TypeError,ArithmeticError) as e: defect(quadrant,"CRITERION_FAILED",rule.get("path",group)+": "+str(e))
    evidence_findings, verified = verify_submission_evidence(workbook, report, scenario)
    findings.extend(evidence_findings)
    caveats=report.get("sections",{}).get("10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities",{}).get("caveats",[])
    disclosed={x.get("gap_id") for x in caveats if isinstance(x,dict) and x.get("disclosure")}
    escrow_rows=spa.get("escrows",[])
    if not isinstance(escrow_rows,list): escrow_rows=[]
    if any(not isinstance(x,dict) or not isinstance(x.get("gap_id"),str) for x in escrow_rows):
        defect(4,"SCOPE_PROTECTION","Malformed escrow entry")
    escrows={x["gap_id"]:x for x in escrow_rows if isinstance(x,dict) and isinstance(x.get("gap_id"),str)}
    for gap,expected in scenario["scope_gaps"].items():
        try:
            if sum(isinstance(x,dict) and x.get("gap_id")==gap for x in escrow_rows)!=1:
                raise ValueError("Missing or duplicate escrow")
            if sum(isinstance(x,dict) and x.get("gap_id")==gap and bool(x.get("disclosure")) for x in caveats)!=1:
                raise ValueError("Missing or duplicate disclosure")
            if gap not in disclosed or money(escrows[gap]["amount"])<money(expected["minimum_escrow"]): raise ValueError("Missing disclosure or insufficient escrow")
        except (KeyError,ValueError,ArithmeticError) as e: defect(4,"SCOPE_PROTECTION",gap+": "+str(e))
    benford=BenfordScanner().scan([money(x["amount"]) for x in scenario["ledger"].values()])
    raw=score_findings(findings,len(verified),len(scenario["anomalies"]))
    scores=RubricScorer.summarize(raw)
    score=RubricScorer.weighted_total(raw)
    gates={"T01":all(str(i).zfill(2)+"_" in " ".join(report.get("sections",{})) for i in range(1,11))
                    and "expert_calibration" not in incomplete,
           "T02":benford["passes_benford_uniformity"],"T03":audit["passed"],
           "T04":not any(f["violation_type"].startswith("CROSS_SCHEDULE") for f in findings),
           "T05":not any(f["quadrant"]==4 for f in findings)}
    passed=score>=80 and all(gates.values()) and not incomplete
    scores.update(composite_score=float(score),passed_institutional_threshold=passed,institutional_honors=passed and score>=92)
    grade=RubricScorer().grade_letter(float(score)) if passed else "FAIL - AUDIT GATE"
    review_status="PENDING" if "expert_calibration" in incomplete else "RECORDED"
    memo=EQCRMemoGenerator().generate(scenario.get("engagement_id",""),"","Automated Level 6 Reviewer",scores,grade,[f["violation_type"]+": "+f["rationale"] for f in findings],["Verified anomaly "+x for x in verified], findings_by_quadrant={q:[f["violation_type"]+": "+f["rationale"] for f in findings if f["quadrant"]==q] for q in range(1,5)},review_status=review_status)
    def json_decimal(value):
        if isinstance(value, Decimal) and value.is_finite():
            return str(value)
        raise TypeError("Review packet contains a non-serializable or non-finite value")

    packet={"status":review_status,"workbook_sha256":hashlib.sha256(workbook_bytes).hexdigest(),
            "report_sha256":hashlib.sha256(json.dumps(report,sort_keys=True,separators=(",",":"),allow_nan=False,default=json_decimal).encode()).hexdigest(),
            "spa_sha256":hashlib.sha256(json.dumps(spa,sort_keys=True,separators=(",",":"),allow_nan=False,default=json_decimal).encode()).hexdigest(),
            "review_protocol":"Blind comparison against an independently obtained real deal deliverable; partner verdict required."}
    return {"rubric_version":RUBRIC_VERSION,"evaluation_complete":not incomplete,"incomplete_checks":incomplete,"passed_institutional_gate":passed,"composite_score":float(score),"quadrant_scores":scores,"ast_report":audit,"benford_result":benford,"findings":findings,"turing_gates":gates,"turing_test_pass":all(gates.values()),"eqcr_memo":memo,"partner_review_packet":packet}


# ========================================================================
# Transactional job persistence and leases
# ========================================================================

from contextlib import contextmanager
import json
import sqlite3
from pathlib import Path


class JobStore:
    def __init__(self, path):
        self.path = str(Path(path))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS leases (id TEXT PRIMARY KEY, owner TEXT NOT NULL, expires REAL NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS submissions (id TEXT PRIMARY KEY, workbook BLOB NOT NULL, payload TEXT NOT NULL, checksum TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            with db:
                yield db
        finally:
            db.close()
    def save(self, job, events=(), owner=None):
        import time
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if owner is not None:
                lease=db.execute("SELECT owner,expires FROM leases WHERE id=?",(job["job_id"],)).fetchone()
                if not lease or lease[0]!=owner or lease[1]<=time.time():
                    raise ValueError("Evaluation lease lost")
            db.execute("INSERT OR REPLACE INTO jobs VALUES (?, ?)", (job["job_id"], json.dumps(job, sort_keys=True, allow_nan=False)))
            for event in events:
                db.execute("INSERT OR IGNORE INTO events VALUES (?, ?)", (event["id"], json.dumps(event, sort_keys=True)))
    def load(self):
        with self.connect() as db:
            return {key: json.loads(body) for key, body in db.execute("SELECT id, body FROM jobs")}
    def events(self):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute("SELECT body FROM events ORDER BY rowid")]

    def enqueue(self, job, workbook, report, spa, scenario):
        import hashlib
        payload=json.dumps({"report":report,"spa":spa,"scenario":scenario},sort_keys=True,separators=(",",":"),allow_nan=False)
        checksum=hashlib.sha256(workbook+payload.encode()).hexdigest()
        with self.connect() as db:
            db.execute("INSERT INTO submissions VALUES (?, ?, ?, ?)",(job["job_id"],workbook,payload,checksum))
            db.execute("INSERT INTO jobs VALUES (?, ?)",(job["job_id"],json.dumps(job,sort_keys=True)))
    def submission(self, job_id):
        import hashlib
        with self.connect() as db:
            row=db.execute("SELECT workbook,payload,checksum FROM submissions WHERE id=?",(job_id,)).fetchone()
        if row is None: raise ValueError("EVALUATION_INTERRUPTED: immutable artifacts unavailable")
        workbook,payload,checksum=row
        if hashlib.sha256(workbook+payload.encode()).hexdigest()!=checksum:
            raise ValueError("Stored submission integrity failure")
        decoded=json.loads(payload)
        return workbook,decoded["report"],decoded["spa"],decoded["scenario"]

    def claim(self, job_id, owner, duration=60):
        import time
        now=time.time()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT body FROM jobs WHERE id=?",(job_id,)).fetchone()
            if not row or json.loads(row[0])["status"] not in ("QUEUED","PROCESSING"):
                return False
            lease=db.execute("SELECT expires FROM leases WHERE id=?",(job_id,)).fetchone()
            if lease and lease[0]>now: return False
            db.execute("INSERT OR REPLACE INTO leases VALUES (?,?,?)",(job_id,owner,now+duration))
            return True
    def get(self, job_id):
        with self.connect() as db:
            row=db.execute("SELECT body FROM jobs WHERE id=?",(job_id,)).fetchone()
        if row is None: raise KeyError(job_id)
        return json.loads(row[0])


# ========================================================================
# Worker resource isolation
# ========================================================================

import os


def enforce_memory_limit(bytes_limit=1024*1024*1024):
    if os.name!="nt":
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(bytes_limit,bytes_limit))
        return None
    import ctypes
    from ctypes import wintypes
    class Basic(ctypes.Structure):
        _fields_=[("PerProcessUserTimeLimit",ctypes.c_longlong),("PerJobUserTimeLimit",ctypes.c_longlong),("LimitFlags",wintypes.DWORD),("MinimumWorkingSetSize",ctypes.c_size_t),("MaximumWorkingSetSize",ctypes.c_size_t),("ActiveProcessLimit",wintypes.DWORD),("Affinity",ctypes.c_size_t),("PriorityClass",wintypes.DWORD),("SchedulingClass",wintypes.DWORD)]
    class IO(ctypes.Structure):
        _fields_=[(n,ctypes.c_ulonglong) for n in ("ReadOperationCount","WriteOperationCount","OtherOperationCount","ReadTransferCount","WriteTransferCount","OtherTransferCount")]
    class Extended(ctypes.Structure):
        _fields_=[("BasicLimitInformation",Basic),("IoInfo",IO),("ProcessMemoryLimit",ctypes.c_size_t),("JobMemoryLimit",ctypes.c_size_t),("PeakProcessMemoryUsed",ctypes.c_size_t),("PeakJobMemoryUsed",ctypes.c_size_t)]
    api=ctypes.WinDLL("kernel32",use_last_error=True)
    api.CreateJobObjectW.restype=wintypes.HANDLE
    api.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR]
    api.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
    api.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE]
    api.GetCurrentProcess.restype=wintypes.HANDLE
    handle=api.CreateJobObjectW(None,None)
    info=Extended();info.BasicLimitInformation.LimitFlags=0x100;info.ProcessMemoryLimit=bytes_limit
    if not handle or not api.SetInformationJobObject(handle,9,ctypes.byref(info),ctypes.sizeof(info)) or not api.AssignProcessToJobObject(handle,api.GetCurrentProcess()):
        raise OSError(ctypes.get_last_error(),"Cannot enforce evaluation memory quota")
    return handle


# ========================================================================
# Asynchronous evaluation lifecycle
# ========================================================================

import hashlib
import json
import multiprocessing
import threading
import time
import uuid
from datetime import datetime, timezone


def _worker(connection, workbook, report, spa, scenario):
    try:
        memory_guard = enforce_memory_limit()
        if scenario.get("_operation") == "ast":
            result={"ast_report":WorkbookAudit(workbook).audit(scenario["workbook_policy"]),
                    "operation":"ast", "passed_institutional_gate":False}
        else:
            result=evaluate_submission(workbook,report,spa,scenario)
        connection.send((True,result))
    except Exception as error:
        connection.send((False,str(error)))
    finally:
        connection.close()


class EvaluationJobs:
    def __init__(self, scenario_provider, timeout=15, store_path=None):
        self.scenario_provider=scenario_provider
        self.timeout=timeout
        self.jobs={}; self.events=[]; self.lock=threading.Lock()
        self.capacity=threading.BoundedSemaphore(2)
        self.threads=[]
        self._active_jobs=set()
        self._recovery_stop=threading.Event()
        self._recovery_thread=None
        self.recovery_error=None
        self.owner=uuid.uuid4().hex
        self.store = JobStore(store_path) if store_path else None
        if self.store:
            self.jobs = self.store.load()
            self.events = self.store.events()
            for job in self.jobs.values():
                if job["status"] in ("QUEUED", "PROCESSING"):
                    try:
                        inputs=self.store.submission(job["job_id"])
                        self._launch(job["job_id"],*inputs)
                    except ValueError as error:
                        if self.store.claim(job["job_id"],self.owner):
                            job.update(status="FAILED", error=str(error))
                            self.store.save(job,owner=self.owner)
    def start_recovery(self, interval=5.0):
        """Start one recovery loop per service; leases coordinate other services."""
        if interval <= 0: raise ValueError("Recovery interval must be positive")
        with self.lock:
            if self._recovery_thread and self._recovery_thread.is_alive(): return
            self._recovery_stop.clear()
            def loop():
                while not self._recovery_stop.wait(interval):
                    try:
                        self.recover_pending()
                        self.recovery_error=None
                    except Exception as error:
                        self.recovery_error=str(error)
            self._recovery_thread=threading.Thread(target=loop,daemon=True,name="qoe-audit-recovery")
            self._recovery_thread.start()

    def stop_recovery(self, timeout=10):
        self._recovery_stop.set()
        if self._recovery_thread:
            self._recovery_thread.join(timeout)
        return not self._recovery_thread or not self._recovery_thread.is_alive()

    def recover_pending(self):
        """Retry durable pending jobs; live leases prevent duplicate evaluation."""
        if not self.store: return
        for job_id,record in self.store.load().items():
            if record["status"] not in ("QUEUED","PROCESSING"): continue
            with self.lock:
                self.jobs[job_id]=record
            try:
                self._launch(job_id,*self.store.submission(job_id))
            except ValueError as error:
                if self.store.claim(job_id,self.owner):
                    record.update(status="FAILED",error=str(error))
                    self.store.save(record,owner=self.owner)

    def _persist(self, job):
        if self.store:
            self.store.save(self.jobs[job], self.events, owner=self.owner)
    def _emit(self, name, job, **data):
        self.events.append({"specversion":"1.0", "id":uuid.uuid4().hex,
            "source":"/qoe/audit", "type":"qoe.audit."+name+".v1",
            "time":datetime.now(timezone.utc).isoformat(), "datacontenttype":"application/json",
            "subject":job, "data":{"job_id":job, "engagement_id":self.jobs[job]["engagement_id"], **data}})

    def submit(self,engagement_id,scenario_id,seed,workbook,report,spa,checksum,operation="grade"):
        if operation not in ("grade", "ast"): raise ValueError("Unknown evaluation operation")
        payload=json.dumps({"report":report,"spa":spa},sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        actual=hashlib.sha256(workbook+payload).hexdigest()
        if actual!=checksum: raise ValueError("Submission checksum mismatch")
        scenario=self.scenario_provider(scenario_id,seed)
        scenario=json.loads(json.dumps(scenario))
        scenario["_operation"]=operation
        job=uuid.uuid4().hex
        record={"job_id":job,"engagement_id":engagement_id,"status":"QUEUED",
                "queued_at":datetime.now(timezone.utc).isoformat()}
        report=json.loads(json.dumps(report)); spa=json.loads(json.dumps(spa))
        with self.lock:
            if self.store: self.store.enqueue(record,bytes(workbook),report,spa,scenario)
            self.jobs[job]=record
        self._launch(job,bytes(workbook),report,spa,scenario)
        return {"job_id":job,"status":"QUEUED","queued_at":record["queued_at"]}
    def _launch(self,job,*inputs):
        with self.lock:
            if job in self._active_jobs: return
            self._active_jobs.add(job)
            self.threads=[thread for thread in self.threads if thread.is_alive()]
            def run():
                try:
                    self._run(job,*inputs)
                finally:
                    with self.lock: self._active_jobs.discard(job)
            thread=threading.Thread(target=run,daemon=True)
            self.threads.append(thread)
            thread.start()
    def wait(self,timeout=30):
        deadline=time.monotonic()+timeout
        for thread in list(self.threads):
            thread.join(max(0,deadline-time.monotonic()))
        return all(not thread.is_alive() for thread in self.threads)
    def _run(self,job,workbook,report,spa,scenario):
        # The scenario policy is sealed independently of the engagement. Bind the
        # engagement only in the worker copy so the generated memo is attributable.
        scenario=dict(scenario,engagement_id=self.jobs[job]["engagement_id"])
        self.capacity.acquire()
        if self.store and not self.store.claim(job,self.owner,duration=max(60,self.timeout+30)):
            self.capacity.release()
            return
        context=multiprocessing.get_context("spawn")
        receiver,sender=context.Pipe(duplex=False)
        process=context.Process(target=_worker,args=(sender,workbook,report,spa,scenario),daemon=True)
        try:
            with self.lock:
                self.jobs[job]["status"]="PROCESSING"
                self._emit("job.started", job)
                self._persist(job)
            process.start(); sender.close()
            if not receiver.poll(self.timeout): raise TimeoutError("EVALUATION_JOB_TIMEOUT")
            ok,result=receiver.recv()
            if not ok: raise ValueError(result)
            with self.lock:
                self.jobs[job].update(status="COMPLETED",result=result,completed_at=datetime.now(timezone.utc).isoformat())
                audit=result["ast_report"]
                self._emit("ast.completed",job,cells_scanned=audit["total_cells_scanned"],
                           hardcodes=sum(f["violation_type"] in ("RAW_HARDCODE","VIO_EMBEDDED_CONSTANT") for f in audit["findings"]),
                           **{"pass":audit["passed"]})
                if "benford_result" in result:
                    scan=result["benford_result"]
                    self._emit("benford.completed",job,ks_stat=scan["kolmogorov_smirnov_statistic"],passes_uniformity=scan["passes_benford_uniformity"])
                if result["passed_institutional_gate"]:
                    self._emit("eqcr.certified", job, score=result["composite_score"], cert_hash=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest())
                self._persist(job)
        except Exception as error:
            with self.lock:
                self.jobs[job].update(status="FAILED",error=str(error))
                self._emit("job.failed", job, error=str(error))
                self._persist(job)
        finally:
            if process.pid:
                if process.is_alive(): process.terminate()
                process.join(timeout=2)
            receiver.close(); sender.close(); self.capacity.release()
    def status(self,job):
        if self.store: return self.store.get(job)
        with self.lock: return json.loads(json.dumps(self.jobs[job]))


# ========================================================================
# Legacy service compatibility facade
# ========================================================================

import hashlib
import json
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Sequence, Tuple



class AuditEvaluationService:
    """Proto-shaped facade mirroring proto/audit_eval.proto AuditEvaluationService."""

    def __init__(self):
        self.ast = ASTAuditor()
        self.benford = BenfordScanner()
        self.rubric = RubricScorer()
        self.memo_gen = EQCRMemoGenerator()
        self.jobs: Dict[str, dict] = {}
        self.events: List[dict] = []
        self._seq = 0

    # rpc SubmitEngagementForGrading
    def submit_engagement_for_grading(self, engagement_id: str, user_id: str,
                                      scenario_id: str, seed_hex_64: str,
                                      fdb_xlsx_blob_uri: str, report_memo_json: str,
                                      spa_exhibit_b_json: str,
                                      submission_checksum_sha256: str) -> dict:
        # Submission receiver validates the SHA-256 checksum.
        payload = json.dumps([report_memo_json, spa_exhibit_b_json, fdb_xlsx_blob_uri],
                             sort_keys=True)
        actual = hashlib.sha256(payload.encode()).hexdigest()
        if actual != submission_checksum_sha256:
            raise PermissionError("submission_checksum_sha256 mismatch")

        self._seq += 1
        job_id = f"JOB_{self._seq:06d}"
        self.jobs[job_id] = {
            "job_id": job_id,
            "engagement_id": engagement_id,
            "user_id": user_id,
            "seed_hex_64": seed_hex_64,
            "status": "QUEUED",
            "report": json.loads(report_memo_json or "{}"),
            "spa": json.loads(spa_exhibit_b_json or "{}"),
            "result": None,
        }
        self.events.append({"type": "qoe.audit.job.started.v1", "engagement_id": engagement_id,
                            "job_id": job_id, "user_id": user_id, "started_at": 0})
        return {
            "job_id": job_id,
            "engagement_id": engagement_id,
            "status": "QUEUED",
            "queued_at": 0,
            "estimated_duration_seconds": 15,
        }

    # Internal async worker step (runs the 5-pass pipeline; deterministic).
    def process_job(self, job_id: str, cells: Sequence[Tuple[str, str, str]],
                    gl_values: Sequence, ground_truth_anomalies: Sequence[str]) -> dict:
        job = self.jobs[job_id]
        job["status"] = "PROCESSING"
        report = job["report"]
        spa = job["spa"]

        detected = [a.get("anomaly_id") for a in
                    report.get("sections", {}).get("03_Quality_of_Earnings", {}).get("anomalies", [])]
        truth = set(ground_truth_anomalies)
        detected = sorted(set(detected) & truth)
        missed = sorted(truth - set(detected))
        audit = self.ast.run(cells)
        hardcodes = audit["hardcoded_constants_flagged"]
        scope = self._scope_from(spa, report)
        double_dip = int(spa.get("double_dipping_count", 0))
        replacement_net = bool(spa.get("replacement_cost_netted", True))

        inputs = EvaluationInputs(
            detected_anomalies=len(detected), missed_anomalies=len(missed),
            hardcode_count=hardcodes, check_bars_passed=0, double_dipping_count=double_dip,
            scope_limitation=scope, replacement_cost_net=replacement_net)
        scores = self.rubric.score(inputs)
        scores["passed_institutional_threshold"] = False
        scores["institutional_honors"] = False
        grade = "INCOMPLETE - NOT CERTIFIED"
        memo = self.memo_gen.generate(
            engagement_id=job["engagement_id"], user_id=job["user_id"],
            partner_name="Robert Sterling, CPA", scores=scores, grade_letter=grade,
            critical_defects=([f"Missed anomaly {m}" for m in missed] +
                              [f"Hardcoded constant in {f.cell_coordinate}" for f in
                               self.ast.audit_formulas(cells)]),
            strengths=[f"Detected anomaly {d}" for d in detected])
        benford = self.benford.scan(gl_values)

        result = {
            "evaluation_id": f"eval_{job['engagement_id']}_{job_id}",
            "engagement_id": job["engagement_id"],
            "evaluated_at": "",
            "composite_score": scores["composite_score"],
            "passed_institutional_gate": False,
            "evaluation_complete": False,
            "incomplete_checks": ["workbook_ingestion", "independent_recalculation", "evidence_traceability", "commercial_verification", "scope_verification"],
            "quadrant_scores": {
                "q1_investigative_rigor": scores["q1_investigative_rigor"],
                "q2_modeling_hygiene": scores["q2_modeling_hygiene"],
                "q3_commercial_judgment": scores["q3_commercial_judgment"],
                "q4_legal_protection": scores["q4_legal_protection"],
            },
            "detected_anomalies_count": len(detected),
            "missed_anomalies_count": len(missed),
            "formula_audit_results": {
                "total_cells_audited": len(cells),
                "broken_formula_count": None,
                "hardcoded_constants_found": hardcodes,
                "check_bars_passed": 0,
                "check_bars_failed": None,
            },
            "benford_result": benford,
            "turing_test_pass": False,
            "eqcr_memo": memo,
            "grade_letter": grade,
        }
        job["result"] = result
        job["status"] = "COMPLETED"
        self.events.append({"type": "qoe.audit.evaluation.incomplete.v1",
                            "engagement_id": job["engagement_id"], "job_id": job_id,
                            "score": scores["composite_score"], "grade": grade,
                            "cert_hash": hashlib.sha256(
                                json.dumps(result, sort_keys=True).encode()).hexdigest()[:16]})
        return result

    @staticmethod
    def _scope_from(spa: dict, report: dict) -> str:
        escrow = spa.get("4_indemnity_escrow", {})
        escrow_amt = escrow.get("amount", "0") if isinstance(escrow, dict) else "0"
        caveats = report.get("sections", {}).get(
            "10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities", {}).get("caveats", [])
        try:
            amount = Decimal(str(escrow_amt).replace("$", "").replace(",", ""))
        except (InvalidOperation, ValueError):
            amount = Decimal(0)
        if amount.is_finite() and amount > 0 and caveats:
            return "escrow"
        if caveats:
            return "caveated"
        return "missed"

    # rpc GetGradingStatus
    def get_grading_status(self, job_id: str) -> dict:
        job = self.jobs[job_id]
        result = job.get("result")
        return {
            "job_id": job_id,
            "status": job["status"],
            "scores": result["quadrant_scores"] if result else None,
            "ast_report": result["formula_audit_results"] if result else None,
            "benford_result": result["benford_result"] if result else None,
            "eqcr_memo": result["eqcr_memo"] if result else None,
            "completed_at": 0,
        }

    # rpc RunASTFormulaAudit
    def run_ast_formula_audit(self, engagement_id: str, cells: Sequence[Tuple[str, str, str]],
                              pvm: Optional[Tuple] = None,
                              check_bars: Sequence[Tuple[str, bool, object]] = (),
                              submitted: Optional[Dict] = None,
                              recomputed: Optional[Dict] = None) -> dict:
        report = self.ast.run(cells, pvm, check_bars, submitted, recomputed)
        report["engagement_id"] = engagement_id
        return report

    # rpc ScanBenfordDistribution
    def scan_benford_distribution(self, engagement_id: str, ledger_table_name: str = "",
                                  account_category_filter: str = "",
                                  values: Sequence = ()) -> dict:
        result = self.benford.scan(values)
        result["engagement_id"] = engagement_id
        return result

    # rpc GenerateEQCRMemo
    def generate_eqcr_memo(self, job_id: str, engagement_id: str) -> dict:
        result = self.jobs[job_id]["result"]
        return result["eqcr_memo"] if result else {}




# ========================================================================
# HTTP service adapters
# ========================================================================

import base64
import json
from pathlib import Path


def load_scenario_policy(scenario_root, scenario_id, seed):
    root=Path(scenario_root).resolve()
    if not scenario_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in scenario_id):
        raise ValueError("Invalid scenario identifier")
    path=(root/scenario_id/"audit_policy.json").resolve()
    if not path.is_relative_to(root): raise ValueError("Invalid scenario path")
    raw=path.read_bytes()
    checksum_file=path.parent/"checksum.sha256"
    if not checksum_file.is_file(): raise FileNotFoundError("Scenario checksum manifest missing: "+str(checksum_file))
    import hashlib
    hashes=dict((name,digest) for digest,name in
                (line.split("  ",1) for line in checksum_file.read_text(encoding="utf-8").splitlines()))
    if hashes.get("audit_policy.json")!=hashlib.sha256(raw).hexdigest():
        raise ValueError("Scenario audit policy checksum mismatch")
    manifest_path=path.parent/"manifest.json"
    manifest_raw=manifest_path.read_bytes()
    if hashes.get("manifest.json")!=hashlib.sha256(manifest_raw).hexdigest():
        raise ValueError("Scenario manifest checksum mismatch")
    manifest=json.loads(manifest_raw)
    if manifest.get("scenario_id")!=scenario_id: raise ValueError("Scenario identifier mismatch")
    if manifest.get("random_seed")!=int(seed,16): raise ValueError("Scenario manifest seed mismatch")
    from app.level0_physics.package_integrity import verify_package_integrity
    verify_package_integrity(path.parent)
    policy=json.loads(raw)
    if policy.get("seed_hex_64")!=seed: raise ValueError("Scenario seed mismatch")
    if "professional_calibration" not in policy: raise ValueError("Scenario calibration state absent")
    return validate_scenario_policy(policy)


def load_postgres_scenario_policy(dsn, scenario_id, seed, connect=None):
    """Read a sealed policy through the isolated qoe_eval_readonly role."""
    if not scenario_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in scenario_id):
        raise ValueError("Invalid scenario identifier")
    if connect is None:
        import psycopg
        connect=psycopg.connect
    with connect(dsn, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("BEGIN READ ONLY")
            try:
                cursor.execute("SET LOCAL statement_timeout = '5000ms'")
                cursor.execute("SELECT current_user, current_setting('transaction_read_only'), "
                               "rolsuper, rolcreatedb, rolcreaterole, rolreplication "
                               "FROM pg_roles WHERE rolname = current_user")
                role=cursor.fetchone()
                if not role or role[0]!="qoe_eval_readonly" or role[1]!="on" or any(role[2:]):
                    raise ValueError("Evaluation database must use an unprivileged read-only role")
                cursor.execute("SELECT has_table_privilege(current_user, 'audit_eval.scenario_policies', 'INSERT'), "
                               "has_table_privilege(current_user, 'audit_eval.scenario_policies', 'UPDATE'), "
                               "has_table_privilege(current_user, 'audit_eval.scenario_policies', 'DELETE'), "
                               "has_table_privilege(current_user, 'audit_eval.scenario_policies', 'TRUNCATE')")
                if any(cursor.fetchone()): raise ValueError("Evaluation role has policy mutation privileges")
                cursor.execute("SELECT policy_json, policy_sha256 FROM audit_eval.scenario_policies "
                               "WHERE scenario_id = %s AND seed_hex_64 = %s",(scenario_id,seed))
                row=cursor.fetchone()
                if not row: raise ValueError("Scenario policy unavailable")
                policy=json.loads(row[0]) if isinstance(row[0],str) else row[0]
                encoded=json.dumps(policy,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
                if hashlib.sha256(encoded).hexdigest()!=row[1]:
                    raise ValueError("Scenario policy checksum mismatch")
                if policy.get("seed_hex_64")!=seed: raise ValueError("Scenario seed mismatch")
                if "professional_calibration" not in policy: raise ValueError("Scenario calibration state absent")
                return validate_scenario_policy(policy)
            finally:
                cursor.execute("ROLLBACK")


def create_router(scenario_root, store_path=None):
    from fastapi import APIRouter, HTTPException
    root=Path(scenario_root).resolve()
    def provider(scenario_id,seed):
        dsn=os.environ.get("QOE_EVAL_READONLY_DSN")
        if dsn: return load_postgres_scenario_policy(dsn,scenario_id,seed)
        return load_scenario_policy(root,scenario_id,seed)
    jobs=EvaluationJobs(provider, store_path=store_path or root.parent / "audit_results" / "jobs.sqlite3")
    from contextlib import asynccontextmanager
    @asynccontextmanager
    async def lifespan(app):
        jobs.start_recovery()
        try:
            yield
        finally:
            jobs.stop_recovery()
    router=APIRouter(prefix="/api/v1/audit", lifespan=lifespan)
    @router.post("/submit")
    def submit(request:dict):
        try:
            encoded=request["workbook_base64"]
            if len(encoded)>90*1024*1024: raise ValueError("Workbook size limit")
            workbook=base64.b64decode(encoded,validate=True)
            return jobs.submit(request["engagement_id"],request["scenario_id"],request["seed_hex_64"],workbook,request["report"],request["spa"],request["checksum_sha256"])
        except (ValueError,KeyError,OSError) as e: raise HTTPException(400,str(e))
    @router.get("/jobs/{job_id}")
    def status(job_id:str):
        try: return jobs.status(job_id)
        except KeyError: raise HTTPException(404,"Unknown evaluation job")
    @router.get("/jobs/{job_id}/memo")
    def memo(job_id:str):
        value=status(job_id)
        if value["status"]!="COMPLETED": raise HTTPException(409,"Evaluation not completed")
        if "eqcr_memo" not in value["result"]: raise HTTPException(409,"Formula-only audit has no grading memo")
        return value["result"]["eqcr_memo"]
    @router.post("/formulas")
    def formulas(request:dict):
        import hashlib
        try:
            encoded=request["workbook_base64"]
            if len(encoded)>90*1024*1024: raise ValueError("Workbook size limit")
            workbook=base64.b64decode(encoded,validate=True)
            if hashlib.sha256(workbook).hexdigest()!=request["checksum_sha256"]:
                raise ValueError("Workbook checksum mismatch")
            envelope=json.dumps({"report":{},"spa":{}},sort_keys=True,separators=(",",":")).encode()
            return jobs.submit(request["engagement_id"],request["scenario_id"],request["seed_hex_64"],
                workbook,{},{},hashlib.sha256(workbook+envelope).hexdigest(),operation="ast")
        except (KeyError,ValueError,OSError) as e: raise HTTPException(400,str(e))
    @router.post("/benford")
    def benford(request:dict):
        try:
            policy=provider(request["scenario_id"],request["seed_hex_64"])
            category=request.get("account_category_filter")
            lines=[line for line in policy["ledger"].values() if not category or line.get("account_category")==category]
            return BenfordScanner().scan([line["amount"] for line in lines])
        except (KeyError,ValueError,OSError) as e: raise HTTPException(400,str(e))
    return router,jobs


# ========================================================================
# Protobuf/gRPC transport (uses the shared contract; no generated source files)
# ========================================================================

def register_grpc_service(server, jobs, artifact_reader, engagement_resolver, proto_path=None):
    """Register all five RPCs. Readers/resolvers are trusted deployment callbacks."""
    import grpc
    from pathlib import Path
    import re
    from google.protobuf import descriptor_pb2, descriptor_pool, message_factory, json_format, timestamp_pb2
    proto = Path(proto_path) if proto_path else Path(__file__).resolve().parents[3] / "proto" / "audit_eval.proto"
    # This contract uses flat messages/enums only. Reject unsupported syntax explicitly.
    source=re.sub(r"//[^\n]*", "", proto.read_text())
    schema=descriptor_pb2.FileDescriptorProto(name="audit_eval.proto",package="qoe.audit.v1",syntax="proto3")
    schema.dependency.append("google/protobuf/timestamp.proto")
    enum_names=set()
    for name,body in re.findall(r"enum\s+(\w+)\s*\{([^{}]*)\}",source):
        enum_names.add(name);enum=schema.enum_type.add(name=name)
        for value,number in re.findall(r"(\w+)\s*=\s*(\d+)\s*;",body): enum.value.add(name=value,number=int(number))
    types={"double":1,"float":2,"int64":3,"uint64":4,"int32":5,"bool":8,"string":9,"bytes":12,"uint32":13}
    for name,body in re.findall(r"message\s+(\w+)\s*\{([^{}]*)\}",source):
        message=schema.message_type.add(name=name)
        field_pattern=r"(repeated\s+)?([\w.]+)\s+(\w+)\s*=\s*(\d+)\s*;"
        if re.sub(field_pattern,"",body).strip(): raise ValueError("Unsupported protobuf field syntax")
        for repeated,kind,field_name,number in re.findall(field_pattern,body):
            field=message.field.add(name=field_name,number=int(number),label=3 if repeated else 1)
            field.type=types.get(kind,14 if kind in enum_names else 11)
            if kind not in types: field.type_name="."+kind if "." in kind else ".qoe.audit.v1."+kind
    for name,body in re.findall(r"service\s+(\w+)\s*\{([^{}]*)\}",source):
        service_descriptor=schema.service.add(name=name)
        for method,request,response in re.findall(r"rpc\s+(\w+)\s*\(\s*(\w+)\s*\)\s*returns\s*\(\s*(\w+)\s*\)\s*;",body):
            service_descriptor.method.add(name=method,input_type=".qoe.audit.v1."+request,output_type=".qoe.audit.v1."+response)
    pool=descriptor_pool.DescriptorPool()
    pool.AddSerializedFile(timestamp_pb2.DESCRIPTOR.serialized_pb)
    pool.Add(schema)
    service = pool.FindServiceByName("qoe.audit.v1.AuditEvaluationService")
    def scores(result):
        raw=result.get("quadrant_scores",{})
        output=dict(raw.get("weighted_quadrant_scores",{}))
        output.update(composite_score=result.get("composite_score",0),
                      passed_institutional_threshold=result.get("passed_institutional_gate",False))
        return output
    def ast_report(result,engagement):
        audit=result["ast_report"]
        def finding(row):
            coordinate=row.get("cell_coordinate","")
            sheet,_,cell=coordinate.rpartition("!")
            code=row["violation_type"]
            return {"sheet_name":sheet,"cell_coordinate":cell or coordinate,
                    "formula_raw":row.get("formula_raw", ""),"violation_type":code,
                    "severity":"CRITICAL_DISQUALIFIER" if code in ("FORMULA_ERROR","RAW_HARDCODE","VIO_EMBEDDED_CONSTANT") else "MATERIAL_DEFECT",
                    "score_deduction":PENALTIES.get(code,0),"rationale":row["rationale"]}
        return {"engagement_id":engagement,"total_cells_scanned":audit["total_cells_scanned"],
                "formulas_verified_reproducible":audit.get("formulas_verified_reproducible",0),
                "circular_references_trapped":audit.get("circular_references_trapped",0),
                "check_bars_reconciled":audit["check_bars_reconciled"],"findings":[finding(row) for row in audit["findings"]],
                "hardcoded_constants_flagged":sum(x["violation_type"] in ("RAW_HARDCODE","VIO_EMBEDDED_CONSTANT") for x in audit["findings"])}
    def memo(result,engagement):
        output=dict(result["eqcr_memo"]);output["engagement_id"]=engagement;output["scores"]=scores(result)
        return output
    def invoke(name,request,context):
        if name=="SubmitEngagementForGrading":
            queued=jobs.submit(request.engagement_id,request.scenario_id,request.seed_hex_64,
                artifact_reader(request.fdb_xlsx_blob_uri),json.loads(request.report_memo_json),
                json.loads(request.spa_exhibit_b_json),request.submission_checksum_sha256)
            return dict(queued,engagement_id=request.engagement_id,estimated_duration_seconds=jobs.timeout)
        if name in ("GetGradingStatus","GenerateEQCRMemo"):
            job=jobs.status(request.job_id)
            if name=="GenerateEQCRMemo":
                if request.engagement_id!=job["engagement_id"]: context.abort(grpc.StatusCode.PERMISSION_DENIED,"Engagement mismatch")
                if job["status"]!="COMPLETED" or "eqcr_memo" not in job["result"]:
                    context.abort(grpc.StatusCode.FAILED_PRECONDITION,"Memo unavailable")
                return memo(job["result"],job["engagement_id"])
            output={"job_id":request.job_id,"status":job["status"]}
            if job["status"]=="COMPLETED":
                result=job["result"];output["ast_report"]=ast_report(result,job["engagement_id"])
                if "eqcr_memo" in result:
                    scan=dict(result["benford_result"],engagement_id=job["engagement_id"])
                    output.update(scores=scores(result),eqcr_memo=memo(result,job["engagement_id"]),benford_result=scan)
                output["completed_at"]=job["completed_at"]
            return output
        scenario_id,seed=engagement_resolver(request.engagement_id)
        if name=="ScanBenfordDistribution":
            policy=jobs.scenario_provider(scenario_id,seed)
            if request.ledger_table_name not in ("", "proj_gl"): raise ValueError("Unsupported ledger table")
            values=[money(v["amount"]) for v in policy["ledger"].values() if not request.account_category_filter or v.get("account_category")==request.account_category_filter]
            result=BenfordScanner().scan(values);result["engagement_id"]=request.engagement_id
            return result
        workbook=artifact_reader(request.fdb_xlsx_blob_uri)
        envelope=json.dumps({"report":{},"spa":{}},sort_keys=True,separators=(",",":")).encode()
        queued=jobs.submit(request.engagement_id,scenario_id,seed,workbook,{},{},hashlib.sha256(workbook+envelope).hexdigest(),operation="ast")
        while context.is_active():
            job=jobs.status(queued["job_id"])
            if job["status"]=="COMPLETED": return ast_report(job["result"],request.engagement_id)
            if job["status"]=="FAILED": context.abort(grpc.StatusCode.FAILED_PRECONDITION,job["error"])
            time.sleep(.02)
        context.abort(grpc.StatusCode.CANCELLED,"Request cancelled")
    handlers={}
    for method in service.methods:
        request_type=message_factory.GetMessageClass(method.input_type)
        response_type=message_factory.GetMessageClass(method.output_type)
        def handler(request,context,name=method.name,response_type=response_type):
            try:
                return json_format.ParseDict(invoke(name,request,context),response_type(),ignore_unknown_fields=False)
            except KeyError: context.abort(grpc.StatusCode.NOT_FOUND,"Evaluation input not found")
            except (ValueError,TypeError): context.abort(grpc.StatusCode.INVALID_ARGUMENT,"Invalid evaluation request")
        handlers[method.name]=grpc.unary_unary_rpc_method_handler(handler,request_deserializer=request_type.FromString,response_serializer=lambda message:message.SerializeToString())
    server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler(service.full_name,handlers),))
    return pool


def validate_scenario_policy(policy):
    """Reject incomplete authoritative mappings before accepting learner work."""
    import re
    import hmac
    required=("seed_hex_64","workbook_policy","ledger","documents","anomalies","scope_gaps",
              "replacement_costs","allocations","reconciliations","professional_checks",
              "commercial_checks","legal_checks","behavior_checks")
    missing=[name for name in required if name not in policy]
    if missing: raise ValueError("Missing scenario mappings: "+", ".join(missing))
    workbook=policy["workbook_policy"]
    sheets=workbook.get("required_sheets",[])
    if len(sheets)!=11 or len(set(sheets))!=11: raise ValueError("Scenario requires eleven distinct sheets")
    def cell(reference):
        if not isinstance(reference,str) or "!" not in reference: raise ValueError("Invalid cell binding")
        sheet,coordinate=reference.rsplit("!",1)
        import re
        if sheet not in sheets or not re.fullmatch(r"[A-Z]{1,3}[1-9][0-9]*",coordinate): raise ValueError("Invalid cell binding: "+reference)
    for reference in workbook.get("calculation_cells",[])+workbook.get("check_bars",[]): cell(reference)
    if "check_bar_formulas" in workbook:
        if set(workbook["check_bar_formulas"])!=set(workbook.get("check_bars",[])):
            raise ValueError("Incomplete check-bar formula mapping")
        for formula in workbook["check_bar_formulas"].values():
            if not isinstance(formula,str) or not formula.startswith("="):
                raise ValueError("Invalid check-bar formula mapping")
    for aid,anomaly in policy["anomalies"].items():
        cell(anomaly["cell"]); money(anomaly["amount"])
        if not anomaly["ledger_ids"]: raise ValueError("Anomaly has no ledger evidence: "+aid)
        for identifier in anomaly["ledger_ids"]:
            if identifier not in policy["ledger"]: raise ValueError("Unknown ledger evidence: "+identifier)
            line=policy["ledger"][identifier]
            cell(line["cell"]); money(line["amount"])
            if line["document_id"] not in policy["documents"]: raise ValueError("Unknown document evidence")
            if path_value(policy["documents"][line["document_id"]],line["document_path"])!=line["document_value"]:
                raise ValueError("Canonical evidence value mismatch")
    for gap,rule in policy["scope_gaps"].items():
        if money(rule["minimum_escrow"])<=0: raise ValueError("Escrow requirement must be positive: "+gap)
    calibration=policy.get("professional_calibration")
    if calibration not in (None,"structural_only","expert_reviewed"):
        raise ValueError("Unknown professional calibration state")
    if calibration=="expert_reviewed":
        review=policy.get("partner_review",{})
        baseline={key:value for key,value in policy.items() if key not in ("partner_review","professional_calibration")}
        digest=hashlib.sha256(json.dumps(baseline,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
        required=("reviewer_id","reviewer_role","blind_comparison_id","comparator_sha256",
                  "reviewed_at","verdict","baseline_policy_sha256")
        if any(not review.get(key) for key in required) or review["baseline_policy_sha256"]!=digest:
            raise ValueError("Missing or unbound blind partner review")
        if review["reviewer_role"]!="transaction_advisory_partner" or review["verdict"]!="indistinguishable":
            raise ValueError("Blind partner review did not meet the specified gate")
        if not re.fullmatch(r"[a-f0-9]{64}",review["comparator_sha256"]):
            raise ValueError("Invalid real-deal comparator digest")
        secret=os.environ.get("QOE_REVIEW_SIGNING_KEY","")
        signature=review.get("review_hmac_sha256","")
        unsigned={key:value for key,value in review.items() if key!="review_hmac_sha256"}
        expected=hmac.new(secret.encode(),json.dumps(unsigned,sort_keys=True,separators=(",",":")).encode(),hashlib.sha256).hexdigest()
        if len(secret)<32 or not hmac.compare_digest(signature,expected):
            raise ValueError("Unverified partner review signature")
    return policy


def record_partner_review(policy, review):
    """Trusted administrative step after an independent, blind human review."""
    import hmac
    secret=os.environ.get("QOE_REVIEW_SIGNING_KEY","")
    if len(secret)<32: raise ValueError("Partner review signing key unavailable")
    baseline={key:value for key,value in policy.items() if key not in ("partner_review","professional_calibration")}
    unsigned={key:value for key,value in review.items() if key!="review_hmac_sha256"}
    signature=hmac.new(secret.encode(),json.dumps(unsigned,sort_keys=True,separators=(",",":")).encode(),hashlib.sha256).hexdigest()
    reviewed=dict(baseline,professional_calibration="expert_reviewed",
                  partner_review=dict(unsigned,review_hmac_sha256=signature))
    return validate_scenario_policy(reviewed)


def store_partner_review(package_dir, review):
    """Trusted offline review step: verify, sign, and reseal the package."""
    import tempfile
    import tarfile
    root=Path(package_dir).resolve()
    policy_path=root/"audit_policy.json"
    original=json.loads(policy_path.read_text(encoding="utf-8"))
    policy=load_scenario_policy(root.parent,root.name,original["seed_hex_64"])
    if policy.get("professional_calibration")!="structural_only":
        raise ValueError("Only a pending review may be recorded")
    reviewed=record_partner_review(policy,review)
    new_policy=json.dumps(reviewed,indent=2,sort_keys=True).encode("utf-8")
    checksum_path=root/"checksum.sha256"
    lines=checksum_path.read_text(encoding="utf-8").splitlines()
    changed=False
    for index,line in enumerate(lines):
        digest,name=line.split("  ",1)
        if name=="audit_policy.json":
            lines[index]=hashlib.sha256(new_policy).hexdigest()+"  audit_policy.json"
            changed=True
    if not changed: raise ValueError("Unsealed audit policy")
    def staged(data,suffix):
        with tempfile.NamedTemporaryFile(dir=root,prefix=".review-",suffix=suffix,delete=False) as output:
            output.write(data)
            return Path(output.name)
    temporary_policy=staged(new_policy,".json")
    temporary_checksum=staged(("\n".join(lines)+"\n").encode(),".sha256")
    try:
        os.replace(temporary_policy,policy_path)
        os.replace(temporary_checksum,checksum_path)
        archive=root.parent/(root.name+"_package.tar.gz")
        if archive.exists():
            with tempfile.NamedTemporaryFile(dir=root.parent,prefix=".review-",suffix=".tar.gz",delete=False) as output:
                temporary_archive=Path(output.name)
            try:
                with tarfile.open(temporary_archive,"w:gz") as target:
                    target.add(root,arcname=root.name)
                os.replace(temporary_archive,archive)
            finally:
                temporary_archive.unlink(missing_ok=True)
    finally:
        temporary_policy.unlink(missing_ok=True)
        temporary_checksum.unlink(missing_ok=True)
    return reviewed


def build_compiled_scenario_policy(package_dir, seed_hex_64):
    """Bind compiler truth to the actual Level 4 grid, without learner input."""
    import re
    from app.level4_databook.formula_graph import Databook, _databook_to_sheets
    root=Path(package_dir)
    provenance=json.loads((root/"audit_evidence.json").read_text(encoding="utf-8"))
    canonical=json.loads((root/"vdr_artifacts"/"canonical_documents.json").read_text(encoding="utf-8"))
    book=Databook().build(str(root),verify_integrity=False)
    rendered=_databook_to_sheets(book)
    bindings=book.audit_cell_bindings()["tabs"]
    bridge=bindings["02_EBITDA_Bridges"]["metrics"]
    ledger={identifier:{"amount":row["signed_amount"]} for identifier,row in provenance["ledger"].items()}
    anomalies={}
    source_fields={"SR-B01":"rebate_total","SR-B06":"unabsorbed_overhead","SR-B14":"capitalized_labor"}
    for key,occurrence in provenance["anomaly_occurrences"].items():
        calculation=bridge[occurrence["document_ref"]]["cell"]
        matched=[identifier for identifier in occurrence["ledger_ids"] if "GL:"+identifier in bridge]
        if len(matched)!=1 or not bridge[occurrence["document_ref"]]["has_formula"]:
            raise ValueError("Incomplete anomaly workbook binding: "+key)
        identifier=matched[0]
        source=provenance["documents"][key]
        field=source_fields[occurrence["anomaly_id"]]
        amount=source[field]
        if abs(money(provenance["ledger"][identifier]["signed_amount"]))!=money(amount):
            raise ValueError("Operational source and ledger disagree: "+key)
        ledger[identifier]={"amount":amount,"signed_amount":provenance["ledger"][identifier]["signed_amount"],
                            "cell":bridge["GL:"+identifier]["cell"],"document_id":key,
                            "document_path":field,"document_value":amount}
        anomalies[key]={"cell":calculation,"amount":occurrence["amount"],"ledger_ids":[identifier]}
    calculation_cells=[f"{sheet}!B{row}" for sheet,rows in rendered.items() for row,values in enumerate(rows[1:],2)
                       if isinstance(values[1],str) and values[1].startswith("=")]
    pvm=bindings["04_Revenue_PVM"]["metrics"]
    pvm_cells={name:pvm[key]["cell"] for name,key in (("delta","total_delta"),("price","price_effect"),
                                                       ("volume","volume_effect"),("mix","mix_effect"))}
    pvm_cells.update({"expected_"+name:book.tabs["04_Revenue_PVM"]["waterfall"][key]
                      for name,key in (("delta","total_delta"),("price","price_effect"),
                                       ("volume","volume_effect"),("mix","mix_effect"))})
    pvm_cells["source_cells"]={}
    for product in book.tabs["04_Revenue_PVM"]["products"]:
        anchor=pvm["product:"+product["product_id"]]["cell"]
        sheet,row=anchor.rsplit("!B",1)
        for col,key in (("B","base_units"),("C","base_revenue"),
                        ("D","current_units"),("E","current_revenue")):
            pvm_cells["source_cells"][f"{sheet}!{col}{row}"]=str(product[key])
    gaps={}
    for record in canonical["missing_records"]:
        match=re.search(r"\$([0-9,]+) specific indemnity escrow",record["recommended_action"],re.I)
        if not match: raise ValueError("Missing explicit escrow amount for "+record["document_type"])
        gaps[record["document_type"]]={"minimum_escrow":match[1].replace(",","")}
    policy={"seed_hex_64":seed_hex_64,"workbook_policy":{
        "required_sheets":list(book.TAB_IDS),"check_bars":[s+"!B1" for s in book.TAB_IDS],
        "check_bar_formulas":{s+"!B1":rendered[s][0][1] for s in book.TAB_IDS},
        "calculation_cells":calculation_cells,"whole_dollar_cells":[],"pvm":[pvm_cells]},
        "ledger":ledger,"documents":provenance["documents"],"anomalies":anomalies,
        "scope_gaps":gaps,"replacement_costs":[],"allocations":{},
        "reconciliations":[
            {"report_path":"sections.01_Executive_Summary.normalized_ebitda","cell":bindings["01_Summary"]["metrics"]["normalized_ebitda"]["cell"],"display_only":True},
            {"report_path":"sections.05_Net_Working_Capital.target_peg","cell":bindings["07_Working_Capital"]["metrics"]["target_nwc_peg"]["cell"],"display_only":True},
            {"report_path":"sections.06_Net_Debt_and_Debt_Like_Items.net_debt","cell":bindings["08_Net_Debt"]["metrics"]["net_debt"]["cell"],"display_only":True}],
        "professional_checks":[{"source":"report","path":"sections.02_Transaction_Context_and_Scope.non_attest_boundary","required":True}],
        "commercial_checks":[{"source":"report","path":"sections.08_Commercial_and_Customer_Analysis.customer_concentration","required":True}],
        "legal_checks":[{"source":"spa","path":"1_target_peg.mechanism","required":True}],
        "behavior_checks":[{"source":"report","path":"sections.09_Operational_Diagnostics.capacity_utilization","required":True}],
        "provenance_kind":"simulated_operational_source",
        "professional_calibration":"structural_only"}
    return validate_scenario_policy(policy)
