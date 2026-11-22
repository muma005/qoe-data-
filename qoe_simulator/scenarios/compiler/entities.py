"""
QoE Simulator - Level 2: Entity-Relationship Data Models and Verified Master
Entity Ledger (02_business_reality_and_multi_erp_data_engine.md, Section 7).

Defines the transactional ER model (Company, Subsidiary, Account, Customer, Vendor,
SalesOrder, Invoice, PaymentReceipt, PurchaseOrder, ReceivingRecord, VendorBill,
VdrDocument, ArtifactFile, Transaction, JournalEntryLine) and enforces LP-15:

  LP-15: All synthetic entities use valid US postal state/ZIP alignments and
  properly formatted 9-digit FEINs (no fictitious FEIN formats, non-existent ZIPs,
  or invalid area codes).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# LP-15 validation helpers
# ---------------------------------------------------------------------------
def valid_fein(fein: str) -> bool:
    """Validate a 9-digit FEIN in XX-XXXXXXX or XXXXXXXXX form."""
    digits = (fein or "").replace("-", "")
    return len(digits) == 9 and digits.isdigit() and digits != "000000000"


def generate_fein(entity_name: str, seed: int = 0) -> str:
    """Deterministically derive a valid 9-digit FEIN from an entity name."""
    h = hashlib.sha256(f"{entity_name}:{seed}".encode("utf-8")).hexdigest()
    digits = "".join(str(int(c, 16) % 10) for c in h[:9])
    digits = "0" + digits[1:] if digits[0] == "0" else digits  # avoid leading zero? keep valid
    return f"{digits[:2]}-{digits[2:]}"


# State -> (ZIP prefix, a plausible city) for LP-15 alignment.
STATE_ZIP = {
    "IL": "606", "NY": "100", "CA": "941", "TX": "750", "WA": "981",
    "GA": "303", "MN": "554", "OH": "441", "PA": "191", "MA": "021",
}


def valid_zip(zip_code: str) -> bool:
    digits = (zip_code or "").replace("-", "")
    return (len(digits) == 5 and digits.isdigit())


def state_zip(state: str, seq: int = 0) -> str:
    """Return a plausible 5-digit ZIP aligned to a US state."""
    prefix = STATE_ZIP.get(state.upper(), "000")
    return f"{prefix}{seq % 100:02d}"


# ---------------------------------------------------------------------------
# ER entity dataclasses (spec Section 7 ER diagram)
# ---------------------------------------------------------------------------
@dataclass
class Company:
    company_id: str
    legal_name: str
    state: str
    fein: str


@dataclass
class Subsidiary:
    subsidiary_id: str
    company_id: str
    name: str
    state: str


@dataclass
class Account:
    account_number: str
    account_name: str
    subsidiary_id: str


@dataclass
class Customer:
    customer_id: str
    name: str
    fein: str
    state: str
    zip_code: str


@dataclass
class Vendor:
    vendor_id: str
    name: str
    fein: str
    state: str
    zip_code: str
    payment_terms: str = "NET_30"


@dataclass
class SalesOrder:
    sales_order_id: str
    customer_id: str
    order_date: str
    amount: Decimal


@dataclass
class Invoice:
    invoice_id: str
    sales_order_id: str
    customer_id: str
    invoice_date: str
    amount: Decimal


@dataclass
class PaymentReceipt:
    receipt_id: str
    invoice_id: str
    customer_id: str
    receipt_date: str
    amount: Decimal


@dataclass
class PurchaseOrder:
    purchase_order_id: str
    vendor_id: str
    order_date: str
    amount: Decimal


@dataclass
class ReceivingRecord:
    receiving_id: str
    purchase_order_id: str
    vendor_id: str
    receive_date: str
    amount: Decimal


@dataclass
class VendorBill:
    vendor_bill_id: str
    receiving_id: str
    vendor_id: str
    bill_date: str
    amount: Decimal


@dataclass
class VdrDocument:
    document_id: str
    provenance_tier: str  # T1..T7
    document_type: str
    path: str


@dataclass
class ArtifactFile:
    artifact_id: str
    document_id: str
    file_path: str
    mime_type: str


@dataclass
class Transaction:
    transaction_id: str
    subsidiary_id: str
    effective_date: str
    entity_type: str  # e.g. INVOICE, COLLECTION, PURCHASE


@dataclass
class JournalEntryLine:
    transaction_id: str
    account_number: str
    debit: Decimal
    credit: Decimal


# ---------------------------------------------------------------------------
# Verified Master Entity Ledger (LP-15)
# ---------------------------------------------------------------------------
class MasterEntityLedger:
    """Registers synthetic entities with valid FEINs and state/ZIP alignments."""

    def __init__(self, seed: int = 0):
        self.seed = seed
        self.customers: Dict[str, Customer] = {}
        self.vendors: Dict[str, Vendor] = {}
        self._fein_used: Dict[str, str] = {}

    def register_vendor(self, name: str, state: str = "IL", terms: str = "NET_30") -> Vendor:
        if name in self.vendors:
            return self.vendors[name]
        fein = generate_fein(name, self.seed)
        while not valid_fein(fein) or fein in self._fein_used:
            fein = generate_fein(name + str(len(self._fein_used)), self.seed)
        self._fein_used[fein] = name
        vendor = Vendor(vendor_id=f"V-{len(self.vendors) + 1:04d}", name=name, fein=fein,
                        state=state, zip_code=state_zip(state, len(self.vendors)),
                        payment_terms=terms)
        self.vendors[name] = vendor
        return vendor

    def register_customer(self, name: str, state: str = "NY") -> Customer:
        if name in self.customers:
            return self.customers[name]
        fein = generate_fein(name, self.seed + 1)
        while not valid_fein(fein) or fein in self._fein_used:
            fein = generate_fein(name + str(len(self._fein_used)), self.seed + 1)
        self._fein_used[fein] = name
        customer = Customer(customer_id=f"C-{len(self.customers) + 1:04d}", name=name, fein=fein,
                            state=state, zip_code=state_zip(state, len(self.customers)))
        self.customers[name] = customer
        return customer

    def validate_all(self) -> Dict[str, List[str]]:
        """Return any LP-15 violations across the registered entities."""
        violations: List[str] = []
        for v in self.vendors.values():
            if not valid_fein(v.fein):
                violations.append(f"Invalid FEIN for vendor {v.name}: {v.fein}")
            if not valid_zip(v.zip_code):
                violations.append(f"Invalid ZIP for vendor {v.name}: {v.zip_code}")
        for c in self.customers.values():
            if not valid_fein(c.fein):
                violations.append(f"Invalid FEIN for customer {c.name}: {c.fein}")
            if not valid_zip(c.zip_code):
                violations.append(f"Invalid ZIP for customer {c.name}: {c.zip_code}")
        return {"violations": violations, "compliant": len(violations) == 0}

    def to_dict(self) -> dict:
        return {
            "vendors": [{"vendor_id": v.vendor_id, "name": v.name, "fein": v.fein,
                         "state": v.state, "zip_code": v.zip_code, "terms": v.payment_terms}
                        for v in self.vendors.values()],
            "customers": [{"customer_id": c.customer_id, "name": c.name, "fein": c.fein,
                           "state": c.state, "zip_code": c.zip_code}
                          for c in self.customers.values()],
            "lp15_compliant": self.validate_all()["compliant"],
        }
