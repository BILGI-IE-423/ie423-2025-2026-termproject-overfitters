# IE 423 Term Project Proposal — Global Food Crisis Early Warning System

---

<hr style="height:3px; border:none; background-color:#666;">

## Team Information

---

- Begüm Acar
- İrem Ural
- Gamze Kılıç
- Sercan Çavuş

<hr style="height:3px; border:none; background-color:#666;">

## Dataset Description

---

We use two primary datasets for this project:

1. **Global Food Prices (2016-2024)**
   - **Source:** Humanitarian Data Exchange (WFP) - [Link](https://data.humdata.org/dataset/global-wfp-food-prices)
   - **Description:** This dataset contains historical tracking of food prices for various commodities across different countries, collected by the World Food Programme. 
2. **FAO Food Insecurity Dataset**
   - **Source:** World Bank Data360 - [Link](https://data360.worldbank.org/en/indicator/FAO_FS_210091)
   - **Description:** This dataset provides macro-level indicators of food insecurity, tracking the prevalence of food vulnerability at a country-year level.

We selected these datasets because combining micro-level economic shocks (monthly food prices) with macro-level vulnerability metrics (FAO food insecurity scores) allows us to explore meaningful patterns that precede humanitarian emergencies. The WFP dataset initially contains millions of rows across 9 years, which we aggregate into a robust panel dataset of monthly country-product observations.

<hr style="height:3px; border:none; background-color:#666;">

## Dataset Access

---

The raw datasets are stored in:

`data/raw/`
- `wfp_food_prices_global_2016.csv` through `2024.csv`
- `FAO_FS_210091.csv`

Raw datasets can be downloaded from:
- [WFP Global Food Prices](https://data.humdata.org/dataset/global-wfp-food-prices)
- [FAO Food Insecurity Dataset](https://data360.worldbank.org/en/indicator/FAO_FS_210091)

<hr style="height:3px; border:none; background-color:#666;">


## Research Questions

---

### Research Question 1
How does short-term price volatility (e.g., 3-month and 6-month rolling standard deviations) interact with baseline FAO food insecurity scores to precipitate sudden food crises in developing nations?

**Explanation:** Gradual price increases are common due to standard inflation, but hyper-volatility combined with high baseline insecurity might be the true trigger for a systemic crisis. By analyzing our engineered features like `volatility_ratio_3` and `volatility_ratio_6` alongside the `food_insecurity_score`, we aim to determine if volatile markets disproportionately trigger the `crisis_label` (a >= 20% price surge within 3 months) in regions that are already vulnerable, offering a more nuanced warning than simple price thresholds.

---

### Research Question 2
Are specific staple commodities (e.g., local grains vs. imported wheat) leading indicators of a broader regional food crisis, and does their predictive power vary significantly across different countries?

**Explanation:** Not all food price spikes trigger a crisis; regional and cultural reliance on specific staples dictates vulnerability. This question explores whether tracking a subset of critical, high-impact products yields higher predictive accuracy for upcoming food crises than aggregating all food items. Answering this can help policymakers build more resource-efficient and targeted monitoring systems.

---

### Research Question 3
Can we identify critical threshold values in short-term price fluctuations (1-month percentage changes) that consistently precede a 20% future price surge?

**Explanation:** For an early warning system to be actionable, humanitarian organizations need concrete triggers. By examining the `pct_change_1m` alongside historical lag features, we want to mathematically pinpoint the "point of no return" where a short-term trend becomes a full-blown crisis.

<hr style="height:3px; border:none; background-color:#666;">


## Project Proposal

---

This project aims to develop a Global Food Crisis Early Warning System by investigating the relationship between historical food price fluctuations and food insecurity indicators. 

First, we will clean and preprocess the raw datasets by handling missing values, filtering out non-food items, and standardizing geographic codes (countryiso3). We will aggregate the high-frequency price data into monthly summaries and engineer temporal features, including lag prices, rolling means, and volatility ratios. We will define our target variable (`crisis_label`) mathematically as a 20% or greater surge in a product's average price within a 3-month future window. The United Nations Food and Agriculture Organization (FAO) consistently defines a short-term price shock of 20% or more in staple foods as a critical turning point that significantly erodes purchasing power and leads to acute food insecurity among vulnerable populations. Therefore, the crisis is defined as a 20% change.

Then, we will conduct an exploratory data analysis (EDA) to understand the distribution of our crisis labels, price volatility across different years, and the correlation between FAO insecurity scores and price shocks. 

Based on our research questions, we will apply descriptive statistics and machine learning classification methods to predict the `crisis_label`. Our goal is not only to build an accurate predictive model but also to generate interpretable findings that indicate *which* conditions most frequently lead to crises. 

Possible challenges include handling data sparsity (missing FAO scores for certain country-year pairs), managing temporal data leakage during cross-validation, and isolating true food crises from general national hyperinflation.

<hr style="height:3px; border:none; background-color:#666;">


## Preprocessing Steps

---

### Step 1 — Loading the Data
The datasets (9 WFP files and 1 FAO file) were loaded using pandas in `scripts/01_load_data.py`. We concatenated the WFP yearly files into a single massive dataframe to ensure continuous time-series analysis.

---

### Step 2 — Initial Inspection
We checked:
- the shape of the concatenated dataset
- column names and data types
- category distributions (identifying and removing "non-food" items)
- missing values in critical columns (country, product, date, price)

---

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

---

### Step 4 — Saving Processed Data
The cleaned, merged, and feature-engineered dataset was saved to:

`data/processed/processed_food_crisis_data.csv`

<hr style="height:3px; border:none; background-color:#666;">


## Initial Outputs

---

### Dataset Shape
- **Raw WFP Shape:** Spans millions of rows across 2016-2024.
- **Cleaned & Engineered Shape:** After monthly aggregation, NA dropping, and merging, the final `model_df` contains distinct monthly observations representing unique country-product pairs over time.

---

### Missing Value Summary
- Future dates where the 3-month forward price could not be observed were intentionally dropped to avoid labeling uncertainty.
- Some country-year pairs lacked FAO food insecurity scores. Observations missing essential engineered features or FAO scores were dropped to ensure a clean modeling dataset.

---

### Data Distributions
- **Target Variable (`crisis_label`):** The data represents an imbalanced classification problem, as a 20% price surge within 3 months represents a true anomaly rather than a daily occurrence. The exact proportion of `1`s vs `0`s is dynamically outputted by the preprocessing script.

<hr style="height:3px; border:none; background-color:#666;">


## Visualizations
All outputs below are generated by `scripts/03_basic_eda.py`.

---

### Figure 1 - Global Food Insecurity Rankings Barchart
>Generated by: scripts/03_basic_eda.py → saved to `outputs/figures/Global_Food_Insecurity_Rankings_Barchart.png`

![Global Food Insecurity Rankings Barchart](https://github.com/BILGI-IE-423/ie423-2025-2026-termproject-overfitters/blob/main/outputs/figures/Global_Food_Insecurity_Rankings_Barchart.png)

This graph compares the average food insecurity indices of the countries in the dataset, clearly revealing that countries like Afghanistan and Ethiopia are in the highest risk group. The visualization provides a hierarchy for identifying which regions are experiencing more chronic and severe food crises, offering a key indicator for your early warning system.

---

### Figure 2 - Global Food Crisis Map Bubblechart
>Generated by: scripts/03_basic_eda.py → saved to `outputs/figures/Global_Food_Crisis_Map_Bubblechart.png`

![Global Food Crisis Map Bubblechart](https://github.com/BILGI-IE-423/ie423-2025-2026-termproject-overfitters/blob/main/outputs/figures/Global_Food_Crisis_Map_Bubblechart.png)

The global food crisis map highlights at-risk hotspots by showing the geographical intensity and severity of crisis events on a coordinate-based system. The balloon sizes represent the degree of impact of the crisis, providing spatial insight into which regions should be prioritized by early warning systems.

---

### Figure 3 - The Relationship Between Price Changes and Crisis Boxplot
>Generated by: scripts/03_basic_eda.py → saved to `outputs/figures/The_Relationship_Between_Price_Changes_and_Crisis_Boxplot.png`

![The Relationship Between Price Changes and Crisis Boxplot](https://github.com/BILGI-IE-423/ie423-2025-2026-termproject-overfitters/blob/main/outputs/figures/The_Relationship_Between_Price_Changes_and_Crisis_Boxplot.png)

A boxplot examines the relationship between percentage changes in food prices and crisis situations, demonstrating that price fluctuations and outliers are much more pronounced during periods of crisis. This analysis proves that price shocks are one of the most critical leading indicators for an early warning system.

---

### Figure 4 - Correlation Matrix of Food Crisis Indicators Heatmap
>Generated by: scripts/03_basic_eda.py → saved to `outputs/figures/Correlation_ Matrix_of_ Food_Crisis _Indicators_Heatmap.png`

![Correlation Matrix of Food Crisis Indicators Heatmap](https://github.com/BILGI-IE-423/ie423-2025-2026-termproject-overfitters/blob/main/outputs/figures/Correlation_%20Matrix_of_%20Food_Crisis%20_Indicators_Heatmap.png)

The correlation matrix analyzes the linear relationships between food crisis indicators, identifying which variables have the strongest correlation with the crisis situation. This visualization provides a scientific basis for selecting the most effective features to be used in the prediction model.

---

### Figure 5 - Annual Crisis Intensity Heatmap
>Generated by: scripts/03_basic_eda.py → saved to `outputs/figures/Annual_crisis_intensity_Heatmap.png`

![Annual Crisis Intensity Heatmap](https://github.com/BILGI-IE-423/ie423-2025-2026-termproject-overfitters/blob/main/outputs/figures/Annual_crisis_intesity_Heatmap.png)

This heatmap shows the distribution of food crisis intensity by year and country, visualizing the continuity of crises over time and global increase trends in specific periods. Color intensity clearly reveals temporal changes in crisis levels and chronic risk zones.

---

### Figure 6 - Distribution of Food Crisis Labels Barchart
>Generated by: scripts/03_basic_eda.py → saved to `outputs/figures/Distribution _of_Food_Crisis_Labels_Barchart.png`

![Distribution of Food Crisis Labels Barchart](https://github.com/BILGI-IE-423/ie423-2025-2026-termproject-overfitters/blob/main/outputs/figures/Distribution%20_of_Food_Crisis_Labels_Barchart.png)

This graph reveals class imbalance by showing the numerical distribution of "crisis present" and "no crisis" states in the dataset. This data guides the sampling strategies to be applied in order to obtain more accurate results during the training phase of the model.

<hr style="height:3px; border:none; background-color:#666;">

## How to Run the Project

---

### 1. Clone the repository
```bash
git clone [https://github.com/BILGI-IE-423/ie423-2025-2026-termproject-overfitters/tree/main]
cd [ie423-2025-2026-termproject-overfitters]
```

---

### 2. Install required packages
```markdown
pip install -r requirements.txt
```

---

### 3. Place the dataset
Download the datasets from the links below:

https://data.humdata.org/dataset/global-wfp-food-prices (download 2016 through 2024)

https://data360.worldbank.org/en/indicator/FAO_FS_210091

After downloading, place all dataset files inside the following directory:
```bash
data/raw/
```
> **Important:** The project assumes that all raw dataset files are located in the `data/raw/` directory with their original filenames.
> If the files are missing or placed incorrectly, the scripts will not run.
> For detailed setup instructions, see `data/README.md`. The folder structure should look like:
```markdown
data/
├── raw/
    ├── FAO_FS_210091.csv
    ├── wfp_food_prices_global_2016.csv
    ├── wfp_food_prices_global_2017.csv
    ├── wfp_food_prices_global_2018.csv
    ├── wfp_food_prices_global_2019.csv
    ├── wfp_food_prices_global_2020.csv
    ├── wfp_food_prices_global_2021.csv
    ├── wfp_food_prices_global_2022.csv
    ├── wfp_food_prices_global_2023.csv
    └── wfp_food_prices_global_2024.csv
```

---

### 4. Run the scripts
Run the scripts in the following order:

```bash
python scripts/01_load_data.py
python scripts/02_preprocess_data.py
python scripts/03_basic_eda.py
```

---

### 5. Outputs
After running the scripts:

* Cleaned dataset will be saved in: `data/processed/processed_food_crisis_data.csv`
* Figures will be saved in: `outputs/figures/`
* Tables will be saved in: `outputs/tables/`

<hr style="height:3px; border:none; background-color:#666;">

## Transparency and Traceability

All outputs presented in this document are generated directly from the Python scripts located in the scripts/ folder.


* Data loading and initial inspection outputs are generated by: `scripts/01_load_data.py`
* Data preprocessing and feature engineering are performed by: `scripts/02_preprocess_data.py`
* All visualizations and analysis results are generated by: `scripts/03_basic_eda.py`

---

### Data Pipeline

The project follows a structured pipeline:

* Raw data is stored in: `data/raw/`

* Processed data is generated and saved in: `data/processed/processed_food_crisis_data.csv`

* Visual outputs (plots) are saved in: `outputs/figures/`

* Tables are stored in: `outputs/tables/`

---

### Reproducibility Guarantee
* All results are reproducible by running the provided scripts.
* No manual modifications are applied to the outputs.
* Every figure and dataset can be traced back to its corresponding script.
