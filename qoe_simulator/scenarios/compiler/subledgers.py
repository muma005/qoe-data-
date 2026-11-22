"""
QoE Simulator - Level 2: Five Specialized Subledger Engines.

Implements spec Section 4.1 (02_business_reality_and_multi_erp_data_engine.md):

  1. Accounts Receivable (AR) Subledger  - invoice balances, payment allocation logs,
     and aging buckets (Current, 1-30, 31-60, 61-90, 90+ days).
  2. Accounts Payable (AP) Subledger     - vendor bills, credit terms (Net 30/60/90),
     payment batch disbursements, and stretched payables > 90 days.
  3. Inventory Valuation Subledger       - FIFO / Standard Costing roll-forwards
     (Beg + In - Out = End) with ASC 330 LCNRV obsolescence reserves.
  4. Fixed Assets & Capex Subledger      - in-service dates, asset classifications,
     straight-line and MACRS depreciation schedules, CIP transfers.
  5. Deferred Revenue Subledger          - contract-level ASC 606 revenue waterfalls,
     ratable recognition, unbilled contract assets, unearned revenue liabilities.

Each engine is a post-hoc read projection of the double-entry JournalEntry stream
(the subledgers are materialized views of the GL, not a second source of truth).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Sequence, Tuple

from sector_models import CoA, JournalEntry, _money  # noqa: E402

# ---------------------------------------------------------------------------
# 1. Accounts Receivable Subledger (day-granular aging)
# ---------------------------------------------------------------------------
class ARSubledger:
    """Tracks invoice batches, payment allocation, and day-granular aging buckets."""

    AGING_BUCKETS = ("current", "1_30", "31_60", "61_90", "over_90")

    def __init__(self):
        self.invoices: List[Dict] = []   # {ord, invoice_id, customer, amount, open}
        self.payments: List[Dict] = []   # {ord, payment_id, amount}
        self.unapplied_cash = _money(0)

    @staticmethod
    def _ord(year: int, month: int, day: int) -> int:
        return date(year, month, day).toordinal()

    def record_invoice(self, year: int, month: int, day: int, invoice_id: str,
                       customer: str, amount: Decimal):
        self.invoices.append({"ord": self._ord(year, month, day), "invoice_id": invoice_id,
                              "customer": customer, "amount": _money(amount), "open": _money(amount)})

    def record_payment(self, year: int, month: int, day: int, payment_id: str, amount: Decimal):
        self.payments.append({"ord": self._ord(year, month, day), "payment_id": payment_id,
                              "amount": _money(amount)})
        self._allocate(amount)

    def _allocate(self, amount: Decimal) -> None:
        remaining = _money(amount)
        for inv in self.invoices:
            if inv["open"] <= 0:
                continue
            applied = min(inv["open"], remaining)
            inv["open"] -= applied
            remaining -= applied
            if remaining <= 0:
                break
        if remaining > 0:
            self.unapplied_cash += remaining

    def total_open(self) -> Decimal:
        return sum((i["open"] for i in self.invoices), _money(0))

    def aging(self, as_of_ordinal: int) -> Dict[str, Decimal]:
        buckets = {b: _money(0) for b in self.AGING_BUCKETS}
        for inv in self.invoices:
            if inv["open"] <= 0:
                continue
            age_days = as_of_ordinal - inv["ord"]
            if age_days <= 0:
                buckets["current"] += inv["open"]
            elif age_days <= 30:
                buckets["1_30"] += inv["open"]
            elif age_days <= 60:
                buckets["31_60"] += inv["open"]
            elif age_days <= 90:
                buckets["61_90"] += inv["open"]
            else:
                buckets["over_90"] += inv["open"]
        return buckets

    def to_dict(self) -> dict:
        latest = max((i["ord"] for i in self.invoices), default=date(2021, 1, 1).toordinal())
        return {
            "open_ar": str(self.total_open()),
            "unapplied_cash": str(self.unapplied_cash),
            "invoice_count": len(self.invoices),
            "payment_count": len(self.payments),
            "aging_buckets": {k: str(v) for k, v in self.aging(latest).items()},
        }


# ---------------------------------------------------------------------------
# 2. Accounts Payable Subledger (day-granular aging)
# ---------------------------------------------------------------------------
class APSubledger:
    """Tracks vendor bills, credit terms, and stretched payables > 90 days."""

    def __init__(self):
        self.bills: List[Dict] = []       # {ord, bill_id, vendor, amount, terms, open}
        self.payments: List[Dict] = []    # {ord, payment_id, amount}

    def record_bill(self, year: int, month: int, day: int, bill_id: str, vendor: str,
                    amount: Decimal, terms: str = "NET_30"):
        self.bills.append({"ord": date(year, month, day).toordinal(), "bill_id": bill_id,
                           "vendor": vendor, "amount": _money(amount), "terms": terms,
                           "open": _money(amount)})

    def record_payment(self, year: int, month: int, day: int, payment_id: str, amount: Decimal):
        self.payments.append({"ord": date(year, month, day).toordinal(), "payment_id": payment_id,
                              "amount": _money(amount)})
        self._allocate(amount)

    def _allocate(self, amount: Decimal) -> None:
        remaining = _money(amount)
        for bill in self.bills:
            if bill["open"] <= 0:
                continue
            applied = min(bill["open"], remaining)
            bill["open"] -= applied
            remaining -= applied
            if remaining <= 0:
                break

    def total_open(self) -> Decimal:
        return sum((b["open"] for b in self.bills), _money(0))

    def stretched_payables(self, as_of_ordinal: int, threshold_days: int = 90) -> Decimal:
        """Payables outstanding longer than `threshold_days` days (debt-like)."""
        return sum((b["open"] for b in self.bills if b["open"] > 0 and
                    as_of_ordinal - b["ord"] > threshold_days), _money(0))

    def to_dict(self) -> dict:
        latest = max((b["ord"] for b in self.bills), default=date(2021, 1, 1).toordinal())
        return {
            "open_ap": str(self.total_open()),
            "stretched_payables_gt_90d": str(self.stretched_payables(latest)),
            "bill_count": len(self.bills),
            "payment_count": len(self.payments),
        }


# ---------------------------------------------------------------------------
# 3. Inventory Valuation Subledger (FIFO / standard costing roll-forward)
# ---------------------------------------------------------------------------
class InventorySubledger:
    """Implements Beg + In - Out = End with ASC 330 LCNRV obsolescence reserves."""

    def __init__(self):
        self.beginning = _money(0)
        self.receipts: List[Dict] = []
        self.issues: List[Dict] = []
        self.reserve = _money(0)

    def record_receipt(self, month: int, year: int, amount: Decimal, units: int = 0):
        self.receipts.append({"month": month, "year": year, "amount": _money(amount), "units": units})

    def record_issue(self, month: int, year: int, amount: Decimal, units: int = 0):
        self.issues.append({"month": month, "year": year, "amount": _money(amount), "units": units})

    def record_lcnrv_reserve(self, reserve: Decimal):
        self.reserve += _money(reserve)

    def ending(self) -> Decimal:
        total_in = sum((r["amount"] for r in self.receipts), _money(0))
        total_out = sum((i["amount"] for i in self.issues), _money(0))
        return self.beginning + total_in - total_out - self.reserve

    def to_dict(self) -> dict:
        total_in = sum((r["amount"] for r in self.receipts), _money(0))
        total_out = sum((i["amount"] for i in self.issues), _money(0))
        return {
            "beginning": str(self.beginning),
            "receipts": str(total_in),
            "issues": str(total_out),
            "lc_nrv_reserve": str(self.reserve),
            "ending": str(self.ending()),
        }


# ---------------------------------------------------------------------------
# 4. Fixed Assets & Capex Subledger
# ---------------------------------------------------------------------------
class FixedAssetSubledger:
    """Straight-line and MACRS depreciation schedules + CIP transfers."""

    MACRS_3YR = (0.3333, 0.4445, 0.1481, 0.0741)
    MACRS_5YR = (0.2000, 0.3200, 0.1920, 0.1152, 0.1152, 0.0576)

    def __init__(self):
        self.assets: List[Dict] = []       # {asset_id, classification, cost, in_service_month, life_months, macrs_class}
        self.cip_assets: List[Dict] = []   # {cip_id, classification, cost}
        self.depreciation_log: List[Dict] = []  # JE-based depreciation (reconciliation)

    def add_asset(self, asset_id: str, classification: str, cost: Decimal,
                  in_service_month: int, life_months: int = 120, macrs_class: str = "5YR"):
        self.assets.append({"asset_id": asset_id, "classification": classification,
                            "cost": _money(cost), "in_service_month": in_service_month,
                            "life_months": life_months, "macrs_class": macrs_class})

    def add_cip(self, cip_id: str, classification: str, cost: Decimal):
        """Construction-in-progress: costs capitalized but not yet depreciable."""
        self.cip_assets.append({"cip_id": cip_id, "classification": classification,
                                "cost": _money(cost)})

    def transfer_cip(self, cip_id: str, in_service_month: int, life_months: int = 120,
                     macrs_class: str = "5YR") -> None:
        """Place a CIP asset in service and begin depreciating it."""
        for cip in list(self.cip_assets):
            if cip["cip_id"] == cip_id:
                self.add_asset(cip_id, cip["classification"], cip["cost"],
                               in_service_month, life_months, macrs_class)
                self.cip_assets.remove(cip)
                return
        raise ValueError(f"Unknown CIP asset {cip_id}")

    def macrs_rate(self, classification: str, year_index: int) -> Decimal:
        table = self.MACRS_5YR if classification in ("5YR", "MACHINERY") else self.MACRS_3YR
        if year_index < len(table):
            return Decimal(str(table[year_index]))
        return Decimal("0")

    def straight_line_accumulated(self, asset: Dict, as_of_month: int) -> Decimal:
        age = as_of_month - asset["in_service_month"] + 1  # inclusive months in service
        if age <= 0:
            return _money(0)
        age = min(age, asset["life_months"])
        return (_money(asset["cost"]) * Decimal(age) / Decimal(asset["life_months"])).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def macrs_accumulated(self, asset: Dict, as_of_month: int) -> Decimal:
        age_months = as_of_month - asset["in_service_month"] + 1
        if age_months <= 0:
            return _money(0)
        total = _money(0)
        months = age_months
        year_index = 0
        while months > 0:
            rate = self.macrs_rate(asset["macrs_class"], year_index)
            months_in_year = min(months, 12)
            total += _money(asset["cost"]) * rate * (Decimal(months_in_year) / Decimal(12))
            months -= 12
            year_index += 1
        return total.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def accumulated_depreciation(self, as_of_month: int, method: str = "straight_line") -> Decimal:
        if method == "macrs":
            return sum((self.macrs_accumulated(a, as_of_month) for a in self.assets), _money(0))
        return sum((self.straight_line_accumulated(a, as_of_month) for a in self.assets), _money(0))

    def record_depreciation(self, global_month: int, amount: Decimal):
        self.depreciation_log.append({"month": global_month, "amount": _money(amount)})

    def to_dict(self) -> dict:
        total_cost = sum((a["cost"] for a in self.assets), _money(0))
        latest = max((d["month"] for d in self.depreciation_log), default=0)
        sl = self.accumulated_depreciation(latest, "straight_line")
        macrs = self.accumulated_depreciation(latest, "macrs")
        je_log = sum((d["amount"] for d in self.depreciation_log), _money(0))
        return {
            "asset_count": len(self.assets),
            "cip_count": len(self.cip_assets),
            "total_cost": str(total_cost),
            "straight_line_accumulated": str(sl),
            "macrs_accumulated": str(macrs),
            "journal_depreciation": str(je_log),
            "depreciation_entries": len(self.depreciation_log),
        }


# ---------------------------------------------------------------------------
# 5. Deferred Revenue Subledger (ASC 606 waterfall)
# ---------------------------------------------------------------------------
class DeferredRevenueSubledger:
    """Contract-level ASC 606 revenue waterfalls and ratable recognition."""

    def __init__(self):
        self.contracts: List[Dict] = []   # {contract_id, invoiced, recognized, deferred}
        self.total_invoiced = _money(0)
        self.total_recognized = _money(0)
        self.unbilled_contract_assets = _money(0)

    def record_billing(self, month: int, year: int, contract_id: str, amount: Decimal):
        self.total_invoiced += _money(amount)
        self.contracts.append({"contract_id": contract_id, "month": month, "year": year,
                               "invoiced": _money(amount), "recognized": _money(0),
                               "deferred": _money(amount)})

    def record_recognition(self, month: int, year: int, amount: Decimal):
        self.total_recognized += _money(amount)
        # ratable drawdown against open contracts (FIFO)
        remaining = _money(amount)
        for c in self.contracts:
            if c["deferred"] <= 0:
                continue
            drawn = min(c["deferred"], remaining)
            c["deferred"] -= drawn
            c["recognized"] += drawn
            remaining -= drawn
            if remaining <= 0:
                break

    def ending_deferred(self) -> Decimal:
        return self.total_invoiced - self.total_recognized

    def to_dict(self) -> dict:
        return {
            "total_invoiced": str(self.total_invoiced),
            "total_recognized": str(self.total_recognized),
            "ending_deferred": str(self.ending_deferred()),
            "unbilled_contract_assets": str(self.unbilled_contract_assets),
            "contract_count": len(self.contracts),
        }


# ---------------------------------------------------------------------------
# Subledger set: post-hoc projections of the GL entry stream
# ---------------------------------------------------------------------------
class SubledgerSet:
    """Builds all five subledger views from the double-entry JournalEntry stream."""

    def __init__(self):
        self.ar = ARSubledger()
        self.ap = APSubledger()
        self.inventory = InventorySubledger()
        self.fixed_assets = FixedAssetSubledger()
        self.deferred_revenue = DeferredRevenueSubledger()

    def build(self, entries: Sequence[JournalEntry]) -> "SubledgerSet":
        for entry in entries:
            self._consume(entry)
        return self

    def _consume(self, entry: JournalEntry) -> None:
        month = entry.sim_month
        year = entry.sim_year
        day = int(entry.entry_date.split("-")[2]) if entry.entry_date else 28
        global_month = entry.sim_year * 12 + entry.sim_month  # monotonic month index
        for line in entry.lines:
            num = line.account_number
            amount = line.debit if line.debit > 0 else line.credit
            if entry.entry_type == "INVOICE" and num == CoA.TRADE_AR and line.debit > 0:
                self.ar.record_invoice(year, month, day, entry.document_ref or entry.entry_id,
                                       entry.entity_name, amount)
            elif entry.entry_type == "COLLECTION" and num == CoA.TRADE_AR and line.credit > 0:
                self.ar.record_payment(year, month, day, entry.document_ref or entry.entry_id, amount)
            elif num == CoA.UNAPPLIED_CASH_CLEARING and line.credit > 0:
                self.ar.unapplied_cash += amount
            elif (entry.entry_type in ("PURCHASE", "EXPENSE", "HOSTING_COGS")
                  and num == CoA.TRADE_AP and line.credit > 0):
                self.ap.record_bill(year, month, day, entry.document_ref or entry.entry_id,
                                    entry.entity_name, amount)
            elif entry.entry_type == "AP_PAYMENT" and num == CoA.TRADE_AP and line.debit > 0:
                self.ap.record_payment(year, month, day, entry.document_ref or entry.entry_id, amount)
            elif num in (CoA.RAW_MATERIALS, CoA.WIP, CoA.FINISHED_GOODS):
                if line.debit > 0:
                    self.inventory.record_receipt(month, year, amount)
                elif line.credit > 0:
                    self.inventory.record_issue(month, year, amount)
            elif num == CoA.INVENTORY_RESERVE and line.credit > 0:
                self.inventory.record_lcnrv_reserve(amount)
            elif num == CoA.MACHINERY and line.debit > 0:
                # Opening PP&E: register as a fixed asset in service since inception.
                self.fixed_assets.add_asset(
                    entry.document_ref or entry.entry_id, "MACHINERY", amount,
                    in_service_month=global_month, life_months=120, macrs_class="5YR")
            elif entry.entry_type in ("DEPRECIATION",) and num == CoA.ACCUM_DEPRECIATION and line.credit > 0:
                self.fixed_assets.record_depreciation(global_month, amount)
            elif entry.entry_type == "BOOKING" and num == CoA.DEFERRED_REVENUE_CURRENT and line.credit > 0:
                self.deferred_revenue.record_billing(month, year, entry.document_ref or entry.entry_id, amount)
            elif entry.entry_type == "REVENUE_RECOGNITION" and num == CoA.DEFERRED_REVENUE_CURRENT and line.debit > 0:
                self.deferred_revenue.record_recognition(month, year, amount)

    def to_dict(self) -> dict:
        return {
            "accounts_receivable": self.ar.to_dict(),
            "accounts_payable": self.ap.to_dict(),
            "inventory": self.inventory.to_dict(),
            "fixed_assets": self.fixed_assets.to_dict(),
            "deferred_revenue": self.deferred_revenue.to_dict(),
        }
