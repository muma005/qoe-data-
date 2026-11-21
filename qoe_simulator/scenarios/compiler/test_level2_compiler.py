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
import sys
import tempfile
import unittest

_COMPILER_DIR = os.path.dirname(os.path.abspath(__file__))
if _COMPILER_DIR not in sys.path:
    sys.path.insert(0, _COMPILER_DIR)

from build_scenario import SCENARIO_PROFILES, compile_scenario, parse_seed  # noqa: E402
from sector_models import (  # noqa: E402
    AccountingCore,
    ERPExporter,
    build_simulator,
)
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


if __name__ == "__main__":
    unittest.main()
