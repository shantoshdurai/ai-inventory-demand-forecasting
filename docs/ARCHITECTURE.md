# Architecture: AI Inventory Demand Forecasting

## Overview

This project is a full-stack AI-powered inventory and demand forecasting dashboard built for MSMEs. It uses machine learning models combined with Google Gemini AI to predict product demand and optimize inventory decisions.

## Folder Structure

```
ai-inventory-demand-forecasting/
├── core/           # Core business logic & data processing utilities
├── data/           # Datasets, sample data, and data loaders
├── ml/             # Machine learning models (XGBoost, Prophet)
├── ui/             # Streamlit UI components and pages
├── app.py          # Application entry point
├── config.py       # Configuration settings and constants
├── requirements.txt # Python dependencies
└── docs/           # Project documentation
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| UI Framework | Streamlit |
| ML Models | XGBoost, Prophet |
| AI Integration | Google Gemini 1.5 Flash |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Matplotlib |

## Data Flow

1. **Data Ingestion** (`data/`) - Load and preprocess inventory CSV data
2. **Feature Engineering** (`core/`) - Extract time-series features, lag variables
3. **Model Training** (`ml/`) - Train XGBoost and Prophet models
4. **AI Augmentation** - Use Gemini to explain predictions in natural language
5. **Dashboard** (`ui/`) - Render interactive Streamlit visualizations

## ML Models

### XGBoost
- Used for short-term demand prediction
- Features: lag values, rolling averages, seasonal indicators

### Prophet
- Used for long-term trend and seasonality forecasting
- Handles holidays, special events, and missing data

## Configuration

All settings are managed in `config.py`:
- API keys (Gemini)
- Model hyperparameters
- Data paths
- UI theme settings

## CI/CD

GitHub Actions workflows located in `.github/workflows/`:
- `python-ci.yml` - Runs tests and linting on every push/PR

---

*Last updated: March 2026*
