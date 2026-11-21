import json

catalog_path = r"research/consolidated_findings/qoe_simulator_parameter_catalog.json"
metrics_path = r"research/accounting_signals/financial_reporting_behaviour_metrics.json"

with open(catalog_path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

with open(metrics_path, "r", encoding="utf-8") as f:
    metrics = json.load(f)

# Update metadata
catalog["metadata"]["sources"]["financial_reporting_behaviour"] = (
    "SEC EDGAR Corporate Operating Filings (5,961 public filers across 14 economic sectors) - "
    "Margins, Sloan Accruals, Cash Conversion Cycles (DSO/DIO/DPO), and Balance Sheet Solvency"
)
catalog["metadata"]["version"] = "1.3.0"

# Add financial reporting behaviour parameters
catalog["financial_reporting_behaviour_and_accruals"] = {
    "quality_of_earnings_accrual_anomalies": {
        "paper_profit_divergence_rate_pct": metrics["overall_metrics"]["quality_of_earnings_accruals"]["divergence_positive_ni_negative_cfo_pct"],
        "non_cash_loss_addback_divergence_pct": metrics["overall_metrics"]["quality_of_earnings_accruals"]["divergence_negative_opinc_positive_cfo_pct"],
        "accruals_to_assets_distribution": metrics["overall_metrics"]["quality_of_earnings_accruals"]["accruals_to_assets_ratio"]
    },
    "working_capital_cycles_and_liquidity": {
        "median_dso_days": metrics["overall_metrics"]["working_capital_days"]["dso_days"]["median"],
        "median_dio_days": metrics["overall_metrics"]["working_capital_days"]["dio_days"]["median"],
        "median_dpo_days": metrics["overall_metrics"]["working_capital_days"]["dpo_days"]["median"],
        "median_cash_conversion_cycle_days": metrics["overall_metrics"]["working_capital_days"]["cash_conversion_cycle_days"]["median"],
        "median_nwc_to_revenue_ratio": metrics["overall_metrics"]["working_capital_days"]["nwc_to_revenue_ratio"]["median"]
    },
    "profitability_margins_overall": {
        "median_gross_margin_pct": metrics["overall_metrics"]["profitability_margins"]["gross_margin"]["median"] * 100,
        "median_operating_margin_pct": metrics["overall_metrics"]["profitability_margins"]["operating_margin"]["median"] * 100,
        "median_net_margin_pct": metrics["overall_metrics"]["profitability_margins"]["net_margin"]["median"] * 100
    },
    "filer_scale_governance_chasm": {
        "large_accelerated_1_LAF": {
            "median_revenue_quarterly": metrics["filer_scale_breakdown"]["1-LAF"]["median_revenue"],
            "median_operating_margin_pct": metrics["filer_scale_breakdown"]["1-LAF"]["median_operating_margin"] * 100,
            "negative_equity_rate_pct": metrics["filer_scale_breakdown"]["1-LAF"]["negative_equity_rate_pct"],
            "cash_to_assets_ratio": metrics["filer_scale_breakdown"]["1-LAF"]["median_cash_to_assets"]
        },
        "accelerated_2_ACC": {
            "median_revenue_quarterly": metrics["filer_scale_breakdown"]["2-ACC"]["median_revenue"],
            "median_operating_margin_pct": metrics["filer_scale_breakdown"]["2-ACC"]["median_operating_margin"] * 100,
            "negative_equity_rate_pct": metrics["filer_scale_breakdown"]["2-ACC"]["negative_equity_rate_pct"],
            "cash_to_assets_ratio": metrics["filer_scale_breakdown"]["2-ACC"]["median_cash_to_assets"]
        },
        "non_accelerated_smaller_4_NON": {
            "median_revenue_quarterly": metrics["filer_scale_breakdown"]["4-NON"]["median_revenue"],
            "median_operating_margin_pct": metrics["filer_scale_breakdown"]["4-NON"]["median_operating_margin"] * 100,
            "negative_equity_rate_pct": metrics["filer_scale_breakdown"]["4-NON"]["negative_equity_rate_pct"],
            "cash_to_assets_ratio": metrics["filer_scale_breakdown"]["4-NON"]["median_cash_to_assets"]
        }
    },
    "balance_sheet_asset_quality": {
        "overall_negative_equity_rate_pct": metrics["overall_metrics"]["balance_sheet_structure"]["negative_equity_rate_pct"],
        "goodwill_p90_share_of_assets_pct": metrics["overall_metrics"]["balance_sheet_structure"]["goodwill_to_assets"]["p90"] * 100,
        "goodwill_p95_share_of_assets_pct": metrics["overall_metrics"]["balance_sheet_structure"]["goodwill_to_assets"]["p95"] * 100,
        "median_cash_to_assets_pct": metrics["overall_metrics"]["balance_sheet_structure"]["cash_to_assets"]["median"] * 100
    },
    "sector_benchmarks": metrics["sector_breakdown"]
}

with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2)

print("Successfully updated Master Parameter Catalog with Financial Reporting Behaviour metrics!")
