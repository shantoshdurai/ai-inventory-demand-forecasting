# AI Inventory Demand Forecasting

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![XGBoost](https://img.shields.io/badge/ML-XGBoost%20%7C%20Prophet-green?style=flat-square)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini%201.5%20Flash-orange?style=flat-square&logo=google)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

> An AI-powered inventory management and demand forecasting dashboard built for MSMEs (Micro, Small & Medium Enterprises). Combines machine learning models with Google Gemini AI to predict product demand, reduce overstock, and prevent stockouts — all through a simple, intuitive interface.

---

## Problem Statement

Small businesses and MSMEs in India struggle with:
- **Overstocking** — tying up capital in unsold inventory
- **Stockouts** — losing sales due to demand miscalculation
- **Manual record-keeping** — handwritten logs and paper receipts
- **No data-driven decisions** — relying on gut feeling for ordering

This project solves all four problems with AI + ML.

---

## Features

| Feature | Description |
|---|---|
| Natural Language Input | Type "sold 5 Dolo 650" — Gemini AI parses it into structured data |
| Photo Receipt OCR | Upload a photo of a handwritten log; AI extracts items & quantities |
| ML Demand Forecasting | XGBoost + Prophet predict future demand from historical sales |
| Low Stock Alerts | Automatic alerts when inventory drops below threshold |
| Interactive Dashboard | Plotly charts for sales trends, forecast graphs, stock levels |
| Bulk Import | Upload CSV/Excel files with auto column detection |
| SQLite Storage | Lightweight local database — no cloud dependency needed |

---

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| ML Models | XGBoost, Facebook Prophet |
| AI Engine | Google Gemini 1.5 Flash |
| Database | SQLite |
| Visualization | Plotly |
| Language | Python 3.10+ |

---

## Project Structure

```
ai-inventory-demand-forecasting/
├── core/                  # Core business logic
│   ├── database.py        # SQLite operations
│   ├── gemini_parser.py   # Gemini AI integration
│   └── alerts.py          # Low-stock alert system
├── data/                  # Sample datasets & CSV templates
│   └── sample_inventory.csv
├── ml/                    # Machine learning models
│   ├── forecaster.py      # XGBoost + Prophet pipeline
│   ├── trainer.py         # Model training scripts
│   └── evaluator.py       # Metrics: MAE, MAPE, RMSE
├── ui/                    # Streamlit UI pages
│   ├── dashboard.py       # Main dashboard
│   ├── input_page.py      # Natural language & photo input
│   └── forecast_page.py   # Forecast visualizations
├── .env.example           # Environment variable template
├── requirements.txt       # Python dependencies
└── README.md
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/shantoshdurai/ai-inventory-demand-forecasting.git
cd ai-inventory-demand-forecasting

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
cp .env.example .env
# Edit .env and add your Gemini API key
```

### Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Run the App

```bash
streamlit run ui/dashboard.py
```

Open your browser at `http://localhost:8501`

---

## Model Performance

| Model | MAE | MAPE | RMSE |
|---|---|---|---|
| XGBoost | ~12 units | ~8.3% | ~15.2 |
| Prophet | ~14 units | ~9.1% | ~18.0 |

*Metrics evaluated on held-out 20% test split of sample retail sales data.*

---

## How It Works

```
User Input (text / photo / CSV)
        ↓
Gemini AI parses & structures the data
        ↓
SQLite stores inventory records
        ↓
XGBoost / Prophet trains on historical sales
        ↓
Forecast displayed on Streamlit dashboard
        ↓
Alerts triggered for low-stock items
```

---

## Roadmap

- [x] Natural language inventory input
- [x] Photo receipt parsing with Gemini Vision
- [x] XGBoost demand forecasting
- [x] Prophet time-series forecasting
- [x] Interactive Plotly dashboard
- [ ] REST API for external integrations
- [ ] Multi-user support with login system
- [ ] Export reports as PDF
- [ ] Mobile-responsive UI
- [ ] Cloud deployment (Streamlit Cloud / Render)
- [ ] Unit tests and CI/CD pipeline

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push and open a Pull Request

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Santosh Durai**
- GitHub: [@shantoshdurai](https://github.com/shantoshdurai)
- LinkedIn: [santoshp123](https://www.linkedin.com/in/santoshp123)
- Portfolio: [shantoshdurai.github.io](https://shantoshdurai.github.io)

---

*Built with passion for MSMEs in Tamil Nadu, India.*
