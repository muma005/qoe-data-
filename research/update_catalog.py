import json

catalog_path = r"research/consolidated_findings/qoe_simulator_parameter_catalog.json"
sec_path = r"research/accounting_signals/sec_fsds_accounting_metrics.json"
mna_path = r"research/mna_qoe_signals/mna_qoe_parameters.json"

with open(catalog_path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

with open(sec_path, "r", encoding="utf-8") as f:
    sec_data = json.load(f)

with open(mna_path, "r", encoding="utf-8") as f:
    mna_data = json.load(f)

# Update metadata
catalog["metadata"]["sources"]["financial_accounting"] = (
    "SEC EDGAR Financial Statement Data Sets (FSDS 2024 Q3) - 6,699 corporate filers, 83,106 tags, 3.52M facts"
)
catalog["metadata"]["sources"]["mna_advisory_and_window_dressing"] = (
    "SEC Form DEFM14A ($44B Twitter / Musk buyout; Goldman Sachs & J.P. Morgan Fairness Opinions) & "
    "SDNY Bankruptcy Examiner Report (Lehman Brothers Repo 105 Forensic Investigation)"
)
catalog["metadata"]["version"] = "1.2.0"

# Add financial accounting parameters
catalog["financial_accounting_and_restatements"] = {
    "corporate_restatements_hazard": {
        "overall_restatement_prevrpt_rate_pct": sec_data["corporate_restatements"]["prevrpt_restatement_rate"] * 100,
        "total_filings_analyzed": sec_data["corporate_restatements"]["total_filings"],
        "total_restatements_count": sec_data["corporate_restatements"]["prevrpt_count"],
        "restatements_by_form": sec_data["corporate_restatements"]["restatements_by_form"],
        "restatements_by_accelerated_filer_status": {
            "1_large_accelerated_filer_1_LAF": {
                "count": 2164,
                "restatements": 6,
                "rate_pct": 0.2773
            },
            "2_accelerated_filer_2_ACC": {
                "count": 833,
                "restatements": 5,
                "rate_pct": 0.6002
            },
            "4_non_accelerated_smaller_4_NON": {
                "count": 3670,
                "restatements": 157,
                "rate_pct": 4.2779
            },
            "hazard_ratio_non_accel_vs_large_accel": 15.42
        }
    },
    "taxonomy_customization_and_reporting_opacity": {
        "custom_extension_tag_ratio_pct": sec_data["reporting_complexity_and_opacity"]["custom_extension_ratio"] * 100,
        "standard_us_gaap_tags_count": sec_data["reporting_complexity_and_opacity"]["standard_us_gaap_tags"],
        "custom_extension_tags_count": sec_data["reporting_complexity_and_opacity"]["custom_extension_tags"],
        "monetary_custom_share_pct": (
            sec_data["reporting_complexity_and_opacity"]["custom_by_datatype"]["monetary"]["sum"] /
            sec_data["reporting_complexity_and_opacity"]["custom_by_datatype"]["monetary"]["count"] * 100
        )
    },
    "financial_statement_architecture": {
        "statement_distribution_pct": sec_data["financial_statement_architecture"]["statement_percentages"],
        "contra_account_negating_rate_pct": sec_data["financial_statement_architecture"]["negating_contra_item_rate"] * 100,
        "balance_sheet_line_stats": sec_data["financial_statement_architecture"]["statement_line_counts"]["BS"],
        "income_statement_line_stats": sec_data["financial_statement_architecture"]["statement_line_counts"]["IS"],
        "cash_flow_statement_line_stats": sec_data["financial_statement_architecture"]["statement_line_counts"]["CF"]
    },
    "numeric_facts_and_footnotes": {
        "total_numeric_facts": sec_data["numeric_disclosure_mechanics"]["total_numeric_facts"],
        "footnote_attachment_rate_pct": sec_data["numeric_disclosure_mechanics"]["footnote_attachment_rate"] * 100,
        "core_gaap_concept_counts": sec_data["numeric_disclosure_mechanics"]["core_gaap_tag_frequency"]
    }
}

# Add M&A advisory and window dressing parameters
catalog["mna_advisory_ebitda_and_window_dressing"] = {
    "prospective_cash_flow_and_sbc_dilution": {
        "revenue_cagr_6yr_pct": mna_data["prospective_ebitda_and_cash_flow_bridge"]["growth_rates"]["revenue_cagr_2022_2027"] * 100,
        "adjusted_ebitda_cagr_6yr_pct": mna_data["prospective_ebitda_and_cash_flow_bridge"]["growth_rates"]["adj_ebitda_cagr_2022_2027"] * 100,
        "cumulative_6yr_revenue_millions": sum(r["revenue"] for r in mna_data["prospective_ebitda_and_cash_flow_bridge"]["projection_table"]),
        "cumulative_6yr_sbc_millions": mna_data["prospective_ebitda_and_cash_flow_bridge"]["stock_based_compensation_dilution"]["cumulative_6yr_sbc_millions"],
        "sbc_as_pct_of_cumulative_revenue": mna_data["prospective_ebitda_and_cash_flow_bridge"]["stock_based_compensation_dilution"]["sbc_as_pct_of_cumulative_revenue"] * 100,
        "cumulative_management_ufcf_millions": mna_data["prospective_ebitda_and_cash_flow_bridge"]["stock_based_compensation_dilution"]["cumulative_mgmt_ufcf_millions"],
        "cumulative_banker_ufcf_millions": mna_data["prospective_ebitda_and_cash_flow_bridge"]["stock_based_compensation_dilution"]["cumulative_banker_ufcf_millions"],
        "sbc_cash_flow_dilution_percentage": mna_data["prospective_ebitda_and_cash_flow_bridge"]["stock_based_compensation_dilution"]["sbc_dilution_percentage"] * 100,
        "cumulative_working_capital_drag_millions": mna_data["prospective_ebitda_and_cash_flow_bridge"]["working_capital_drag"]["cumulative_nwc_drain_millions"]
    },
    "historical_ebitda_normalization_bridge": {
        "reported_adj_ebitda_base_millions": mna_data["historical_ebitda_normalizations"]["fy21_reported_adj_ebitda_millions"],
        "litigation_one_time_addback_millions": mna_data["historical_ebitda_normalizations"]["one_time_litigation_addback_millions"],
        "unadjusted_base_ebitda_millions": mna_data["historical_ebitda_normalizations"]["unadjusted_base_ebitda_millions"],
        "addback_share_of_adj_ebitda_pct": mna_data["historical_ebitda_normalizations"]["addback_share_of_adj_ebitda"] * 100,
        "transaction_multiple_range": mna_data["historical_ebitda_normalizations"]["transaction_valuation_multiple_range"],
        "enterprise_value_swing_millions": mna_data["historical_ebitda_normalizations"]["implied_enterprise_value_swing_millions"]
    },
    "fairness_opinion_valuation_parameters": mna_data["fairness_opinion_valuation_parameters"],
    "forensic_window_dressing_mechanics_lehman_repo105": {
        "accounting_rule_exploited": mna_data["forensic_window_dressing_repo105"]["accounting_standard_exploited"],
        "collateral_haircuts_pct": mna_data["forensic_window_dressing_repo105"]["haircut_overcollateralization_rule"],
        "quarterly_derecognition_scale_billions": mna_data["forensic_window_dressing_repo105"]["quarterly_derecognition_scale_billions"],
        "execution_lead_days_pre_close": mna_data["forensic_window_dressing_repo105"]["timing_dynamics"]["execution_lead_days_prior_to_quarter_end"],
        "unwind_lag_days_post_close": mna_data["forensic_window_dressing_repo105"]["timing_dynamics"]["unwind_lag_days_after_quarter_start"],
        "leverage_suppression_pct": {
            "net_leverage_suppression_pct": mna_data["forensic_window_dressing_repo105"]["leverage_distortion_q2_2008"]["net_leverage_suppression_pct"] * 100,
            "gross_leverage_suppression_pct": mna_data["forensic_window_dressing_repo105"]["leverage_distortion_q2_2008"]["gross_leverage_suppression_pct"] * 100
        }
    }
}

with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2)

print("Successfully updated Master Parameter Catalog with Financial Accounting and M&A / Repo 105 parameters!")
