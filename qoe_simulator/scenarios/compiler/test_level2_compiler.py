"""
Test harness for the Level 2 Offline Scenario Compiler (biz-gen).

Validates:
  - End-to-end compilation of all three sectors with the Level 0.5 invariant gate.
  - Double-entry equilibrium (INV1) and balance-sheet conservation (INV2).
  - ASC 330 SKU mass-balance (INV4) and ASC 606 revenue waterfall (INV5).
  - Anomaly injection (SR-B01, SR-B06, SR-B14).
  - Deterministic reproducibility for a fixed seed.
  - Multi-ERP export rendering.

Run directly from the repo root:
    python scenarios/compiler/test_level2_compiler.py
"""

import os
import re
import sys
import tempfile
import unittest
from decimal import Decimal

_COMPILER_DIR = os.path.dirname(os.path.abspath(__file__))
if _COMPILER_DIR not in sys.path:
    sys.path.insert(0, _COMPILER_DIR)

from build_scenario import (  # noqa: E402
    DataGenerationService,
    SCENARIO_PROFILES,
    compile_scenario,
    parse_seed,
)
from sector_models import (  # noqa: E402
    AccountingCore,
    DegradationEngine,
    ERPExporter,
    ERPSchemaType,
    ERP_TYPE_TO_EXPORTER,
    _money,
    build_simulator,
)
from subledgers import SubledgerSet  # noqa: E402
from entities import MasterEntityLedger, generate_fein, valid_fein, valid_zip  # noqa: E402
from macro_volatility import IndustrySector  # noqa: E402


