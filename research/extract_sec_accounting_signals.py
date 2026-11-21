import os
import json
import pandas as pd
import numpy as np

def run_sec_accounting_extraction():
    base_dir = r"research/original_datasets/financial_accounting/sec_fsds_2024q3"
    out_dir = r"research/accounting_signals"
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- 1. Analyzing Submissions (sub.txt) ---")
    sub_path = os.path.join(base_dir, "sub.txt")
    df_sub = pd.read_csv(sub_path, sep="\t", encoding="latin1", low_memory=False)
    
    total_filings = len(df_sub)
    unique_ciks = df_sub["cik"].nunique()
    
    # Form distribution
    form_dist = df_sub["form"].value_counts().to_dict()
    
    # Accelerated Filer Status (AFS)
    # 1-LAF (Large Accelerated), 2-ACC (Accelerated), 3-SNC (Smaller Reporting Non-Accelerated), 4-NON (Non-Accelerated), 5-SBC (Smaller Reporting Accelerated)
    afs_dist = df_sub["afs"].value_counts(dropna=False).to_dict()
    
    # Restatement / Previous Report indicator (prevrpt)
    # prevrpt: 1 if filing was previously reported (e.g. amendment / restatement / revision), 0 otherwise
    prevrpt_dist = df_sub["prevrpt"].value_counts(dropna=False).to_dict()
    prevrpt_rate = float(df_sub["prevrpt"].mean())
    
    # Restatements by Form type (e.g. 10-K/A, 10-Q/A vs normal)
    restatements_by_form = df_sub[df_sub["prevrpt"] == 1]["form"].value_counts().to_dict()
    
    # Restatement rate by Filer Status
    restatements_by_afs = df_sub.groupby("afs")["prevrpt"].agg(["count", "mean"]).to_dict(orient="index")
    
    print(f"Total Submissions: {total_filings}, Unique CIKs: {unique_ciks}")
    print(f"Prior Report / Restatement Rate: {prevrpt_rate:.4%}")
    print(f"Top forms: {dict(list(form_dist.items())[:5])}")
    
    print("\n--- 2. Analyzing Taxonomy Tags (tag.txt) ---")
    tag_path = os.path.join(base_dir, "tag.txt")
    df_tag = pd.read_csv(tag_path, sep="\t", encoding="latin1", low_memory=False)
    
    total_tags = len(df_tag)
    unique_tags = df_tag["tag"].nunique()
    
    # Custom vs Standard US-GAAP tags
    # custom: 1 if tag is custom extension created by the filer, 0 if standard US-GAAP taxonomy tag
    custom_dist = df_tag["custom"].value_counts().to_dict()
    custom_ratio = float(df_tag["custom"].mean())
    
    # Abstract tags (headers vs line items)
    abstract_dist = df_tag["abstract"].value_counts().to_dict()
    abstract_ratio = float(df_tag["abstract"].mean())
    
    # Datatype distribution
    datatype_dist = df_tag["datatype"].value_counts().head(10).to_dict()
    
    # Credit/Debit natural balance distribution
    crdr_dist = df_tag["crdr"].value_counts(dropna=False).to_dict()
    
    # Custom tag breakdown by datatype
    custom_by_datatype = df_tag.groupby("datatype")["custom"].agg(["count", "sum", "mean"]).head(10).to_dict(orient="index")
    
    print(f"Total Tags: {total_tags}, Unique: {unique_tags}")
    print(f"Custom Extension Tag Ratio: {custom_ratio:.4%}")
    print(f"Abstract Tag Ratio: {abstract_ratio:.4%}")
    print(f"Top Datatypes: {list(datatype_dist.items())[:4]}")
    
    print("\n--- 3. Analyzing Presentation Linkbase (pre.txt) ---")
    pre_path = os.path.join(base_dir, "pre.txt")
    # Read pre.txt in chunks or sample if large, but 90MB fits easily in memory
    df_pre = pd.read_csv(pre_path, sep="\t", encoding="latin1", low_memory=False)
    
    total_pre_lines = len(df_pre)
    unique_filings_pre = df_pre["adsh"].nunique()
    
    # Statement distribution (stmt: BS, IS, CF, EQ, CI, UN, CP)
    stmt_dist = df_pre["stmt"].value_counts().to_dict()
    stmt_pct = (df_pre["stmt"].value_counts(normalize=True) * 100).to_dict()
    
    # Lines per filing per statement
    lines_per_stmt = df_pre.groupby(["adsh", "stmt"])["line"].count().groupby("stmt").describe().to_dict(orient="index")
    
    # Negating line items (contra-accounts, deduction lines)
    negating_dist = df_pre["negating"].value_counts().to_dict()
    negating_rate = float(df_pre["negating"].mean())
    
    # Hierarchy depth (inpth)
    depth_stats = df_pre["inpth"].describe().to_dict()
    
    print(f"Total Presentation Lines: {total_pre_lines} across {unique_filings_pre} filings")
    print(f"Statement Distribution: {stmt_pct}")
    print(f"Negating / Contra-Account Rate: {negating_rate:.4%}")
    
    print("\n--- 4. Analyzing Numeric Facts (num.txt) ---")
    # num.txt is 498 MB. We can process in chunks to get footnote frequency and core GAAP line statistics
    num_path = os.path.join(base_dir, "num.txt")
    
    total_num_rows = 0
    footnoted_rows = 0
    uom_counts = {}
    core_tags_found = {
        "Revenues": 0,
        "NetIncomeLoss": 0,
        "GrossProfit": 0,
        "OperatingIncomeLoss": 0,
        "Assets": 0,
        "Liabilities": 0,
        "StockholdersEquity": 0,
        "CashAndCashEquivalentsAtCarryingValue": 0,
        "AccountsReceivableNetCurrent": 0,
        "InventoryNet": 0,
        "AccountsPayableCurrent": 0,
        "Goodwill": 0
    }
    
    chunksize = 500000
    print("Reading num.txt in chunks...")
    for chunk in pd.read_csv(num_path, sep="\t", encoding="latin1", chunksize=chunksize, low_memory=False, 
                             usecols=["tag", "uom", "footnote"]):
        total_num_rows += len(chunk)
        # Footnote presence
        has_fn = chunk["footnote"].notna() & (chunk["footnote"].str.strip() != "")
        footnoted_rows += int(has_fn.sum())
        
        # UOM
        for uom, cnt in chunk["uom"].value_counts().items():
            uom_counts[uom] = uom_counts.get(uom, 0) + int(cnt)
            
        # Core tags
        tag_series = chunk["tag"].value_counts()
        for t in core_tags_found.keys():
            if t in tag_series:
                core_tags_found[t] += int(tag_series[t])
                
    footnote_rate = footnoted_rows / total_num_rows if total_num_rows > 0 else 0
    print(f"Total Numeric Facts: {total_num_rows}")
    print(f"Footnoted Numeric Facts: {footnoted_rows} ({footnote_rate:.4%})")
    print(f"Top Core Tags Occurrences: {core_tags_found}")
    
    results = {
        "metadata": {
            "dataset": "SEC EDGAR Financial Statement Data Sets (FSDS) 2024 Q3",
            "source": "U.S. Securities and Exchange Commission (SEC)",
            "filing_quarter": "2024 Q3 (Filings received July 1, 2024 to September 30, 2024)",
            "total_submissions": total_filings,
            "unique_ciks": unique_ciks,
            "total_taxonomy_tags": total_tags,
            "total_presentation_lines": total_pre_lines,
            "total_numeric_facts": total_num_rows
        },
        "corporate_restatements": {
            "total_filings": total_filings,
            "prevrpt_count": prevrpt_dist.get(1, 0),
            "prevrpt_restatement_rate": prevrpt_rate,
            "restatements_by_form": restatements_by_form,
            "restatements_by_accelerated_filer_status": restatements_by_afs
        },
        "reporting_complexity_and_opacity": {
            "total_tags": total_tags,
            "standard_us_gaap_tags": custom_dist.get(0, 0),
            "custom_extension_tags": custom_dist.get(1, 0),
            "custom_extension_ratio": custom_ratio,
            "abstract_structure_ratio": abstract_ratio,
            "custom_by_datatype": custom_by_datatype
        },
        "financial_statement_architecture": {
            "total_presentation_lines": total_pre_lines,
            "statement_distribution": stmt_dist,
            "statement_percentages": stmt_pct,
            "negating_contra_item_rate": negating_rate,
            "depth_statistics": depth_stats,
            "statement_line_counts": lines_per_stmt
        },
        "numeric_disclosure_mechanics": {
            "total_numeric_facts": total_num_rows,
            "footnoted_facts": footnoted_rows,
            "footnote_attachment_rate": footnote_rate,
            "units_of_measure": dict(sorted(uom_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "core_gaap_tag_frequency": core_tags_found
        }
    }
    
    out_json = os.path.join(out_dir, "sec_fsds_accounting_metrics.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved SEC accounting metrics to: {out_json}")

if __name__ == "__main__":
    run_sec_accounting_extraction()
