import streamlit as st

st.set_page_config(
    page_title="StockSense AI",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── COMPLETE CSS REWRITE ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Kill sidebar completely ── */
    section[data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* ── Background ── */
    .stApp {
        background: #0a0a0f;
    }

    /* ── Main container ── */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ── Hide chrome ── */
    #MainMenu, footer, header { display: none !important; }
    .stDeployButton { display: none !important; }

    /* ── TOP NAV BAR via Streamlit columns ── */
    .nav-bar {
        display: flex;
        align-items: center;
        padding: 16px 0;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nav-logo {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #7c6ef0, #5b8af0);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        color: white;
    }
    .nav-name {
        font-size: 17px;
        font-weight: 700;
        color: #f0eff5;
        letter-spacing: -0.3px;
    }

    /* Style the nav radio as pill buttons */
    div[data-testid="stHorizontalBlock"]:has(.nav-radio) .stRadio > div {
        flex-direction: row;
        gap: 0;
    }
    .nav-radio .stRadio > div[role="radiogroup"] {
        background: rgba(255,255,255,0.04);
        padding: 4px;
        border-radius: 12px;
        gap: 2px;
        display: flex;
    }
    .nav-radio .stRadio > div[role="radiogroup"] label {
        padding: 8px 22px !important;
        border-radius: 9px !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        color: rgba(240,238,250,0.55) !important;
        cursor: pointer;
        transition: all 0.2s ease;
        background: transparent;
        border: none !important;
        margin: 0 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    .nav-radio .stRadio > div[role="radiogroup"] label:hover {
        color: rgba(240,238,250,0.9) !important;
        background: rgba(255,255,255,0.06);
    }
    .nav-radio .stRadio > div[role="radiogroup"] label[data-checked="true"],
    .nav-radio .stRadio > div[role="radiogroup"] label:has(input:checked) {
        color: #f0eff5 !important;
        background: rgba(124, 110, 240, 0.25) !important;
    }
    /* Hide the radio circle */
    .nav-radio .stRadio > div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    .nav-radio .stRadio > label { display: none !important; }

    /* ── PAGE CONTAINER ── */
    .page-wrap {
        max-width: 1200px;
        margin: 0 auto;
        padding: 40px 48px 80px 48px;
    }

    /* ── HEADINGS — large, clear, Anthropic-style ── */
    .page-title {
        font-size: 36px;
        font-weight: 800;
        color: #f0eff5;
        letter-spacing: -1px;
        line-height: 1.1;
        margin-bottom: 8px;
    }
    .page-desc {
        font-size: 16px;
        font-weight: 400;
        color: rgba(240, 238, 250, 0.5);
        line-height: 1.5;
        margin-bottom: 36px;
    }

    /* ── SECTION HEADERS ── */
    .sh {
        font-size: 13px;
        font-weight: 600;
        color: rgba(240, 238, 250, 0.35);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 16px;
    }
    .sh2 {
        font-size: 20px;
        font-weight: 700;
        color: #f0eff5;
        letter-spacing: -0.3px;
        margin-bottom: 20px;
    }

    /* ── CARDS ── */
    .card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px 28px;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        border-color: rgba(124, 110, 240, 0.15);
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    .card-stat-label {
        font-size: 12px;
        font-weight: 600;
        color: rgba(240, 238, 250, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
    }
    .card-stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #f0eff5;
        letter-spacing: -1px;
        font-family: 'JetBrains Mono', monospace;
    }
    .card-stat-value.accent {
        color: #7c6ef0;
    }
    .card-stat-value.green {
        color: #4ade80;
    }
    .card-stat-value.amber {
        color: #fbbf24;
    }

    /* ── GRID LAYOUTS ── */
    .grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 40px;
    }
    .grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 40px;
    }
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
        margin-bottom: 40px;
    }
    .grid-2-1 {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 24px;
        margin-bottom: 40px;
    }
    .grid-1-2 {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 24px;
        margin-bottom: 40px;
    }

    /* ── METRIC CARDS (streamlit native) ── */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 24px 28px;
        transition: border-color 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(124, 110, 240, 0.15);
    }
    div[data-testid="stMetric"] label {
        color: rgba(240, 238, 250, 0.4) !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #f0eff5 !important;
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: -0.5px !important;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        background: #7c6ef0 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 12px rgba(124, 110, 240, 0.25) !important;
    }
    .stButton > button:hover {
        background: #6b5ce0 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(124, 110, 240, 0.35) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.06);
        width: fit-content;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        padding: 10px 24px;
        font-weight: 500;
        font-size: 14px;
        color: rgba(240,238,250,0.5) !important;
        background: transparent;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: rgba(240,238,250,0.8) !important;
    }
    .stTabs [aria-selected="true"] {
        background: #7c6ef0 !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(124, 110, 240, 0.3);
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* ── SELECT / INPUT ── */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        color: #f0eff5 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stSelectbox label, .stSlider label, .stRadio label, .stTextArea label {
        color: rgba(240, 238, 250, 0.6) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    .stTextArea textarea {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        color: #f0eff5 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 15px !important;
    }
    .stTextArea textarea:focus {
        border-color: rgba(124, 110, 240, 0.4) !important;
        box-shadow: 0 0 0 2px rgba(124, 110, 240, 0.1) !important;
    }

    /* ── SLIDER ── */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: #7c6ef0 !important;
        border: none !important;
        width: 16px !important;
        height: 16px !important;
    }

    /* ── FILE UPLOADER ── */
    [data-testid="stFileUploader"] section {
        border: 2px dashed rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        background: rgba(255,255,255,0.02) !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: rgba(124, 110, 240, 0.3) !important;
    }

    /* ── ALERTS ── */
    .stAlert { border-radius: 12px !important; }

    /* ── DATAFRAME ── */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* ── HR ── */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }

    /* ── PLOTLY containers ── */
    .stPlotlyChart { border-radius: 12px; overflow: hidden; }

    @media (max-width: 768px) {
        .topnav { padding: 12px 20px; }
        .topnav-links { display: none; }
        .page-wrap { padding: 24px 20px 60px 20px; }
        .grid-4, .grid-3, .grid-2, .grid-2-1, .grid-1-2 {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)


def main():
    # ── Top Navigation using Streamlit native controls ──
    brand_col, nav_col = st.columns([1, 3])
    
    with brand_col:
        st.markdown("""
        <div class="nav-brand">
            <div class="nav-logo">◆</div>
            <div class="nav-name">StockSense</div>
        </div>
        """, unsafe_allow_html=True)
    
    with nav_col:
        st.markdown('<div class="nav-radio">', unsafe_allow_html=True)
        page = st.radio(
            "nav",
            ["Dashboard", "Input", "Forecast", "Simulator"],
            horizontal=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="border-bottom:1px solid rgba(255,255,255,0.06); margin-bottom:24px;"></div>', unsafe_allow_html=True)

    # ── Page Content ──
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    
    if page == "Dashboard":
        from ui.dashboard import render_dashboard
        render_dashboard()
    elif page == "Input":
        from ui.input_page import render_input_page
        render_input_page()
    elif page == "Forecast":
        from ui.forecast_page import render_forecast_page
        render_forecast_page()
    elif page == "Simulator":
        from ui.whatif_page import render_whatif_page
        render_whatif_page()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

