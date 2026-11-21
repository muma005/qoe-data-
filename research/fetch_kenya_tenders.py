"""
Fetch Kenyan PPIP Procurement Tenders & Contracts Data
======================================================
Connects to Kenya's Public Procurement Information Portal (PPIP) API,
pulls tenders and awards with complete 60+ attributes, and saves to JSON & CSV.
"""

import os
import json
import time
import requests
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.join(BASE_DIR, "original_datasets", "procurement_expenses", "kenya_procurement")
os.makedirs(DEST_DIR, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

def fetch_kenya_tenders(max_pages=50):
    all_tenders = []
    base_url = "https://tenders.go.ke/api/active-tenders"
    
    print(f"Connecting to Kenyan PPIP API: {base_url}...")
    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code != 200:
                print(f"Page {page} returned status {resp.status_code}, stopping.")
                break
            payload = resp.json()
            data = payload.get('data', [])
            if not data:
                print(f"No more data at page {page}.")
                break
            all_tenders.extend(data)
            total = payload.get('total', 'Unknown')
            last_page = payload.get('last_page', 'Unknown')
            if page % 10 == 0 or page == 1:
                print(f"Fetched page {page}/{last_page} ({len(all_tenders)} tenders total / {total} available)...")
            time.sleep(0.3)  # Polite crawling delay
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
    print(f"\nTotal Kenyan tenders acquired: {len(all_tenders)}")
    
    # Save raw JSON
    json_path = os.path.join(DEST_DIR, "kenya_tenders_raw.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_tenders, f, indent=2, default=str)
    print(f"Saved raw JSON: {json_path} ({os.path.getsize(json_path):,} bytes)")
    
    # Flatten core attributes for tabular analysis
    flat_rows = []
    for t in all_tenders:
        pe_info = t.get('pe') if isinstance(t.get('pe'), dict) else {}
        proc_method = t.get('procurement_method') if isinstance(t.get('procurement_method'), dict) else {}
        flat_rows.append({
            'tender_id': t.get('id'),
            'ocid': t.get('ocid'),
            'tender_ref': t.get('tender_ref'),
            'title': t.get('title'),
            'procuring_entity_id': t.get('pe_id'),
            'procuring_entity_name': pe_info.get('name') if pe_info else None,
            'procurement_category_id': t.get('procurement_category_id'),
            'procurement_method_id': t.get('procurement_method_id'),
            'procurement_method_name': proc_method.get('name') if proc_method else None,
            'procurement_method_justification': t.get('procurement_method_justification'),
            'selection_reason': t.get('selection_reason'),
            'is_agpo': t.get('is_agpo'),  # Access to Government Procurement Opportunities (preference groups)
            'status_id': t.get('status_id'),
            'published_at': t.get('published_at'),
            'close_at': t.get('close_at'),
            'opening_date': t.get('opening_date'),
            'evaluation_start_date': t.get('evaluation_start_date'),
            'evaluation_end_date': t.get('evaluation_end_date'),
            'validity_in_days': t.get('validity_in_days'),
            'tender_fee': t.get('tender_fee'),
            'bid_security_percent': t.get('bid_security_percent'),
            'bid_security_value': t.get('bid_security_value'),
            'passmark': t.get('passmark'),
            'financial_year_id': t.get('financial_year_id'),
            'contracts_count': len(t.get('contracts', [])) if isinstance(t.get('contracts'), list) else 0,
            'bidders_count': len(t.get('bidders', [])) if isinstance(t.get('bidders'), list) else 0,
            'addenda_count': len(t.get('addenda', [])) if isinstance(t.get('addenda'), list) else 0,
            'created_at': t.get('created_at'),
            'updated_at': t.get('updated_at')
        })
        
    df = pd.DataFrame(flat_rows)
    csv_path = os.path.join(DEST_DIR, "kenya_tenders_flattened.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved flattened CSV: {csv_path} ({os.path.getsize(csv_path):,} bytes, {len(df)} rows, {len(df.columns)} columns)")

if __name__ == "__main__":
    fetch_kenya_tenders(max_pages=60)
