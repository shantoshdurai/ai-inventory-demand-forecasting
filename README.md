# 📦 StockSense AI

**Intelligent Demand Forecasting for Small Businesses**

Built for the **TNI26086 Hackathon**, StockSense AI is a full-stack, machine-learning-powered web dashboard designed to bring enterprise-level forecasting logic to local medical shops, supermarkets, and restaurants.

## 🌟 Key Features

1. **AI-Powered Input** 🗣️📸  
   Log daily transactions (sales & restocks) intuitively via **Voice/Text** or by snapping **Photo Receipts**. The backend uses Gemini 1.5 Flash to automatically map natural language and images into structured database records.
2. **Bulk Data Imports** 📁  
   Migrating from Excel? Our `pandas` driven data importer automatically detects the item columns, quantity, and dates from historical spreadsheets to instantly seed your AI logic.
3. **Machine Learning Forecasting** 🔮  
   Choose between **XGBoost** (for complex feature interactions like weekends, seasonality, and rolling averages) or **Facebook Prophet** (for pure time-series trend analysis) to accurately project your unit demand up to 30 days into the future.
4. **Interactive What-If Simulator** 🎛️  
   Planning a discount? Use the simulator to calculate the **price elasticity of demand**. The system instantly tells you exactly how a price drop will affect your unit sales, overall revenue, and warns you if the sale will trigger an inventory stockout.
5. **Premium UI Dashboard** ✨  
   Fully responsive Streamlit dashboard featuring glassmorphism design, native Plotly interactive line/bar charts, and intelligent KPI logic giving you critical alerts for low stock before it physically runs out.

## 🛠️ Technology Stack

* **Frontend:** Streamlit, Vanilla Custom CSS
* **Data & Visualization:** Pandas, Plotly Express, Plotly Graph Objects
* **Database:** SQLite3
* **AI & Machine Learning:** Google GenAI (Gemini 1.5), XGBoost, Facebook Prophet

## 🚀 Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shantoshdurai/StockSense-AI.git
   cd StockSense-AI
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Provide your API Keys:**
   Create a `.env` file in the root directory and add your Google Gemini Key:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

4. **Launch the Application:**
   ```bash
   python -m streamlit run app.py
   ```
   Navigate to `http://localhost:8501` to view your live AI Dashboard!

## 🧪 Demo Data

A script is included to generate 6-months of simulated medical shop data to observe the forecasting algorithms immediately.
```bash
python -m core.generate_demo_data
```

---
*Built to empower small businesses lacking the budget for enterprise ERPs. Because every business deserves to know what's coming.*