class TestLevel2Compiler(unittest.TestCase):

    def _compile(self, scenario_id, years=3, seed="0x4a9f82c1e703bd55", tmp=None):
        tmp = tmp or tempfile.mkdtemp()
        profile = SCENARIO_PROFILES[scenario_id]
        return compile_scenario(profile, years, parse_seed(seed), tmp), tmp

    def test_all_sectors_compile_and_pass_invariants(self):
        for scenario_id in ("target_apex_supply", "titan_precision_machining", "cloudpulse_saas"):
            with tempfile.TemporaryDirectory() as tmp:
                result, _ = self._compile(scenario_id, tmp=tmp)
                self.assertTrue(result["invariant_check_passed"], scenario_id)
                self.assertGreater(result["total_journal_entries"], 0, scenario_id)
                self.assertGreater(result["total_gl_lines"], 0, scenario_id)
                # Artifacts written
                pkg = result["package_dir"]
                self.assertTrue(os.path.exists(os.path.join(pkg, "ground_truth.duckdb")))
                self.assertTrue(os.path.exists(os.path.join(pkg, "checksum.sha256")))
                self.assertTrue(os.path.exists(result["tar_path"]))

    def test_anomaly_injection_per_sector(self):
        expected = {
            "target_apex_supply": "SR-B01",
            "titan_precision_machining": "SR-B06",
            "cloudpulse_saas": "SR-B14",
        }
        for scenario_id, anomaly_id in expected.items():
            with tempfile.TemporaryDirectory() as tmp:
                result, _ = self._compile(scenario_id, tmp=tmp)
                pkg = result["package_dir"]
                with open(os.path.join(pkg, "injected_anomalies.json"), encoding="utf-8") as f:
                    import json
                    data = json.load(f)
                ids = {a["anomaly_id"] for a in data["anomalies"]}
                self.assertIn(anomaly_id, ids, scenario_id)

    def test_deterministic_reproducibility(self):
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            r1, _ = self._compile("target_apex_supply", tmp=tmp1)
            r2, _ = self._compile("target_apex_supply", tmp=tmp2)
            with open(os.path.join(r1["package_dir"], "checksum.sha256"), encoding="utf-8") as f:
                c1 = f.read()
            with open(os.path.join(r2["package_dir"], "checksum.sha256"), encoding="utf-8") as f:
                c2 = f.read()
            self.assertEqual(c1, c2)

    def test_inv1_double_entry_global_equilibrium(self):
        core = AccountingCore("test", 42, 52_000_000, start_year=2021, start_month=1)
        self.assertEqual(core.total_debits(), core.total_credits())
        passed, delta = core.assert_inv2_balance_sheet()
        self.assertTrue(passed)
        self.assertEqual(delta, 0)

    def test_inv5_asc606_waterfall_for_saas(self):
        core = AccountingCore("test_saas", 42, 48_000_000, start_year=2021, start_month=1)
        sim = build_simulator(core, IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS, ["SR-B14"])
        from macro_volatility import VolatilityEngine, VolatilityScenarioConfig
        traj = VolatilityEngine().generate_trajectory(VolatilityScenarioConfig(
            scenario_id="test_saas", seed=42,
            sector=IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS,
            simulation_months=12, base_annual_revenue=48_000_000,
            base_gross_margin=0.72, base_ebit_margin=0.15,
        ))
        for idx, t in enumerate(traj.monthly_trajectories, start=1):
            sim.simulate_month(t, idx)
        # INV5: Invoiced == Recognized + Deferred
        self.assertEqual(
            core.total_contract_invoiced,
            core.cumulative_recognized + core.deferred_revenue,
        )
        # INV1 still holds after all SaaS postings
        self.assertEqual(core.total_debits(), core.total_credits())

    def test_erp_exporters_render_all_four_schemas(self):
        core = AccountingCore("test", 42, 52_000_000, start_year=2021, start_month=1)
        sim = build_simulator(core, IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION, [])
        from macro_volatility import VolatilityEngine, VolatilityScenarioConfig
        traj = VolatilityEngine().generate_trajectory(VolatilityScenarioConfig(
            scenario_id="test", seed=42,
            sector=IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION,
            simulation_months=3, base_annual_revenue=52_000_000,
        ))
        for idx, t in enumerate(traj.monthly_trajectories, start=1):
            sim.simulate_month(t, idx)

        for erp in (ERPExporter.ERP_NETSUITE, ERPExporter.ERP_SAP_S4HANA,
                    ERPExporter.ERP_QUICKBOOKS, ERPExporter.ERP_DYNAMICS365):
            text = ERPExporter.export(erp, core.entries)
            self.assertGreater(len(text), 0, erp)
            self.assertIn("\n", text, erp)

    def test_expense_granularity_and_reconciliation(self):
        """Expenses must be decomposed into hundreds of driver-based vendor invoices,
        not a fixed 3-bucket split, and must reconcile exactly to Module 10's control total."""
        core = AccountingCore("test", 42, 52_000_000, start_year=2021, start_month=1)
        sim = build_simulator(core, IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION, [])
        from macro_volatility import VolatilityEngine, VolatilityScenarioConfig
        traj = VolatilityEngine().generate_trajectory(VolatilityScenarioConfig(
            scenario_id="test", seed=42,
            sector=IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION,
            simulation_months=12, base_annual_revenue=52_000_000,
        ))
        for idx, t in enumerate(traj.monthly_trajectories, start=1):
            sim.simulate_month(t, idx)

        expense_entries = [e for e in core.entries
                           if e.entry_type in ("EXPENSE", "PAYROLL", "DEPRECIATION", "AMORTIZATION")]

        # Hundreds of expense line items over a year (not 1-2 per month)
        self.assertGreater(len(expense_entries), 100)

        # Many distinct expense accounts (granular taxonomy, not 3 buckets)
        expense_accounts = {line.account_number for e in expense_entries for line in e.lines if line.debit > 0}
        self.assertGreater(len(expense_accounts), 15)

        # Many distinct vendors (not a single generic entity)
        vendors = {e.entity_name for e in expense_entries if e.entry_type == "EXPENSE"}
        self.assertGreater(len(vendors), 10)

        # Exact reconciliation: bottom-up expense debits == top-down opex control total
        total_expense_debit = sum((line.debit for e in expense_entries for line in e.lines), Decimal("0.0000"))
        total_opex = sum((Decimal(str(t.opex_runrate)) for t in traj.monthly_trajectories), Decimal("0.0000"))
        self.assertEqual(
            total_expense_debit.quantize(Decimal("0.0001")),
            _money(total_opex).quantize(Decimal("0.0001")),
        )


