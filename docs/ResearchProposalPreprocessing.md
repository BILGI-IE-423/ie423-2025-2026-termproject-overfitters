# IE 423 Term Project Proposal — Global Food Crisis Early Warning System

## Team Information

- Begüm Acar
- İrem Ural
- Gamze Kılıç
- Sercan Çavuş

## Dataset Description

We use two primary datasets for this project:

1. **Global Food Prices (2016-2024)**
   - **Source:** Humanitarian Data Exchange (WFP) - [Link](https://data.humdata.org/dataset/global-wfp-food-prices)
   - **Description:** This datasets contains historical monthly food price data for various commodities across multiple countries and markets. It includes variables such as country, market, commodity type, price, unit, currency, and date, enabling the analysis of food price trends and sudden price fluctuations over time.  
2. **FAO Food Insecurity Dataset**
   - **Source:** World Bank Data360 - [Link](https://data360.worldbank.org/en/indicator/FAO_FS_210091)
   - **Description:** This dataset provides country-level measurements of food insecurity, offering macro-level insights into population vulnerability. It tracks the prevalence of moderate or severe food insecurity, which estimates the percentage of people living in households classified as moderately or severely food insecure.

We selected these datasets because combining micro-level economic shocks (monthly food prices) with macro-level vulnerability metrics (FAO food insecurity scores) allows us to explore meaningful patterns that precede humanitarian emergencies. The WFP dataset initially contains millions of rows across 9 years, which we aggregate into a robust panel dataset of monthly country-product observations.

## Dataset Access

The raw datasets are stored in:

`data/raw/`
- `wfp_food_prices_global_2016.csv` through `2024.csv`
- `FAO_FS_210091.csv`

Raw datasets can be downloaded from:
- [WFP Global Food Prices](https://data.humdata.org/dataset/global-wfp-food-prices)
- [FAO Food Insecurity Dataset](https://data360.worldbank.org/en/indicator/FAO_FS_210091)


## Research Questions

### Research Question 1
How does short-term price volatility (e.g., 3-month and 6-month rolling standard deviations) interact with baseline FAO food insecurity scores to precipitate sudden food crises in developing nations?

**Explanation:** Gradual price increases are common due to standard inflation, but hyper-volatility combined with high baseline insecurity might be the true trigger for a systemic crisis. By analyzing our engineered features like `volatility_ratio_3` and `volatility_ratio_6` alongside the `food_insecurity_score`, we aim to determine if volatile markets disproportionately trigger the `crisis_label` (a >= 20% price surge within 3 months) in regions that are already vulnerable, offering a more nuanced warning than simple price thresholds.

### Research Question 2
Are specific staple commodities (e.g., local grains vs. imported wheat) leading indicators of a broader regional food crisis, and does their predictive power vary significantly across different countries?

**Explanation:** Not all food price spikes trigger a crisis; regional and cultural reliance on specific staples dictates vulnerability. This question explores whether tracking a subset of critical, high-impact products yields higher predictive accuracy for upcoming food crises than aggregating all food items. Answering this can help policymakers build more resource-efficient and targeted monitoring systems.

### Research Question 3
Can we identify critical threshold values in short-term price fluctuations (1-month percentage changes) that consistently precede a 20% future price surge, and how do these patterns shift during global systemic anomalies like the 2020 pandemic?

**Explanation:** For an early warning system to be actionable, humanitarian organizations need concrete triggers. By examining the `pct_change_1m` alongside historical lag features, we want to mathematically pinpoint the "point of no return" where a short-term trend becomes a full-blown crisis. Furthermore, observing how these thresholds behave during known global disruptions (e.g., COVID-19 in 2020) will help us assess the model's robustness to unprecedented systemic shocks.

## Project Proposal

This project aims to develop a Global Food Crisis Early Warning System by investigating the relationship between historical food price fluctuations and food insecurity indicators. 

First, we will clean and preprocess the raw datasets by handling missing values, filtering out non-food items, and standardizing geographic codes (countryiso3). We will aggregate the high-frequency price data into monthly summaries and engineer temporal features, including lag prices, rolling means, and volatility ratios. We will define our target variable (`crisis_label`) mathematically as a 20% or greater surge in a product's average price within a 3-month future window.

Then, we will conduct an exploratory data analysis (EDA) to understand the distribution of our crisis labels, price volatility across different years, and the correlation between FAO insecurity scores and price shocks. 

Based on our research questions, we will apply descriptive statistics and machine learning classification methods to predict the `crisis_label`. Our goal is not only to build an accurate predictive model but also to generate interpretable findings that indicate *which* conditions most frequently lead to crises. 

Possible challenges include handling data sparsity (missing FAO scores for certain country-year pairs), managing temporal data leakage during cross-validation, and isolating true food crises from general national hyperinflation.

## Preprocessing Steps

### Step 1 — Loading the Data
The datasets (9 WFP files and 1 FAO file) were loaded using pandas in `scripts/01_load_data.py`. We concatenated the WFP yearly files into a single massive dataframe to ensure continuous time-series analysis.

### Step 2 — Initial Inspection
We checked:
- the shape of the concatenated dataset
- column names and data types
- category distributions (identifying and removing "non-food" items)
- missing values in critical columns (country, product, date, price)

### Step 3 — Cleaning and Feature Engineering
Using `scripts/02_preprocess_data.py`, we:
- Cleaned strings (countryiso3, products) and converted dates to datetime objects.
- Aggregated data to a monthly level (`wfp_monthly`), calculating mean, median, max, and std of prices.
- Engineered time-series features: 1, 3, and 6-month price lags (`price_lag_x`).
- Engineered rolling window features: 3 and 6-month rolling means and standard deviations to capture momentum and volatility.
- Clipped extreme outliers in the 1-month percentage change feature.
- **Target Creation:** Shifted the average price by -3 months to calculate `future_price_3m`. We dropped unresolved future dates (NaNs) and created a binary `crisis_label` (1 if future price surge >= 20%, else 0).
- Merged the WFP monthly data with the median-aggregated FAO food insecurity scores using a left join on `countryiso3` and `year`.
- Dropped intermediate columns to prevent data leakage.

### Step 4 — Saving Processed Data
The cleaned, merged, and feature-engineered dataset was saved to:

`data/processed/processed_food_crisis_data.csv`

## Initial Outputs

### Dataset Shape
- **Raw WFP Shape:** Spans millions of rows across 2016-2024.
- **Cleaned & Engineered Shape:** After monthly aggregation, NA dropping, and merging, the final `model_df` contains distinct monthly observations representing unique country-product pairs over time.

### Missing Value Summary
- Future dates where the 3-month forward price could not be observed were intentionally dropped to avoid labeling uncertainty.
- Some country-year pairs lacked FAO food insecurity scores. Observations missing essential engineered features or FAO scores were dropped to ensure a clean modeling dataset.

### Data Distributions
- **Target Variable (`crisis_label`):** The data represents an imbalanced classification problem, as a 20% price surge within 3 months represents a true anomaly rather than a daily occurrence. The exact proportion of `1`s vs `0`s is dynamically outputted by the preprocessing script.

### Example Visualization
*(Placeholder for actual EDA output)* The figure below, showing the historical price trend and crisis points of a specific staple commodity, was generated by `scripts/03_basic_eda.py`.

![Example Plot](../outputs/figures/example_plot.png)

## How to Run the Project

### 1. Clone the repository
```bash
git clone [https://github.com/BILGI-IE-423/ie423-2025-2026-termproject-overfitters/tree/main]
cd [ie423-2025-2026-termproject-overfitters]
```
### 2. Install required packages
```bash
pip install -r requirements.txt
```
### 3. Place the dataset
Put the raw WFP and FAO .csv files inside: `data/raw/`

### 4. Run the scripts
```bash
python scripts/01_load_data.py
python scripts/02_preprocess_data.py
python scripts/03_basic_eda.py
```

```markdown
## Transparency and Traceability
All outputs presented in this markdown file are generated from the Python scripts in the `scripts/` folder.

Figures are stored in `outputs/figures/`, tables are stored in `outputs/tables/`, and cleaned datasets are stored in `data/processed/`.

The repository is designed so that another user can reproduce the same outputs by installing the required packages and running the scripts in order.
