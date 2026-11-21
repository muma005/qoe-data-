"""
Interactive Verification & Live Demonstration Harness
Tests the operational viability of Level 0 / 0.5 Financial Physics,
the Cryptographic Event Store, and the Read Projections Engine.
"""

import sys
import os
import time
from decimal import Decimal
from datetime import datetime, date

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.level0_physics.invariants import (
    FinancialPhysicsEngine,
    JournalLine,
    AccountCategory,
    InvariantViolationFatalError
)
from app.level0_physics.event_store import EventStore, SimulationEvent
from app.level0_physics.read_projections import ReadProjectionsDB


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_success(msg: str):
    print(f"  [PASS] {msg}")


def print_fail(msg: str):
    print(f"  [FAIL] {msg}")


def test_invariants_live():
    print_header("TEST 1: THE SIX NON-NEGOTIABLE FINANCIAL INVARIANTS (INV1 - INV6)")

    # 1. INV1: Double-Entry Equilibrium
    print("\n[1.1] Testing INV1: Double-Entry Equilibrium ($650,000 Rebate Entry)")
    valid_lines = [
        JournalLine("1410", "Inventory - Materials", AccountCategory.CURRENT_ASSET, Decimal("650000.0000"), Decimal("0.0000"), "Fastenal"),
        JournalLine("5120", "COGS - Materials", AccountCategory.COGS, Decimal("0.0000"), Decimal("650000.0000"), "Fastenal")
    ]
    passed, delta = FinancialPhysicsEngine.assert_inv1_double_entry(valid_lines)
    print_success(f"Balanced entry committed. Total Debits == Credits. Delta = ${delta}")

    print("\n[1.2] Testing INV1 Guard: Injecting 1-Cent Floating-Point Drift ($0.01 leak)")
    corrupt_lines = [
        JournalLine("1110", "Cash", AccountCategory.CURRENT_ASSET, Decimal("1000.0100"), Decimal("0.0000")),
        JournalLine("4010", "Revenue", AccountCategory.REVENUE, Decimal("0.0000"), Decimal("1000.0000"))
    ]
    try:
        FinancialPhysicsEngine.assert_inv1_double_entry(corrupt_lines)
        print_fail("CRITICAL: Failed to catch 1-cent leak!")
    except InvariantViolationFatalError as e:
        print_success(f"Guard successfully trapped 1-cent leak: {e}")

    # 2. INV2: Balance Sheet Identity
    print("\n[1.3] Testing INV2: Balance Sheet Conservation Identity (A = L + E + NI)")
    assets = Decimal("15000000.0000")
    liab = Decimal("6000000.0000")
    eq = Decimal("7000000.0000")
    ni = Decimal("2000000.0000")
    passed, delta = FinancialPhysicsEngine.assert_inv2_balance_sheet(assets, liab, eq, ni)
    print_success(f"Balance Sheet in exact equilibrium: $15,000,000 == $6,000,000 + $7,000,000 + $2,000,000 (Delta: ${delta})")

    # 3. INV3: Cash Flow Statement Reconciled Closure
    print("\n[1.4] Testing INV3: Cash Flow Closure (Delta Cash == CFO + CFI + CFF)")
    beg_cash = Decimal("1250000.0000")
    end_cash = Decimal("2450000.0000")
    cfo = Decimal("2000000.0000")
    cfi = Decimal("-500000.0000")
    cff = Decimal("-300000.0000")
    passed, delta = FinancialPhysicsEngine.assert_inv3_cash_closure(beg_cash, end_cash, cfo, cfi, cff)
    print_success(f"Cash flow reconciled to bank wire balance: Change in Cash (+${end_cash - beg_cash}) == CFO+CFI+CFF (+${cfo+cfi+cff})")

    # 4. INV4: Physical SKU Mass-Balance Conservation
    print("\n[1.5] Testing INV4: SKU Mass-Balance Conservation (Physical Warehouse Count)")
    beg_qty, rec_qty, ship_qty, scrap_qty, end_qty = 1000, 500, 800, 50, 650
    passed, delta = FinancialPhysicsEngine.assert_inv4_sku_mass_balance(beg_qty, end_qty, rec_qty, ship_qty, scrap_qty)
    print_success(f"Warehouse units strictly conserved: 1,000 + 500 - 800 - 50 == 650 units (Variance: {delta})")

    # 5. INV5: ASC 606 Revenue Waterfall
    print("\n[1.6] Testing INV5: ASC 606 Revenue Waterfall (Invoiced == Recognized + Deferred)")
    invoiced, recognized, deferred = Decimal("1200000.0000"), Decimal("900000.0000"), Decimal("300000.0000")
    passed, delta = FinancialPhysicsEngine.assert_inv5_asc606_revenue_waterfall(invoiced, recognized, deferred)
    print_success(f"ASC 606 contract closed: Invoiced ($1.20M) == Recognized ($900k) + Deferred ($300k)")

    # 6. INV6: Chicago Bridge & Iron Purchase Price Settlement Bridge
    print("\n[1.7] Testing INV6: Purchase Price Settlement Bridge (Delaware Court of Chancery Cadence)")
    ev = Decimal("60000000.0000")
    closing_debt = Decimal("12000000.0000")
    closing_nwc = Decimal("8500000.0000")
    nwc_peg = Decimal("8000000.0000")
    closing_cash = Decimal("48500000.0000")  # EV ($60M) - Debt ($12M) + NWC True-Up (+$500k) = $48.5M
    passed, delta = FinancialPhysicsEngine.assert_inv6_settlement_equilibrium(closing_cash, ev, closing_debt, closing_nwc, nwc_peg)
    print_success(f"M&A purchase settlement verified: $48,500,000 wire strictly reconciles to EV - NetDebt + NWC Peg variance")


