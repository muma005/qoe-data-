import os
import json
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

def run_benford_analysis():
    print("--- 1. Benford's Law Analysis on Authentic Transaction Populations ---")
    
    benford_theory = {d: np.log10(1 + 1/d) for d in range(1, 10)}
    
    def get_first_digit_dist(series):
        s = series.dropna()
        s = s[s > 0]
        # Extract first non-zero digit
        first_digits = s.astype(str).str.replace(r'^[0\.]+', '', regex=True).str[0]
        first_digits = pd.to_numeric(first_digits, errors='coerce').dropna().astype(int)
        first_digits = first_digits[(first_digits >= 1) & (first_digits <= 9)]
        counts = first_digits.value_counts(normalize=True).to_dict()
        dist = {d: float(counts.get(d, 0.0)) for d in range(1, 10)}
        mad = float(np.mean([abs(dist[d] - benford_theory[d]) for d in range(1, 10)]))
        return dist, mad, len(first_digits)

    # Dataset A: AkzoNobel SAP ERP (Spend / Item Values)
    bpi_path = r"research/original_datasets/procurement_expenses/bpi_2019/BPI_Challenge_2019.csv"
    print("Analyzing AkzoNobel BPI 2019 spend values...")
    df_bpi = pd.read_csv(bpi_path, encoding="latin1", usecols=["event Cumulative net worth (EUR)"], nrows=500000)
    bpi_spend = pd.to_numeric(df_bpi["event Cumulative net worth (EUR)"], errors="coerce")
    bpi_spend_pos = bpi_spend.dropna()
    bpi_spend_pos = bpi_spend_pos[bpi_spend_pos > 0]
    bpi_benford, bpi_mad, bpi_n = get_first_digit_dist(bpi_spend_pos)
    bpi_skew = float(skew(bpi_spend_pos))
    bpi_kurt = float(kurtosis(bpi_spend_pos))
    
    # Dataset B: UCI Online Retail Commercial Sales Amounts
    uci_path = r"research/original_datasets/revenue_commercial/uci_online_retail/online_retail.csv"
    print("Analyzing UCI Retail commercial invoice line values...")
    df_uci = pd.read_csv(uci_path, encoding="latin1")
    df_uci["LineTotal"] = df_uci["Quantity"] * df_uci["UnitPrice"]
    uci_pos = df_uci[df_uci["LineTotal"] > 0]["LineTotal"]
    uci_benford, uci_mad, uci_n = get_first_digit_dist(uci_pos)
    uci_skew = float(skew(uci_pos.dropna()))
    uci_kurt = float(kurtosis(uci_pos.dropna()))
    
    # Dataset C: Czech Bank Berka Cashbook Transactions
    bank_path = r"research/original_datasets/working_capital_banking/czech_bank/trans.csv"
    print("Analyzing Czech Bank transaction amounts...")
    df_bank = pd.read_csv(bank_path, low_memory=False) # comma separated
    bank_amt = pd.to_numeric(df_bank["amount"], errors="coerce")
    bank_pos = bank_amt.dropna()
    bank_pos = bank_pos[bank_pos > 0]
    bank_benford, bank_mad, bank_n = get_first_digit_dist(bank_pos)
    bank_skew = float(skew(bank_pos))
    bank_kurt = float(kurtosis(bank_pos))
    
    # Dataset D: SF Employee Compensation Payroll Base Salary
    sf_path = r"research/original_datasets/payroll_employees/sf_employee_compensation/sf_employee_compensation.csv"
    print("Analyzing SF Employee payroll base salaries...")
    df_sf = pd.read_csv(sf_path)
    sf_base = pd.to_numeric(df_sf["salaries"], errors="coerce")
    sf_pos = sf_base.dropna()
    sf_pos = sf_pos[sf_pos > 0]
    sf_benford, sf_mad, sf_n = get_first_digit_dist(sf_pos)
    sf_skew = float(skew(sf_pos))
    sf_kurt = float(kurtosis(sf_pos))

    # Conformity benchmarks: Nigrini (2012)
    def get_conformity(mad):
        if mad < 0.006: return "Close Conformity"
        elif mad < 0.012: return "Acceptable Conformity"
        elif mad < 0.015: return "Marginally Acceptable"
        else: return "Non-Conforming"

    results = {
        "theoretical_benford_distribution": {d: float(benford_theory[d]) for d in range(1, 10)},
        "populations": {
            "bpi_sap_procurement_spend": {
                "sample_size": bpi_n,
                "first_digit_distribution": bpi_benford,
                "mean_absolute_deviation_mad": bpi_mad,
                "conformity_status": get_conformity(bpi_mad),
                "skewness": bpi_skew,
                "kurtosis": bpi_kurt
            },
            "uci_commercial_sales_lines": {
                "sample_size": uci_n,
                "first_digit_distribution": uci_benford,
                "mean_absolute_deviation_mad": uci_mad,
                "conformity_status": get_conformity(uci_mad),
                "skewness": uci_skew,
                "kurtosis": uci_kurt
            },
            "czech_bank_cashbook_transactions": {
                "sample_size": bank_n,
                "first_digit_distribution": bank_benford,
                "mean_absolute_deviation_mad": bank_mad,
                "conformity_status": get_conformity(bank_mad),
                "skewness": bank_skew,
                "kurtosis": bank_kurt
            },
            "sf_payroll_base_salaries": {
                "sample_size": sf_n,
                "first_digit_distribution": sf_benford,
                "mean_absolute_deviation_mad": sf_mad,
                "conformity_status": get_conformity(sf_mad),
                "skewness": sf_skew,
                "kurtosis": sf_kurt
            }
        }
    }
    
    out_dir = r"research/hypothesis_register"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "benford_and_distribution_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved Benford results to {out_file}")
    
    print("\n--- Summary of Benford Conformity & Moments ---")
    for k, v in results["populations"].items():
        print(f"Population: {k}")
        print(f"  Sample Size: {v['sample_size']:,}")
        print(f"  MAD: {v['mean_absolute_deviation_mad']:.4f} ({v['conformity_status']})")
        print(f"  Skewness: {v['skewness']:.2f}, Kurtosis: {v['kurtosis']:.2f}")

if __name__ == "__main__":
    run_benford_analysis()
