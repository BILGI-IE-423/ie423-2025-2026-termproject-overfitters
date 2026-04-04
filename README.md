# IE 423 2025-2026 Term Project Proposal - Global Food Crisis Early Warning System

## Team Members
- Begüm Acar (122203037)
- İrem Ural 
- Gamze Kılıç 
- Sercan Çavuş

## Project Objective

The goal of this project is to develop an early warning system for food crises by integrating historical global food price data with food insecurity indicators. By analyzing these datasets together, we aim to identify regions at risk of rising food insecurity, detect early signs of potential crises, and provide actionable insights for policymakers and humanitarian organizations to mitigate the impact on vulnerable populations.

## Datasets

**Dataset:** Global Food Prices (2016-2024)
- Source: https://data.humdata.org/dataset/global-wfp-food-prices

**Dataset:** FAO Food Insecurity Dataset
- Source: https://data360.worldbank.org/en/indicator/FAO_FS_210091

## Repository Structure
```text
├── README.md                  → project overview and setup instructions
├── requirements.txt           → python dependencies list
├── data/
│   ├── raw/                   → original datasets
│   ├── processed/             → final ML-ready dataset
│   └── README.md              → dataset download links and guide
├── scripts/
│   ├── 01_load_data.py        → verifies file paths and imports data
│   ├── 02_preprocess_data.py  → handles missing values, merges, and creates features
│   └── 03_basic_eda.py        → creates visualizations and statistical summaries
├── outputs/
│   ├── figures/               → generated charts and graphs
│   └── tables/                → generated tables
└── docs/
    └── ResearchProposalPreprocessing.md   → detailed project proposal file
```
## Installation
```bash
pip install -r requirements.txt
```
## Running the Project
```bash
python scripts/01_load_data.py
python scripts/02_preprocess_data.py
python scripts/03_basic_eda.py
```
## Main Proposal File
See: [docs/ResearchProposalPreprocessing.md](docs/ResearchProposalPreprocessing.md)

