import os
import pandas as pd

# Pandas display options
pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 200)

# Define paths relative to this script file (works regardless of working directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
FAO_FILE = os.path.join(RAW_DIR, "FAO_FS_210091.csv")


def load_data():
    # CHECK FILE PATHS

    print("\n---VERIFYING FILE PATHS ---")
    if not os.path.exists(RAW_DIR):
        print(f"[ERROR] Raw data directory not found at: {RAW_DIR}")
        return None, None

    if not os.path.exists(FAO_FILE):
        print(f"[ERROR] FAO file not found at: {FAO_FILE}")
        return None, None

    # Generate WFP expected file paths and check them
    wfp_files = [os.path.join(RAW_DIR, f"wfp_food_prices_global_{year}.csv") for year in range(2016, 2025)]
    valid_wfp_files = [f for f in wfp_files if os.path.exists(f)]

    if len(valid_wfp_files) != len(wfp_files):
        print(f"[WARNING] Only {len(valid_wfp_files)} out of {len(wfp_files)} WFP files found.")

    if not valid_wfp_files:
        print("[ERROR] No valid WFP data files found! Please check your raw data directory.")
        return None, None

    print("[SUCCESS] Target file paths verified.")

    # LOAD THE DATASET

    print("\n---LOADING DATASETS ---")
    wfp_list = []

    for f in valid_wfp_files:
        # encoding='latin1' parametresi eklendi
        temp = pd.read_csv(f, encoding='latin1')
        wfp_list.append(temp)
        print(f"Loaded: {os.path.basename(f):<35} | {temp.shape[0]:>8} rows")

    wfp_df = pd.concat(wfp_list, ignore_index=True)

    # encoding='latin1' parametresi eklendi
    fao_df = pd.read_csv(FAO_FILE, encoding='latin1')
    print("[SUCCESS] All datasets combined and loaded into Pandas DataFrames.")

    # BASIC DATASET INFORMATION

    print("\n---BASIC DATASET INFORMATION ---")

    print("\n[WFP Combined Dataset Info]")
    print(f"Total Rows: {wfp_df.shape[0]} | Total Columns: {wfp_df.shape[1]}")
    # Display missing values per column for WFP
    print("\nMissing Values per column (WFP):")
    print(wfp_df.isnull().sum())

    print("\n" + "-" * 40)

    print("\n[FAO Dataset Info]")
    print(f"Total Rows: {fao_df.shape[0]} | Total Columns: {fao_df.shape[1]}")
    # Display missing values per column for FAO
    print("\nMissing Values per column (FAO):")
    print(fao_df.isnull().sum())

    print("\n---DATA PREVIEWS (First 3 Rows) ---")
    print("\nWFP Dataset Preview:")
    print(wfp_df.head(3))
    print("\nFAO Dataset Preview:")
    print(fao_df.head(3))

    return wfp_df, fao_df


if __name__ == "__main__":
    wfp_data, fao_data = load_data()