# ---------------------------------------------------------------------------
# Proto-contract helpers (parse biz_gen.proto text; no proto edits)
# ---------------------------------------------------------------------------
def _proto_path() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(_COMPILER_DIR)), "proto", "biz_gen.proto")


def _read_proto() -> str:
    with open(_proto_path(), encoding="utf-8") as f:
        return f.read()


def _parse_enum(text: str, enum_name: str) -> dict:
    m = re.search(r"enum\s+" + enum_name + r"\s*\{(.*?)\}", text, re.DOTALL)
    body = m.group(1)
    return {k: int(v) for k, v in re.findall(r"(\w+)\s*=\s*(\d+)\s*;", body)}


def _parse_service_rpcs(text: str) -> list:
    m = re.search(r"service\s+\w+\s*\{(.*?)\}", text, re.DOTALL)
    body = m.group(1)
    return re.findall(r"rpc\s+(\w+)\s*\(\s*(\w+)\s*\)\s*returns\s*\(\s*(\w+)\s*\)", body)


def _parse_message_fields(text: str) -> dict:
    messages = {}
    for name, body in re.findall(r"message\s+(\w+)\s*\{(.*?)\}", text, re.DOTALL):
        messages[name] = [f for f in re.findall(r"(\w+)\s*=\s*\d+\s*;", body)]
    return messages


class TestBizGenProtoContract(unittest.TestCase):
    """Confirms Level 2 is wired to proto/biz_gen.proto without editing the proto."""

    RPC_TO_METHOD = {
        "CompileScenarioPackage": "compile_scenario_package",
        "ExportERPDataset": "export_erp_dataset",
    }

    @classmethod
    def setUpClass(cls):
        cls.proto = _read_proto()
        cls.proto_enum = _parse_enum(cls.proto, "ERPSchemaType")
        cls.rpcs = _parse_service_rpcs(cls.proto)
        cls.messages = _parse_message_fields(cls.proto)

    def test_erp_schema_enum_matches_proto(self):
        py_enum = {e.name: e.value for e in ERPSchemaType}
        self.assertEqual(py_enum, self.proto_enum)

    def test_erp_enum_maps_to_all_exporters(self):
        for erp_enum in (ERPSchemaType.ERP_ORACLE_NETSUITE, ERPSchemaType.ERP_SAP_S4HANA,
                         ERPSchemaType.ERP_QUICKBOOKS_DESKTOP, ERPSchemaType.ERP_MICROSOFT_DYNAMICS_365):
            self.assertIn(erp_enum, ERP_TYPE_TO_EXPORTER)

    def test_service_rpcs_have_python_methods(self):
        svc = DataGenerationService()
        for rpc_name, _req, _resp in self.rpcs:
            self.assertTrue(hasattr(svc, self.RPC_TO_METHOD[rpc_name]), rpc_name)

    def test_response_fields_align_with_proto(self):
        svc = DataGenerationService()
        for rpc_name, _req, resp_msg in self.rpcs:
            method = self.RPC_TO_METHOD[rpc_name]
            result = self._call(svc, method)
            expected_fields = self.messages[resp_msg]
            self.assertTrue(expected_fields, f"no fields parsed for {resp_msg}")
            for field in expected_fields:
                self.assertIn(field, result, f"{rpc_name} response missing field '{field}'")

    def _call(self, svc, method):
        if method == "compile_scenario_package":
            return svc.compile_scenario_package(
                scenario_id="target_apex_supply",
                random_seed=42,
                sector_naics="4238",
                base_annual_revenue=52_000_000.0,
                historical_months=36,
                target_erp=ERPSchemaType.ERP_ORACLE_NETSUITE,
                active_anomaly_ids=["SR-B01"],
            )
        if method == "export_erp_dataset":
            svc.compile_scenario_package(
                scenario_id="target_apex_supply",
                random_seed=42,
                sector_naics="4238",
                base_annual_revenue=52_000_000.0,
                historical_months=36,
                target_erp=ERPSchemaType.ERP_ORACLE_NETSUITE,
                active_anomaly_ids=["SR-B01"],
            )
            return svc.export_erp_dataset(
                scenario_id="target_apex_supply",
                erp_type=ERPSchemaType.ERP_SAP_S4HANA,
                start_date="2021-01-01",
                end_date="2023-12-31",
            )
        raise AssertionError(f"unknown method {method}")


