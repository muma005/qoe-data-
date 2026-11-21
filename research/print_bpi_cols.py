import pandas as pd
df = pd.read_csv(r'research/original_datasets/procurement_expenses/bpi_2019/BPI_Challenge_2019.csv', nrows=5, encoding='latin1')
print("Columns in BPI:", df.columns.tolist())
