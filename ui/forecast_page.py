import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from ml.feature_engineering import prepare_time_series_data
from ml.forecaster import train_xgboost, train_prophet
from core.database import get_connection

def get_product_list():
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, name FROM products", conn)
    conn.close()
    return dict(zip(df['name'], df['id']))

def render_forecast_page():
    st.markdown("""
    <div class="page-title">Forecast</div>
    <div class="page-desc">Machine learning predictions for future product demand.</div>
    """, unsafe_allow_html=True)
    
    product_map = get_product_list()
    if not product_map:
        st.warning("No products found. Add data first.")
        return
    
    # ── Config row — different layout than dashboard ──
    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    with c1:
        selected = st.selectbox("Product", list(product_map.keys()))
    with c2:
        days = st.slider("Days", 7, 30, 14)
    with c3:
        engine = st.radio("Engine", ["XGBoost", "Prophet"], horizontal=True)
    with c4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        run = st.button("Generate Forecast")

    if run:
        with st.spinner(f"Training {engine}..."):
            df = prepare_time_series_data(product_id=product_map[selected])
            if df.empty or len(df) < 14:
                st.error("Need at least 14 days of data.")
                return
                
            hist = df[['date', 'qty']].copy()
            
            if engine == "XGBoost":
                _, future = train_xgboost(df, steps=days)
            else:
                _, future = train_prophet(df, steps=days)
                
            if future.empty:
                st.error("Model failed.")
                return

            fplot = future[['date', 'predicted_qty']].rename(columns={'predicted_qty': 'qty'})
            
            st.markdown("---")
            
            # ── DIFFERENT LAYOUT: Full-width chart, then 3-col stats below ──
            st.markdown(f'<div class="sh2">{selected} — {days}-day outlook</div>', unsafe_allow_html=True)
            
            fig = go.Figure()
            
            h = hist.tail(60)
            fig.add_trace(go.Scatter(
                x=h['date'], y=h['qty'], mode='lines', name='Historical',
                line=dict(color='rgba(255,255,255,0.2)', width=1.5, shape='spline'),
                hovertemplate='%{x|%b %d}: %{y}<extra></extra>'
            ))
            fig.add_trace(go.Scatter(
                x=fplot['date'], y=fplot['qty'], mode='lines+markers', name='Forecast',
                line=dict(color='#7c6ef0', width=3, shape='spline'),
                marker=dict(size=8, color='#7c6ef0', line=dict(width=2, color='#0a0a0f')),
                fill='tozeroy', fillcolor='rgba(124, 110, 240, 0.06)',
                hovertemplate='%{x|%b %d}: <b>%{y:.0f}</b><extra></extra>'
            ))
            
            today = datetime.now()
            all_y = pd.concat([h['qty'], fplot['qty']])
            ymax = all_y.max() * 1.3 if len(all_y) > 0 else 50
            fig.add_shape(type="line", x0=today, x1=today, y0=0, y1=ymax,
                          line=dict(color="rgba(248,113,113,0.3)", width=1, dash="dot"))
            fig.add_annotation(x=today, y=ymax*0.92, text="today", showarrow=False,
                               font=dict(size=11, color="#f87171", family="Plus Jakarta Sans"))
            
            fig.update_layout(
                template='plotly_dark',
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0), height=380,
                xaxis=dict(showgrid=False, color='#666', tickfont=dict(size=11, family='Plus Jakarta Sans')),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', color='#666', tickfont=dict(size=11), title=''),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(size=12, color='#999', family='Plus Jakarta Sans')),
                hoverlabel=dict(bgcolor='#1a1a2e', bordercolor='#7c6ef0', font=dict(family='Plus Jakarta Sans'))
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # ── 3 stat cards below chart ──
            total = int(future['predicted_qty'].sum())
            avg = int(future['predicted_qty'].mean())
            peak = future.loc[future['predicted_qty'].idxmax()]
            peak_date = peak['date'].strftime('%b %d') if hasattr(peak['date'], 'strftime') else str(peak['date'])[:10]
            
            st.markdown(f"""
            <div class="grid-3">
                <div class="card">
                    <div class="card-stat-label">Total Projected</div>
                    <div class="card-stat-value accent">{total}</div>
                </div>
                <div class="card">
                    <div class="card-stat-label">Average per Day</div>
                    <div class="card-stat-value">{avg}</div>
                </div>
                <div class="card">
                    <div class="card-stat-label">Peak Day</div>
                    <div class="card-stat-value" style="font-size:24px;">{peak_date}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # ── Table ──
            st.markdown('<div class="sh">Day-by-Day Breakdown</div>', unsafe_allow_html=True)
            tbl = future[['date', 'predicted_qty']].copy()
            tbl.columns = ['Date', 'Projected Demand']
            tbl['Projected Demand'] = tbl['Projected Demand'].astype(int)
            st.dataframe(tbl, hide_index=True, use_container_width=True)
            
            st.info(f"Ensure you have at least **{total} units** of {selected} to prevent stockouts over {days} days.")
