import streamlit as st
import sys
import os

# ─── Premium Page Config ───
st.set_page_config(
    page_title="StockSense AI — Smart Inventory Forecasting",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Premium Custom CSS ───
st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global Styles ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Main container ── */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29, #302b63, #24243e);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #a5b4fc !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* ── Metric Cards ── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.25);
    }
    div[data-testid="stMetric"] label {
        color: #a5b4fc !important;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(99, 102, 241, 0.08);
        border-radius: 10px;
        border: 1px solid rgba(99, 102, 241, 0.15);
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border-color: transparent !important;
    }

    /* ── DataFrames ── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Info / Success / Warning / Error alerts ── */
    .stAlert {
        border-radius: 12px;
        border-left-width: 4px;
    }

    /* ── Hero Header ── */
    .hero-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    .hero-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .hero-header p {
        color: #94a3b8;
        font-size: 1rem;
        font-weight: 400;
    }

    /* ── Glassmorphism cards ── */
    .glass-card {
        background: rgba(30, 27, 75, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }

    /* ── Page section titles ── */
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.3);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def main():
    # ── Sidebar ──
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0;">
            <div style="font-size:2.5rem;">🧠</div>
            <h2 style="background: linear-gradient(135deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:800; margin:0;">StockSense AI</h2>
            <p style="color:#94a3b8; font-size:0.8rem; margin-top:4px;">Intelligent Inventory Forecasting</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        menu = ["📊 Dashboard", "📥 Input Data", "🔮 Forecast", "🎛️ What-If Simulator"]
        choice = st.selectbox("Navigate", menu)
        
        st.markdown("---")
        st.markdown("""
        <div style="color:#64748b; font-size:0.75rem; text-align:center;">
            <p>Built for <b>TNI26086</b> Hackathon</p>
            <p>Powered by Gemini AI + XGBoost</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ── Hero Header ──
    st.markdown("""
    <div class="hero-header">
        <h1>StockSense AI</h1>
        <p>Smart Demand Forecasting for Small Businesses — Powered by Machine Learning & Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)

    if "Dashboard" in choice:
        from ui.dashboard import render_dashboard
        render_dashboard()
    elif "Input" in choice:
        from ui.input_page import render_input_page
        render_input_page()
    elif "Forecast" in choice:
        from ui.forecast_page import render_forecast_page
        render_forecast_page()
    elif "What-If" in choice:
        from ui.whatif_page import render_whatif_page
        render_whatif_page()

if __name__ == "__main__":
    main()
