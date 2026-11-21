import os
import json
import pandas as pd

DEST_DIR = r"research\original_datasets\procurement_expenses\kenya_procurement"
json_path = os.path.join(DEST_DIR, "kenya_tenders_raw.json")

with open(json_path, "r", encoding="utf-8") as f:
    all_tenders = json.load(f)

flat_rows = []
for t in all_tenders:
    pe_info = t.get('pe') if isinstance(t.get('pe'), dict) else {}
    proc_method = t.get('procurement_method') if isinstance(t.get('procurement_method'), dict) else {}
    proc_cat = t.get('procurement_category') if isinstance(t.get('procurement_category'), dict) else {}
    fin_year = t.get('financial_year') if isinstance(t.get('financial_year'), dict) else {}
    creator = t.get('created_by') if isinstance(t.get('created_by'), dict) else {}
    justification = t.get('procurement_method_justification') if isinstance(t.get('procurement_method_justification'), dict) else {}
    
    # Submissions
    sub_methods = t.get('submission_methods', [])
    sub_method_titles = [m.get('title') for m in sub_methods if isinstance(m, dict) and 'title' in m] if isinstance(sub_methods, list) else []
    
    # AGPO groups
    agpo_list = t.get('agpo_groups', [])
    agpo_titles = [g.get('name') or g.get('title') for g in agpo_list if isinstance(g, dict)] if isinstance(agpo_list, list) else []

    flat_rows.append({
        'tender_id': t.get('id'),
        'ocid': t.get('ocid'),
        'tender_ref': t.get('tender_ref'),
        'title': t.get('title'),
        'procuring_entity_id': t.get('pe_id'),
        'procuring_entity_name': pe_info.get('name') if pe_info else None,
        'procuring_entity_type_id': pe_info.get('pe_type_id') if pe_info else None,
        'procurement_category_id': t.get('procurement_category_id'),
        'procurement_category_title': proc_cat.get('title') if proc_cat else None,
        'procurement_method_id': t.get('procurement_method_id'),
        'procurement_method_title': proc_method.get('title') if proc_method else None,
        'procurement_method_code': proc_method.get('code') if proc_method else None,
        'procurement_method_justification': justification.get('justification') if justification else t.get('procurement_method_justification'),
        'selection_reason': t.get('selection_reason'),
        'is_reservation': t.get('is_reservation'),
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
        'financial_year': fin_year.get('name') if fin_year else None,
        'quarter_id': t.get('quarter_id'),
        'created_by_user': creator.get('name') if creator else None,
        'created_by_email': creator.get('username') if creator else None,
        'venue': t.get('venue'),
        'submission_methods': "; ".join([str(s) for s in sub_method_titles if s]),
        'agpo_groups': "; ".join([str(a) for a in agpo_titles if a]),
        'documents_count': len(t.get('documents', [])) if isinstance(t.get('documents'), list) else 0,
        'contracts_count': len(t.get('contracts', [])) if isinstance(t.get('contracts'), list) else 0,
        'bidders_count': len(t.get('bidders', [])) if isinstance(t.get('bidders'), list) else 0,
        'addenda_count': len(t.get('addenda', [])) if isinstance(t.get('addenda'), list) else 0,
        'created_at': t.get('created_at'),
        'updated_at': t.get('updated_at')
    })

df = pd.DataFrame(flat_rows)
csv_path = os.path.join(DEST_DIR, "kenya_tenders_flattened.csv")
df.to_csv(csv_path, index=False)
print(f"Successfully reflattened {len(df)} rows to {csv_path}!")
print("\nProcurement methods:")
print(df['procurement_method_title'].value_counts())
print("\nProcurement categories:")
print(df['procurement_category_title'].value_counts())
print("\nTop 5 Procuring Entities:")
print(df['procuring_entity_name'].value_counts().head(5))
