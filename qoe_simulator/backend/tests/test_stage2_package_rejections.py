"""Negative handoff tests against a freshly compiled, disposable Apex package."""

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from app.level4_databook.formula_graph import Databook
from app.level5_workspace.gateway import WorkspaceGatewayService
from app.level6_audit.rubric_scorer import load_scenario_policy


SCENARIOS = Path(__file__).resolve().parents[2] / "scenarios"
sys.path.insert(0, str(SCENARIOS / "compiler"))
sys.path.insert(0, str(SCENARIOS))

from build_scenario import SCENARIO_PROFILES, compile_scenario  # noqa: E402
from verify_stage2_checksums import verify  # noqa: E402


class TestStage2PackageRejections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="stage2-rejection-fixture-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.source = Path(compile_scenario(
            SCENARIO_PROFILES["target_apex_supply"], 2, 42, cls.temporary.name
        )["package_dir"])
        cls.seed = "0x000000000000002a"

    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="stage2-rejection-case-")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.package = self.root / self.source.name
        shutil.copytree(self.source, self.package)
        self.source_hash = hashlib.sha256((self.source / "ground_truth.duckdb").read_bytes()).hexdigest()

    def tearDown(self):
        self.assertEqual(self.source_hash,
                         hashlib.sha256((self.source / "ground_truth.duckdb").read_bytes()).hexdigest())

    def load(self):
        return load_scenario_policy(self.root, self.package.name, self.seed)

    def test_intact_control_and_policy_identity(self):
        self.assertEqual(self.load()["seed_hex_64"], self.seed)
        self.assertEqual(len(Databook().build(str(self.package)).tabs), 11)
        tree = WorkspaceGatewayService(package_dir=str(self.package)).get_vdr_tree("sim", "user", 20)
        self.assertEqual(tree["total_unlocked_documents"] + tree["total_locked_documents"], 25)

    def test_tampered_policy_and_manifest_fail_before_loading(self):
        policy = self.package / "audit_policy.json"
        policy.write_bytes(policy.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "policy checksum mismatch"):
            self.load()
        shutil.copy2(self.source / "audit_policy.json", policy)
        manifest = self.package / "manifest.json"
        data = json.loads(manifest.read_text())
        data["random_seed"] = 43
        manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "manifest checksum mismatch"):
            self.load()

    def test_wrong_scenario_and_wrong_seed_fail(self):
        with self.assertRaisesRegex(ValueError, "seed mismatch"):
            load_scenario_policy(self.root, self.package.name, "0x000000000000002b")
        renamed = self.root / "different_scenario"
        self.package.rename(renamed)
        self.package = renamed
        with self.assertRaisesRegex(ValueError, "identifier mismatch"):
            load_scenario_policy(self.root, renamed.name, self.seed)

    def test_resealed_wrong_manifest_seed_still_fails_identity(self):
        manifest = self.package / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["random_seed"] = 43
        manifest.write_text(json.dumps(data), encoding="utf-8")
        checksum = self.package / "checksum.sha256"
        lines = checksum.read_text(encoding="utf-8").splitlines()
        lines = [f"{hashlib.sha256(manifest.read_bytes()).hexdigest()}  manifest.json"
                 if line.endswith("  manifest.json") else line for line in lines]
        checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "manifest seed mismatch"):
            self.load()

    def test_missing_checksum_and_policy_fail(self):
        (self.package / "checksum.sha256").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "checksum manifest missing"):
            self.load()
        shutil.copy2(self.source / "checksum.sha256", self.package / "checksum.sha256")
        (self.package / "audit_policy.json").unlink()
        with self.assertRaises(FileNotFoundError):
            self.load()

    def test_missing_ledger_never_creates_replacement(self):
        database = self.package / "ground_truth.duckdb"
        database.unlink()
        with self.assertRaisesRegex(FileNotFoundError, "Sealed package file missing: ground_truth.duckdb"):
            Databook().build(str(self.package))
        self.assertFalse(database.exists())

    def test_missing_subledgers_closes_database(self):
        (self.package / "subledgers.json").unlink()
        with self.assertRaises(FileNotFoundError):
            Databook().build(str(self.package))
        # Windows permits this rename only when the reader closed its connection.
        database = self.package / "ground_truth.duckdb"
        moved = self.package / "moved.duckdb"
        database.rename(moved)
        moved.rename(database)

    def test_vdr_rejects_changed_or_missing_sealed_document(self):
        document = self.package / "vdr_artifacts/json/entity_master.json"
        document.write_bytes(document.read_bytes() + b" ")
        gateway = WorkspaceGatewayService(package_dir=str(self.package))
        with self.assertRaisesRegex(ValueError, "VDR document checksum mismatch"):
            gateway.get_vdr_tree("sim", "user", 20)
        document.unlink()
        with self.assertRaises(FileNotFoundError):
            gateway.get_vdr_tree("sim", "user", 20)

    def test_separate_package_verifier_rejects_other_sealed_mutation(self):
        path = self.package / "operational_trajectory.json"
        path.write_bytes(path.read_bytes() + b" ")
        _entries, _rows, problems = verify(self.package, 43)
        self.assertIn("Hash mismatch: operational_trajectory.json", problems)
        with self.assertRaisesRegex(ValueError, "Package checksum mismatch: operational_trajectory.json"):
            Databook().build(str(self.package))
        with self.assertRaisesRegex(ValueError, "Package checksum mismatch: operational_trajectory.json"):
            self.load()

    def test_required_subledgers_are_sealed(self):
        path = self.package / "subledgers.json"
        path.write_bytes(path.read_bytes() + b" ")
        _entries, _rows, problems = verify(self.package, 43)
        self.assertIn("Hash mismatch: subledgers.json", problems)
        with self.assertRaisesRegex(ValueError, "Package checksum mismatch: subledgers.json"):
            Databook().build(str(self.package))
        with self.assertRaisesRegex(ValueError, "Package checksum mismatch: subledgers.json"):
            self.load()


if __name__ == "__main__":
    unittest.main()
