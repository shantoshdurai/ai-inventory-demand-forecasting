# StockSense AI — Kirana Shop Intelligence Platform

![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)
![Gemma](https://img.shields.io/badge/AI-Gemma%204%2031B-orange?style=flat-square&logo=google)
![XGBoost](https://img.shields.io/badge/ML-XGBoost%20%7C%20Prophet-green?style=flat-square)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

> AI-powered inventory management and demand forecasting built specifically for **Kirana shops** (Indian grocery/general stores). Combines Gemma 4 31B vision + voice AI with XGBoost/Prophet ML models inside a modern Claymorphism UI — with a persistent AI side panel, multilingual support (English, Tamil, Hindi), and live demand simulations.

---

## Screenshots

### Dashboard — Live inventory overview with AI insights, sales trend chart, and stock levels

![Dashboard](images/Screenshot%202026-04-11%20011126.png)

---

### Demand Forecast — ML-powered day-by-day demand predictions with XGBoost or Prophet

![Demand Forecast](images/Screenshot%202026-04-11%20011232.png)

---

### What-If Simulator — Simulate price discounts and instantly see the impact on demand and revenue

![What-If Simulator](images/Screenshot%202026-04-11%20011242.png)

---

## Key Features

| Feature | Description |
|---|---|
| **Persistent AI Side Panel** | Always-visible chat panel — ask questions, attach receipt photos, use voice input without leaving the page |
| **Multilingual UI** | Full interface in English, Tamil (தமிழ்), and Hindi (हिंदी) — persists across sessions |
| **AI Chat (Gemma 4 31B)** | Business advisor answers in English, Tamil, or Hindi — language-locked responses |
| **Voice Input** | Speak transactions in English, Tamil, or Hindi using Web Speech API |
| **Receipt Vision** | Upload a photo of a bill/receipt — Gemma 4 extracts all items and quantities |
| **Demand Forecast** | XGBoost + Prophet ML predict future demand with historical sales data |
| **What-If Simulator** | Simulate any discount % over any period — see demand uplift and revenue impact |
| **Auto Demo Data** | Database auto-seeds 6 months of realistic Kirana data on first run |
| **Claymorphism UI** | Light pastel design with 3D clay cards, glassmorphism panels, fully responsive |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite, Recharts |
| Backend | FastAPI + Uvicorn |
| AI Engine | Google Gemma 4 31B (via `google-genai`) |
| ML Models | XGBoost, Facebook Prophet |
| Database | SQLite |
| Styling | Pure CSS — Claymorphism design system |

---

## Project Structure

```
ai-inventory-demand-forecasting/
├── api/
│   └── main.py              # FastAPI backend — all REST endpoints
├── core/
│   ├── database.py          # SQLite + auto-seed demo data
│   ├── gemini_engine.py     # Gemma 4 — chat, vision, voice parsing
│   ├── insights_engine.py   # Rule-based instant insights (no AI timeout)
│   ├── stock_tracker.py     # Transaction logging
│   └── data_importer.py     # CSV / Excel import
├── ml/
│   ├── forecaster.py        # XGBoost + Prophet pipeline
│   └── feature_engineering.py
├── web/                     # React frontend
│   ├── src/
│   │   ├── i18n.js          # English / Tamil / Hindi translations
│   │   ├── api.js           # API client
│   │   ├── App.jsx          # Root layout with side panel
│   │   ├── components/
│   │   │   ├── Nav.jsx      # Top nav with language switcher
│   │   │   └── SidePanel.jsx # Persistent AI chat panel
│   │   └── pages/
│   │       ├── Dashboard.jsx
│   │       ├── InputData.jsx
│   │       ├── Forecast.jsx
│   │       └── Simulator.jsx
│   └── dist/                # Production build (served by FastAPI)
├── images/                  # Screenshots
├── config.py                # API key + model config
├── requirements.txt
└── start.bat                # Windows: starts both servers at once
```

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google AI Studio API key — free at [aistudio.google.com](https://aistudio.google.com)

### 1. Clone & install Python dependencies

```bash
git clone https://github.com/shantoshdurai/ai-inventory-demand-forecasting.git
cd ai-inventory-demand-forecasting

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

python -m pip install -r requirements.txt
```

### 2. Add your API key

Create a `.env` file in the root:

```env
GEMINI_API_KEY=your_api_key_here
```

> Without a key the app runs in **Demo mode** — all UI and ML features work, AI chat is disabled.

### 3. Install frontend dependencies

```bash
cd web
npm install
cd ..
```

### 4. Run the app

**Option A — Windows one-click:**
```bash
start.bat
```

**Option B — Manual (two terminals):**

Terminal 1 — API server:
```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Terminal 2 — React dev server:
```bash
cd web
npm run dev
```

Open **http://localhost:5173** (or whichever port Vite picks).

---

## Hosting a Live Demo

### Option 1 — Render (Recommended, Free)

Render can host both the FastAPI backend and serve the React build as static files.

**Step 1 — Build the frontend:**
```bash
cd web && npm run build && cd ..
```
This creates `web/dist/` which FastAPI already serves automatically.

**Step 2 — Push to GitHub (already done).**

**Step 3 — Create a Render Web Service:**
1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repo: `shantoshdurai/ai-inventory-demand-forecasting`
3. Set these values:

| Field | Value |
|---|---|
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |

4. Add environment variable: `GEMINI_API_KEY` → your key
5. Click **Deploy** — Render gives you a public URL like `https://stocksense.onrender.com`

> The React build in `web/dist/` is automatically served by FastAPI at the root URL.

---

### Option 2 — Railway (One-click, Free tier)

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Select this repo
3. Add variable: `GEMINI_API_KEY=your_key`
4. Set start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Railway auto-detects Python and deploys — public URL in ~2 minutes

---

### Option 3 — Vercel (Frontend) + Render (Backend)

If you want the fastest frontend CDN delivery:

**Frontend → Vercel:**
```bash
cd web
npm run build
npx vercel --prod
```
Set environment variable `VITE_API_BASE=https://your-render-backend.onrender.com`

**Backend → Render:** same as Option 1 above.

Then in `web/src/api.js` change:
```js
const BASE = import.meta.env.VITE_API_BASE || '/api'
```

---

### Before deploying — rebuild the frontend

Any time you change React code, run:
```bash
cd web && npm run build && cd ..
git add web/dist
git commit -m "Rebuild frontend"
git push
```

Render/Railway will auto-redeploy on every push.

---

## Model Performance

| Model | MAE | MAPE | RMSE |
|---|---|---|---|
| XGBoost | ~12 units | ~8.3% | ~15.2 |
| Prophet | ~14 units | ~9.1% | ~18.0 |

*Evaluated on held-out 20% test split of Kirana sales data.*

---

## Roadmap

- [x] Natural language inventory input (English, Tamil, Hindi)
- [x] Photo receipt parsing with Gemma 4 vision
- [x] XGBoost + Prophet demand forecasting
- [x] What-If price discount simulator
- [x] Persistent AI side panel (always visible)
- [x] Multilingual UI — English, Tamil, Hindi
- [x] Claymorphism responsive UI
- [x] Voice input (Web Speech API)
- [x] Auto demo data seeding
- [ ] One-click Render/Railway deployment
- [ ] PDF export of forecast reports
- [ ] Multi-user login system
- [ ] WhatsApp integration for Kirana owners

---

## Author

**Santosh Durai**
- GitHub: [@shantoshdurai](https://github.com/shantoshdurai)
- LinkedIn: [santoshp123](https://www.linkedin.com/in/santoshp123)

---

*Built for Kirana shop owners across Tamil Nadu and India.*
