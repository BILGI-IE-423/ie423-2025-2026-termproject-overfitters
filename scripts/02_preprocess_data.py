import pandas as pd
import numpy as np
import os
from IPython.display import display

pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 200)

# Load previously saved raw datasets
wfp_raw = pd.read_csv("data/processed/wfp_raw_loaded.csv")
fao_raw = pd.read_csv("data/processed/fao_raw_loaded.csv")

# -----------------------------
# WFP SELECTION AND CLEANING
# -----------------------------
wfp = wfp_raw[["countryiso3", "date", "commodity", "category", "usdprice"]].copy()
wfp.columns = ["countryiso3", "date", "product", "category", "price"]

wfp["date"] = pd.to_datetime(wfp["date"], errors="coerce")
wfp["price"] = pd.to_numeric(wfp["price"], errors="coerce")

print("Category distribution (before cleaning):")
print(wfp["category"].value_counts())

# Remove non-food category
wfp = wfp[wfp["category"] != "non-food"].copy()
wfp = wfp.dropna(subset=["countryiso3", "date", "product", "price"]).copy()

wfp["year"] = wfp["date"].dt.year
wfp["month"] = wfp["date"].dt.month

print("\nCleaned WFP shape:", wfp.shape)
display(wfp.head())

# -----------------------------
# COUNTRY FILTERING — WFP
# -----------------------------
MIN_YEARS = 4        # minimum number of distinct years required
MAX_GAP_YEARS = 1    # maximum allowed gap between consecutive years

# Distinct years of each country in WFP
country_years = (
    wfp.groupby("countryiso3")["year"]
    .apply(lambda x: sorted(x.unique()))
)

def has_gap(years):
    """Is there any gap between consecutive years? (Even 2017→2019 is excluded)"""
    for a, b in zip(years[:-1], years[1:]):
        if b - a > 1:
            return True
    return False

# Filter 1: < MIN_YEARS years
too_few = country_years[country_years.apply(len) < MIN_YEARS].index.tolist()

# Filter 2: fragmented coverage (among countries with enough years)
has_enough = country_years[country_years.apply(len) >= MIN_YEARS]
gapped = has_enough[has_enough.apply(has_gap)].index.tolist()

excluded = sorted(set(too_few + gapped))

print("=== WFP Country Filtering Results ===")
print(f"Total countries (raw):            {country_years.shape[0]}")
print(f"Removed (<{MIN_YEARS} years):      {len(too_few)}  → {too_few}")
print(f"Removed (fragmented data):         {len(gapped)}  → {gapped}")
print(f"Total removed countries:           {len(excluded)}")
print(f"Remaining countries:               {country_years.shape[0] - len(excluded)}")

# Apply the filter
wfp = wfp[~wfp["countryiso3"].isin(excluded)].copy()
print(f"\nWFP shape (after filtering): {wfp.shape}")

# -----------------------------
# MONTHLY AGGREGATION
# -----------------------------
wfp_monthly = (
    wfp.groupby(["countryiso3", "product", "year", "month"], as_index=False)
       .agg(
           avg_price=("price", "mean"),
           median_price=("price", "median"),
           max_price=("price", "max"),
           price_std=("price", "std"),
           obs_count=("price", "count")
       )
)

wfp_monthly["date"] = pd.to_datetime(
    wfp_monthly["year"].astype(str) + "-" +
    wfp_monthly["month"].astype(str) + "-01"
)

print("\nwfp_monthly shape:", wfp_monthly.shape)
display(wfp_monthly.head())

# -----------------------------
# MONTHLY FREQUENCY ALIGNMENT
# -----------------------------
g = ["countryiso3", "product"]

wfp_monthly = (
    wfp_monthly.sort_values(g + ["date"])
        .set_index("date")
        .groupby(g, group_keys=False)
        .apply(lambda df: df.asfreq("MS"))
        .reset_index()
)

wfp_monthly["year"] = wfp_monthly["date"].dt.year
wfp_monthly["month"] = wfp_monthly["date"].dt.month

print("\nwfp_monthly shape after asfreq:", wfp_monthly.shape)
display(wfp_monthly.head())

# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
wfp_monthly = wfp_monthly.sort_values(["countryiso3", "product", "date"]).copy()

g = ["countryiso3", "product"]

# Lag prices
wfp_monthly["price_lag_1"] = wfp_monthly.groupby(g)["avg_price"].shift(1)
wfp_monthly["price_lag_3"] = wfp_monthly.groupby(g)["avg_price"].shift(3)
wfp_monthly["price_lag_6"] = wfp_monthly.groupby(g)["avg_price"].shift(6)

# Rolling averages
wfp_monthly["rolling_mean_3"] = (
    wfp_monthly.groupby(g)["avg_price"]
    .transform(lambda x: x.rolling(3, min_periods=3).mean())
)

wfp_monthly["rolling_mean_6"] = (
    wfp_monthly.groupby(g)["avg_price"]
    .transform(lambda x: x.rolling(6, min_periods=6).mean())
)

# Rolling standard deviations
wfp_monthly["rolling_std_3"] = (
    wfp_monthly.groupby(g)["avg_price"]
    .transform(lambda x: x.rolling(3, min_periods=3).std())
)

wfp_monthly["rolling_std_6"] = (
    wfp_monthly.groupby(g)["avg_price"]
    .transform(lambda x: x.rolling(6, min_periods=6).std())
)

# Percentage change (1 month)
wfp_monthly["pct_change_1m"] = (
    (wfp_monthly["avg_price"] - wfp_monthly["price_lag_1"]) / wfp_monthly["price_lag_1"]
) * 100

