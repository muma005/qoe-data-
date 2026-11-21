"""
QoE Simulator - Level 2 Offline Scenario Compiler (`build_scenario.py`).

Orchestrates the Level 2 (`biz-gen`) pipeline end-to-end and seals the output
into a Canonical Scenario Package (`.csp`), per 02_business_reality_and_multi_erp_data_engine.md:

    Scenario JSON -> Module 10 Volatility Engine -> Tri-Sector Simulators
                  -> Double-Entry Core -> Level 0.5 Invariant Gate
                  -> Multi-ERP Exporters -> Degradation Engine -> .csp + SHA-256

Invoked by the GitHub Actions workflow `generate_scenario.yml`:

    python scenarios/compiler/build_scenario.py \
        --scenario target_apex_supply --years 10 --seed 0x4a9f82c1e703bd55 --output-dir ./dist

All output is deterministic for a given (scenario, years, seed).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tarfile
from dataclasses import dataclass
from typing import Dict, List

# ---------------------------------------------------------------------------
# Path bootstrap (backend invariant gate + projections; macro_volatility & sector_models siblings)
# ---------------------------------------------------------------------------
_COMPILER_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_COMPILER_DIR))
_BACKEND = os.path.join(_ROOT, "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)
if _COMPILER_DIR not in sys.path:
    sys.path.insert(0, _COMPILER_DIR)

from app.level0_physics.read_projections import ReadProjectionsDB  # noqa: E402
from macro_volatility import (  # noqa: E402
    IndustrySector,
    MacroArchetype,
    OperationalTrajectoryPayload,
    VolatilityEngine,
    VolatilityScenarioConfig,
)
from sector_models import (  # noqa: E402
    AccountingCore,
    DegradationEngine,
    ERPExporter,
    build_simulator,
)

# ---------------------------------------------------------------------------
# Scenario registry: maps workflow scenario IDs to Level 2 compilation configs
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ScenarioProfile:
    scenario_id: str
    company_name: str
    sector: IndustrySector
    naics: str
    target_erp: str
    anomaly_ids: List[str]
    base_annual_revenue: float
    base_gross_margin: float
    base_ebit_margin: float
    macro_archetype: MacroArchetype


SCENARIO_PROFILES: Dict[str, ScenarioProfile] = {
    "target_apex_supply": ScenarioProfile(
        scenario_id="target_apex_supply",
        company_name="Target Apex Supply Co.",
        sector=IndustrySector.SECTOR_WHOLESALE_DISTRIBUTION,
        naics="4238",
        target_erp=ERPExporter.ERP_NETSUITE,
        anomaly_ids=["SR-B01"],
        base_annual_revenue=52_000_000.00,
        base_gross_margin=0.26,
        base_ebit_margin=0.075,
        macro_archetype=MacroArchetype.MACRO_INDUSTRIAL_DESTOCK_2023,
    ),
    "titan_precision_machining": ScenarioProfile(
        scenario_id="titan_precision_machining",
        company_name="Titan Precision Machining Inc.",
        sector=IndustrySector.SECTOR_PRECISION_MANUFACTURING,
        naics="3327",
        target_erp=ERPExporter.ERP_SAP_S4HANA,
        anomaly_ids=["SR-B06"],
        base_annual_revenue=58_000_000.00,
        base_gross_margin=0.30,
        base_ebit_margin=0.10,
        macro_archetype=MacroArchetype.MACRO_GREAT_RECESSION_2008,
    ),
    "cloudpulse_saas": ScenarioProfile(
        scenario_id="cloudpulse_saas",
        company_name="CloudScale SaaS Inc.",
        sector=IndustrySector.SECTOR_B2B_ENTERPRISE_SAAS,
        naics="5112",
        target_erp=ERPExporter.ERP_DYNAMICS365,
        anomaly_ids=["SR-B14"],
        base_annual_revenue=48_000_000.00,
        base_gross_margin=0.72,
        base_ebit_margin=0.15,
        macro_archetype=MacroArchetype.MACRO_COVID_SHOCK_2020,
    ),
}


def parse_seed(value: str) -> int:
    """Parse a seed that may be hex (with/without 0x) or decimal."""
    s = value.strip()
    try:
        if s.lower().startswith("0x"):
            return int(s, 16)
        if all(c in "0123456789abcdefABCDEF" for c in s):
            return int(s, 16)
        return int(s, 10)
    except ValueError:
        return int(s, 16)


def trajectory_to_dict(payload: OperationalTrajectoryPayload) -> dict:
    """Serialize the Module 10 trajectory to a JSON-safe dict (monthly summaries)."""
    months = []
    for t in payload.monthly_trajectories:
        months.append({
            "month_index": t.month_index,
            "calendar_year": t.calendar_year,
            "calendar_month": t.calendar_month,
            "billable_shipping_days": t.billable_shipping_days,
            "calendar_multiplier": t.calendar_multiplier,
            "macro_demand_factor": t.macro_demand_factor,
            "raw_material_price_index": t.raw_material_price_index,
            "customer_selling_price_index": t.customer_selling_price_index,
            "opex_stickiness_beta": t.opex_stickiness_beta,
            "expected_dio": t.expected_dio,
            "asc330_eo_reserve_rate": t.asc330_eo_reserve_rate,
            "revenue_runrate": t.revenue_runrate,
            "cogs_runrate": t.cogs_runrate,
            "gross_margin": t.gross_margin,
            "opex_runrate": t.opex_runrate,
            "ebitda_runrate": t.ebitda_runrate,
            "active_shocks": [
                {
                    "shock_type": s.shock_type,
                    "description": s.description,
                    "revenue_impact_pct": s.revenue_impact_pct,
                    "cost_impact_pct": s.cost_impact_pct,
                    "discrete_cash_charge": s.discrete_cash_charge,
                    "recovery_lag_months": s.recovery_lag_months,
                }
                for s in t.active_shocks
            ],
        })
    return {
        "scenario_id": payload.scenario_id,
        "seed": payload.seed,
        "monthly_trajectories": months,
    }


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: str, obj: object) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def compile_scenario(profile: ScenarioProfile, years: int, seed: int, output_dir: str) -> dict:
    """Run the full Level 2 pipeline and seal a .csp package."""

    simulation_months = years * 12
    pkg_dir = os.path.join(output_dir, profile.scenario_id)
    vdr_dir = os.path.join(pkg_dir, "vdr_artifacts")
    erp_dir = os.path.join(vdr_dir, "erp_exports")
    os.makedirs(erp_dir, exist_ok=True)

    # --- Stage 1.5: Module 10 Volatility & Cyclicality Engine -----------------
    vol_config = VolatilityScenarioConfig(
        scenario_id=profile.scenario_id,
        seed=seed,
        sector=profile.sector,
        macro_archetype=profile.macro_archetype,
        simulation_months=simulation_months,
        base_annual_revenue=profile.base_annual_revenue,
        base_gross_margin=profile.base_gross_margin,
        base_ebit_margin=profile.base_ebit_margin,
        enable_window_dressing=False,
        start_year=2021,
        start_month=1,
    )
    trajectory = VolatilityEngine().generate_trajectory(vol_config)

    # --- Stage 2-3: Tri-Sector Simulators + Double-Entry Core -----------------
    core = AccountingCore(profile.scenario_id, seed, profile.base_annual_revenue,
                          start_year=2021, start_month=1)
    simulator = build_simulator(core, profile.sector, profile.anomaly_ids)
    for idx, traj in enumerate(trajectory.monthly_trajectories, start=1):
        simulator.simulate_month(traj, idx)

    # --- Stage 4: Level 0.5 Invariant Gate ------------------------------------
    # INV1 is gated per-entry inside core.post(); INV4/INV5 gated in the simulators.
    # Assert global INV2 (balance sheet conservation) and global double-entry.
    total_debits = core.total_debits()
    total_credits = core.total_credits()
    if total_debits != total_credits:
        raise SystemExit(f"FATAL: Global INV1 violation: debits {total_debits} != credits {total_credits}")
    core.assert_inv2_balance_sheet()

    # --- Stage 5: Materialize ground_truth.duckdb -----------------------------
    ledger_path = os.path.join(pkg_dir, "ground_truth.duckdb")
    db = ReadProjectionsDB(ledger_path)
    rows = []
    for entry in core.entries:
        for i, line in enumerate(entry.lines):
            rows.append((
                f"{entry.entry_id}-{i:03d}",
                entry.entry_id,
                entry.entry_date,
                entry.sim_month,
                entry.sim_year,
                line.account_number,
                line.account_name,
                line.category.value,
                float(line.debit),
                float(line.credit),
                entry.entity_name,
                entry.memo,
                entry.document_ref,
            ))
    db.insert_transaction_batch(rows)
    db.close()

    # --- Stage 6: ERP exports + documentary degradation -----------------------
    erp_exporter_map = {
        ERPExporter.ERP_NETSUITE: "netsuite_gl.csv",
        ERPExporter.ERP_SAP_S4HANA: "sap_acdoca.txt",
        ERPExporter.ERP_QUICKBOOKS: "quickbooks.iif",
        ERPExporter.ERP_DYNAMICS365: "dynamics365.csv",
    }
    primary_erp_text = ERPExporter.export(profile.target_erp, core.entries)
    with open(os.path.join(erp_dir, erp_exporter_map[profile.target_erp]), "w", encoding="utf-8") as f:
        f.write(primary_erp_text)

    degradation = DegradationEngine(seed)
    wc_schedule, _ = degradation.render_working_capital_schedule(core)
    ar_schedule, _ = degradation.render_aged_ar_schedule(core)
    with open(os.path.join(vdr_dir, "working_capital_schedule.csv"), "w", encoding="utf-8") as f:
        f.write(wc_schedule)
    with open(os.path.join(vdr_dir, "aged_ar_schedule.csv"), "w", encoding="utf-8") as f:
        f.write(ar_schedule)

    # --- Provenance hierarchy + missing records ------------------------------
    canonical_documents = {
        "provenance_hierarchy": ["T1", "T2", "T3", "T4", "T5", "T6", "T7"],
        "artifacts": [
            {"tier": "T3", "path": f"erp_exports/{erp_exporter_map[profile.target_erp]}", "type": "ERP_GL_EXPORT"},
            {"tier": "T5", "path": "working_capital_schedule.csv", "type": "MANAGEMENT_EXCEL"},
            {"tier": "T5", "path": "aged_ar_schedule.csv", "type": "MANAGEMENT_EXCEL"},
        ],
        "missing_records": degradation.missing_records(),
        "defects": degradation.defects,
    }

    # --- Manifest + solution key ---------------------------------------------
    manifest = {
        "scenario_id": profile.scenario_id,
        "company_name": profile.company_name,
        "sector_naics": profile.naics,
        "random_seed": seed,
        "historical_months": simulation_months,
        "target_erp": profile.target_erp,
        "total_journal_entries": len(core.entries),
        "total_gl_lines": sum(len(e.lines) for e in core.entries),
        "active_anomaly_ids": profile.anomaly_ids,
    }

    injected_anomalies = {
        "scenario_id": profile.scenario_id,
        "anomalies": core.anomalies,
        "evaluation_notes": "Ground truth ledger reflects the target's as-booked records; anomalies document mis-classifications requiring EBITDA adjustment.",
    }

    # --- Write deterministic artifacts ---------------------------------------
    write_json(os.path.join(pkg_dir, "manifest.json"), manifest)
    write_json(os.path.join(pkg_dir, "operational_trajectory.json"), trajectory_to_dict(trajectory))
    write_json(os.path.join(pkg_dir, "injected_anomalies.json"), injected_anomalies)
    write_json(os.path.join(vdr_dir, "canonical_documents.json"), canonical_documents)

    # --- SHA-256 checksum over deterministic data artifacts ------------------
    checksum_lines = []
    for rel in ("ground_truth.duckdb", "manifest.json", "operational_trajectory.json", "injected_anomalies.json"):
        p = os.path.join(pkg_dir, rel)
        checksum_lines.append(f"{sha256_file(p)}  {rel}")
    checksum_path = os.path.join(pkg_dir, "checksum.sha256")
    with open(checksum_path, "w", encoding="utf-8") as f:
        f.write("\n".join(checksum_lines) + "\n")

    # --- Seal .csp as a tarball ----------------------------------------------
    tar_path = os.path.join(output_dir, f"{profile.scenario_id}_package.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(pkg_dir, arcname=profile.scenario_id)

    return {
        "package_dir": pkg_dir,
        "tar_path": tar_path,
        "checksum_path": checksum_path,
        "total_journal_entries": len(core.entries),
        "total_gl_lines": len(rows),
        "invariant_check_passed": True,
        "net_income": str(core.net_income()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a Level 2 QoE scenario package (.csp)")
    parser.add_argument("--scenario", required=True, help="Scenario ID (target_apex_supply | titan_precision_machining | cloudpulse_saas)")
    parser.add_argument("--years", type=int, default=10, help="Years of history (3, 5, or 10)")
    parser.add_argument("--seed", default="0x4a9f82c1e703bd55", help="Deterministic master seed (hex or decimal)")
    parser.add_argument("--output-dir", default="./dist", help="Output directory for the sealed package")
    args = parser.parse_args()

    if args.scenario not in SCENARIO_PROFILES:
        raise SystemExit(f"Unknown scenario '{args.scenario}'. Valid: {sorted(SCENARIO_PROFILES)}")

    seed = parse_seed(args.seed)
    profile = SCENARIO_PROFILES[args.scenario]
    result = compile_scenario(profile, args.years, seed, args.output_dir)

    print(f"Scenario package compiled: {result['package_dir']}")
    print(f"  Journal entries : {result['total_journal_entries']}")
    print(f"  GL lines        : {result['total_gl_lines']}")
    print(f"  Net income      : ${result['net_income']}")
    print(f"  Invariants      : INV1 (per-entry) + INV2 (balance sheet) PASS")
    print(f"  Checksum        : {result['checksum_path']}")
    print(f"  Package         : {result['tar_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
