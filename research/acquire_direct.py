"""
Fast robust acquisition for SF Payroll, UK Spend, and SEC FSDS
Includes SSL unverified context workaround for Python 3.14 Windows certs.
"""
import os
import urllib.request
import zipfile
import shutil
import ssl
import pandas as pd
import time

# Disable SSL verification for government data portals on Windows Python 3.14
ssl._create_default_https_context = ssl._create_unverified_context

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'acquisition_log', 'acquisition_log.csv')

def log_event(dataset_name, category, source_url, local_path, status, file_size_bytes, record_count, notes):
    file_exists = os.path.exists(LOG_FILE)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        if not file_exists:
            f.write("timestamp,dataset_name,category,source_url,local_path,status,file_size_bytes,record_count,notes\n")
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        notes_clean = notes.replace('"', '""')
        row = f'"{ts}","{dataset_name}","{category}","{source_url}","{local_path}","{status}",{file_size_bytes},{record_count},"{notes_clean}"\n'
        f.write(row)
    print(f"[{status}] {dataset_name} ({category}): {notes} (Size: {file_size_bytes:,} bytes, Records: {record_count:,})")

def download_with_progress(url, dest_path, headers=None, timeout=120):
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response, open(dest_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    return os.path.getsize(dest_path)

def acquire_sf():
    cat = "payroll_employees"
    name = "City of San Francisco Employee Compensation"
    dest_dir = os.path.join(BASE_DIR, "original_datasets", cat, "sf_employee_compensation")
    os.makedirs(dest_dir, exist_ok=True)
    csv_path = os.path.join(dest_dir, "sf_employee_compensation.csv")
    url = "https://data.sfgov.org/resource/88g8-5mnd.csv?$limit=50000&$order=year%20DESC"
    print(f"Downloading {name}...")
    size = download_with_progress(url, csv_path)
    df = pd.read_csv(csv_path)
    log_event(name, cat, url, csv_path, "ACQUIRED", size, len(df), "50,000 public employee compensation records with base salary, overtime, other pay, retirement benefits, health/dental, and total compensation")

def acquire_uk():
    cat = "financial_accounting"
    name = "UK HM Treasury Spend Over £25,000 (Accounts Payable Line Items)"
    dest_dir = os.path.join(BASE_DIR, "original_datasets", cat, "uk_hm_treasury_spend")
    os.makedirs(dest_dir, exist_ok=True)
    files = [
        ("https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/184401/transparency_april.csv", "transparency_april.csv"),
        ("https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/184399/transparency_may.csv", "transparency_may.csv")
    ]
    clean_dfs = []
    for url, filename in files:
        target = os.path.join(dest_dir, filename)
        download_with_progress(url, target)
        try:
            df = pd.read_csv(target, encoding='utf-8')
        except:
            df = pd.read_csv(target, encoding='latin1')
        valid_cols = [c for c in df.columns if not c.startswith('Unnamed:')]
        df_clean = df[valid_cols].dropna(how='all')
        clean_file = os.path.join(dest_dir, f"clean_{filename}")
        df_clean.to_csv(clean_file, index=False)
        clean_dfs.append(df_clean)
    combined = pd.concat(clean_dfs, ignore_index=True)
    comb_path = os.path.join(dest_dir, "hm_treasury_spend_combined.csv")
    combined.to_csv(comb_path, index=False)
    log_event(name, cat, "https://data.gov.uk/dataset/spend-over-25-000-in-hm-treasury", comb_path, "ACQUIRED", os.path.getsize(comb_path), len(combined), "Real accounts payable / GL vouchers over £25k: Entity, Expense Type, Expense Area, Supplier, Transaction Number, Amount, Narrative")

def acquire_sec():
    cat = "financial_accounting"
    name = "SEC EDGAR Financial Statement Data Sets (2024 Q3)"
    dest_dir = os.path.join(BASE_DIR, "original_datasets", cat, "sec_fsds_2024q3")
    os.makedirs(dest_dir, exist_ok=True)
    zip_path = os.path.join(dest_dir, "2024q3.zip")
    url = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/2024q3.zip"
    headers = {'User-Agent': 'AcademicResearchQoESimulator researcher@university.edu'}
    print(f"Downloading {name}...")
    size = download_with_progress(url, zip_path, headers=headers)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest_dir)
    sub_df = pd.read_csv(os.path.join(dest_dir, "sub.txt"), sep='\t', low_memory=False)
    log_event(name, cat, url, dest_dir, "ACQUIRED", size, len(sub_df), f"Real-world SEC corporate financial statements ({len(sub_df):,} corporate submissions, sub.txt, num.txt, tag.txt, pre.txt)")

if __name__ == "__main__":
    acquire_sf()
    acquire_uk()
    acquire_sec()
    print("Direct acquisition completed successfully!")
