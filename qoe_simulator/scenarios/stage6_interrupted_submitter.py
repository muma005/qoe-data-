"""Test helper: submit a real job, signal PROCESSING, and await controller termination."""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    for argument in ("package", "handoff", "store", "marker"):
        parser.add_argument("--" + argument, type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
    from app.level6_audit.rubric_scorer import EvaluationJobs, load_scenario_policy

    workbook = (args.handoff / "apex_databook.xlsx").read_bytes()
    report = json.loads((args.handoff / "apex_report.json").read_text(encoding="utf-8"))
    spa = json.loads((args.handoff / "apex_spa_exhibit_b.json").read_text(encoding="utf-8"))
    payload = json.dumps({"report": report, "spa": spa}, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode()
    jobs = EvaluationJobs(lambda s, k: load_scenario_policy(args.package.parent, s, k),
                          timeout=20, store_path=args.store)
    job = jobs.submit("STAGE6_INTERRUPTED_APEX", "target_apex_supply", "0x4a9f82c1e703bd55",
                      workbook, report, spa, hashlib.sha256(workbook + payload).hexdigest())
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        state = jobs.status(job["job_id"])["status"]
        if state == "PROCESSING":
            args.marker.write_text(json.dumps({"pid": os.getpid(), "job_id": job["job_id"],
                                               "status": state}), encoding="utf-8")
            time.sleep(120)
            return
        if state in ("FAILED", "COMPLETED"):
            raise RuntimeError("Job settled before interruption marker: " + state)
        time.sleep(.01)
    raise TimeoutError("Job did not enter PROCESSING")


if __name__ == "__main__":
    main()
