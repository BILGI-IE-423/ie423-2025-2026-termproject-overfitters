import os
import pandas as pd

pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 200)

# Paths
WFP_DIR = "data/raw"
FAO_FILE = "data/raw/FAO_FS_210091.csv"

# WFP files from 2016 to 2024
wfp_files = [
    os.path.join(WFP_DIR, f"wfp_food_prices_global_{year}.csv")
    for year in range(2016, 2025)
]

# Load WFP files
wfp_list = []

for f in wfp_files:
    temp = pd.read_csv(f)
    wfp_list.append(temp)
    print(f"Loaded: {os.path.basename(f):<35} | {temp.shape[0]:>8} rows")

# Combine WFP files
wfp = pd.concat(wfp_list, ignore_index=True)
print("\nCombined WFP shape:", wfp.shape)

# Load FAO file
fao = pd.read_csv(FAO_FILE)
print("FAO shape:", fao.shape)

# Save loaded datasets for preprocessing
os.makedirs("data/processed", exist_ok=True)

wfp.to_csv("data/processed/wfp_loaded.csv", index=False)
fao.to_csv("data/processed/fao_loaded.csv", index=False)

print("\nSaved loaded datasets to data/processed/")
