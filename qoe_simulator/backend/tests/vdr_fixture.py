"""Minimal sealed JSON VDR package for workspace unit tests."""

import hashlib
import json
from pathlib import Path


def create_vdr_fixture(directory):
    root = Path(directory)
    folder = root / "vdr_artifacts" / "json"
    folder.mkdir(parents=True, exist_ok=True)
    specifications = (
        ("01_Corporate_Governance_and_Legal", "Entity_Master.json", "entity_master.json", 1),
        ("02_Financial_and_Accounting", "ERP_General_Ledger.json", "erp_general_ledger.json", 7),
        ("05_Operations_and_Procurement", "Supplier_Rebate_Terms.json", "operational_source_documents.json", 14),
        ("06_Human_Resources_and_Compensation", "Payroll_Run_Rate.json", "subledgers.json", 20),
    )
    docs = []
    hashes = {}
    for section, title, filename, day in specifications:
        relative = "vdr_artifacts/json/" + filename
        content = json.dumps({"source": title, "records": [1]}, sort_keys=True).encode()
        (root / relative).write_bytes(content)
        hashes[relative] = hashlib.sha256(content).hexdigest()
        docs.append({"section": section, "title": title, "path": relative, "unlock_day": day})
    catalog_rel = "vdr_artifacts/json/catalog.json"
    catalog = json.dumps({"schema_version": 1, "documents": docs}, sort_keys=True).encode()
    (root / catalog_rel).write_bytes(catalog)
    hashes[catalog_rel] = hashlib.sha256(catalog).hexdigest()
    (root / "checksum.sha256").write_text(
        "".join(f"{digest}  {path}\n" for path, digest in hashes.items()), encoding="utf-8")
    return str(root)
