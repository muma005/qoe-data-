"""Source-linked JSON records for VDR categories not materialized by the ledger exporter.

These records expose what the simulator actually knows. External attestations,
filings, signed contracts, and individual employees are never inferred from a GL.
"""

from collections import defaultdict
from decimal import Decimal


def build_supplemental_vdr(profile, core, trajectory, entity_ledger, simulator):
    public_ledger_ref = "vdr_artifacts/json/erp_general_ledger.json"
    years = sorted({m.calendar_year for m in trajectory.monthly_trajectories})
    entities = entity_ledger.to_dict()
    customers = entities["customers"]
    vendors = entities["vendors"]
    annual = defaultdict(lambda: defaultdict(Decimal))
    cash = defaultdict(lambda: Decimal(0))
    payroll = defaultdict(lambda: Decimal(0))
    rent = defaultdict(lambda: Decimal(0))
    cash_refs = defaultdict(list)
    payroll_refs = defaultdict(list)
    rent_refs = defaultdict(list)
    credit_refs = []
    for entry in core.entries:
        if entry.sim_year not in years:
            continue
        period = f"{entry.sim_year:04d}-{entry.sim_month:02d}"
        if entry.entry_type in ("CREDIT_MEMO", "CREDIT_NOTE"):
            credit_refs.append({"journal_entry_id": entry.entry_id,
                                "document_ref": entry.document_ref, "period": period})
        for line in entry.lines:
            category = line.category.value
            if category == "REVENUE":
                annual[entry.sim_year]["revenue"] += line.credit - line.debit
            elif category in ("COGS", "OPEX"):
                annual[entry.sim_year][category.lower()] += line.debit - line.credit
            if line.account_number == "101000":
                cash[period] += line.debit - line.credit
                cash_refs[period].append(entry.entry_id)
            if entry.entry_type == "PAYROLL" and category == "OPEX":
                payroll[period] += line.debit - line.credit
                payroll_refs[period].append(entry.entry_id)
            if line.account_number in ("621700", "631000"):
                rent[period] += line.debit - line.credit
                rent_refs[period].append(entry.entry_id)

    def amount(value):
        return str(value.quantize(Decimal("0.0001")))

    annual_rows = [{"year": year, "revenue": amount(annual[year]["revenue"]),
                    "cogs": amount(annual[year]["cogs"]),
                    "opex": amount(annual[year]["opex"])} for year in years]
    cash_rows = [{"period": period, "net_cash_journal_movement": amount(value),
                  "journal_entry_ids": cash_refs[period]}
                 for period, value in sorted(cash.items())]
    payroll_rows = [{"period": period, "posted_payroll_opex": amount(value),
                     "journal_entry_ids": payroll_refs[period]}
                    for period, value in sorted(payroll.items())]
    rent_rows = [{"period": period, "posted_rent_expense": amount(value),
                  "journal_entry_ids": rent_refs[period]}
                 for period, value in sorted(rent.items())]
    shocks = [{"period": f"{m.calendar_year:04d}-{m.calendar_month:02d}",
               "shock_type": shock.shock_type, "description": shock.description}
              for m in trajectory.monthly_trajectories for shock in m.active_shocks
              if shock.shock_type == "CUSTOMER_CHURN"]
    sales_by_product = defaultdict(lambda: Decimal(0))
    for row in simulator.sales_lines:
        sales_by_product[row["product_id"]] += Decimal(row["sales_amount"])
    product_rows = [{"product_id": sku, "ending_units": units,
                     "recorded_sales": amount(sales_by_product[sku])}
                    for sku, units in sorted(simulator._sku_units.items())]

    # Each record names its actual package sources and distinguishes a simulated
    # financial schedule from an external document whose existence is unknown.
    specs = [
        ("01_Corporate_Governance_and_Legal", "Corporate_Identity_and_Bylaws_Register.json",
         "corporate_identity.json", 1, ["manifest.json", "entity_ledger.json"],
         {"legal_name": profile.company_name, "sector_naics": profile.naics,
          "customer_count": len(customers), "vendor_count": len(vendors),
          "bylaws_verification": "external_record_pending"}),
        ("01_Corporate_Governance_and_Legal", "Board_Minutes_Register.json",
         "board_minutes_register.json", 1, ["manifest.json", public_ledger_ref],
         {"years_with_financial_activity": years, "annual_activity": annual_rows,
          "minutes_verification": "no_board_minutes_source_modeled"}),
        ("01_Corporate_Governance_and_Legal", "Litigation_and_Claims_Register.json",
         "litigation_register.json", 14, ["manifest.json", public_ledger_ref],
         {"reviewed_years": years, "claim_records": [],
          "absence_of_claims_verified": False}),
        ("02_Financial_and_Accounting", "Annual_Financial_Statements.json",
         "annual_financial_statements.json", 1, [public_ledger_ref, "manifest.json"],
         {"annual_income_statement_activity": annual_rows,
          "audit_opinion": "not_modeled", "externally_audited": False}),
        ("02_Financial_and_Accounting", "Cash_Ledger_and_Bank_Reconciliation_Register.json",
         "cash_reconciliation_register.json", 14, [public_ledger_ref],
         {"monthly_cash_ledger_movements": cash_rows,
          "external_bank_statements": "not_modeled", "bank_reconciliation_verified": False}),
        ("03_Tax_and_Regulatory", "Federal_Tax_Return_Source_Register.json",
         "federal_tax_register.json", 14, [public_ledger_ref, "manifest.json"],
         {"annual_book_activity": annual_rows, "form_1120_filing": "not_modeled",
          "taxable_income_calculated": False}),
        ("03_Tax_and_Regulatory", "State_Apportionment_Source_Register.json",
         "state_apportionment_register.json", 14, ["entity_ledger.json"],
         {"customer_states": sorted({customer["state"] for customer in customers}),
          "revenue_by_state": "not_modeled", "filed_apportionment": False}),
        ("03_Tax_and_Regulatory", "Sales_Tax_Correspondence_Register.json",
         "sales_tax_correspondence.json", 14, ["manifest.json"],
         {"reviewed_years": years, "correspondence_records": [],
          "absence_of_correspondence_verified": False}),
        ("04_Commercial_and_Customers", "Customer_Agreement_Register.json",
         "customer_agreement_register.json", 14, ["entity_ledger.json", "sales_lines.json"],
         {"customers": [{"customer_id": c["customer_id"], "name": c["name"]}
                        for c in customers[:20]], "executed_msa_terms": "not_modeled"}),
        ("04_Commercial_and_Customers", "Customer_Churn_and_Credit_Activity.json",
         "customer_churn_credit_activity.json", 14,
         ["operational_trajectory.json", public_ledger_ref],
         {"modeled_churn_shocks": shocks, "credit_memo_journals": credit_refs,
          "customer_level_churn": "not_modeled"}),
        ("05_Operations_and_Procurement", "Facility_Rent_and_Lease_Register.json",
         "facility_lease_register.json", 14, [public_ledger_ref],
         {"monthly_rent_postings": rent_rows, "executed_lease_terms": "not_modeled"}),
        ("05_Operations_and_Procurement", "Product_Units_and_BOM_Register.json",
         "product_bom_register.json", 7, ["sku_inventory.json", "sales_lines.json"],
         {"products": product_rows, "component_bills_of_material": "not_modeled"}),
        ("06_Human_Resources_and_Compensation", "Payroll_and_Employee_Census_Register.json",
         "employee_census_register.json", 14, [public_ledger_ref],
         {"monthly_payroll_postings": payroll_rows, "individual_employee_census": "not_modeled"}),
        ("06_Human_Resources_and_Compensation", "Executive_Employment_Register.json",
         "executive_employment_register.json", 20, [public_ledger_ref],
         {"payroll_periods": [row["period"] for row in payroll_rows],
          "executive_contracts": "not_modeled"}),
        ("06_Human_Resources_and_Compensation", "Owner_Expense_Attribution_Register.json",
         "owner_expense_register.json", 20, [public_ledger_ref],
         {"annual_opex": [{"year": row["year"], "amount": row["opex"]}
                          for row in annual_rows], "owner_attribution": "not_modeled"}),
    ]
    return [(section, title, filename, day,
             {"record_type": filename.removesuffix(".json"),
              "scenario_id": profile.scenario_id, "source_refs": refs,
              "verification_status": "source_derived_external_verification_pending",
              "data": data})
            for section, title, filename, day, refs, data in specs]
