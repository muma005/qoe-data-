import pandas as pd

bpi_path = r"research\original_datasets\procurement_expenses\bpi_2019\BPI_Challenge_2019.csv"
cols = ['case concept:name', 'event concept:name', 'event time:timestamp']

print("Checking trace start activities and maverick buying definitions...")
df = pd.read_csv(bpi_path, usecols=cols, encoding='latin1', low_memory=False)
df.columns = [c.strip() for c in df.columns]

# Parse timestamps
df['dt'] = pd.to_datetime(df['event time:timestamp'], format='%d-%m-%Y %H:%M:%S.%f', errors='coerce')
df = df.dropna(subset=['case concept:name', 'dt']).sort_values(by=['case concept:name', 'dt'])

# What is the FIRST event in each case trace?
first_events = df.groupby('case concept:name')['event concept:name'].first()
print("\nDistribution of FIRST activity in case trace:")
print(first_events.value_counts().head(10))

# Cases where 'Vendor creates invoice' occurs before 'Create Purchase Order Item'
ts_po = df[df['event concept:name'] == 'Create Purchase Order Item'].groupby('case concept:name')['dt'].first()
ts_vendor_inv = df[df['event concept:name'] == 'Vendor creates invoice'].groupby('case concept:name')['dt'].first()
ts_ir = df[df['event concept:name'] == 'Record Invoice Receipt'].groupby('case concept:name')['dt'].first()

m_df = pd.DataFrame(index=df['case concept:name'].unique())
m_df['t_po'] = ts_po
m_df['t_vendor_inv'] = ts_vendor_inv
m_df['t_ir'] = ts_ir

v_inv_before_po = (m_df['t_vendor_inv'] < m_df['t_po']).sum()
ir_before_po = (m_df['t_ir'] < m_df['t_po']).sum()
no_po = m_df['t_po'].isnull().sum()

print(f"\nTotal Cases: {len(m_df):,}")
print(f"Cases without 'Create Purchase Order Item': {no_po:,} ({no_po/len(m_df)*100:.2f}%)")
print(f"'Vendor creates invoice' < 'Create Purchase Order Item': {v_inv_before_po:,} ({v_inv_before_po/len(m_df)*100:.2f}%)")
print(f"'Record Invoice Receipt' < 'Create Purchase Order Item': {ir_before_po:,} ({ir_before_po/len(m_df)*100:.2f}%)")

# Also check how often 'Vendor creates invoice' occurs BEFORE 'Create Purchase Requisition Item'
ts_pr = df[df['event concept:name'] == 'Create Purchase Requisition Item'].groupby('case concept:name')['dt'].first()
m_df['t_pr'] = ts_pr
po_without_pr = (m_df['t_po'].notnull() & m_df['t_pr'].isnull()).sum()
print(f"Cases with PO created directly WITHOUT Purchase Requisition: {po_without_pr:,} ({po_without_pr/len(m_df)*100:.2f}%)")
