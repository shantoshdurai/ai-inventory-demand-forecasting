# AI Inventory Demand Forecasting

A machine learning–powered inventory management dashboard that forecasts product demand using historical sales data. Built with Streamlit, XGBoost, and Facebook Prophet.

## What it does

- **Natural language input** — type "sold 5 Dolo 650" and Gemini AI parses it into structured data
- **Photo receipts** — upload a photo of a handwritten log or printed receipt, AI extracts items and quantities
- **ML forecasting** — XGBoost and Prophet models predict demand up to 30 days ahead
- **What-if simulator** — test how a discount would affect demand, revenue, and stock levels
- **Bulk import** — upload CSV/Excel files with auto column detection

## Tech stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| ML Models | XGBoost, Prophet |
| AI Engine | Google Gemini 1.5 Flash |
| Database | SQLite |
| Charts | Plotly |

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```

Run:
```bash
streamlit run app.py
```

To load demo data (6 months of simulated medical shop transactions):
```bash
python -m core.generate_demo_data
```

## Project structure

```
├── app.py                  # Entry point
├── config.py               # Environment config
├── core/
│   ├── database.py         # SQLite schema and connections
│   ├── gemini_engine.py    # Gemini AI text and image parsing
│   ├── stock_tracker.py    # Stock CRUD operations
│   ├── data_importer.py    # CSV/Excel bulk import
│   └── generate_demo_data.py
├── ml/
│   ├── feature_engineering.py  # Lag features, rolling averages
│   └── forecaster.py          # XGBoost and Prophet models
└── ui/
    ├── dashboard.py
    ├── input_page.py
    ├── forecast_page.py
    └── whatif_page.py
```

## License

MIT
