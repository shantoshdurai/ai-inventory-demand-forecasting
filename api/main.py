from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import sys
import os

# Add parent dir so we can import existing core/ml modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GEMINI_API_KEY, GEMINI_MODEL, DEMO_MODE
from core.database import get_connection, auto_seed_demo_data
from core.stock_tracker import log_transaction
from core.data_importer import process_uploaded_file
from core.insights_engine import get_smart_insights, generate_rule_based_insights, get_inventory_summary_text
from core.gemini_engine import (
    parse_text_input, parse_image_input, parse_voice_input,
    chat_with_advisor, analyze_performance, generate_ai_insights
)
from ml.feature_engineering import prepare_time_series_data
from ml.forecaster import train_xgboost, train_prophet

app = FastAPI(title="StockSense API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ──────────────────────────────────────────────────────────────────

class TransactionIn(BaseModel):
    product_name: str
    qty: float
    type: str = "sale"
    date: Optional[str] = None
    source: Optional[str] = "manual"
    price: Optional[float] = None
    category: Optional[str] = None

class ParseTextIn(BaseModel):
    text: str

class ParseVoiceIn(BaseModel):
    transcribed_text: str

class ChatIn(BaseModel):
    message: str
    chat_history: Optional[List[dict]] = None

class ForecastIn(BaseModel):
    product_id: int
    days: Optional[int] = 14
    engine: Optional[str] = "xgboost"

class SimulatorIn(BaseModel):
    product_id: int
    discount_percent: float
    period_days: int = 14

# ── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "api_key_configured": bool(GEMINI_API_KEY),
        "demo_mode": DEMO_MODE,
        "model": GEMINI_MODEL,
    }

# ── Dashboard ────────────────────────────────────────────────────────────────

@app.get("/api/dashboard")
def get_dashboard():
    conn = get_connection()

    stock_df = pd.read_sql_query("""
        SELECT p.name as item, p.category, p.price, s.current_qty as stock
        FROM stock s JOIN products p ON s.product_id = p.id
    """, conn)

    trend_df = pd.read_sql_query("""
        SELECT t.date, SUM(t.qty) as sales
        FROM transactions t
        WHERE t.type = 'sale' AND t.date IS NOT NULL
        GROUP BY t.date ORDER BY t.date DESC LIMIT 60
    """, conn)

    recent_df = pd.read_sql_query("""
        SELECT p.name as item, t.qty, t.type, t.date
        FROM transactions t JOIN products p ON t.product_id = p.id
        ORDER BY t.id DESC LIMIT 10
    """, conn)
    conn.close()

    total_items = len(stock_df)
    low_stock = int((stock_df['stock'] < 30).sum()) if not stock_df.empty else 0
    total_value = float((stock_df['stock'] * stock_df['price']).sum()) if not stock_df.empty else 0
    total_units = float(stock_df['stock'].sum()) if not stock_df.empty else 0

    trend = trend_df.sort_values('date').to_dict(orient='records') if not trend_df.empty else []
    recent = recent_df.to_dict(orient='records') if not recent_df.empty else []

    # Stock levels with status
    stock_levels = []
    for _, r in stock_df.iterrows():
        status = "critical" if r['stock'] < 10 else ("low" if r['stock'] < 30 else "healthy")
        stock_levels.append({"item": r['item'], "category": r['category'],
                              "price": r['price'], "stock": r['stock'], "status": status})

    # Use only rule-based insights here (instant, no AI call)
    insights = generate_rule_based_insights()

    return {
        "stats": {
            "total_items": total_items,
            "low_stock_alerts": low_stock,
            "inventory_value": round(total_value, 2),
            "total_units": round(total_units, 2),
        },
        "insights": insights,
        "sales_trend": trend,
        "recent_transactions": recent,
        "stock_levels": sorted(stock_levels, key=lambda x: x['stock']),
    }

# ── Products ─────────────────────────────────────────────────────────────────

