"""
Comprehensive Dataset Acquisition Suite for QoE Simulator
==========================================================
Handles downloads, verification, and extraction across all categories.
"""

import os
import sys
import zipfile
import gzip
import shutil
import urllib.request
import time
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'acquisition_log', 'acquisition_log.csv')

def log_event(dataset_name, category, source_url, local_path, status, file_size_bytes, record_count, notes):
    file_exists = os.path.exists(LOG_FILE)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        if not file_exists:
            f.write("timestamp,dataset_name,category,source_url,local_path,status,file_size_bytes,record_count,notes\n")
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        row = f'"{ts}","{dataset_name}","{category}","{source_url}","{local_path}","{status}",{file_size_bytes},{record_count},"{notes}"\n'
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

def acquire_uci_online_retail():
    cat = "revenue_commercial"
    name = "UCI Online Retail"
    dest_dir = os.path.join(BASE_DIR, "original_datasets", cat, "uci_online_retail")
    os.makedirs(dest_dir, exist_ok=True)
    zip_path = os.path.join(dest_dir, "online_retail.zip")
    url = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
    
    print(f"Downloading {name} from {url}...")
    size = download_with_progress(url, zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest_dir)
        extracted_files = zf.namelist()
    
    excel_file = os.path.join(dest_dir, "Online Retail.xlsx")
    csv_file = os.path.join(dest_dir, "online_retail.csv")
    
    print(f"Converting {excel_file} to CSV for high-performance profiling...")
    df = pd.read_excel(excel_file)
    rec_count = len(df)
    df.to_csv(csv_file, index=False)
    
    log_event(name, cat, url, csv_file, "ACQUIRED", os.path.getsize(csv_file), rec_count, 
              "Real UK online giftware retail transactions 2010-2011 with credit notes and cancellations")

def acquire_sf_payroll():
    cat = "payroll_employees"
    name = "City of San Francisco Employee Compensation"
    dest_dir = os.path.join(BASE_DIR, "original_datasets", cat, "sf_employee_compensation")
    os.makedirs(dest_dir, exist_ok=True)
    csv_path = os.path.join(dest_dir, "sf_employee_compensation.csv")
    
    # Download 50,000 recent compensation records via Socrata API for robust statistical coverage
    url = "https://data.sfgov.org/resource/88g8-5mnd.csv?$limit=50000&$order=year%20DESC"
    print(f"Downloading {name} from {url}...")
    size = download_with_progress(url, csv_path)
    
    df = pd.read_csv(csv_path)
    rec_count = len(df)
    
    log_event(name, cat, url, csv_path, "ACQUIRED", size, rec_count,
              "Real-world public municipal employee compensation register with base, overtime, other pay, and benefits")

def acquire_sec_fsds():
    cat = "financial_accounting"
    name = "SEC EDGAR Financial Statement Data Sets (2024 Q3)"
    dest_dir = os.path.join(BASE_DIR, "original_datasets", cat, "sec_fsds_2024q3")
    os.makedirs(dest_dir, exist_ok=True)
    zip_path = os.path.join(dest_dir, "2024q3.zip")
    url = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/2024q3.zip"
    
    headers = {'User-Agent': 'AcademicResearchQoESimulator researcher@university.edu'}
    print(f"Downloading {name} from {url}...")
    size = download_with_progress(url, zip_path, headers=headers)
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(dest_dir)
        files = zf.namelist()
    
    sub_df = pd.read_csv(os.path.join(dest_dir, "sub.txt"), sep='\t', low_memory=False)
    rec_count = len(sub_df)
    
    log_event(name, cat, url, dest_dir, "ACQUIRED", size, rec_count,
              f"Real-world SEC corporate financial statements (sub.txt: {rec_count:,} filings, num.txt, tag.txt, pre.txt)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target == "uci":
            acquire_uci_online_retail()
        elif target == "sf":
            acquire_sf_payroll()
        elif target == "sec":
            acquire_sec_fsds()
    else:
        print("Usage: python acquire_datasets.py [uci|sf|sec]")