# Volatility ratios
wfp_monthly["volatility_ratio_3"] = wfp_monthly["rolling_std_3"] / wfp_monthly["rolling_mean_3"]
wfp_monthly["volatility_ratio_6"] = wfp_monthly["rolling_std_6"] / wfp_monthly["rolling_mean_6"]

# Clip extreme values in pct_change_1m
wfp_monthly["pct_change_1m"] = wfp_monthly["pct_change_1m"].clip(
    lower=wfp_monthly["pct_change_1m"].quantile(0.01),
    upper=wfp_monthly["pct_change_1m"].quantile(0.99)
)

print("Feature engineering completed.")
display(wfp_monthly.head(10))

# -----------------------------
# CRISIS LABEL
# -----------------------------
# 1. Get the price 3 months later
wfp_monthly["future_price_3m"] = wfp_monthly.groupby(
    ["countryiso3", "product"]
)["avg_price"].shift(-3)

# 2. Drop rows where future value is unknown
wfp_monthly = wfp_monthly.dropna(subset=["future_price_3m"])

# 3. Create crisis label
wfp_monthly["crisis_label"] = np.where(
    (wfp_monthly["future_price_3m"] - wfp_monthly["avg_price"]) /
     wfp_monthly["avg_price"] >= 0.20,
    1, 0
)

# 4. Drop temporary column
wfp_monthly = wfp_monthly.drop(columns=["future_price_3m"])

print("Crisis label distribution:")
print(wfp_monthly["crisis_label"].value_counts())
print(wfp_monthly["crisis_label"].value_counts(normalize=True).round(3))

# -----------------------------
# FAO PREPARATION
# -----------------------------
fao = fao_raw[
    fao_raw["SEX_LABEL"].astype(str).str.strip().str.lower() == "total"
][["REF_AREA", "REF_AREA_LABEL", "TIME_PERIOD", "OBS_VALUE"]].copy()

fao.columns = ["countryiso3", "country", "year", "food_insecurity_score"]

# If there are multiple records for the same country-year, take the median
fao_ready = (
    fao.groupby(["countryiso3", "country", "year"], as_index=False)["food_insecurity_score"]
    .median()
)

print("Prepared FAO shape:", fao_ready.shape)
display(fao_ready.head())

# -----------------------------
# MERGE
# -----------------------------
merged = pd.merge(
    wfp_monthly,
    fao_ready[["countryiso3", "year", "food_insecurity_score", "country"]],
    on=["countryiso3", "year"],
    how="left"
)

matched = merged["food_insecurity_score"].notna().sum()
total = len(merged)

print("Shape:", merged.shape)
print("Number of countries:", merged["countryiso3"].nunique())
print("Number of products:", merged["product"].nunique())
print("Year range:", merged["year"].min(), "-", merged["year"].max())
print(f"FAO match rate: {matched}/{total} countries ({matched/total*100:.1f}%)")
print("FAO missing rate:", merged["food_insecurity_score"].isna().mean().round(3))

# -----------------------------
# COUNTRY FILTERING — FAO
# -----------------------------
MIN_YEARS_FAO = 4   # Minimum threshold for FAO years matched with WFP

# Count distinct years with available FAO scores for each country
fao_years_per_country = (
    merged.dropna(subset=["food_insecurity_score"])
    .groupby("countryiso3")["year"]
    .nunique()
)

# Countries present in WFP but with no FAO score at all are also removed
wfp_countries = set(merged["countryiso3"].unique())
fao_countries = set(fao_years_per_country.index.tolist())

wfp_only_countries = sorted(list(wfp_countries - fao_countries))
low_fao_countries = fao_years_per_country[fao_years_per_country < MIN_YEARS_FAO].index.tolist()

excluded_fao = sorted(set(wfp_only_countries + low_fao_countries))

print("=== FAO Country Filtering Results ===")
print(f"Present in WFP, missing entirely in FAO: {len(wfp_only_countries)}  → {sorted(wfp_only_countries)}")
print(f"FAO < {MIN_YEARS_FAO} matched years:     {len(low_fao_countries)}  → {low_fao_countries}")
print(f"Total removed (FAO filter):              {len(excluded_fao)}")

merged = merged[~merged["countryiso3"].isin(excluded_fao)].copy()

print(f"\nMerged shape after FAO filtering: {merged.shape}")
print(f"Remaining number of countries: {merged['countryiso3'].nunique()}")

# -----------------------------
# FINAL MODEL DATASET
# -----------------------------
index_cols = ["countryiso3", "country", "product", "year", "month", "date"]

feature_cols = [
    "avg_price",
    "median_price",
    "max_price",
    "price_std",
    "obs_count",
    "price_lag_1",
    "price_lag_3",
    "price_lag_6",
    "rolling_mean_3",
    "rolling_mean_6",
    "rolling_std_3",
    "rolling_std_6",
    "pct_change_1m",
    "volatility_ratio_3",
    "volatility_ratio_6",
    "food_insecurity_score"
]

model_df = merged[index_cols + feature_cols + ["crisis_label"]].copy()
model_df = model_df.dropna(subset=feature_cols).copy()

print("model_df shape:", model_df.shape)
print("Number of countries:", model_df["countryiso3"].nunique())
print("Number of products:", model_df["product"].nunique())
print("Year range:", model_df["year"].min(), "-", model_df["year"].max())
print()
print("Crisis label distribution:")
print(model_df["crisis_label"].value_counts())
print(model_df["crisis_label"].value_counts(normalize=True).round(3))
display(model_df.head())

# Save processed dataset
os.makedirs("data/processed", exist_ok=True)
output_path = "data/processed/processed_food_crisis_data.csv"
model_df.to_csv(output_path, index=False)

print("Saved processed data to:", output_path)
print("Shape:", model_df.shape)
