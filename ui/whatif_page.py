import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.database import get_connection
from ml.feature_engineering import prepare_time_series_data
from ml.forecaster import train_xgboost

def fetch_product_details():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT p.id, p.name, p.price, p.category, s.current_qty 
        FROM products p LEFT JOIN stock s ON s.product_id = p.id
    """, conn)
    conn.close()
    return df

def render_whatif_page():
    st.markdown("""
    <div class="page-title">What-If Simulator</div>
    <div class="page-desc">See how price changes affect demand, revenue, and stock before you commit.</div>
    """, unsafe_allow_html=True)

    prod_df = fetch_product_details()
    if prod_df.empty:
        st.warning("No products available.")
        return

    prod_map = dict(zip(prod_df['name'], prod_df['id']))
    
    # ── DIFFERENT LAYOUT: 1fr 2fr (config narrow, results wide) ──
    left, right = st.columns([1, 2], gap="large")
    
    with left:
        selected = st.selectbox("Product", list(prod_map.keys()))
        row = prod_df[prod_df['name'] == selected].iloc[0]
        price = float(row['price']) if row['price'] else 0
        stock = float(row['current_qty']) if row['current_qty'] else 0
        
        # Product card
        st.markdown(f"""
        <div class="card" style="margin:16px 0;">
            <div class="card-stat-label">Current Price</div>
            <div class="card-stat-value accent" style="font-size:28px;">₹{price:.0f}</div>
            <div style="height:16px"></div>
            <div class="card-stat-label">Stock on Hand</div>
            <div class="card-stat-value green" style="font-size:28px;">{int(stock)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        discount = st.slider("Discount %", 0, 50, 10, step=5)
        new_price = price * (1 - discount/100)
        st.markdown(f"**New Price:** ₹{new_price:.2f}")
        
        sim_days = st.slider("Period (days)", 7, 30, 14)
        
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        run = st.button("Run Simulation")

    with right:
        if run:
            if price <= 0:
                st.error("Product has no price.")
                return
                
            with st.spinner("Computing..."):
                df = prepare_time_series_data(product_id=prod_map[selected])
                if df.empty or len(df) < 30:
                    st.error("Need 30+ days of data.")
                    return
                    
                _, base_fc = train_xgboost(df, steps=sim_days)
                if base_fc.empty:
                    st.error("Forecast failed.")
                    return
                    
                base_demand = base_fc['predicted_qty'].sum()
                base_rev = base_demand * price
                
                elasticity = 1.5
                mult = 1 + ((discount/100) * elasticity)
                sim_demand = base_demand * mult
                sim_rev = sim_demand * new_price
                
                delta_demand = int(sim_demand - base_demand)
                delta_rev = int(sim_rev - base_rev)
                
                # ── Results as stat grid ──
                st.markdown(f"""
                <div class="grid-2" style="margin-top:0;">
                    <div class="card">
                        <div class="card-stat-label">Baseline Units</div>
                        <div class="card-stat-value">{int(base_demand)}</div>
                    </div>
                    <div class="card">
                        <div class="card-stat-label">Simulated Units</div>
                        <div class="card-stat-value accent">{int(sim_demand)}</div>
                        <div style="color:#4ade80; font-size:14px; font-weight:600; margin-top:4px;">+{delta_demand} units</div>
                    </div>
                </div>
                <div class="grid-2">
                    <div class="card">
                        <div class="card-stat-label">Baseline Revenue</div>
                        <div class="card-stat-value">₹{int(base_rev):,}</div>
                    </div>
                    <div class="card">
                        <div class="card-stat-label">Simulated Revenue</div>
                        <div class="card-stat-value accent">₹{int(sim_rev):,}</div>
                        <div style="color:{'#4ade80' if delta_rev >= 0 else '#f87171'}; font-size:14px; font-weight:600; margin-top:4px;">
                            {'↑' if delta_rev >= 0 else '↓'} ₹{abs(delta_rev):,}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # ── Bar comparison ──
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Baseline', f'{discount}% Off'],
                    y=[int(base_demand), int(sim_demand)],
                    marker=dict(color=['rgba(255,255,255,0.1)', '#7c6ef0'], cornerradius=8),
                    text=[int(base_demand), int(sim_demand)], textposition='outside',
                    textfont=dict(size=14, color='#ccc', family='JetBrains Mono'),
                    width=0.5
                ))
                fig.update_layout(
                    template='plotly_dark',
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=8, b=0), height=240,
                    xaxis=dict(showgrid=False, color='#999', tickfont=dict(size=13, family='Plus Jakarta Sans')),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', color='#666', tickfont=dict(size=10)),
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # ── Stockout check ──
                if sim_demand > stock:
                    shortage = int(sim_demand - stock)
                    days_left = int(stock / (sim_demand / sim_days)) if sim_demand > 0 else sim_days
                    st.error(f"⚠️ **Stockout in ~{days_left} days.** You need {shortage} more units to sustain this promotion.")
                else:
                    surplus = int(stock - sim_demand)
                    st.success(f"✅ Stock is sufficient. Surplus of **{surplus} units** after the sale period.")
        else:
            # Empty state
            st.markdown("""
            <div style="display:flex; align-items:center; justify-content:center; height:400px; color:rgba(240,238,250,0.2);">
                <div style="text-align:center;">
                    <div style="font-size:48px; margin-bottom:16px;">🧪</div>
                    <div style="font-size:18px; font-weight:600;">Configure and run a simulation</div>
                    <div style="font-size:14px; margin-top:8px; color:rgba(240,238,250,0.15);">Results will appear here</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
