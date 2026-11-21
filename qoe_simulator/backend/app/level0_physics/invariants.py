"""
Financial Physics Invariant Engine (Level 0.5)
Enforces the Six Non-Negotiable Conservation Laws of Financial Reality.
Floating-point arithmetic is strictly prohibited; all currency calculations
use 64-bit/128-bit fixed-point Decimal representation with $0.0000 tolerance.
"""

from decimal import Decimal, ROUND_HALF_EVEN
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class InvariantViolationFatalError(Exception):
    """Thrown when an accounting transaction violates physical conservation laws."""
    def __init__(self, invariant_code: str, message: str, delta: Decimal):
        super().__init__(f"[{invariant_code}] FATAL INVARIANT VIOLATION: {message} (Delta: {delta})")
        self.invariant_code = invariant_code
        self.delta = delta


class AccountCategory(Enum):
    REVENUE = "REVENUE"
    COGS = "COGS"
    OPEX = "OPEX"
    CURRENT_ASSET = "CURRENT_ASSET"
    NON_CURRENT_ASSET = "NON_CURRENT_ASSET"
    CURRENT_LIABILITY = "CURRENT_LIABILITY"
    NON_CURRENT_LIABILITY = "NON_CURRENT_LIABILITY"
    EQUITY = "EQUITY"


@dataclass(frozen=True)
class JournalLine:
    account_number: str
    account_name: str
    category: AccountCategory
    debit: Decimal
    credit: Decimal
    entity_name: str = ""
    memo: str = ""
    document_ref: str = ""

    def __post_init__(self):
        if self.debit < Decimal("0.0000") or self.credit < Decimal("0.0000"):
            raise ValueError("Debits and credits must be non-negative fixed-point numbers.")
        if self.debit > Decimal("0.0000") and self.credit > Decimal("0.0000"):
            raise ValueError("A single journal line cannot contain both a debit and a credit.")


class FinancialPhysicsEngine:
    """Enforces absolute mathematical conservation before commits."""
    
    ZERO = Decimal("0.0000")
    TOLERANCE = Decimal("0.0000")  # Exact equilibrium required

    @classmethod
    def assert_inv1_double_entry(cls, lines: List[JournalLine]) -> Tuple[bool, Decimal]:
        """
        INV1: Double-Entry Equilibrium Invariant
        Sum(Debits) - Sum(Credits) == 0.0000
        """
        total_debits = sum((line.debit for line in lines), cls.ZERO)
        total_credits = sum((line.credit for line in lines), cls.ZERO)
        delta = (total_debits - total_credits).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        
        if delta != cls.ZERO:
            raise InvariantViolationFatalError(
                "INV1_DOUBLE_ENTRY_EQUILIBRIUM",
                f"Transaction debits ({total_debits}) do not equal credits ({total_credits}).",
                delta
            )
        return True, delta

    @classmethod
    def assert_inv2_balance_sheet(
        cls,
        total_assets: Decimal,
        total_liabilities: Decimal,
        total_equity: Decimal,
        cumulative_net_income: Decimal
    ) -> Tuple[bool, Decimal]:
        """
        INV2: Balance Sheet Conservation Identity
        Assets == Liabilities + Equity + CumulativeNetIncome
        """
        rhs = (total_liabilities + total_equity + cumulative_net_income).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        assets = total_assets.quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        delta = (assets - rhs).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        
        if delta != cls.ZERO:
            raise InvariantViolationFatalError(
                "INV2_BALANCE_SHEET_CONSERVATION",
                f"Assets ({assets}) != Liab + Equity + NetIncome ({rhs}).",
                delta
            )
        return True, delta

    @classmethod
    def assert_inv3_cash_closure(
        cls,
        beg_cash: Decimal,
        end_cash: Decimal,
        cfo: Decimal,
        cfi: Decimal,
        cff: Decimal
    ) -> Tuple[bool, Decimal]:
        """
        INV3: Cash Flow Statement Reconciled Closure
        EndCash - BegCash == CFO + CFI + CFF
        """
        delta_cash = (end_cash - beg_cash).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        total_cf = (cfo + cfi + cff).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        delta = (delta_cash - total_cf).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        
        if delta != cls.ZERO:
            raise InvariantViolationFatalError(
                "INV3_CASH_CLOSURE_MISMATCH",
                f"Delta Cash ({delta_cash}) != Operating + Investing + Financing ({total_cf}).",
                delta
            )
        return True, delta

    @classmethod
    def assert_inv4_sku_mass_balance(
        cls,
        beg_qty: int,
        end_qty: int,
        received_qty: int,
        shipped_qty: int,
        scrap_qty: int
    ) -> Tuple[bool, int]:
        """
        INV4: Physical SKU Mass-Balance Conservation
        EndQty == BegQty + ReceivedQty - ShippedQty - ScrapQty
        """
        calculated_end = beg_qty + received_qty - shipped_qty - scrap_qty
        delta = end_qty - calculated_end
        
        if delta != 0:
            raise InvariantViolationFatalError(
                "INV4_SKU_MASS_BALANCE_MISMATCH",
                f"Physical SKU EndQty ({end_qty}) != Calculated ({calculated_end}).",
                Decimal(str(delta))
            )
        return True, delta

    @classmethod
    def assert_inv5_asc606_revenue_waterfall(
        cls,
        total_invoiced_contract_value: Decimal,
        cumulative_recognized_revenue: Decimal,
        ending_deferred_revenue: Decimal
    ) -> Tuple[bool, Decimal]:
        """
        INV5: ASC 606 Contract Revenue Waterfall Closure
        TotalInvoiced == RecognizedRevenue + DeferredRevenue
        """
        invoiced = total_invoiced_contract_value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        accounted = (cumulative_recognized_revenue + ending_deferred_revenue).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        delta = (invoiced - accounted).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        
        if delta != cls.ZERO:
            raise InvariantViolationFatalError(
                "INV5_REVREC_WATERFALL_LEAK",
                f"Invoiced ({invoiced}) != Recognized ({cumulative_recognized_revenue}) + Deferred ({ending_deferred_revenue}).",
                delta
            )
        return True, delta

    @classmethod
    def assert_inv6_settlement_equilibrium(
        cls,
        closing_cash_settlement: Decimal,
        enterprise_value: Decimal,
        closing_net_debt: Decimal,
        closing_nwc: Decimal,
        nwc_target_peg: Decimal
    ) -> Tuple[bool, Decimal]:
        """
        INV6: Purchase Price Allocation & Settlement Equilibrium (Chicago Bridge & Iron cadence)
        Closing Cash Settlement == Enterprise Value - Closing Net Debt + (Closing NWC - NWC Target Peg)
        """
        nwc_true_up = (closing_nwc - nwc_target_peg).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        calculated_settlement = (enterprise_value - closing_net_debt + nwc_true_up).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        actual = closing_cash_settlement.quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        delta = (actual - calculated_settlement).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN)
        
        if delta != cls.ZERO:
            raise InvariantViolationFatalError(
                "INV6_SETTLEMENT_ARITHMETIC_ERROR",
                f"Closing Settlement ({actual}) != EV ({enterprise_value}) - NetDebt ({closing_net_debt}) + NWC TrueUp ({nwc_true_up}).",
                delta
            )
        return True, delta
