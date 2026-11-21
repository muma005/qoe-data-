import os
import json
import numpy as np
import pandas as pd

def extract_mna_qoe_signals():
    out_dir = r"research/mna_qoe_signals"
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- 1. Modeling Prospective Financial Information & Quality of Earnings Bridge ---")
    years = ["2022E", "2023E", "2024E", "2025E", "2026E", "2027E"]
    
    # Financial metrics in $ Millions from SEC DEFM14A
    revenue = [5928, 7200, 8481, 9793, 11264, 12917]
    cash_opex = [4326, 4515, 5238, 5947, 6706, 7518]
    adj_ebitda = [1602, 2685, 3243, 3846, 4558, 5399]
    gaap_ebit = [-47, 917, 1192, 1517, 1932, 2455]
    cash_taxes = [0, 165, 215, 273, 348, 442]
    amort_intangibles = [33, 45, 51, 58, 64, 71]
    depreciation = [669, 823, 934, 1033, 1132, 1230]
    capex = [968, 982, 1018, 1077, 1014, 1033]
    nwc_change = [11, -259, -111, -125, -150, -181]
    sbc = [864, 900, 1066, 1238, 1430, 1643]
    mgmt_ufcf = [561, 1279, 1900, 2371, 3046, 3742]
    banker_ufcf = [-303, 379, 834, 1133, 1616, 2099]
    
    df_proj = pd.DataFrame({
        "year": years,
        "revenue": revenue,
        "cash_opex": cash_opex,
        "adj_ebitda": adj_ebitda,
        "gaap_ebit": gaap_ebit,
        "cash_taxes": cash_taxes,
        "amort_intangibles": amort_intangibles,
        "depreciation": depreciation,
        "capex": capex,
        "nwc_change": nwc_change,
        "sbc": sbc,
        "mgmt_ufcf": mgmt_ufcf,
        "banker_ufcf": banker_ufcf
    })
    
    # Calculated QoE metrics
    df_proj["adj_ebitda_margin"] = df_proj["adj_ebitda"] / df_proj["revenue"]
    df_proj["gaap_ebit_margin"] = df_proj["gaap_ebit"] / df_proj["revenue"]
    df_proj["ebitda_to_ebit_spread"] = df_proj["adj_ebitda"] - df_proj["gaap_ebit"]
    df_proj["sbc_pct_revenue"] = df_proj["sbc"] / df_proj["revenue"]
    df_proj["sbc_pct_adj_ebitda"] = df_proj["sbc"] / df_proj["adj_ebitda"]
    df_proj["capex_pct_revenue"] = df_proj["capex"] / df_proj["revenue"]
    df_proj["ufcf_dilution_from_sbc"] = df_proj["mgmt_ufcf"] - df_proj["banker_ufcf"]
    df_proj["banker_to_mgmt_ufcf_ratio"] = df_proj["banker_ufcf"] / df_proj["mgmt_ufcf"]
    
    # Summary aggregates
    total_rev = sum(revenue)
    total_adj_ebitda = sum(adj_ebitda)
    total_gaap_ebit = sum(gaap_ebit)
    total_sbc = sum(sbc)
    total_capex = sum(capex)
    total_nwc_drain = sum(nwc_change)
    total_mgmt_ufcf = sum(mgmt_ufcf)
    total_banker_ufcf = sum(banker_ufcf)
    total_ufcf_sbc_dilution = total_mgmt_ufcf - total_banker_ufcf
    
    cagr_revenue = (revenue[-1] / revenue[0]) ** (1 / (len(revenue) - 1)) - 1
    cagr_adj_ebitda = (adj_ebitda[-1] / adj_ebitda[0]) ** (1 / (len(adj_ebitda) - 1)) - 1
    
    print(f"Revenue CAGR (2022E-2027E): {cagr_revenue:.2%}")
    print(f"Adjusted EBITDA CAGR: {cagr_adj_ebitda:.2%}")
    print(f"Cumulative 6-Year SBC: ${total_sbc:,.0f}M ({total_sbc/total_rev:.2%} of revenue)")
    print(f"Cumulative NWC Cash Drain: ${total_nwc_drain:,.0f}M")
    print(f"Cumulative Management UFCF: ${total_mgmt_ufcf:,.0f}M")
    print(f"Cumulative Banker UFCF (less SBC): ${total_banker_ufcf:,.0f}M")
    print(f"Cumulative Cash Flow Dilution via SBC: ${total_ufcf_sbc_dilution:,.0f}M ({total_ufcf_sbc_dilution/total_mgmt_ufcf:.2%})")
    
    print("\n--- 2. Historical Adjusted EBITDA Normalization & One-Time Add-Back ---")
    fy21_adj_ebitda = 1448  # $M
    litigation_net_charge_addback = 766  # $M
    fy21_unadjusted_ebitda = fy21_adj_ebitda - litigation_net_charge_addback  # $682M
    
    addback_pct_of_adj_ebitda = litigation_net_charge_addback / fy21_adj_ebitda
    addback_pct_of_unadjusted = litigation_net_charge_addback / fy21_unadjusted_ebitda
    
    ev_ebitda_multiple_low = 28.0
    ev_ebitda_multiple_high = 36.0
    implied_ev_impact_low = litigation_net_charge_addback * ev_ebitda_multiple_low
    implied_ev_impact_high = litigation_net_charge_addback * ev_ebitda_multiple_high
    
    print(f"FY21 Adjusted EBITDA: ${fy21_adj_ebitda:,.0f}M")
    print(f"Litigation Settlement Add-Back: ${litigation_net_charge_addback:,.0f}M ({addback_pct_of_adj_ebitda:.2%} of Adj EBITDA)")
    print(f"Implied EV Impact at 28x-36x: ${implied_ev_impact_low:,.0f}M to ${implied_ev_impact_high:,.0f}M")
    
    print("\n--- 3. Valuation & Fairness Opinion Parameters ---")
    fairness_params = {
        "goldman_sachs": {
            "wacc_discount_rate_range": [0.10, 0.12],
            "cost_of_equity": 0.114,
            "exit_terminal_ebitda_multiples": [10.0, 15.0],
            "implied_perpetuity_growth_rates": [0.056, 0.090],
            "ltm_ev_ebitda_peer_multiples": [28.2, 35.7],
            "discounting_convention": "mid-year"
        },
        "jp_morgan": {
            "wacc_discount_rate_range": [0.1025, 0.1125],
            "terminal_perpetuity_growth_rates": [0.060, 0.070],
            "ltm_ev_ebitda_peer_multiples": [28.0, 36.0],
            "discounting_convention": "mid-year"
        }
    }
    
    print("\n--- 4. Off-Balance-Sheet & Window Dressing Mechanics (Lehman Repo 105) ---")
    repo105_data = {
        "examiner_report": "Anton R. Valukas Report, Jenner & Block LLP, In re Lehman Brothers Holdings Inc.",
        "accounting_standard_exploited": "SFAS 140 (Accounting for Transfers and Servicing of Financial Assets)",
        "haircut_overcollateralization_rule": {
            "equities_haircut_pct": 105.0,
            "fixed_income_haircut_pct": 108.0,
            "legal_fiction": "Surrender of control under English law true-sale opinion (Linklaters) despite operational intent to repurchase"
        },
        "quarterly_derecognition_scale_billions": {
            "Q4_2007_Nov": 38.6,
            "Q1_2008_Feb": 49.1,
            "Q2_2008_May": 50.38
        },
        "timing_dynamics": {
            "execution_lead_days_prior_to_quarter_end": [2, 3],
            "unwind_lag_days_after_quarter_start": [2, 4],
            "reversal_mechanism": "Cash returned plus repo interest to re-acquire securities into inventory"
        },
        "leverage_distortion_q2_2008": {
            "reported_net_leverage": 10.2,
            "actual_net_leverage_without_repo105": 12.1,
            "net_leverage_suppression_pct": (12.1 - 10.2) / 12.1,
            "reported_gross_leverage": 12.1,
            "actual_gross_leverage_without_repo105": 13.9,
            "gross_leverage_suppression_pct": (13.9 - 12.1) / 13.9
        }
    }
    
    mna_qoe_catalog = {
        "metadata": {
            "source_documents": [
                "SEC Form DEFM14A Definitive Merger Proxy Statement (Twitter, Inc. / Elon Musk, 2022)",
                "Examiner Anton Valukas Report on Lehman Brothers Holdings Inc. (SDNY Bankruptcy, 2010)"
            ],
            "domain": "M&A Advisory, Adjusted EBITDA Bridges, Net Working Capital, and Window-Dressing Mechanics"
        },
        "prospective_ebitda_and_cash_flow_bridge": {
            "projection_table": df_proj.to_dict(orient="records"),
            "growth_rates": {
                "revenue_cagr_2022_2027": cagr_revenue,
                "adj_ebitda_cagr_2022_2027": cagr_adj_ebitda
            },
            "stock_based_compensation_dilution": {
                "cumulative_6yr_sbc_millions": total_sbc,
                "sbc_as_pct_of_cumulative_revenue": total_sbc / total_rev,
                "cumulative_mgmt_ufcf_millions": total_mgmt_ufcf,
                "cumulative_banker_ufcf_millions": total_banker_ufcf,
                "sbc_cash_flow_dilution_millions": total_ufcf_sbc_dilution,
                "sbc_dilution_percentage": total_ufcf_sbc_dilution / total_mgmt_ufcf
            },
            "working_capital_drag": {
                "cumulative_nwc_drain_millions": total_nwc_drain,
                "peak_annual_nwc_drain_year": "2023E",
                "peak_annual_nwc_drain_millions": -259
            }
        },
        "historical_ebitda_normalizations": {
            "fy21_reported_adj_ebitda_millions": fy21_adj_ebitda,
            "one_time_litigation_addback_millions": litigation_net_charge_addback,
            "unadjusted_base_ebitda_millions": fy21_unadjusted_ebitda,
            "addback_share_of_adj_ebitda": addback_pct_of_adj_ebitda,
            "addback_share_of_unadjusted_ebitda": addback_pct_of_unadjusted,
            "transaction_valuation_multiple_range": [ev_ebitda_multiple_low, ev_ebitda_multiple_high],
            "implied_enterprise_value_swing_millions": [implied_ev_impact_low, implied_ev_impact_high]
        },
        "fairness_opinion_valuation_parameters": fairness_params,
        "forensic_window_dressing_repo105": repo105_data
    }
    
    out_json = os.path.join(out_dir, "mna_qoe_parameters.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(mna_qoe_catalog, f, indent=2)
    print(f"\nSaved M&A QoE Parameters to: {out_json}")

if __name__ == "__main__":
    extract_mna_qoe_signals()
