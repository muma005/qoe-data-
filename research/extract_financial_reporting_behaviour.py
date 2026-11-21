import os
import json
import numpy as np
import pandas as pd

def run_financial_reporting_analysis():
    base_dir = r"research/original_datasets/financial_accounting/sec_fsds_2024q3"
    out_dir = r"research/accounting_signals"
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- 1. Loading Submissions and Industry Mapping (sub.txt) ---")
    sub_path = os.path.join(base_dir, "sub.txt")
    df_sub = pd.read_csv(sub_path, sep="\t", encoding="latin1", low_memory=False)
    
    # Filter for operating reports (10-Q, 10-K, 10-Q/A, 10-K/A)
    valid_forms = ["10-Q", "10-K", "10-Q/A", "10-K/A"]
    df_sub = df_sub[df_sub["form"].isin(valid_forms)].copy()
    print(f"Total valid periodic filings: {len(df_sub)}")
    
    # Map SIC to major sector divisions
    def get_sector(sic):
        if pd.isna(sic):
            return "Unclassified / Other"
        try:
            sic = int(sic)
        except:
            return "Unclassified / Other"
        if 100 <= sic <= 999:
            return "Agriculture & Forestry"
        elif 1000 <= sic <= 1499:
            return "Mining & Extraction"
        elif 1500 <= sic <= 1799:
            return "Construction"
        elif 2000 <= sic <= 3999:
            if 2830 <= sic <= 2836:
                return "Life Sciences & Pharma"
            elif 3570 <= sic <= 3679:
                return "Technology Hardware & Electronics"
            else:
                return "Manufacturing & Industrial"
        elif 4000 <= sic <= 4999:
            return "Transportation & Utilities"
        elif 5000 <= sic <= 5199:
            return "Wholesale Trade"
        elif 5200 <= sic <= 5999:
            return "Retail Trade"
        elif 6000 <= sic <= 6799:
            return "Finance, Banking & Real Estate"
        elif 7000 <= sic <= 8999:
            if 7370 <= sic <= 7379:
                return "Software & Tech Services"
            elif 8000 <= sic <= 8099:
                return "Healthcare Services"
            else:
                return "Commercial & Professional Services"
        elif 9000 <= sic <= 9999:
            return "Public Administration"
        else:
            return "Unclassified / Other"

    df_sub["sector"] = df_sub["sic"].apply(get_sector)
    sector_counts = df_sub["sector"].value_counts().to_dict()
    print(f"Filings by Sector:\n{sector_counts}")
    
    valid_adsh_set = set(df_sub["adsh"])
    filing_meta = df_sub.set_index("adsh")[["cik", "name", "form", "afs", "sector", "fye", "period"]].to_dict(orient="index")
    
    print("\n--- 2. Streaming Fact Extraction from num.txt ---")
    num_path = os.path.join(base_dir, "num.txt")
    
    # Key tags to target
    tag_mapping = {
        # Revenues
        "Revenues": "revenue",
        "RevenueFromContractWithCustomerExcludingAssessedTax": "revenue",
        "SalesRevenueNet": "revenue",
        "RevenueFromContractWithCustomerIncludingAssessedTax": "revenue",
        # COGS
        "CostOfGoodsAndServicesSold": "cogs",
        "CostOfRevenue": "cogs",
        # Gross profit
        "GrossProfit": "gross_profit",
        # Operating income
        "OperatingIncomeLoss": "operating_income",
        # Net income
        "NetIncomeLoss": "net_income",
        "ProfitLoss": "net_income",
        # Cash flow from operations
        "NetCashProvidedByUsedInOperatingActivities": "cfo",
        # Accounts receivable
        "AccountsReceivableNetCurrent": "ar",
        "AccountsReceivableNet": "ar",
        "AccountsReceivableTradeCurrent": "ar",
        # Inventory
        "InventoryNet": "inventory",
        # Accounts payable
        "AccountsPayableCurrent": "ap",
        "AccountsPayableAndAccruedLiabilitiesCurrent": "ap",
        # Total assets
        "Assets": "assets",
        # Total liabilities
        "Liabilities": "liabilities",
        # Equity
        "StockholdersEquity": "equity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest": "equity",
        # Goodwill
        "Goodwill": "goodwill",
        # Cash
        "CashAndCashEquivalentsAtCarryingValue": "cash",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": "cash"
    }
    
    target_tags = set(tag_mapping.keys())
    
    # We will accumulate facts per filing
    filing_data = {}
    
    chunksize = 500000
    rows_processed = 0
    print("Reading num.txt in 500k chunks...")
    for chunk in pd.read_csv(num_path, sep="\t", encoding="latin1", chunksize=chunksize, low_memory=False,
                             usecols=["adsh", "tag", "qtrs", "uom", "value"]):
        rows_processed += len(chunk)
        # Filter for valid adsh, USD uom, and target tags
        c_filtered = chunk[(chunk["adsh"].isin(valid_adsh_set)) & 
                           (chunk["uom"] == "USD") & 
                           (chunk["tag"].isin(target_tags))]
        
        for row in c_filtered.itertuples(index=False):
            adsh = row.adsh
            tag = row.tag
            qtrs = row.qtrs
            val = row.value
            concept = tag_mapping[tag]
            
            if adsh not in filing_data:
                filing_data[adsh] = {}
                
            # For flow items (revenue, cogs, operating_income, net_income, cfo), prefer qtrs == 1 (quarterly) or qtrs == 4 (annual)
            # or track both
            if concept in ["revenue", "cogs", "gross_profit", "operating_income", "net_income", "cfo"]:
                # If qtrs in [1, 2, 3, 4], store with priority for qtrs==1 or latest
                key = f"{concept}_{qtrs}q"
                if key not in filing_data[adsh] or abs(val) > abs(filing_data[adsh][key]):
                    filing_data[adsh][key] = val
                # Also store generic concept if not set
                if concept not in filing_data[adsh]:
                    filing_data[adsh][concept] = val
                elif qtrs == 1: # prefer 1 quarter for quarterly reports
                    filing_data[adsh][concept] = val
            else:
                # Stock/Balance sheet items (qtrs == 0)
                if concept not in filing_data[adsh] or abs(val) > abs(filing_data[adsh][concept]):
                    filing_data[adsh][concept] = val
                    
    print(f"Finished parsing {rows_processed:,} facts from num.txt.")
    print(f"Total filings with extracted financial facts: {len(filing_data)}")
    
    print("\n--- 3. Computing Financial Reporting & Quality of Earnings Metrics ---")
    records = []
    for adsh, facts in filing_data.items():
        meta = filing_meta.get(adsh, {})
        rec = {
            "adsh": adsh,
            "cik": meta.get("cik"),
            "name": meta.get("name"),
            "form": meta.get("form"),
            "afs": meta.get("afs"),
            "sector": meta.get("sector"),
            "revenue": facts.get("revenue"),
            "cogs": facts.get("cogs"),
            "gross_profit": facts.get("gross_profit"),
            "operating_income": facts.get("operating_income"),
            "net_income": facts.get("net_income"),
            "cfo": facts.get("cfo"),
            "ar": facts.get("ar"),
            "inventory": facts.get("inventory"),
            "ap": facts.get("ap"),
            "assets": facts.get("assets"),
            "liabilities": facts.get("liabilities"),
            "equity": facts.get("equity"),
            "goodwill": facts.get("goodwill", 0.0),
            "cash": facts.get("cash", 0.0)
        }
        records.append(rec)
        
    df = pd.DataFrame(records)
    print(f"Dataframe constructed with {len(df)} filings.")
    
    # Fill gross profit if missing and revenue & cogs exist
    df["gross_profit_calc"] = df["gross_profit"].combine_first(df["revenue"] - df["cogs"])
    
    # 1. Profitability Margins
    # Filter positive revenue > $100k
    has_rev = df["revenue"] > 100000
    df["gross_margin"] = np.where(has_rev & df["gross_profit_calc"].notna(), df["gross_profit_calc"] / df["revenue"], np.nan)
    df["operating_margin"] = np.where(has_rev & df["operating_income"].notna(), df["operating_income"] / df["revenue"], np.nan)
    df["net_margin"] = np.where(has_rev & df["net_income"].notna(), df["net_income"] / df["revenue"], np.nan)
    
    # 2. Sloan Accruals & Quality of Earnings Metrics
    # Accruals = Net Income - Operating Cash Flow
    has_ni_cfo = df["net_income"].notna() & df["cfo"].notna()
    has_assets = df["assets"] > 100000
    df["sloan_accruals"] = np.where(has_ni_cfo, df["net_income"] - df["cfo"], np.nan)
    df["accruals_to_assets"] = np.where(has_ni_cfo & has_assets, df["sloan_accruals"] / df["assets"], np.nan)
    
    # Cash Conversion Ratio: CFO / Operating Income
    has_opinc = df["operating_income"].notna() & (df["operating_income"] != 0)
    df["cfo_to_operating_income"] = np.where(has_opinc & df["cfo"].notna(), df["cfo"] / df["operating_income"], np.nan)
    
    # Cash Conversion Ratio: CFO / Net Income
    has_ni = df["net_income"].notna() & (df["net_income"] != 0)
    df["cfo_to_net_income"] = np.where(has_ni & df["cfo"].notna(), df["cfo"] / df["net_income"], np.nan)
    
    # Negative Cash Flow Divergence (QoE Red Flag: Net Income > 0 but CFO < 0)
    df["flag_ni_pos_cfo_neg"] = np.where(has_ni_cfo, (df["net_income"] > 0) & (df["cfo"] < 0), np.nan)
    
    # Operating Loss with Positive Cash Flow (CFO > 0 but Operating Income < 0)
    df["flag_opinc_neg_cfo_pos"] = np.where(has_opinc & df["cfo"].notna(), (df["operating_income"] < 0) & (df["cfo"] > 0), np.nan)
    
    # 3. Working Capital Ratios (DSO, DIO, DPO)
    # DSO = (AR / Revenue) * 91.25 (assuming quarterly revenue) or * 365 (annual)
    # Since most are 10-Q (quarterly), we annualize revenue * 4 for days calculation
    annualized_rev = df["revenue"] * 4
    annualized_cogs = df["cogs"] * 4
    
    has_ann_rev = annualized_rev > 100000
    has_ann_cogs = annualized_cogs > 100000
    
    df["dso_days"] = np.where(has_ann_rev & df["ar"].notna() & (df["ar"] >= 0), (df["ar"] / annualized_rev) * 365, np.nan)
    df["dio_days"] = np.where(has_ann_cogs & df["inventory"].notna() & (df["inventory"] >= 0), (df["inventory"] / annualized_cogs) * 365, np.nan)
    df["dpo_days"] = np.where(has_ann_cogs & df["ap"].notna() & (df["ap"] >= 0), (df["ap"] / annualized_cogs) * 365, np.nan)
    
    # Cash Conversion Cycle = DSO + DIO - DPO
    df["ccc_days"] = df["dso_days"] + df["dio_days"].fillna(0) - df["dpo_days"].fillna(0)
    
    # Net Working Capital = (AR + Inventory) - AP
    df["nwc_calc"] = df["ar"].fillna(0) + df["inventory"].fillna(0) - df["ap"].fillna(0)
    df["nwc_to_revenue"] = np.where(has_rev & (df["ar"].notna() | df["ap"].notna()), df["nwc_calc"] / annualized_rev, np.nan)
    
    # 4. Balance Sheet Health & Asset Quality
    df["goodwill_to_assets"] = np.where(has_assets & df["goodwill"].notna(), df["goodwill"] / df["assets"], np.nan)
    df["cash_to_assets"] = np.where(has_assets & df["cash"].notna(), df["cash"] / df["assets"], np.nan)
    df["liabilities_to_assets"] = np.where(has_assets & df["liabilities"].notna(), df["liabilities"] / df["assets"], np.nan)
    df["flag_negative_equity"] = np.where(df["equity"].notna(), df["equity"] < 0, np.nan)
    
    print("\n--- 4. Computing Empirical Distributions & Summary Stats ---")
    
    def get_stats(series, min_q=0.01, max_q=0.99):
        s = series.dropna()
        if len(s) == 0:
            return {}
        # Clip extreme outliers for mean/std if specified
        s_clipped = s[(s >= s.quantile(min_q)) & (s <= s.quantile(max_q))]
        return {
            "count": int(len(s)),
            "mean": float(s_clipped.mean()),
            "std": float(s_clipped.std()),
            "median": float(s.median()),
            "p10": float(s.quantile(0.10)),
            "p25": float(s.quantile(0.25)),
            "p75": float(s.quantile(0.75)),
            "p90": float(s.quantile(0.90)),
            "p95": float(s.quantile(0.95))
        }

    # Summary metrics across all companies
    overall_metrics = {
        "profitability_margins": {
            "gross_margin": get_stats(df["gross_margin"]),
            "operating_margin": get_stats(df["operating_margin"]),
            "net_margin": get_stats(df["net_margin"])
        },
        "quality_of_earnings_accruals": {
            "accruals_to_assets_ratio": get_stats(df["accruals_to_assets"]),
            "divergence_positive_ni_negative_cfo_pct": float(df["flag_ni_pos_cfo_neg"].mean() * 100),
            "divergence_negative_opinc_positive_cfo_pct": float(df["flag_opinc_neg_cfo_pos"].mean() * 100)
        },
        "working_capital_days": {
            "dso_days": get_stats(df["dso_days"]),
            "dio_days": get_stats(df["dio_days"]),
            "dpo_days": get_stats(df["dpo_days"]),
            "cash_conversion_cycle_days": get_stats(df["ccc_days"]),
            "nwc_to_revenue_ratio": get_stats(df["nwc_to_revenue"])
        },
        "balance_sheet_structure": {
            "goodwill_to_assets": get_stats(df["goodwill_to_assets"]),
            "cash_to_assets": get_stats(df["cash_to_assets"]),
            "liabilities_to_assets": get_stats(df["liabilities_to_assets"]),
            "negative_equity_rate_pct": float(df["flag_negative_equity"].mean() * 100)
        }
    }
    
    # Sector Breakdown
    sector_breakdown = {}
    top_sectors = df["sector"].value_counts().head(7).index.tolist()
    for sec in top_sectors:
        sub_sec = df[df["sector"] == sec]
        sector_breakdown[sec] = {
            "filings_count": int(len(sub_sec)),
            "median_gross_margin": float(sub_sec["gross_margin"].median()) if sub_sec["gross_margin"].notna().sum() > 10 else None,
            "median_operating_margin": float(sub_sec["operating_margin"].median()) if sub_sec["operating_margin"].notna().sum() > 10 else None,
            "median_dso_days": float(sub_sec["dso_days"].median()) if sub_sec["dso_days"].notna().sum() > 10 else None,
            "median_dio_days": float(sub_sec["dio_days"].median()) if sub_sec["dio_days"].notna().sum() > 10 else None,
            "median_dpo_days": float(sub_sec["dpo_days"].median()) if sub_sec["dpo_days"].notna().sum() > 10 else None,
            "median_ccc_days": float(sub_sec["ccc_days"].median()) if sub_sec["ccc_days"].notna().sum() > 10 else None,
            "divergence_pos_ni_neg_cfo_pct": float(sub_sec["flag_ni_pos_cfo_neg"].mean() * 100) if sub_sec["flag_ni_pos_cfo_neg"].notna().sum() > 10 else None,
            "median_goodwill_to_assets": float(sub_sec["goodwill_to_assets"].median()) if sub_sec["goodwill_to_assets"].notna().sum() > 10 else None
        }

    # Filer Status Scale Breakdown (Large Accel vs Non-Accel)
    afs_breakdown = {}
    for afs_val in ["1-LAF", "2-ACC", "4-NON"]:
        sub_afs = df[df["afs"] == afs_val]
        afs_breakdown[afs_val] = {
            "filings_count": int(len(sub_afs)),
            "median_revenue": float(sub_afs["revenue"].median()) if sub_afs["revenue"].notna().sum() > 10 else None,
            "median_operating_margin": float(sub_afs["operating_margin"].median()) if sub_afs["operating_margin"].notna().sum() > 10 else None,
            "divergence_pos_ni_neg_cfo_pct": float(sub_afs["flag_ni_pos_cfo_neg"].mean() * 100) if sub_afs["flag_ni_pos_cfo_neg"].notna().sum() > 10 else None,
            "negative_equity_rate_pct": float(sub_afs["flag_negative_equity"].mean() * 100) if sub_afs["flag_negative_equity"].notna().sum() > 10 else None,
            "median_cash_to_assets": float(sub_afs["cash_to_assets"].median()) if sub_afs["cash_to_assets"].notna().sum() > 10 else None
        }

    results = {
        "metadata": {
            "title": "Empirical Corporate Financial Reporting Behaviour Study",
            "source": "SEC EDGAR Financial Statement Data Sets (FSDS 2024 Q3)",
            "filings_analyzed": len(df),
            "reporting_quarter": "2024 Q3"
        },
        "overall_metrics": overall_metrics,
        "sector_breakdown": sector_breakdown,
        "filer_scale_breakdown": afs_breakdown
    }
    
    out_json = os.path.join(out_dir, "financial_reporting_behaviour_metrics.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved Financial Reporting Behaviour metrics to: {out_json}")
    
    # Print highlights
    print("\n================== KEY EMPIRICAL HIGHLIGHTS ==================")
    print(f"Total Periodic Filings Analyzed: {len(df)}")
    print(f"Positive Net Income but Negative Operating Cash Flow (QoE Red Flag): {overall_metrics['quality_of_earnings_accruals']['divergence_positive_ni_negative_cfo_pct']:.2f}%")
    print(f"Negative Operating Income but Positive Operating Cash Flow: {overall_metrics['quality_of_earnings_accruals']['divergence_negative_opinc_positive_cfo_pct']:.2f}%")
    print(f"Overall Median DSO: {overall_metrics['working_capital_days']['dso_days']['median']:.1f} days")
    print(f"Overall Median DIO: {overall_metrics['working_capital_days']['dio_days']['median']:.1f} days")
    print(f"Overall Median DPO: {overall_metrics['working_capital_days']['dpo_days']['median']:.1f} days")
    print(f"Overall Median Cash Conversion Cycle (CCC): {overall_metrics['working_capital_days']['cash_conversion_cycle_days']['median']:.1f} days")
    print(f"Negative Stockholders Equity Rate: {overall_metrics['balance_sheet_structure']['negative_equity_rate_pct']:.2f}%")
    print("==============================================================")

if __name__ == "__main__":
    run_financial_reporting_analysis()
