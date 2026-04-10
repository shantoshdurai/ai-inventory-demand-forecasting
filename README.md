# StockSense AI — Kirana Shop Intelligence Platform

![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)
![Gemma](https://img.shields.io/badge/AI-Gemma%204%2031B-orange?style=flat-square&logo=google)
![XGBoost](https://img.shields.io/badge/ML-XGBoost%20%7C%20Prophet-green?style=flat-square)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## 🔗 Live Demo → [stocksense-yk37.onrender.com](https://stocksense-yk37.onrender.com)

> Free tier — may take 30–60 seconds to wake up on first visit.

---

## What This Is

Most inventory software is built for large retailers with IT teams. **Kirana shops** — the 12 million small grocery stores across India — run on handwritten ledgers, paper bills, and gut instinct.

I built StockSense to change that. A shop owner can:
- **Speak** "aaj 10 packet Maggi becha" and it logs the sale
- **Photo** a distributor bill and AI extracts every item and quantity
- **Ask** "what should I reorder this week?" and get a specific answer in Tamil, Hindi, or English
- **See** a 14-day ML demand forecast for any product
- **Simulate** "what happens to revenue if I give 15% off on rice?"

The whole thing runs on a ₹0/month free tier.

---

## Screenshots

### Dashboard — Live inventory with AI insights, sales trend, and stock levels

![Dashboard](images/Screenshot%202026-04-11%20011126.png)

---

### Demand Forecast — Day-by-day ML predictions using XGBoost or Prophet

![Demand Forecast](images/Screenshot%202026-04-11%20011232.png)

---

### What-If Simulator — Discount impact on demand and revenue, with stockout risk detection

![What-If Simulator](images/Screenshot%202026-04-11%20011242.png)

---

## What Was Hard to Build

**1. The dashboard was timing out on every load.**
The original design called Gemini AI on every dashboard request to generate insights. Under load (or a slow API), this caused a 10–15 second blank screen. I decoupled it: the dashboard now uses a rule-based insights engine (instant, zero API calls) that checks critical stock thresholds, stockout velocity, and trending products from the DB directly. AI insights are available on demand via the side panel.

**2. The AI kept responding in Hindi even when asked in English.**
The model (Gemma 4 31B) was ignoring soft language instructions. Fixed it by placing a strict override at the *end* of the system prompt — models follow end-of-prompt instructions more reliably. The rule says "ENGLISH ONLY. Every single word. No exceptions." Three separate language modes: English, Tamil, Hindi — each locked independently.

**3. Render's Python runtime doesn't have npm.**
The build was failing because the deploy script tried to run `npm run build` on a Python dyno. Solved by committing the pre-built React `dist/` folder to the repo and removing it from `.gitignore`. FastAPI serves it as static files — single service, single URL, zero extra cost.

---

## Key Features

| Feature | Description |
|---|---|
| **Persistent AI Side Panel** | Always-visible chat — ask questions, attach bills, use voice without leaving the page |
| **Multilingual UI** | Full interface in English, Tamil (தமிழ்), Hindi (हिंदी) — saved per browser |
| **AI Chat — Language Locked** | Responses strictly in your chosen language — no Hinglish mixing |
| **Voice Input** | Web Speech API — works in English, Tamil, Hindi |
| **Receipt Vision** | Upload a photo of any bill — Gemma 4 extracts items and quantities |
| **Demand Forecast** | XGBoost + Prophet with day-by-day breakdown and stats |
| **What-If Simulator** | Simulate any discount % — demand uplift, revenue delta, stockout risk |
| **Auto Demo Data** | Realistic 6-month Kirana dataset seeds on first run |
| **Claymorphism UI** | Light pastel design, 3D clay cards, glassmorphism panels, fully responsive |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite, Recharts |
| Backend | FastAPI + Uvicorn |
| AI Engine | Google Gemma 4 31B (`google-genai`) |
| ML Models | XGBoost, Facebook Prophet |
| Database | SQLite |
| Hosting | Render (free tier) |

---

## Project Structure

```
ai-inventory-demand-forecasting/
├── api/
│   └── main.py              # FastAPI — all REST endpoints
├── core/
│   ├── database.py          # SQLite + auto-seed 6 months of Kirana data
│   ├── gemini_engine.py     # Gemma 4 — chat, vision, voice, language enforcement
│   ├── insights_engine.py   # Rule-based instant insights (no AI timeout)
│   ├── stock_tracker.py     # Transaction logging
│   └── data_importer.py     # CSV / Excel import
├── ml/
│   ├── forecaster.py        # XGBoost + Prophet pipeline
│   └── feature_engineering.py
├── web/
│   ├── src/
│   │   ├── i18n.js          # English / Tamil / Hindi translations
│   │   ├── App.jsx          # Root — splash screen, demo banner, footer
│   │   ├── components/
│   │   │   ├── Nav.jsx      # Nav + language switcher dropdown
│   │   │   └── SidePanel.jsx # Persistent AI chat panel
│   │   └── pages/
│   │       ├── Dashboard.jsx
│   │       ├── InputData.jsx
│   │       ├── Forecast.jsx
│   │       └── Simulator.jsx
│   └── dist/                # Pre-built React (committed for Render deployment)
├── images/                  # Screenshots
├── render.yaml              # One-click Render deploy config
├── config.py
└── requirements.txt
```

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google AI Studio API key — free at [aistudio.google.com](https://aistudio.google.com)

### Steps

```bash
git clone https://github.com/shantoshdurai/ai-inventory-demand-forecasting.git
cd ai-inventory-demand-forecasting

# Python backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
python -m pip install -r requirements.txt

# Create .env
echo GEMINI_API_KEY=your_key_here > .env

# React frontend
cd web && npm install && npm run build && cd ..

# Start both servers
# Terminal 1:
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
# Terminal 2:
cd web && npm run dev
```

Open **http://localhost:5173**

> Without an API key the app runs in **Demo mode** — all ML features work, AI chat is disabled.

---

## Deploying to Render

1. Fork this repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your fork
4. Render auto-detects `render.yaml` — just add one environment variable:
   - `GEMINI_API_KEY` = your Google AI Studio key
5. Click **Deploy** — live in ~3 minutes

---

## Model Performance

| Model | MAE | MAPE | RMSE |
|---|---|---|---|
| XGBoost | ~12 units | ~8.3% | ~15.2 |
| Prophet | ~14 units | ~9.1% | ~18.0 |

---

## Author

**Santosh Durai** — Full Stack Developer, Tamil Nadu, India

- GitHub: [@shantoshdurai](https://github.com/shantoshdurai)
- LinkedIn: [santoshp123](https://www.linkedin.com/in/santoshp123)

*Built for the 12 million Kirana shops that keep India fed.*
