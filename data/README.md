# Data Directory & Dataset Instructions

This directory contains the raw datasets and the processed outputs for the Global Food Crisis Early Warning System project. Although the CSV files are included in this repository, the original dataset links are also provided below for transparency and reproducibility. 

## 1. WFP Global Food Prices
* **Dataset Source:** Humanitarian Data Exchange (HDX) / World Food Programme (WFP)
* **Dataset Link:** [Global WFP Food Prices](https://data.humdata.org/dataset/global-wfp-food-prices) (2016-2024)
* **Description:** This dataset tracks monthly market prices for various food and non-food commodities across different markets globally. For this project, we utilize the data spanning from 2016 to 2024 to capture local price volatility and market shocks.
* **File Name(s):** `wfp_food_prices_global_2016.csv` through `wfp_food_prices_global_2024.csv` (9 separate files).

## 2. FAO Food Insecurity Dataset
* **Dataset Source:** World Bank Data360 / Food and Agriculture Organization (FAO)
* **Dataset Link:** [Prevalence of Moderate or Severe Food Insecurity](https://data360.worldbank.org/en/indicator/FAO_FS_210091)
* **Description:** This dataset provides the prevalence of moderate or severe food insecurity in the total population (measured as a percentage) over a 3-year average. It serves as our macro-level vulnerability baseline for each country.
* **File Name(s):** `FAO_FS_210091.csv`

---

## Instructions for Reproducibility  

### Is Manual Download Needed?   
**No manual download is required.** Since the individual CSV files are within GitHub's file size limits, all raw datasets have been directly pushed to this repository to ensure immediate reproducibility.    

### Where to Place the Files  
If you are updating the dataset or pulling fresh data from the links provided above, ensure all downloaded `.csv` files are placed directly into the `data/raw/` directory.

The expected folder structure before running any scripts must look exactly like this:

```text
data/
├── raw/
│   ├── FAO_FS_210091.csv
│   ├── wfp_food_prices_global_2016.csv
│   ├── wfp_food_prices_global_2017.csv
│   ├── wfp_food_prices_global_2018.csv
│   ├── wfp_food_prices_global_2019.csv
│   ├── wfp_food_prices_global_2020.csv
│   ├── wfp_food_prices_global_2021.csv
│   ├── wfp_food_prices_global_2022.csv
│   ├── wfp_food_prices_global_2023.csv
│   └── wfp_food_prices_global_2024.csv
├── processed/
│   └── processed_food_crisis_data.csv
└── README.md
