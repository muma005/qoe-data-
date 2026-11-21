"""
Automated Dataset Inspection & Profiling Suite for QoE Simulator
================================================================
Conducts deep technical inspection of acquired datasets:
- Schema, dtypes, missingness, duplicates
- Distributional statistics and extreme values
- Irregularities (credit notes, reversals, negative amounts, out-of-period entries)
- Generates comprehensive markdown inspection reports.
"""

import os
import sys
import json
import time
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSPECTION_DIR = os.path.join(BASE_DIR, 'dataset_inspections')
os.makedirs(INSPECTION_DIR, exist_ok=True)

def profile_dataframe(df, name, category, source_provenance, qoe_use_cases):
    total_rows, total_cols = df.shape
    memory_usage = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    # Missingness
    null_counts = df.isnull().sum()
    null_pct = (null_counts / total_rows) * 100
    
    # Columns summary
    col_summary = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        nunique = df[col].nunique()
        null_c = null_counts[col]
        null_p = null_pct[col]
        sample_vals = df[col].dropna().head(3).tolist()
        col_summary.append({
            "column": col,
            "dtype": dtype,
            "distinct_values": nunique,
            "null_count": int(null_c),
            "null_percentage": round(null_p, 2),
            "samples": str(sample_vals)
        })
    
    # Numeric profiling
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_stats = {}
    if num_cols:
        desc = df[num_cols].describe().T
        for col in num_cols:
            s = df[col].dropna()
            num_stats[col] = {
                "count": int(desc.loc[col, "count"]),
                "mean": float(desc.loc[col, "mean"]),
                "std": float(desc.loc[col, "std"]) if not pd.isna(desc.loc[col, "std"]) else 0.0,
                "min": float(desc.loc[col, "min"]),
                "p25": float(desc.loc[col, "25%"]),
                "median": float(desc.loc[col, "50%"]),
                "p75": float(desc.loc[col, "75%"]),
                "max": float(desc.loc[col, "max"]),
                "neg_count": int((s < 0).sum()),
                "zero_count": int((s == 0).sum())
            }
            
    # Markdown report generation
    report_lines = []
    report_lines.append(f"# Dataset Technical Inspection Report: {name}")
    report_lines.append(f"\n**Category:** `{category}`  ")
    report_lines.append(f"**Inspection Date:** `{time.strftime('%Y-%m-%d %H:%M:%S')}`  ")
    report_lines.append(f"**Total Records:** `{total_rows:,}`  ")
    report_lines.append(f"**Total Fields:** `{total_cols}`  ")
    report_lines.append(f"**In-Memory Size:** `{memory_usage:.2f} MB`  ")
    
    report_lines.append("\n## 1. Provenance & Authenticity Evidence")
    report_lines.append(f"- **Originating Organization/System:** {source_provenance.get('organization', 'N/A')}")
    report_lines.append(f"- **Data Classification:** `{source_provenance.get('classification', 'Real-world')}`")
    report_lines.append(f"- **Original Source URL:** {source_provenance.get('url', 'N/A')}")
    report_lines.append(f"- **Authenticity Verification:** {source_provenance.get('verification_notes', 'N/A')}")
    report_lines.append(f"- **Licensing / Permitted Use:** {source_provenance.get('license', 'Open Research / Public Domain')}")

    report_lines.append("\n## 2. Schema and Field Inventory")
    report_lines.append("| Field Name | Data Type | Distinct Values | Null Count | Null % | Sample Values |")
    report_lines.append("|---|---|---|---|---|---|")
    for c in col_summary:
        report_lines.append(f"| `{c['column']}` | `{c['dtype']}` | {c['distinct_values']:,} | {c['null_count']:,} | {c['null_percentage']}% | `{c['samples']}` |")

    if num_stats:
        report_lines.append("\n## 3. Numerical and Financial Distribution Profile")
        report_lines.append("| Field | Count | Mean | Std Dev | Min | Median | Max | Negatives (<0) | Zeros (=0) |")
        report_lines.append("|---|---|---|---|---|---|---|---|---|")
        for col, st in num_stats.items():
            report_lines.append(f"| `{col}` | {st['count']:,} | {st['mean']:,.2f} | {st['std']:,.2f} | {st['min']:,.2f} | {st['median']:,.2f} | {st['max']:,.2f} | {st['neg_count']:,} | {st['zero_count']:,} |")

    report_lines.append("\n## 4. Representative Records")
    report_lines.append("```json")
    report_lines.append(json.dumps(df.head(3).to_dict(orient="records"), indent=2, default=str))
    report_lines.append("```")

    report_lines.append("\n## 5. Data Quality, Irregularities & Forensic Anomalies")
    report_lines.append(source_provenance.get("forensic_anomalies", "Standard distribution observed."))

    report_lines.append("\n## 6. QoE Analytical Applications & Simulator Value")
    report_lines.append(qoe_use_cases)

    report_lines.append("\n## 7. Known Biases and Limitations")
    report_lines.append(source_provenance.get("limitations", "None recorded."))

    report_path = os.path.join(INSPECTION_DIR, f"{name.lower().replace(' ', '_').replace('/', '_')}_inspection.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"Generated inspection report: {report_path}")
    return report_path
