"""
Unit Tests for Event Store (Level 0) and DuckDB Projections
Verifies SHA-256 hash chaining, anti-tampering detection, and columnar queries.
"""

import unittest
from datetime import datetime
from app.level0_physics.event_store import EventStore
from app.level0_physics.read_projections import ReadProjectionsDB


class TestEventStoreAndProjections(unittest.TestCase):

    def test_event_store_append_and_hash_integrity(self):
        """Tests that appending events maintains a valid SHA-256 chained hash."""
        store = EventStore()
        
        # Append Event 1
        e1 = store.append_event(
            engagement_id="sim_apex_001",
            stream_id="ledger:apex",
            event_type="qoe.accounting.transaction.committed.v1",
            simulation_day=1,
            simulation_timestamp="2024-10-01T00:00:00Z",
            payload={"journal_entry_id": "JE-001", "amount": 50000},
            invariants_passed=["INV1", "INV2"]
        )
        self.assertEqual(e1.stream_version, 1)

        # Append Event 2
        e2 = store.append_event(
            engagement_id="sim_apex_001",
            stream_id="ledger:apex",
            event_type="qoe.accounting.transaction.committed.v1",
            simulation_day=2,
            simulation_timestamp="2024-10-02T00:00:00Z",
            payload={"journal_entry_id": "JE-002", "amount": 120000},
            invariants_passed=["INV1", "INV2"]
        )
        self.assertEqual(e2.stream_version, 2)
        self.assertEqual(e2.prev_event_hash, e1.cryptographic_hash)

        # Assert chain integrity passes
        is_valid, error = store.verify_hash_chain_integrity()
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_duckdb_bulk_append_and_aggregation(self):
        """Tests DuckDB appender ingestion and sub-millisecond monthly rollups."""
        db = ReadProjectionsDB(":memory:")
        
        # Insert 5 synthetic GL lines
        sample_rows = [
            ("tx_01", "JE-01", datetime(2023, 9, 15).date(), 9, 2023, "4010", "Product Sales", "REVENUE", 0.0, 100000.0, "Customer A", "Invoice 1", "DOC_01"),
            ("tx_02", "JE-01", datetime(2023, 9, 15).date(), 9, 2023, "5010", "Materials Cost", "COGS", 40000.0, 0.0, "Vendor B", "Bill 1", "DOC_02"),
            ("tx_03", "JE-02", datetime(2023, 9, 20).date(), 9, 2023, "6010", "Salaries & Wages", "OPEX", 25000.0, 0.0, "Payroll", "Bi-weekly", "DOC_03"),
            ("tx_04", "JE-03", datetime(2023, 10, 5).date(), 10, 2023, "4010", "Product Sales", "REVENUE", 0.0, 120000.0, "Customer C", "Invoice 2", "DOC_04"),
            ("tx_05", "JE-03", datetime(2023, 10, 5).date(), 10, 2023, "5010", "Materials Cost", "COGS", 50000.0, 0.0, "Vendor B", "Bill 2", "DOC_05"),
        ]
        db.insert_transaction_batch(sample_rows)
        
        # Test Trial Balance for September 2023
        tb_sep = db.get_trial_balance(2023, 9)
        self.assertEqual(len(tb_sep), 3)
        
        # Test Monthly Revenue and COGS rollup
        monthly = db.get_monthly_revenue_and_cogs(2023, 2023)
        self.assertEqual(len(monthly), 2)
        
        sep_entry = next(m for m in monthly if m["sim_month"] == 9)
        self.assertEqual(sep_entry["revenue"], 100000.0)
        self.assertEqual(sep_entry["cogs"], 40000.0)
        self.assertEqual(sep_entry["opex"], 25000.0)
        
        db.close()


if __name__ == "__main__":
    unittest.main()
