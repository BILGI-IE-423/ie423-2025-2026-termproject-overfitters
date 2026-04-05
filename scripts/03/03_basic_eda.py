import pandas as pd
from IPython.display import display

pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 200)

model_df = pd.read_csv("data/processed/processed_food_crisis_data.csv")
model_df["date"] = pd.to_datetime(model_df["date"])

print("=" * 60)
print("FINAL DATASET SUMMARY")
print("=" * 60)
print(f"Shape                      : {model_df.shape}")
print(f"Number of Countries        : {model_df['countryiso3'].nunique()}")
print(f"Number of Products         : {model_df['product'].nunique()}")
print(f"Year Range                 : {model_df['year'].min()} - {model_df['year'].max()}")
print(f"Date Range                 : {model_df['date'].min().date()} → {model_df['date'].max().date()}")
print()

print("Crisis label distribution:")
print(model_df["crisis_label"].value_counts())
print(model_df["crisis_label"].value_counts(normalize=True).round(3))
print()

missing = model_df.isna().sum()
print("Missing value check (feature columns):")
print(missing[missing > 0] if missing.any() else "  ✓ No missing values")
print()

print("Number of years per country (min/max/median):")
years_per_country = model_df.groupby("countryiso3")["year"].nunique()
print(years_per_country.describe())
print()

print("Row count per country (min/max):")
rows_per_country = model_df.groupby("countryiso3").size()
print(rows_per_country.describe())
print()

display(model_df.head())
