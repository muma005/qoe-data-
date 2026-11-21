import os
import json
import numpy as np
import pandas as pd

def run_deep_forensics():
    base_dir = r"research/original_datasets/financial_accounting/sec_fsds_2024q3"
    out_dir = r"research/accounting_signals"
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- 1. Ingesting Submissions (sub.txt) with Restatements and AFS ---")
    sub_path = os.path.join(base_dir, "sub.txt")
    df_sub = pd.read_csv(sub_path, sep="\t", encoding="latin1", low_memory=False)
    valid_forms = ["10-Q", "10-K", "10-Q/A", "10-K/A"]
    df_sub = df_sub[df_sub["form"].isin(valid_forms)].copy()
    
    # Map sectors
    def get_sector(sic):
        if pd.isna(sic): return "Unclassified"
        try: sic = int(sic)
        except: return "Unclassified"
        if 2000 <= sic <= 3999:
            if 2830 <= sic <= 2836: return "Life Sciences"
            elif 3570 <= sic <= 3679: return "Tech Hardware"
            else: return "Manufacturing"
        elif 7000 <= sic <= 7399:
            if 7370 <= sic <= 7379: return "Software & SaaS"
            else: return "Services"
        elif 5000 <= sic <= 5999: return "Retail & Wholesale"
        elif 6000 <= sic <= 6799: return "Finance & Real Estate"
        elif 4000 <= sic <= 4999: return "Transport & Utilities"
        else: return "Other"

    df_sub["sector"] = df_sub["sic"].apply(get_sector)
    valid_adsh = set(df_sub["adsh"])
    meta_dict = df_sub.set_index("adsh")[["cik", "name", "form", "afs", "sector", "prevrpt", "period", "fye"]].to_dict(orient="index")
    
    print(f"Total valid filings: {len(df_sub)}, Restatements (prevrpt==1): {df_sub['prevrpt'].sum()}")
    
    print("\n--- 2. Targeted Streaming Extraction from num.txt for Add-Backs & Line Items ---")
    num_path = os.path.join(base_dir, "num.txt")
    
    # Primary tags
    primary_tags = {
        # Revenues
        "Revenues": "rev",
        "RevenueFromContractWithCustomerExcludingAssessedTax": "rev",
        "SalesRevenueNet": "rev",
        # COGS
        "CostOfGoodsAndServicesSold": "cogs",
        "CostOfRevenue": "cogs",
        # Operating income
        "OperatingIncomeLoss": "ebit",
        # Net Income
        "NetIncomeLoss": "ni",
        "ProfitLoss": "ni",
        # CFO
        "NetCashProvidedByUsedInOperatingActivities": "cfo",
        # Balance sheet
        "Assets": "assets",
        "Liabilities": "liab",
        "StockholdersEquity": "equity",
        "CashAndCashEquivalentsAtCarryingValue": "cash",
        "AccountsReceivableNetCurrent": "ar",
        "InventoryNet": "inv",
        "AccountsPayableCurrent": "ap",
        "Goodwill": "goodwill",
        # Forensic Add-backs
        "AdjustmentsToAdditionalPaidInCapitalSharebasedCompensationRequisiteServicePeriodRecognitionValue": "sbc",
        "ShareBasedCompensation": "sbc",
        "AllocatedShareBasedCompensationExpense": "sbc",
        "DepreciationDepletionAndAmortization": "dda",
        "DepreciationAndAmortization": "dda",
        "AmortizationOfIntangibleAssets": "amort",
        "Depreciation": "depr",
        "RestructuringCharges": "restruct",
        "RestructuringSettlementAndImpairmentProvisions": "restruct",
        "AssetImpairmentCharges": "impair",
        "GoodwillImpairmentLoss": "goodwill_impair",
        "ContractWithCustomerAssetNetCurrent": "contract_asset"
    }
    
    target_set = set(primary_tags.keys())
    
    filing_records = {}
    # Track time periods for YoY / QoQ comparisons: filing -> tag -> ddate -> val
    filing_dates = {}
    
    chunksize = 500000
    for chunk in pd.read_csv(num_path, sep="\t", encoding="latin1", chunksize=chunksize, low_memory=False,
                             usecols=["adsh", "tag", "ddate", "qtrs", "uom", "value"]):
        filtered = chunk[(chunk["adsh"].isin(valid_adsh)) & 
                         (chunk["uom"] == "USD") & 
                         (chunk["tag"].isin(target_set))]
        
        for r in filtered.itertuples(index=False):
            adsh = r.adsh
            tag = r.tag
            ddate = r.ddate
            qtrs = r.qtrs
            val = r.value
            concept = primary_tags[tag]
            
            if adsh not in filing_records:
                filing_records[adsh] = {}
                filing_dates[adsh] = {}
                
            # Store in filing_dates for multi-period growth tracking
            if concept not in filing_dates[adsh]:
                filing_dates[adsh][concept] = {}
            if qtrs in [0, 1, 4]:
                filing_dates[adsh][concept][(ddate, qtrs)] = val
                
            # Base record tracking (prefer largest or qtrs==1)
            if concept in ["sbc", "dda", "amort", "depr", "restruct", "impair", "goodwill_impair"]:
                # Sum or take max of positive add-backs
                if val > 0:
                    filing_records[adsh][concept] = max(filing_records[adsh].get(concept, 0.0), val)
            elif concept in ["rev", "cogs", "ebit", "ni", "cfo"]:
                if concept not in filing_records[adsh] or (qtrs == 1 and abs(val) > 0):
                    filing_records[adsh][concept] = val
            else:
                if concept not in filing_records[adsh] or abs(val) > abs(filing_records[adsh][concept]):
                    filing_records[adsh][concept] = val

    print(f"Extracted deep financial data across {len(filing_records)} filings.")
    
    print("\n--- 3. Structuring Comprehensive Forensic Metrics ---")
    data = []
    for adsh, facts in filing_records.items():
        meta = meta_dict.get(adsh, {})
        row = {
            "adsh": adsh,
            "cik": meta.get("cik"),
            "name": meta.get("name"),
            "form": meta.get("form"),
            "afs": meta.get("afs"),
            "sector": meta.get("sector"),
            "prevrpt": meta.get("prevrpt", 0),
            "period": meta.get("period"),
            # Core financial items
            "rev": facts.get("rev"),
            "cogs": facts.get("cogs"),
            "ebit": facts.get("ebit"),
            "ni": facts.get("ni"),
            "cfo": facts.get("cfo"),
            "assets": facts.get("assets"),
            "liab": facts.get("liab"),
            "equity": facts.get("equity"),
            "cash": facts.get("cash", 0.0),
            "ar": facts.get("ar", 0.0),
            "inv": facts.get("inv", 0.0),
            "ap": facts.get("ap", 0.0),
            "goodwill": facts.get("goodwill", 0.0),
            # Add-backs
            "sbc": facts.get("sbc", 0.0),
            "dda": facts.get("dda", 0.0),
            "amort": facts.get("amort", 0.0),
            "depr": facts.get("depr", 0.0),
            "restruct": facts.get("restruct", 0.0),
            "impair": facts.get("impair", 0.0),
            "goodwill_impair": facts.get("goodwill_impair", 0.0),
            "contract_asset": facts.get("contract_asset", 0.0)
        }
        
        # Calculate YoY growth if multiple dates exist
        dates = filing_dates.get(adsh, {})
        # AR growth vs Rev growth
        ar_dates = sorted(dates.get("ar", {}).keys(), key=lambda x: x[0], reverse=True)
        rev_dates = sorted(dates.get("rev", {}).keys(), key=lambda x: x[0], reverse=True)
        if len(ar_dates) >= 2 and len(rev_dates) >= 2:
            ar_curr, ar_prior = dates["ar"][ar_dates[0]], dates["ar"][ar_dates[1]]
            rev_curr, rev_prior = dates["rev"][rev_dates[0]], dates["rev"][rev_dates[1]]
            if ar_prior > 10000 and rev_prior > 10000:
                row["ar_growth"] = (ar_curr - ar_prior) / ar_prior
                row["rev_growth"] = (rev_curr - rev_prior) / rev_prior
                row["ar_rev_growth_spread"] = row["ar_growth"] - row["rev_growth"]
            else:
                row["ar_growth"] = row["rev_growth"] = row["ar_rev_growth_spread"] = np.nan
        else:
            row["ar_growth"] = row["rev_growth"] = row["ar_rev_growth_spread"] = np.nan

        # Inv growth vs COGS growth
        inv_dates = sorted(dates.get("inv", {}).keys(), key=lambda x: x[0], reverse=True)
        cogs_dates = sorted(dates.get("cogs", {}).keys(), key=lambda x: x[0], reverse=True)
        if len(inv_dates) >= 2 and len(cogs_dates) >= 2:
            inv_curr, inv_prior = dates["inv"][inv_dates[0]], dates["inv"][inv_dates[1]]
            cogs_curr, cogs_prior = dates["cogs"][cogs_dates[0]], dates["cogs"][cogs_dates[1]]
            if inv_prior > 10000 and cogs_prior > 10000:
                row["inv_growth"] = (inv_curr - inv_prior) / inv_prior
                row["cogs_growth"] = (cogs_curr - cogs_prior) / cogs_prior
                row["inv_cogs_growth_spread"] = row["inv_growth"] - row["cogs_growth"]
            else:
                row["inv_growth"] = row["cogs_growth"] = row["inv_cogs_growth_spread"] = np.nan
        else:
            row["inv_growth"] = row["cogs_growth"] = row["inv_cogs_growth_spread"] = np.nan

        data.append(row)
        
    df = pd.DataFrame(data)
    print(f"Constructed master dataframe with {len(df)} filings.")
    
    # 1. EBITDA & Adjusted EBITDA Construction
    # DDA total: dda or (depr + amort)
    df["total_dda"] = df["dda"].combine_first(df["depr"] + df["amort"]).fillna(0.0)
    df["standard_ebitda"] = df["ebit"] + df["total_dda"]
    # Total Add-backs: SBC + Restructuring + Impairments
    df["total_addbacks"] = df["sbc"] + df["restruct"] + df["impair"] + df["goodwill_impair"]
    df["adjusted_ebitda"] = df["standard_ebitda"] + df["total_addbacks"]
    
    has_rev = (df["rev"] > 100000)
    df["ebit_margin"] = np.where(has_rev & df["ebit"].notna(), df["ebit"] / df["rev"], np.nan)
    df["ebitda_margin"] = np.where(has_rev & df["standard_ebitda"].notna(), df["standard_ebitda"] / df["rev"], np.nan)
    df["adj_ebitda_margin"] = np.where(has_rev & df["adjusted_ebitda"].notna(), df["adjusted_ebitda"] / df["rev"], np.nan)
    df["ebitda_expansion_spread"] = df["adj_ebitda_margin"] - df["ebit_margin"]
    
    # Add-backs intensity (% of revenue)
    df["sbc_to_rev"] = np.where(has_rev & (df["sbc"] > 0), df["sbc"] / df["rev"], np.nan)
    df["restruct_to_rev"] = np.where(has_rev & (df["restruct"] > 0), df["restruct"] / df["rev"], np.nan)
    df["impair_to_assets"] = np.where((df["assets"] > 100000) & (df["impair"] > 0), df["impair"] / df["assets"], np.nan)
    
    # 2. Channel Stuffing & Working Capital Divergence Flags
    # Channel stuffing: AR growth exceeds Rev growth by > 15 percentage points
    df["flag_channel_stuffing"] = np.where(df["ar_rev_growth_spread"].notna(), df["ar_rev_growth_spread"] > 0.15, np.nan)
    # Inventory accumulation: Inv growth exceeds COGS growth by > 15 percentage points
    df["flag_inventory_bloat"] = np.where(df["inv_cogs_growth_spread"].notna(), df["inv_cogs_growth_spread"] > 0.15, np.nan)
    
    # Contract asset presence (unbilled revenues)
    df["contract_asset_to_rev"] = np.where(has_rev & (df["contract_asset"] > 0), df["contract_asset"] / df["rev"], np.nan)
    
    # 3. Restatement Forensic Autopsy (prevrpt==1 vs prevrpt==0)
    restatements_df = df[df["prevrpt"] == 1]
    normal_df = df[df["prevrpt"] == 0]
    
    restatement_autopsy = {
        "restated_filings_count": int(len(restatements_df)),
        "normal_filings_count": int(len(normal_df)),
        "median_revenue": {
            "restated": float(restatements_df["rev"].median()) if restatements_df["rev"].notna().sum() > 5 else None,
            "normal": float(normal_df["rev"].median()) if normal_df["rev"].notna().sum() > 5 else None
        },
        "median_operating_margin": {
            "restated": float(restatements_df["ebit_margin"].median()) if restatements_df["ebit_margin"].notna().sum() > 5 else None,
            "normal": float(normal_df["ebit_margin"].median()) if normal_df["ebit_margin"].notna().sum() > 5 else None
        },
        "negative_equity_rate_pct": {
            "restated": float((restatements_df["equity"] < 0).mean() * 100),
            "normal": float((normal_df["equity"] < 0).mean() * 100)
        },
        "paper_profit_rate_pct": {
            "restated": float(((restatements_df["ni"] > 0) & (restatements_df["cfo"] < 0)).mean() * 100),
            "normal": float(((normal_df["ni"] > 0) & (normal_df["cfo"] < 0)).mean() * 100)
        }
    }
    
    # 4. Forensic Add-Back Prevalence & Intensity Statistics
    sbc_filings = df[df["sbc"] > 0]
    restruct_filings = df[df["restruct"] > 0]
    impair_filings = df[df["impair"] > 0]
    goodwill_impair_filings = df[df["goodwill_impair"] > 0]
    
    addback_stats = {
        "share_based_compensation": {
            "reporting_filings_count": int(len(sbc_filings)),
            "prevalence_rate_pct": float(len(sbc_filings) / len(df) * 100),
            "median_sbc_usd": float(sbc_filings["sbc"].median()),
            "mean_sbc_usd": float(sbc_filings["sbc"].mean()),
            "median_sbc_to_revenue_pct": float(sbc_filings["sbc_to_rev"].median() * 100) if sbc_filings["sbc_to_rev"].notna().sum() > 10 else None,
            "p75_sbc_to_revenue_pct": float(sbc_filings["sbc_to_rev"].quantile(0.75) * 100) if sbc_filings["sbc_to_rev"].notna().sum() > 10 else None,
            "p90_sbc_to_revenue_pct": float(sbc_filings["sbc_to_rev"].quantile(0.90) * 100) if sbc_filings["sbc_to_rev"].notna().sum() > 10 else None
        },
        "restructuring_charges": {
            "reporting_filings_count": int(len(restruct_filings)),
            "prevalence_rate_pct": float(len(restruct_filings) / len(df) * 100),
            "median_restruct_usd": float(restruct_filings["restruct"].median()),
            "mean_restruct_usd": float(restruct_filings["restruct"].mean()),
            "median_restruct_to_revenue_pct": float(restruct_filings["restruct_to_rev"].median() * 100) if restruct_filings["restruct_to_rev"].notna().sum() > 10 else None
        },
        "asset_impairments": {
            "reporting_filings_count": int(len(impair_filings)),
            "prevalence_rate_pct": float(len(impair_filings) / len(df) * 100),
            "median_impairment_usd": float(impair_filings["impair"].median()),
            "mean_impairment_usd": float(impair_filings["impair"].mean()),
            "median_impair_to_assets_pct": float(impair_filings["impair_to_assets"].median() * 100) if impair_filings["impair_to_assets"].notna().sum() > 10 else None
        },
        "goodwill_impairments": {
            "reporting_filings_count": int(len(goodwill_impair_filings)),
            "prevalence_rate_pct": float(len(goodwill_impair_filings) / len(df) * 100),
            "median_goodwill_impair_usd": float(goodwill_impair_filings["goodwill_impair"].median()),
            "mean_goodwill_impair_usd": float(goodwill_impair_filings["goodwill_impair"].mean())
        }
    }
    
    # 5. Channel Stuffing & Working Capital Bloat Prevalence
    growth_test_ar = df["flag_channel_stuffing"].dropna()
    growth_test_inv = df["flag_inventory_bloat"].dropna()
    
    working_capital_forensics = {
        "channel_stuffing_risk": {
            "companies_evaluated": int(len(growth_test_ar)),
            "positive_channel_stuffing_flags": int(growth_test_ar.sum()),
            "channel_stuffing_prevalence_pct": float(growth_test_ar.mean() * 100),
            "median_ar_rev_growth_spread": float(df["ar_rev_growth_spread"].median()),
            "p75_ar_rev_growth_spread": float(df["ar_rev_growth_spread"].quantile(0.75)),
            "p90_ar_rev_growth_spread": float(df["ar_rev_growth_spread"].quantile(0.90))
        },
        "inventory_bloat_risk": {
            "companies_evaluated": int(len(growth_test_inv)),
            "positive_inventory_bloat_flags": int(growth_test_inv.sum()),
            "inventory_bloat_prevalence_pct": float(growth_test_inv.mean() * 100),
            "median_inv_cogs_growth_spread": float(df["inv_cogs_growth_spread"].median()),
            "p75_inv_cogs_growth_spread": float(df["inv_cogs_growth_spread"].quantile(0.75)),
            "p90_inv_cogs_growth_spread": float(df["inv_cogs_growth_spread"].quantile(0.90))
        }
    }
    
    # 6. Sector-Specific EBITDA Bridge Expansion
    sector_ebitda_bridges = {}
    for sec in ["Software & SaaS", "Manufacturing", "Tech Hardware", "Life Sciences", "Services", "Retail & Wholesale"]:
        sec_df = df[df["sector"] == sec]
        has_sec_rev = sec_df["rev"] > 100000
        sec_ebit = sec_df.loc[has_sec_rev, "ebit_margin"].median()
        sec_ebitda = sec_df.loc[has_sec_rev, "ebitda_margin"].median()
        sec_adj_ebitda = sec_df.loc[has_sec_rev, "adj_ebitda_margin"].median()
        sector_ebitda_bridges[sec] = {
            "filings": int(len(sec_df)),
            "median_ebit_margin": float(sec_ebit) if pd.notna(sec_ebit) else None,
            "median_standard_ebitda_margin": float(sec_ebitda) if pd.notna(sec_ebitda) else None,
            "median_adjusted_ebitda_margin": float(sec_adj_ebitda) if pd.notna(sec_adj_ebitda) else None,
            "median_margin_expansion_bps": float((sec_adj_ebitda - sec_ebit) * 10000) if (pd.notna(sec_adj_ebitda) and pd.notna(sec_ebit)) else None
        }

    # 7. Extract 3 Concrete Corporate Forensic Profiles
    # Profile A: SaaS company with heavy SBC & negative EBIT
    saas_candidates = df[(df["sector"] == "Software & SaaS") & (df["rev"] > 50000000) & (df["sbc"] > 10000000) & (df["ebit"] < 0)]
    cand_a = saas_candidates.sort_values(by="rev", ascending=False).iloc[0].to_dict() if len(saas_candidates) > 0 else {}
    
    # Profile B: Manufacturing company with heavy inventory & working capital
    mfg_candidates = df[(df["sector"] == "Manufacturing") & (df["inv"] > 100000000) & (df["rev"] > 200000000) & (df["cfo"] < 0)]
    cand_b = mfg_candidates.sort_values(by="inv", ascending=False).iloc[0].to_dict() if len(mfg_candidates) > 0 else {}
    
    # Profile C: Restating company with negative equity
    restat_candidates = df[(df["prevrpt"] == 1) & (df["equity"] < 0) & (df["rev"] > 1000000)]
    cand_c = restat_candidates.sort_values(by="rev", ascending=False).iloc[0].to_dict() if len(restat_candidates) > 0 else {}
    
    profiles = {
        "profile_a_saas_sbc_swing": {
            "name": cand_a.get("name"),
            "cik": cand_a.get("cik"),
            "adsh": cand_a.get("adsh"),
            "revenue": cand_a.get("rev"),
            "ebit": cand_a.get("ebit"),
            "cfo": cand_a.get("cfo"),
            "sbc": cand_a.get("sbc"),
            "total_dda": cand_a.get("total_dda"),
            "adjusted_ebitda": cand_a.get("adjusted_ebitda")
        },
        "profile_b_mfg_working_capital_trap": {
            "name": cand_b.get("name"),
            "cik": cand_b.get("cik"),
            "adsh": cand_b.get("adsh"),
            "revenue": cand_b.get("rev"),
            "cogs": cand_b.get("cogs"),
            "inventory": cand_b.get("inv"),
            "ar": cand_b.get("ar"),
            "ap": cand_b.get("ap"),
            "ebit": cand_b.get("ebit"),
            "cfo": cand_b.get("cfo")
        },
        "profile_c_restatement_distress": {
            "name": cand_c.get("name"),
            "cik": cand_c.get("cik"),
            "adsh": cand_c.get("adsh"),
            "revenue": cand_c.get("rev"),
            "ebit": cand_c.get("ebit"),
            "net_income": cand_c.get("ni"),
            "equity": cand_c.get("equity"),
            "liabilities": cand_c.get("liab")
        }
    }

    full_results = {
        "metadata": {
            "title": "Deep Forensic Corporate Financial Reporting Study",
            "source": "SEC EDGAR FSDS 2024 Q3 (US-GAAP Filings)",
            "total_filings_evaluated": len(df)
        },
        "addback_prevalence_and_intensity": addback_stats,
        "working_capital_forensics": working_capital_forensics,
        "restatement_autopsy": restatement_autopsy,
        "sector_ebitda_bridges": sector_ebitda_bridges,
        "archetype_profiles": profiles
    }
    
    out_json = os.path.join(out_dir, "deep_financial_reporting_forensics.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2)
        
    print(f"\nSaved Deep Forensic Financial Reporting Results to: {out_json}")
    
    print("\n================== DEEP FORENSIC HIGHLIGHTS ==================")
    print(f"Share-Based Compensation Prevalence: {addback_stats['share_based_compensation']['prevalence_rate_pct']:.2f}% (Median SBC: ${addback_stats['share_based_compensation']['median_sbc_usd']:,.0f})")
    print(f"SBC % of Revenue (Software/Tech P90): {addback_stats['share_based_compensation']['p90_sbc_to_revenue_pct']:.2f}%")
    print(f"Channel Stuffing Flag Prevalence (AR YoY > Rev YoY + 15%): {working_capital_forensics['channel_stuffing_risk']['channel_stuffing_prevalence_pct']:.2f}%")
    print(f"Inventory Bloat Flag Prevalence (Inv YoY > COGS YoY + 15%): {working_capital_forensics['inventory_bloat_risk']['inventory_bloat_prevalence_pct']:.2f}%")
    print(f"Restatement Negative Equity Rate: {restatement_autopsy['negative_equity_rate_pct']['restated']:.2f}% vs Normal: {restatement_autopsy['negative_equity_rate_pct']['normal']:.2f}%")
    print("==============================================================")

if __name__ == "__main__":
    run_deep_forensics()