class TestLevel2FillBuild(unittest.TestCase):
    """Covers the spec subsections added in the full fill-build: subledgers, entities,
    cutoff defect, provenance, LP-10, and the REST-facing facade methods."""

    def _compiled_core(self, scenario_id="target_apex_supply", months=12):
        core = AccountingCore("test", 42, 52_000_000, start_year=2021, start_month=1)
        sim = build_simulator(core, IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION, ["SR-B01"])
        from macro_volatility import VolatilityEngine, VolatilityScenarioConfig
        traj = VolatilityEngine().generate_trajectory(VolatilityScenarioConfig(
            scenario_id=scenario_id, seed=42,
            sector=IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION,
            simulation_months=months, base_annual_revenue=52_000_000,
        ))
        for idx, t in enumerate(traj.monthly_trajectories, start=1):
            sim.simulate_month(t, idx)
        return core

    def test_subledger_set_builds_all_five(self):
        core = self._compiled_core()
        sub = SubledgerSet().build(core.entries)
        d = sub.to_dict()
        for key in ("accounts_receivable", "accounts_payable", "inventory",
                    "fixed_assets", "deferred_revenue"):
            self.assertIn(key, d)
        self.assertGreater(sub.ar.total_open(), 0)
        self.assertGreater(sub.ap.total_open(), 0)

    def test_ar_aging_buckets(self):
        core = self._compiled_core()
        sub = SubledgerSet().build(core.entries)
        buckets = sub.ar.aging(13)
        self.assertIn("current", buckets)
        self.assertIn("over_90", buckets)

    def test_entity_ledger_lp15(self):
        ledger = MasterEntityLedger(seed=7)
        v = ledger.register_vendor("Deloitte & Touche LLP")
        c = ledger.register_customer("Grainger Supply")
        self.assertTrue(valid_fein(v.fein))
        self.assertTrue(valid_fein(c.fein))
        self.assertTrue(valid_zip(v.zip_code))
        self.assertTrue(valid_zip(c.zip_code))
        self.assertTrue(ledger.validate_all()["compliant"])

    def test_generate_fein_format(self):
        self.assertTrue(valid_fein(generate_fein("Acme Corp", 1)))
        self.assertFalse(valid_fein("123"))

    def test_cutoff_defect(self):
        deg = DegradationEngine(42)
        text, defects = deg.render_cutoff_break(Decimal("125000"))
        self.assertTrue(any(d["defect_type"] == "STUB_PERIOD_CUTOFF" for d in defects))
        self.assertIn("2023-12-31", text)

    def test_provenance_manifest_seven_tiers(self):
        deg = DegradationEngine(42)
        manifest = deg.render_provenance_manifest()
        self.assertEqual(len(manifest["tiers"]), 7)

    def test_lp10_pdf_metadata(self):
        meta = DegradationEngine.pdf_metadata("2023-12-31")
        self.assertEqual(meta["CreationDate"], "2023-12-31")
        self.assertTrue(meta["generative_software_tag_stripped"])

    def test_facade_subledgers_and_vdr_batch(self):
        svc = DataGenerationService()
        svc.compile_scenario_package("target_apex_supply", 42, "4238", 52_000_000.0, 36,
                                     ERPSchemaType.ERP_ORACLE_NETSUITE, ["SR-B01"])
        ar_view = svc.subledgers("aged_ar")
        self.assertIn("aging_buckets", ar_view)
        batch = svc.render_vdr_batch("wave_2_subledgers")
        self.assertEqual(batch["wave"], "wave_2_subledgers")
        self.assertGreater(batch["new_file_count"], 0)

    def test_per_invoice_granularity(self):
        """Revenue must be generated as per-invoice entries, not one monthly aggregate."""
        core = self._compiled_core(months=12)
        invoices = [e for e in core.entries if e.entry_type == "INVOICE"]
        # ~19-23 invoices/month (one per shipping day), not 12 monthly aggregates
        self.assertGreater(len(invoices), 200)
        customers = {e.entity_name for e in invoices}
        self.assertGreater(len(customers), 5)


if __name__ == "__main__":
    unittest.main()