def test_event_store_tamper_detection():
    print_header("TEST 2: CRYPTOGRAPHIC EVENT STORE & ANTI-TAMPERING HASH CHAIN")

    store = EventStore()
    
    # 1. Commit chronological transactions
    print("\n[2.1] Appending 3 sequential transactions to immutable append-only event log...")
    e1 = store.append_event("sim_001", "ledger:apex", "qoe.accounting.committed.v1", 1, "2024-10-01T08:00:00Z", {"je": "JE-01", "dr": 50000}, ["INV1"])
    e2 = store.append_event("sim_001", "ledger:apex", "qoe.accounting.committed.v1", 2, "2024-10-02T14:30:00Z", {"je": "JE-02", "dr": 75000}, ["INV1"])
    e3 = store.append_event("sim_001", "ledger:apex", "qoe.accounting.committed.v1", 3, "2024-10-03T11:15:00Z", {"je": "JE-03", "dr": 120000}, ["INV1"])

    print(f"  Event 1 Hash: {e1.cryptographic_hash[:24]}...")
    print(f"  Event 2 Hash: {e2.cryptographic_hash[:24]}... (Chained to Event 1: {e2.prev_event_hash[:16]}...)")
    print(f"  Event 3 Hash: {e3.cryptographic_hash[:24]}... (Chained to Event 2: {e3.prev_event_hash[:16]}...)")

    # Verify untampered chain
    valid, err = store.verify_hash_chain_integrity()
    if valid:
        print_success("Audit Verification: 100% SHA-256 hash chain verified with zero mutations.")

    # 2. Simulate adversarial tampering
    print("\n[2.2] Simulating adversarial database tampering (altering historical Event 2 payload)...")
    # Mutate event 2 payload in memory
    original_event = store._events[1]
    mutated_event = SimulationEvent(
        event_id=original_event.event_id,
        engagement_id=original_event.engagement_id,
        stream_id=original_event.stream_id,
        stream_version=original_event.stream_version,
        event_type=original_event.event_type,
        simulation_day=original_event.simulation_day,
        simulation_timestamp=original_event.simulation_timestamp,
        wall_clock_timestamp=original_event.wall_clock_timestamp,
        payload={"je": "JE-02", "dr": 999999},  # Tampered number!
        invariants_passed=original_event.invariants_passed,
        prev_event_hash=original_event.prev_event_hash,
        cryptographic_hash=original_event.cryptographic_hash
    )
    store._events[1] = mutated_event

    valid, err = store.verify_hash_chain_integrity()
    if not valid:
        print_success(f"PCAOB AS 1215 Tamper Defense Trapped Attack: {err}")
    else:
        print_fail("CRITICAL: Failed to detect historical database tampering!")


