import json

catalog_path = r"research/consolidated_findings/qoe_simulator_parameter_catalog.json"
forensic_path = r"research/accounting_signals/deep_financial_reporting_forensics.json"

with open(catalog_path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

with open(forensic_path, "r", encoding="utf-8") as f:
    forensics = json.load(f)

# Update metadata
catalog["metadata"]["sources"]["deep_financial_reporting_forensics"] = (
    "SEC EDGAR 5,961 Corporate Filings Forensic Deep Dive - EBITDA Add-Backs (SBC, Restructuring, Impairments), "
    "Channel Stuffing & Inventory Decoupling Tests, Restatement Autopsies, and Real Corporate Case Studies"
)
catalog["metadata"]["version"] = "1.4.0"

# Add deep forensic parameters
catalog["deep_financial_reporting_forensics"] = {
    "ebitda_addback_prevalence_and_severity": {
        "share_based_compensation": forensics["addback_prevalence_and_intensity"]["share_based_compensation"],
        "restructuring_charges": forensics["addback_prevalence_and_intensity"]["restructuring_charges"],
        "asset_impairments": forensics["addback_prevalence_and_intensity"]["asset_impairments"],
        "goodwill_impairments": forensics["addback_prevalence_and_intensity"]["goodwill_impairments"]
    },
    "working_capital_decoupling_hazards": {
        "channel_stuffing_risk_pct": forensics["working_capital_forensics"]["channel_stuffing_risk"]["channel_stuffing_prevalence_pct"],
        "channel_stuffing_spread_p75": forensics["working_capital_forensics"]["channel_stuffing_risk"]["p75_ar_rev_growth_spread"],
        "inventory_bloat_risk_pct": forensics["working_capital_forensics"]["inventory_bloat_risk"]["inventory_bloat_prevalence_pct"],
        "inventory_bloat_spread_p75": forensics["working_capital_forensics"]["inventory_bloat_risk"]["p75_inv_cogs_growth_spread"]
    },
    "restatement_autopsy_signatures": {
        "restated_median_revenue": forensics["restatement_autopsy"]["median_revenue"]["restated"],
        "normal_median_revenue": forensics["restatement_autopsy"]["median_revenue"]["normal"],
        "restated_negative_equity_rate_pct": forensics["restatement_autopsy"]["negative_equity_rate_pct"]["restated"],
        "normal_negative_equity_rate_pct": forensics["restatement_autopsy"]["negative_equity_rate_pct"]["normal"],
        "restated_median_ebit_margin": forensics["restatement_autopsy"]["median_operating_margin"]["restated"]
    },
    "sector_ebitda_margin_expansion_bps": {
        sec: data["median_margin_expansion_bps"] for sec, data in forensics["sector_ebitda_bridges"].items()
    },
    "benchmark_corporate_archetypes": forensics["archetype_profiles"]
}

with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2)

print("Successfully updated Master Parameter Catalog with Deep Forensics parameters!")
