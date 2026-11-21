# Quality of Earnings (QoE) Diligence Simulation Platform

An institutional-grade, adversarial training and evaluation simulation environment for M&A Financial Due Diligence and Transaction Advisory Services (TAS).

Complies with **PCAOB AS 1215**, **AICPA CS Section 100**, **ICAEW Guideline 71**, and **Delaware Court of Chancery** evidentiary precedents (*Chicago Bridge & Iron*).

---

## Repository Structure & Systems Topography

```
qoe-data/
├── qoe_simulator/                           # The Core Software Simulation Platform
│   ├── proto/                               # Shared gRPC / Protobuf v3 Contracts (Levels 0–6)
│   ├── scenarios/                           # Offline Scenario Compiler & Pre-compiled Packages (.csp)
│   ├── backend/                             # Python 3.12 / FastAPI Core Execution Engines
│   │   ├── app/level0_physics/              # Level 0/0.5: Invariant Engine (INV1–INV6) & Event Store
│   │   ├── app/level1_clock/                # Level 1: DES Clock, 25-Day Timeline, DSM Rework
│   │   ├── app/level3_friction/             # Level 3: 13 Executive Personas & Wealth-Loss Pushback
│   │   ├── app/level4_databook/             # Level 4: 11-Tab Headless Spreadsheet DAG & Check Bars
│   │   └── app/level6_audit/                # Level 6: Automated AST Formula Auditor & Turing Test
│   └── frontend/                            # Level 5: React / TypeScript Three-Pane Diligence Cockpit
│
├── QOE_SYSTEMS_DESIGN/                      # Self-Contained Autonomous Level (SCAL) Specifications
│   ├── 00_systems_architecture_charter_and_topography.md
│   ├── 01_core_simulation_engine_and_temporal_state_machine.md
│   ├── 02_business_reality_and_multi_erp_data_engine.md
│   ├── 03_multi_agent_human_behavior_and_friction_engine.md
│   ├── 04_financial_databook_and_calculation_engine.md
│   ├── 05_user_workspace_and_interaction_surfaces.md
│   ├── 06_assessment_audit_and_diligence_turing_test_engine.md
│   ├── 07_master_system_integration_and_api_specification.md
│   ├── 08_engineering_specifications_fault_isolation_and_modular_independence.md
│   ├── 09_engineering_loopholes_and_forensic_risk_mitigation_register.md
│   └── 10_business_cyclicality_volatility_and_ups_and_downs_simulation_model.md
│
├── RESEARCH_CYCLICALITY_AND_VOLATILITY/     # Empirical Macro & Operational Volatility Research
│   ├── TRACK_01_MACRO_AND_INDUSTRY_CYCLES.md
│   ├── TRACK_02_OPERATING_LEVERAGE_AND_STICKY_COSTS.md
│   ├── TRACK_03_BULLWHIP_AND_WORKING_CAPITAL_WHIPLASH.md
│   ├── TRACK_04_WINDOW_DRESSING_AND_FORENSIC_CASE_LAW.md
│   ├── TRACK_05_IDIOSYNCRATIC_OPERATIONAL_SHOCKS.md
│   └── RESEARCH_SYNTHESIS_AND_PARAMETRIC_BENCHMARKS.md
│
├── QOE_REALISM_RESEARCH/                    # The 126 Realism Requirements Specification
│   ├── 09_MASTER_REALISM_SPECIFICATION/master_qoe_simulation_realism_specification.md
│   └── Modules 01 through 08
│
└── research/                                # Data Mining, Dataset Inspections & Parameter Extraction
    ├── [domain]_signals/                    # Calibrated JSON Parameter Registries (P2P, O2C, Payroll, Banking)
    └── *.py                                 # Statistical tests (Benford's Law, Chi-Square, Distribution Scans)
```

---

## Core Architectural Pillars

1. **The Six Financial Invariants (INV1–INV6):**
   Absolute conservation of financial reality enforced at the database layer with zero floating-point drift (`Decimal(18, 4)` precision).
2. **Offline Compilation Boundary:**
   Multi-year historical general ledgers and VDR documents are compiled offline and distributed via GitHub Releases (`.duckdb`), guaranteeing a 0 MB permanent disk footprint and zero database locks.
3. **Decoupled Level Autonomy (SCAL):**
   Every level natively implements its own domain bulkhead, typed `.proto` interface, and anti-cheating loophole defenses.

---

## Verification & Testing

To run the automated verification suite:
```bash
cd qoe_simulator/backend
python demo_verification.py
```
To run the full unit test suite:
```bash
python -m unittest discover tests
```
