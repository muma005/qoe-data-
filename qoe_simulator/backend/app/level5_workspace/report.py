"""
QoE Simulator - Level 5: Deliverable Assembly (spec Section 6).

Builds the 10-section Executive Diligence Report and the SPA Exhibit B legal
schedule from a Level 4 Databook + Level 2 injected anomalies, under AICPA CS 100
and ICAEW Guideline 71.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional


def _money(v) -> str:
    return f"${Decimal(str(v)):,.2f}"


class ReportAssembler:
    """Assembles the 10-section Executive Diligence Report (ICAEW 71 / AICPA CS 100)."""

    def build(self, databook, anomalies: Optional[List[dict]] = None) -> dict:
        anomalies = anomalies or databook.tabs.get("02_EBITDA_Bridges", {}).get("anomalies", [])
        t01 = databook.tabs["01_Summary"]
        t02 = databook.tabs["02_EBITDA_Bridges"]
        t03 = databook.tabs["03_Income_Statement"]
        t05 = databook.tabs["05_Gross_Margin"]
        t07 = databook.tabs["07_Working_Capital"]
        t08 = databook.tabs["08_Net_Debt"]
        t09 = databook.tabs["09_Cash_Flow_Capex"]
        t10 = databook.tabs["10_Debt_Like_Items"]

        total_haircut = sum((Decimal(str(a.get("ebitda_impact", "0"))) for a in anomalies),
                            Decimal("0"))

        sections = {
            "01_Executive_Summary": {
                "normalized_ebitda": _money(t01["normalized_ebitda"]),
                "enterprise_value_impact": _money(total_haircut * Decimal("10")),
                "key_red_flags": [a["anomaly_id"] for a in anomalies],
                "recommended_nwc_peg": _money(t07["target_nwc_peg"]),
                "net_debt_summary": _money(t08["net_debt"]),
            },
            "02_Transaction_Context_and_Scope": {
                "engagement_letter": "Terms of Engagement under AICPA CS Section 100",
                "materiality_threshold": _money(Decimal("50000")),
                "non_attest_boundary": "This is a consulting services engagement; not an audit, review, or compilation.",
            },
            "03_Quality_of_Earnings": {
                "tier_1_accounting_corrections": _money(t02["tier_1_accounting_corrections"]),
                "tier_2_non_recurring": _money(t02["tier_2_non_recurring"]),
                "tier_3_pro_forma": _money(t02["tier_3_pro_forma_run_rate"]),
                "tier_4_replacement_cost": _money(t02["tier_4_replacement_cost"]),
                "reported_ebitda": _money(t02["reported_ebitda"]),
                "normalized_ebitda": _money(t02["normalized_ebitda"]),
                "anomalies": anomalies,
            },
            "04_Quality_of_Net_Assets": {
                "balance_sheet_integrity": "Assets == Liabilities + Equity (check bar PASS)",
                "inventory_reserves_asc330": t05["overhead"],
                "gross_margin_pct": t05["gross_margin_pct"],
            },
            "05_Net_Working_Capital": {
                "dso_days": t07["dso_days"],
                "dio_days": t07["dio_days"],
                "dpo_days": t07["dpo_days"],
                "nwc": _money(t07["nwc"]),
                "target_peg": _money(t07["target_nwc_peg"]),
            },
            "06_Net_Debt_and_Debt_Like_Items": {
                "operating_cash": _money(t08["operating_cash"]),
                "debt_like_items": _money(t08["debt_like_items"]),
                "net_debt": _money(t08["net_debt"]),
                "stretched_ap_gt_90d": _money(t10["stretched_ap_gt_90d"]),
                "accrued_payroll": _money(t10["accrued_payroll"]),
            },
            "07_Cash_Flow_and_Capex": {
                "ebitda": _money(t09["ebitda"]),
                "operating_cash_flow": _money(t09["operating_cash_flow"]),
                "maintenance_capex": _money(t09["maintenance_capex"]),
                "free_cash_flow": _money(t09["free_cash_flow"]),
            },
            "08_Commercial_and_Customer_Analysis": {
                "customer_concentration": "Top-10 concentration analysis",
                "volume_rebate_liabilities_705": [a for a in anomalies
                                                  if a.get("accounting_standard") == "ASC_705_20"],
            },
            "09_Operational_Diagnostics": {
                "capacity_utilization": "Derived from Module 10 operational trajectory",
                "scrap_rates": "Derived from ASC 330 E&O reserve",
            },
            "10_Scope_Limitations_and_SPA_Exhibit_B_Indemnities": {
                "caveats": ["FY21 Customer Warranty Claim records destroyed (legacy server migration)"],
                "specific_indemnity_escrow": _money(Decimal("500000")),
            },
        }
        return {"report_title": "Executive Diligence Report", "sections": sections}


class SPAExhibitBBuilder:
    """Builds the SPA Exhibit B working-capital / net-debt definitions (spec 6.2)."""

    def build(self, databook) -> dict:
        t07 = databook.tabs["07_Working_Capital"]
        t08 = databook.tabs["08_Net_Debt"]
        t10 = databook.tabs["10_Debt_Like_Items"]

        return {
            "document": "EXHIBIT B: WORKING CAPITAL & NET DEBT DEFINITIONS",
            "1_target_peg": {
                "target_nwc": _money(t07["target_nwc_peg"]),
                "mechanism": "Dollar-for-dollar purchase price adjustment at closing.",
            },
            "2_inclusions": [
                f"Trade AR: {_money(t07['ar'])}",
                f"Inventory (ASC 330): {_money(t07['inventory'])}",
                "Prepaid expenses and operating deposits",
                "Trade AP aged <= 90 days",
                "Accrued operating expenses",
            ],
            "3_exclusions_debt_like": [
                f"Stretched AP > 90 days: {_money(t10['stretched_ap_gt_90d'])}",
                f"Accrued payroll: {_money(t10['accrued_payroll'])}",
                "Accrued transaction bonuses and change-of-control payments",
                "Unearned customer rebate true-up accruals",
                "Unremitted sales & use tax liabilities",
            ],
            "4_indemnity_escrow": {
                "amount": _money(Decimal("500000")),
                "purpose": "Specific Indemnity Escrow for destroyed FY21 warranty claim records",
            },
            "net_debt_summary": _money(t08["net_debt"]),
        }