@app.get("/api/products")
def get_products():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT p.id, p.name, p.category, p.unit, p.price, COALESCE(s.current_qty, 0) as stock
        FROM products p LEFT JOIN stock s ON s.product_id = p.id
        ORDER BY p.name
    """, conn)
    conn.close()
    return df.to_dict(orient='records')

# ── Transactions ──────────────────────────────────────────────────────────────

@app.post("/api/transactions")
def create_transaction(txn: TransactionIn):
    try:
        log_transaction(
            product_name=txn.product_name,
            qty=txn.qty,
            txn_type=txn.type,
            date=txn.date,
            source=txn.source or "manual",
            price=txn.price,
            category=txn.category,
        )
        return {"success": True, "message": f"Logged {txn.type} of {txn.qty} x {txn.product_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transactions/bulk")
def create_transactions_bulk(items: List[TransactionIn]):
    saved = 0
    for txn in items:
        try:
            log_transaction(
                product_name=txn.product_name,
                qty=txn.qty,
                txn_type=txn.type,
                date=txn.date,
                source=txn.source or "manual",
                price=txn.price,
                category=txn.category,
            )
            saved += 1
        except Exception:
            pass
    return {"success": True, "saved": saved}

# ── Insights ──────────────────────────────────────────────────────────────────

@app.get("/api/insights")
def get_insights():
    return get_smart_insights()

# ── AI Parsing ────────────────────────────────────────────────────────────────

@app.post("/api/ai/parse/text")
def ai_parse_text(body: ParseTextIn):
    result = parse_text_input(body.text)
    return {"items": result}

@app.post("/api/ai/parse/voice")
def ai_parse_voice(body: ParseVoiceIn):
    result = parse_voice_input(body.transcribed_text)
    return {"items": result}

@app.post("/api/ai/parse/image")
async def ai_parse_image(file: UploadFile = File(...)):
    import io
    content = await file.read()
    result = parse_image_input(io.BytesIO(content))
    return {"items": result}

@app.post("/api/ai/chat")
def ai_chat(body: ChatIn):
    context = get_inventory_summary_text()
    response = chat_with_advisor(body.message, context, body.chat_history)
    return {"response": response}

@app.get("/api/ai/performance")
def ai_performance():
    context = get_inventory_summary_text()
    analysis = analyze_performance(context)
    return {"analysis": analysis}

# ── Import ────────────────────────────────────────────────────────────────────

@app.post("/api/import/file")
async def import_file(file: UploadFile = File(...)):
    import io
    content = await file.read()
    buf = io.BytesIO(content)
    buf.name = file.filename or "upload.csv"
    result = process_uploaded_file(buf)
    return result

# ── Forecast ──────────────────────────────────────────────────────────────────

@app.post("/api/forecast")
def get_forecast(body: ForecastIn):
    df = prepare_time_series_data(product_id=body.product_id)
    if df.empty or len(df) < 14:
        raise HTTPException(status_code=400, detail="Not enough data (need 14+ days of sales)")

    hist = df[['date', 'qty']].copy()

    if body.engine == "prophet":
        _, future = train_prophet(df, steps=body.days)
    else:
        if len(df) < 30:
            raise HTTPException(status_code=400, detail="XGBoost needs 30+ days of data")
        _, future = train_xgboost(df, steps=body.days)

    if future is None or future.empty:
        raise HTTPException(status_code=500, detail="Model training failed")

    # Get product name
    conn = get_connection()
    row = conn.execute("SELECT name FROM products WHERE id = ?", (body.product_id,)).fetchone()
    conn.close()
    product_name = row['name'] if row else str(body.product_id)

    hist_data = hist.tail(60).copy()
    hist_data['date'] = hist_data['date'].astype(str)

    future_data = future[['date', 'predicted_qty']].copy()
    future_data['date'] = future_data['date'].astype(str)
    future_data['predicted_qty'] = future_data['predicted_qty'].astype(int)

    total = int(future['predicted_qty'].sum())
    avg = int(future['predicted_qty'].mean())
    peak_row = future.loc[future['predicted_qty'].idxmax()]
    peak_date = str(peak_row['date'])[:10]

    return {
        "product_name": product_name,
        "engine": body.engine,
        "historical": hist_data.to_dict(orient='records'),
        "forecast": future_data.to_dict(orient='records'),
        "stats": {"total_projected": total, "average_per_day": avg, "peak_date": peak_date},
    }

# ── Simulator ─────────────────────────────────────────────────────────────────

@app.post("/api/simulator")
def run_simulator(body: SimulatorIn):
    conn = get_connection()
    row = conn.execute("""
        SELECT p.id, p.name, p.price, COALESCE(s.current_qty, 0) as stock
        FROM products p LEFT JOIN stock s ON s.product_id = p.id
        WHERE p.id = ?
    """, (body.product_id,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    price = float(row['price'] or 0)
    stock = float(row['stock'] or 0)
    new_price = price * (1 - body.discount_percent / 100)

    df = prepare_time_series_data(product_id=body.product_id)
    if df.empty or len(df) < 30:
        raise HTTPException(status_code=400, detail="Need 30+ days of sales data")

    _, base_fc = train_xgboost(df, steps=body.period_days)
    if base_fc is None or base_fc.empty:
        raise HTTPException(status_code=500, detail="Forecast failed")

    base_demand = float(base_fc['predicted_qty'].sum())
    base_rev = base_demand * price
    sim_demand = base_demand * (1 + (body.discount_percent / 100) * 1.5)
    sim_rev = sim_demand * new_price
    delta_demand = int(sim_demand - base_demand)
    delta_rev = int(sim_rev - base_rev)

    stockout_risk = None
    if sim_demand > stock:
        shortage = int(sim_demand - stock)
        days_until = int(stock / (sim_demand / body.period_days)) if sim_demand > 0 else body.period_days
        stockout_risk = {"has_risk": True, "shortage_units": shortage, "days_until_stockout": days_until}

    return {
        "product_name": row['name'],
        "current_price": price,
        "current_stock": stock,
        "new_price": round(new_price, 2),
        "discount_percent": body.discount_percent,
        "base_demand": int(base_demand),
        "simulated_demand": int(sim_demand),
        "delta_demand": delta_demand,
        "base_revenue": int(base_rev),
        "simulated_revenue": int(sim_rev),
        "delta_revenue": delta_rev,
        "stockout_risk": stockout_risk,
    }

# ── Demo ──────────────────────────────────────────────────────────────────────

@app.post("/api/demo/seed")
def seed_demo():
    try:
        from core.generate_demo_data import generate_medical_shop_data, seed_database_with_demo_data
        df = generate_medical_shop_data(days=180)
        seed_database_with_demo_data(df)
        return {"success": True, "message": "Demo data seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Serve React build ─────────────────────────────────────────────────────────

frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        index = os.path.join(frontend_dist, "index.html")
        return FileResponse(index)