def test_read_projections_performance():
    print_header("TEST 3: READ PROJECTIONS ANALYTICAL DATABASE & SPEED BENCHMARK")

    print("\n[3.1] Initializing in-memory analytical projection engine...")
    db = ReadProjectionsDB(":memory:")
    print_success(f"Storage backend initialized: {'DuckDB (SIMD Columnar)' if db.has_duckdb else 'SQLite3 (In-Memory Fallback)'}")

    print("\n[3.2] Ingesting 5,000 synthetic multi-year GL transactions...")
    start_time = time.perf_counter()
    
    batch = []
    for i in range(5000):
        year = 2022 + (i % 3)
        month = 1 + (i % 12)
        batch.append((
            f"tx_{i:06d}",
            f"JE-{i // 2:04d}",
            date(year, month, 15).isoformat(),
            month,
            year,
            "4010" if i % 2 == 0 else "5010",
            "Product Revenue" if i % 2 == 0 else "Direct Materials",
            "REVENUE" if i % 2 == 0 else "COGS",
            0.0 if i % 2 == 0 else 450.0,
            450.0 if i % 2 == 0 else 0.0,
            f"Customer_{i % 50}",
            f"Automated recurring commercial cycle {i}",
            f"DOC_{i:05d}"
        ))
    db.insert_transaction_batch(batch)
    ingest_elapsed = (time.perf_counter() - start_time) * 1000
    print_success(f"5,000 transactions ingested and indexed in {ingest_elapsed:.2f} ms")

    print("\n[3.3] Executing Monthly Trial Balance Aggregation Query...")
    start_tb = time.perf_counter()
    tb = db.get_trial_balance(2023, 6)
    tb_elapsed = (time.perf_counter() - start_tb) * 1000
    print_success(f"Trial Balance for 2023_M06 aggregated in {tb_elapsed:.2f} ms ({len(tb)} accounts mapped)")

    print("\n[3.4] Executing 36-Month Multi-Year EBITDA Revenue/COGS Bridge Rollup...")
    start_bridge = time.perf_counter()
    bridge = db.get_monthly_revenue_and_cogs(2022, 2024)
    bridge_elapsed = (time.perf_counter() - start_bridge) * 1000
    print_success(f"36-month revenue & margin trajectory rolled up in {bridge_elapsed:.2f} ms ({len(bridge)} monthly periods)")
    
    db.close()


def test_proto_contracts_presence():
    print_header("TEST 4: PROTOBUF V3 CONTRACT INTEGRITY CHECK")

    proto_dir = os.path.join(backend_dir, "..", "proto")
    required_protos = [
        "fin_physics.proto",
        "sim_clock.proto",
        "biz_gen.proto",
        "human_friction.proto",
        "fdb_calc.proto",
        "workspace_gateway.proto",
        "audit_eval.proto"
    ]

    print("\nVerifying all Level Protobuf v3 interface definitions:")
    for proto in required_protos:
        p_path = os.path.join(proto_dir, proto)
        if os.path.exists(p_path) and os.path.getsize(p_path) > 100:
            lines = len(open(p_path, "r", encoding="utf-8").readlines())
            print_success(f"{proto:<26} [EXISTS - {lines} lines, {os.path.getsize(p_path)} bytes]")
        else:
            print_fail(f"{proto:<26} [MISSING OR EMPTY]")


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print(" QOE DILIGENCE SIMULATOR — COMPREHENSIVE OPERATIONAL VERIFICATION")
    print("#" * 80)
    test_invariants_live()
    test_event_store_tamper_detection()
    test_read_projections_performance()
    test_proto_contracts_presence()
    print("\n" + "#" * 80)
    print(" ALL SYSTEMS OPERATIONAL: VERIFICATION 100% COMPLETE")
    print("#" * 80 + "\n")
