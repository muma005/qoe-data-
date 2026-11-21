import os
import pandas as pd

bpi_path = r"research\original_datasets\procurement_expenses\bpi_2019\BPI_Challenge_2019.csv"

with open(bpi_path, 'r', encoding='utf-8', errors='ignore') as f:
    for i in range(15):
        print(f"L{i+1}: {f.readline().strip()}")
