# IE 423 2025-2026 Term Project Proposal - Global Food Crisis Early Warning System
Website: https://iremmural.github.io/ie423-2025-2026-termproject-overfitters/

## Team Members
- Begüm Acar (122203037)
- İrem Ural (121203037)
- Gamze Kılıç (122203118)
- Sercan Çavuş (122203045)


## Project Objective

The objective of this project is to develop a Machine Learning–based early warning system for global food crises by combining food price data from WFP with a baseline food insecurity indicator from FAO. By analyzing historical trends, seasonal patterns, and sudden price fluctuations, the model aims to identify regions at risk of increasing food insecurity and predict major price surges up to three months in advance. This early detection system is designed to support policymakers, humanitarian organizations, and international agencies in making proactive decisions, allocating resources efficiently, and implementing preventive measures before food shortages escalate into large-scale humanitarian crises.

## Research Questions

- **RQ1** — Which countries and food products experience the highest price volatility — and are these patterns seasonal?
- **RQ2** — Can a food price crisis be predicted 3 months in advance using past price movements and food insecurity scores?
- **RQ3** — What factors drive crisis risk most — product type, country vulnerability, or seasonality?


## Datasets

**Dataset:** Global Food Prices (2016-2024)
- Source: https://data.humdata.org/dataset/global-wfp-food-prices

**Dataset:** FAO Food Insecurity Dataset
- Source: https://data360.worldbank.org/en/indicator/FAO_FS_210091

## Repository Structure
```text
├── README.md                  → project overview and setup instructions
├── requirements.txt           → python dependencies list
├── index.html                 → the website — all content, figures, tables, results
├── data/
│   ├── raw/                   → original datasets
│   ├── processed/             → final ML-ready dataset
│   └── README.md              → dataset download links and guide
├── scripts/
│   ├── 01_load_data.py        → verifies file paths and imports data
│   ├── 02_preprocess_data.py  → handles missing values, merges, and creates features
│   ├── 03_basic_eda.py        → creates visualizations and statistical summaries
│   ├── 04_baseline_model.py   → trains and evaluates the baseline ML model
│   └── 05_shap_analysis.py    → generates SHAP feature importance explanations
├── visuals/
│   ├── figures/               → generated charts and graphs
│   └── tables/                → generated tables

```
## Installation
```bash
pip install -r requirements.txt
```
## Running the Project
Run scripts in order:
```bash
python scripts/01_load_data.py
python scripts/02_preprocess_data.py
python scripts/03_basic_eda.py
python scripts/04_baseline_model.py
python scripts/05_shap_analysis.py
```
## Conclusion

Food price crises leave detectable traces in price data weeks before they materialize at household level. By combining WFP price dynamics with FAO vulnerability scores and applying temporal machine learning, we can raise an alarm 3 months in advance with meaningful accuracy.

XGBoost (tuned) delivered the strongest performance on both validation and test sets. SHAP analysis confirmed that the model's logic is consistent with domain knowledge — lag prices and volatility are the primary drivers, with country vulnerability as an amplifier — making it potentially deployable in a real humanitarian monitoring context.


