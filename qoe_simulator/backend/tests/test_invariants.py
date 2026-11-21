"""
Test Harness for Level 0.5 Financial Physics Invariants (INV1 - INV6)
Validates double-entry equilibrium, balance sheet identity, cash flow closure,
SKU mass-balance, ASC 606 revenue recognition, and settlement bridge.
"""

import unittest
from decimal import Decimal
from app.level0_physics.invariants import (
    FinancialPhysicsEngine,
    JournalLine,
    AccountCategory,
    InvariantViolationFatalError
)


class TestFinancialPhysicsInvariants(unittest.TestCase):

    def test_inv1_balanced_transaction_passes(self):
        """INV1: Balanced $650,000 inventory supplier rebate reclassification."""
        lines = [
            JournalLine(
                account_number="1410",
                account_name="Inventory - Raw Materials",
                category=AccountCategory.CURRENT_ASSET,
                debit=Decimal("650000.0000"),
                credit=Decimal("0.0000"),
                entity_name="Fastenal Inc",
                memo="Rebate adjustment under ASC 705-20"
            ),
            JournalLine(
                account_number="5120",
                account_name="Cost of Goods Sold - Materials",
                category=AccountCategory.COGS,
                debit=Decimal("0.0000"),
                credit=Decimal("650000.0000"),
                entity_name="Fastenal Inc",
                memo="Credit to COGS for volume rebate"
            )
        ]
        passed, delta = FinancialPhysicsEngine.assert_inv1_double_entry(lines)
        self.assertTrue(passed)
        self.assertEqual(delta, Decimal("0.0000"))

    def test_inv1_unbalanced_transaction_raises_fatal_error(self):
        """INV1: Unbalanced transaction (1 cent leak) must raise InvariantViolationFatalError."""
        lines = [
            JournalLine(
                account_number="1110",
                account_name="Cash",
                category=AccountCategory.CURRENT_ASSET,
                debit=Decimal("1000.0100"),
                credit=Decimal("0.0000")
            ),
            JournalLine(
                account_number="4010",
                account_name="Revenue",
                category=AccountCategory.REVENUE,
                debit=Decimal("0.0000"),
                credit=Decimal("1000.0000")
            )
        ]
        with self.assertRaises(InvariantViolationFatalError) as ctx:
            FinancialPhysicsEngine.assert_inv1_double_entry(lines)
        self.assertEqual(ctx.exception.invariant_code, "INV1_DOUBLE_ENTRY_EQUILIBRIUM")
        self.assertEqual(ctx.exception.delta, Decimal("0.0100"))

    def test_inv2_balance_sheet_equilibrium_passes(self):
        """INV2: Assets == Liabilities + Equity + Net Income."""
        assets = Decimal("15000000.0000")
        liabilities = Decimal("6000000.0000")
        equity = Decimal("7000000.0000")
        net_income = Decimal("2000000.0000")
        passed, delta = FinancialPhysicsEngine.assert_inv2_balance_sheet(
            assets, liabilities, equity, net_income
        )
        self.assertTrue(passed)
        self.assertEqual(delta, Decimal("0.0000"))

    def test_inv2_balance_sheet_rupture_fails(self):
        """INV2: Imbalance must fail."""
        assets = Decimal("15000000.0000")
        liabilities = Decimal("6000000.0000")
        equity = Decimal("7000000.0000")
        net_income = Decimal("1999999.0000")  # $1 break
        with self.assertRaises(InvariantViolationFatalError):
            FinancialPhysicsEngine.assert_inv2_balance_sheet(assets, liabilities, equity, net_income)

    def test_inv3_cash_closure_passes(self):
        """INV3: Delta Cash == CFO + CFI + CFF."""
        beg_cash = Decimal("1250000.0000")
        end_cash = Decimal("2450000.0000")  # +$1,200,000
        cfo = Decimal("2000000.0000")
        cfi = Decimal("-500000.0000")
        cff = Decimal("-300000.0000")
        passed, delta = FinancialPhysicsEngine.assert_inv3_cash_closure(
            beg_cash, end_cash, cfo, cfi, cff
        )
        self.assertTrue(passed)
        self.assertEqual(delta, Decimal("0.0000"))

    def test_inv4_sku_mass_balance_passes(self):
        """INV4: SKU units End == Beg + Received - Shipped - Scrap."""
        beg = 1000
        rec = 500
        ship = 800
        scrap = 50
        end = 650  # 1000 + 500 - 800 - 50 = 650
        passed, delta = FinancialPhysicsEngine.assert_inv4_sku_mass_balance(beg, end, rec, ship, scrap)
        self.assertTrue(passed)
        self.assertEqual(delta, 0)

    def test_inv5_asc606_revenue_waterfall_passes(self):
        """INV5: Invoiced == Recognized + Deferred."""
        invoiced = Decimal("1200000.0000")
        recognized = Decimal("900000.0000")
        deferred = Decimal("300000.0000")
        passed, delta = FinancialPhysicsEngine.assert_inv5_asc606_revenue_waterfall(
            invoiced, recognized, deferred
        )
        self.assertTrue(passed)
        self.assertEqual(delta, Decimal("0.0000"))

    def test_inv6_settlement_equilibrium_passes(self):
        """INV6: Chicago Bridge & Iron purchase price settlement bridge."""
        ev = Decimal("60000000.0000")
        closing_debt = Decimal("12000000.0000")
        closing_nwc = Decimal("8500000.0000")
        nwc_peg = Decimal("8000000.0000")  # +$500k true-up to seller
        # Expected = 60M - 12M + (8.5M - 8.0M) = 48.5M
        closing_cash = Decimal("48500000.0000")
        passed, delta = FinancialPhysicsEngine.assert_inv6_settlement_equilibrium(
            closing_cash, ev, closing_debt, closing_nwc, nwc_peg
        )
        self.assertTrue(passed)
        self.assertEqual(delta, Decimal("0.0000"))


if __name__ == "__main__":
    unittest.main()
