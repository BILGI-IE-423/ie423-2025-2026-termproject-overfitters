import pandas as pd
import numpy as np
import os
from glob import glob


def run_pure_hybrid_preprocessing():
    # -----------------------------
    # 1. DYNAMIC FILE PATHS
    # -----------------------------
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    input_dir = os.path.join(project_root, "data", "raw")
    output_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------
    # 2. DATA LOADING AND CLEANING
    # -----------------------------
    wfp_files = glob(os.path.join(input_dir, "wfp_food_prices_global_*.csv"))
    if not wfp_files:
        print("ERROR: No WFP files found in data/raw directory!")
        return

    wfp_raw = pd.concat([pd.read_csv(f, encoding='latin-1', low_memory=False) for f in wfp_files], ignore_index=True)

    # Selection including coordinates
    wfp = wfp_raw[["countryiso3", "date", "commodity", "category", "price"]].copy()
    wfp.columns = ["countryiso3", "date", "product", "category", "price"]

    wfp["date"] = pd.to_datetime(wfp["date"], errors="coerce")
    wfp["price"] = pd.to_numeric(wfp["price"], errors="coerce")

    wfp = wfp[wfp["category"] != "non-food"].copy()
    wfp = wfp.dropna(subset=["countryiso3", "date", "product", "price"]).copy()

    wfp["year"] = wfp["date"].dt.year
    wfp["month"] = wfp["date"].dt.month

    # -----------------------------
    # 3. WFP COUNTRY FILTERING (Continuity Check)
    # -----------------------------
    MIN_YEARS_WFP = 4
    country_years = wfp.groupby("countryiso3")["year"].apply(lambda x: sorted(x.unique()))

    def has_gap(years):
        for a, b in zip(years[:-1], years[1:]):
            if b - a > 1: return True
        return False

    too_few_wfp = country_years[country_years.apply(len) < MIN_YEARS_WFP].index.tolist()
    gapped_wfp = country_years[country_years.apply(len) >= MIN_YEARS_WFP]
    gapped_wfp = gapped_wfp[gapped_wfp.apply(has_gap)].index.tolist()

    excluded_wfp = sorted(set(too_few_wfp + gapped_wfp))
    wfp = wfp[~wfp["countryiso3"].isin(excluded_wfp)].copy()

    # -----------------------------
    # 4. MONTHLY AGGREGATION AND ALIGNMENT
    # -----------------------------
    wfp_monthly = wfp.groupby(["countryiso3", "product", "year", "month"], as_index=False).agg(
        avg_price=("price", "mean"),
        median_price=("price", "median"),
        max_price=("price", "max"),
        price_std=("price", "std"),
        obs_count=("price", "count")
    )

    wfp_monthly["date"] = pd.to_datetime(
        wfp_monthly["year"].astype(str) + "-" + wfp_monthly["month"].astype(str) + "-01")

    g = ["countryiso3", "product"]
    wfp_monthly = (
        wfp_monthly.sort_values(g + ["date"])
        .set_index("date")
        .groupby(g)
        .apply(lambda x: x.asfreq("MS"))
        .drop(columns=g, errors='ignore')
        .reset_index()
    )
    wfp_monthly["year"] = wfp_monthly["date"].dt.year
    wfp_monthly["month"] = wfp_monthly["date"].dt.month

    # -----------------------------
    # 5. FEATURE ENGINEERING
    # -----------------------------
    wfp_monthly = wfp_monthly.sort_values(["countryiso3", "product", "date"]).copy()

    wfp_monthly["price_lag_1"] = wfp_monthly.groupby(g)["avg_price"].shift(1)
    wfp_monthly["price_lag_3"] = wfp_monthly.groupby(g)["avg_price"].shift(3)
    wfp_monthly["price_lag_6"] = wfp_monthly.groupby(g)["avg_price"].shift(6)

    wfp_monthly["rolling_mean_3"] = wfp_monthly.groupby(g)["avg_price"].transform(
        lambda x: x.rolling(3, min_periods=3).mean())
    wfp_monthly["rolling_mean_6"] = wfp_monthly.groupby(g)["avg_price"].transform(
        lambda x: x.rolling(6, min_periods=6).mean())
    wfp_monthly["rolling_std_3"] = wfp_monthly.groupby(g)["avg_price"].transform(
        lambda x: x.rolling(3, min_periods=3).std())
    wfp_monthly["rolling_std_6"] = wfp_monthly.groupby(g)["avg_price"].transform(
        lambda x: x.rolling(6, min_periods=6).std())

    wfp_monthly["pct_change_1m"] = ((wfp_monthly["avg_price"] - wfp_monthly["price_lag_1"]) / wfp_monthly[
        "price_lag_1"]) * 100
    wfp_monthly["volatility_ratio_3"] = wfp_monthly["rolling_std_3"] / wfp_monthly["rolling_mean_3"]
    wfp_monthly["volatility_ratio_6"] = wfp_monthly["rolling_std_6"] / wfp_monthly["rolling_mean_6"]
    wfp_monthly["pct_change_1m"] = wfp_monthly["pct_change_1m"].clip(lower=wfp_monthly["pct_change_1m"].quantile(0.01),
                                                                     upper=wfp_monthly["pct_change_1m"].quantile(0.99))

    # -----------------------------
    # 6. TARGET LABELING (Predictive - 3 months ahead)
    # -----------------------------
    wfp_monthly["future_price_3m"] = wfp_monthly.groupby(g)["avg_price"].shift(-3)
    wfp_monthly = wfp_monthly.dropna(subset=["future_price_3m"])
    # Crisis if price increases by 20% or more in 3 months
    wfp_monthly["crisis_label"] = np.where(
        (wfp_monthly["future_price_3m"] - wfp_monthly["avg_price"]) / wfp_monthly["avg_price"] >= 0.20, 1, 0)
    wfp_monthly = wfp_monthly.drop(columns=["future_price_3m"])

    # -----------------------------
    # 7. FAO DATA AND MERGING
    # -----------------------------
    fao_path = os.path.join(input_dir, "FAO_FS_210091.csv")
    if os.path.exists(fao_path):
        fao_raw = pd.read_csv(fao_path, encoding='latin-1', low_memory=False)
        fao = fao_raw[fao_raw["SEX_LABEL"].astype(str).str.contains("Total", case=False)]
        fao_ready = fao[["REF_AREA", "REF_AREA_LABEL", "TIME_PERIOD", "OBS_VALUE"]].copy()
        fao_ready.columns = ["countryiso3", "country_name", "year", "fao_score"]
        fao_ready = fao_ready.groupby(["countryiso3", "country_name", "year"], as_index=False)["fao_score"].median()

        merged = pd.merge(wfp_monthly, fao_ready, on=["countryiso3", "year"], how="inner")

        # -----------------------------
        # 8. FAO COUNTRY FILTERING
        # -----------------------------
        MIN_YEARS_FAO = 4
        fao_years_per_country = merged.groupby("countryiso3")["year"].nunique()
        excluded_low_fao = fao_years_per_country[fao_years_per_country < MIN_YEARS_FAO].index.tolist()

        print(f"Removing {len(excluded_low_fao)} countries with insufficient FAO data duration (<{MIN_YEARS_FAO} years)...")
        merged = merged[~merged["countryiso3"].isin(excluded_low_fao)].copy()
    else:
        print("CRITICAL WARNING: FAO file not found!")
        merged = wfp_monthly

    # -----------------------------
    # 9. FINAL EXPORT
    # -----------------------------
    index_cols = ["countryiso3", "country_name", "product", "year", "month"]
    feature_cols = ["avg_price", "median_price", "max_price", "price_std", "obs_count",
                    "price_lag_1", "price_lag_3", "price_lag_6", "rolling_mean_3",
                    "rolling_mean_6", "rolling_std_3", "rolling_std_6", "pct_change_1m",
                    "volatility_ratio_3", "volatility_ratio_6", "fao_score"]

    available_features = [col for col in feature_cols if col in merged.columns]
    model_df = merged[index_cols + available_features + ["crisis_label"]].dropna(subset=available_features).copy()

    output_path = os.path.join(output_dir, "processed_food_crisis_data.csv")
    model_df.to_csv(output_path, index=False)

    print("-" * 50)
    print(f"SUCCESS! Dataset saved: {output_path}")
    print(f"Total Number of Countries: {model_df['countryiso3'].nunique()}")
    print(f"Total Number of Rows: {len(model_df)}")
    print(f"Columns: {list(model_df.columns)}")

    # --------------------------------
    # 10. CLASS BALANCE REPORT
    # --------------------------------
    crisis_ratio = model_df["crisis_label"].mean()
    print("-" * 50)
    print(f"Class Distribution -> Crisis=1: {crisis_ratio * 100:.1f}% | No Crisis=0: {(1 - crisis_ratio) * 100:.1f}%")
    if crisis_ratio < 0.3:
        print("WARNING: Class imbalance detected.")
        print("  -> Use class_weight='balanced' during model training.")
        print("  -> Or apply SMOTE AFTER the train/test split.")


if __name__ == "__main__":
    run_pure_hybrid_preprocessing()