# Research

This directory contains all R&D artifacts produced during StrideTrack's development. It is intentionally separate from the application code (`backend/`, `frontend/`) and is provided as a reference for future development.

## Structure

```
research/
├── scripts/          Analysis and data pipeline scripts
├── data/
│   ├── mock/         Generated synthetic sensor data (sprint + hurdle, 4 distances each)
│   ├── real/         Real hardware recordings from insole sensor prototypes
│   │   ├── NewSensorBatch1/   First batch of field recordings
│   │   ├── NewSensorBatch2/   Second batch of field recordings
│   │   └── FingerTestData/    Single-sensor finger prototype recordings
│   ├── training/     Competition result PDFs sourced from AthleteFirst, used as model training inputs
│   └── processed/    Pipeline outputs — dual-sensor merged files, flight time extractions
├── client_resources/ Deliverables — pitch deck, metrics dashboard, demo, technical docs
└── docs/
    ├── planning/     Architecture decisions, model deployment plans, sensor research
    └── research/     Competitive analysis, IMU hardware, distance model, chart library evaluations
```

## Scripts

| Script | Purpose |
|---|---|
| `mock_ble_client.py` | Simulates a BLE insole sensor peripheral, streams any CSV at 100 Hz |
| `generate_mock_data.py` | Generates synthetic 400m hurdles sensor data into `data/mock/` |
| `phase_shift.py` | Merges single-sensor finger CSVs into dual-channel format |
| `mock_foot.py` | Merges dual foot sensor sprint recordings into unified CSVs |
| `flight_times_foot.py` | Extracts flight time intervals from dual-foot sprint data |
| `flight_times_finger.py` | Extracts flight time intervals from dual-channel finger data |
| `anomaly_detection.py` | Neural network autoencoder for detecting anomalous race splits |
| `split_score.py` | Parses AthleteFirst competition PDFs to build population split distributions |
| `split_score_report.py` | Generates per-segment race report cards |
| `distance_model_eda.py` | Piecewise linear model for distance estimation from split times |
| `w100h.py` | Scrapes and parses Women's 100m Hurdles meet data |
| `combined_analysis.py` | Combined PDF extraction and model analysis pipeline |
| `pdf_plumber.py` | PDF table extraction utilities using pdfplumber |

## Data Pipeline

```
data/real/          →  phase_shift.py / mock_foot.py  →  data/processed/ (*_BothFeet.csv)
data/processed/     →  flight_times_*.py              →  data/processed/ (*_FlightTimes.csv)
data/training/      →  split_score.py                 →  population split distributions
                    →  anomaly_detection.py            →  anomaly detection model
```

## Notes

- `data/mock/` files are generated — `generate_mock_data.py` regenerates `hurdle_400m.csv` in place
- `backend/tests/test_data/` contains its own copies of selected mock CSVs for integration tests — do not remove those
- Training PDFs sourced from [AthleteFirst](https://www.athletefirst.org)
