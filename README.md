# Electricity Consumption Insight

**Organisation:** GridSense Energy Services  
**Sector:** Energy  
**Assessment:** Data Science SAT — Challenge 18

> ⚠️ **SYNTHETIC DATA DISCLOSURE**: All datasets used in this project are synthetically generated practice data. They are NOT official GridSense Energy Services data and do NOT describe real customers or real utility measurements. Results are illustrative only and must not be presented as official findings.

---

## Business Question

> What temporal and environmental factors influence electricity consumption?

---

## Project Structure

```
Electricity-Consumption-Insight/
├── data/
│   ├── raw/                    # Original unmodified input CSVs
│   └── processed/              # Cleaned and integrated datasets, predictions, metrics
├── notebooks/
│   └── electricity_consumption_analysis.ipynb
├── src/
│   ├── data_inspection.py      # Phase A — data quality audit
│   ├── preprocessing.py        # Phase B/C — cleaning and integration
│   ├── analysis.py             # Phase D — EDA and visualizations
│   ├── modeling.py             # Phase E/F — feature engineering and ML
│   └── export_reports.py       # Phase G/I — Excel and PowerPoint
├── reports/
│   ├── figures/                # All saved PNG charts
│   ├── dataset_inspection.md
│   ├── preprocessing_audit.md
│   ├── eda_findings.md
│   └── submission_summary.md
├── excel/
│   └── electricity_consumption_analysis.xlsx
├── presentation/
│   └── electricity_consumption_insights.pptx
├── models/
│   └── rf_pipeline.pkl         # Serialized Random Forest pipeline
├── tests/
│   └── test_pipeline.py        # 28 automated tests
├── run_pipeline.py             # End-to-end pipeline runner
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Datasets

| File | Rows | Description |
|---|---|---|
| `meter_readings.csv` | 229,658 | Hourly consumption per customer (timestamp, customer, consumption) |
| `customers.csv` | 80 | Customer attributes (segment, area, connection_type, tariff_category) |
| `weather.csv` | 2,868 | Hourly weather observations (temperature, humidity, rain) |
| `calendar.csv` | 120 | Daily calendar (weekday, holiday, season) |
| `tariff.csv` | 72 | Tariff schedule (tariff_category, hour, peak_period, tariff_rate) |

Coverage: 2025-01-01 to 2025-04-30 | 80 customers | Hourly granularity

---

## Technologies

- Python 3.14
- pandas, numpy — data manipulation
- matplotlib, seaborn — visualization
- scikit-learn — machine learning pipeline
- openpyxl — Excel workbook generation
- python-pptx — PowerPoint generation

---

## Data Cleaning Methodology

1. **Exact duplicates** removed from meter readings
2. **Conflicting customer+timestamp keys** resolved by keeping the higher consumption value
3. **Negative consumption** removed (confirmed synthetic errors)
4. **Segment labels** normalized: strip whitespace + title-case
5. **Missing weather measurements** forward-filled then back-filled
6. **Missing consumption** retained as NaN (excluded from ML training only)
7. **All joins validated** as many-to-one; row count preserved at 229,249

---

## EDA Approach

- Overall consumption statistics (total, mean, median, std, percentiles)
- Hourly demand: aggregate per timestamp, then average by hour
- Weather relationships: system-level correlation (one demand value per timestamp)
- Customer segment comparison: mean, median, total, std
- Weekday vs weekend: hourly patterns and mean comparison
- Area variability: box plots and coefficient of variation
- Tariff period: mean consumption by peak/off-peak designation

---

## Feature Engineering

18 features engineered from timestamp, weather, customer, and tariff data:
- Temporal: hour, day_of_week, month, is_weekend, holiday
- Cyclic: hour_sin, hour_cos, month_sin, month_cos
- Weather: temperature, humidity, rain
- Customer: segment, area, connection_type, tariff_category
- Tariff: peak_period, tariff_rate

---

## Model Evaluation

- **Algorithm:** Random Forest Regressor (100 trees, seed=42)
- **Baseline:** DummyRegressor (mean prediction)
- **Split:** Chronological — train on earlier 80%, test on later 20%
- **Train period:** 2025-01-01 → 2025-04-06 (182,663 rows)
- **Test period:** 2025-04-07 → 2025-04-30 (45,668 rows)

| Metric | Baseline | Random Forest |
|---|---|---|
| MAE | 2.9156 | **0.9010** |
| RMSE | 3.7699 | **1.4887** |
| R² | −0.0036 | **0.8435** |

---

## Main Business Findings

1. **Peak demand at 17:00** — Average aggregate demand peaks at 5 PM. Demand-response programs targeting flexible loads during 17:00–19:00 can reduce peak grid stress.

2. **Temperature is the strongest demand driver (r = 0.68)** — Higher temperatures correlate strongly with higher consumption, suggesting HVAC cooling load dominates. Weather-integrated forecasting is well-justified.

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Running the Analysis

```bash
# Run the complete pipeline (all phases)
python run_pipeline.py

# Run individual phases
python src/data_inspection.py
python src/preprocessing.py
python src/analysis.py
python src/modeling.py
python src/export_reports.py

# Run tests
python -m pytest tests/ -v
```

---

## Outputs

- **Excel workbook:** `excel/electricity_consumption_analysis.xlsx` — open in Microsoft Excel or LibreOffice Calc
- **PowerPoint:** `presentation/electricity_consumption_insights.pptx` — open in PowerPoint or LibreOffice Impress
- **Notebook:** `notebooks/electricity_consumption_analysis.ipynb` — open with Jupyter Lab/Notebook
- **Figures:** `reports/figures/*.png`
- **Reports:** `reports/*.md`

---

## Limitations

- All data is synthetic; results cannot be generalized to real electricity networks
- The Random Forest model is not calibrated for production forecasting
- Weather data covers only 4 months; seasonal patterns are limited
- No external validation against real consumption benchmarks

---

## Reproducibility

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python run_pipeline.py`
4. All outputs are regenerated deterministically (random_state=42)

---

*Synthetic practice project — not official GridSense data.*
