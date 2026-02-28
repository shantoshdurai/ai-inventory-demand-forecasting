import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
    st.markdown('<div class="section-title">🔮 AI Demand Forecasting</div>', unsafe_allow_html=True)
    st.write("Select a product and let our ML models predict future demand.")
    
    product_map = get_product_list()
    if not product_map:
        st.warning("No products found in the database. Please input data first.")
        return
    
    # ── Controls ──
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        selected_product_name = st.selectbox("🏷️ Product", list(product_map.keys()))
    with c2:
        forecast_days = st.slider("📅 Days Ahead", min_value=7, max_value=30, value=14)
    with c3:
        model_choice = st.radio("⚙️ ML Engine", ["XGBoost", "Prophet"])

    selected_product_id = product_map[selected_product_name]

    if st.button("🚀 Generate Forecast", type="primary"):
        with st.spinner(f"Training {model_choice} model on {selected_product_name}..."):
            
            # Step 1: Feature Engineering
            df = prepare_time_series_data(product_id=selected_product_id)
            if df.empty or len(df) < 14:
                st.error("Not enough historical data for this product (need at least 14 days).")
                return
                
            # Historical data for plotting
            hist_df = df[['date', 'qty']].copy()
            hist_df['Type'] = 'Historical Sales'

            # Step 2: Train and Predict
            future_df = pd.DataFrame()
            if model_choice == "XGBoost":
                _, future_df = train_xgboost(df, steps=forecast_days)
            else:
                _, future_df = train_prophet(df, steps=forecast_days)
                
            if future_df.empty:
                 st.error("Model training failed or insufficient data.")
                 return

            # Combine for plotting
            forecast_plot_df = future_df[['date', 'predicted_qty']].rename(columns={'predicted_qty': 'qty'})
            forecast_plot_df['Type'] = 'AI Forecast'
            
            combined_df = pd.concat([hist_df.tail(60), forecast_plot_df])
            
            st.success("✅ Forecast Model Trained Successfully!")
            st.markdown("---")
            
            # ── Results ──
            st.markdown(f'<div class="section-title">📈 {selected_product_name} — Next {forecast_days} Days</div>', unsafe_allow_html=True)
            
            # Split historical vs forecast for different styling
            fig = go.Figure()
            
            hist_plot = hist_df.tail(60)
            fig.add_trace(go.Scatter(
                x=hist_plot['date'], y=hist_plot['qty'],
                mode='lines',
                name='Historical',
                line=dict(color='#64748b', width=2),
                fill='tozeroy', fillcolor='rgba(100, 116, 139, 0.08)'
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_plot_df['date'], y=forecast_plot_df['qty'],
                mode='lines+markers',
                name=f'{model_choice} Forecast',
                line=dict(color='#22c55e', width=3, dash='dot'),
                marker=dict(size=8, color='#22c55e', symbol='diamond'),
                fill='tozeroy', fillcolor='rgba(34, 197, 94, 0.08)'
            ))
            
            # Today marker
            today = datetime.now()
            fig.add_shape(
                type="line",
                x0=today, x1=today,
                y0=0, y1=combined_df['qty'].max() * 1.2,
                line=dict(color="#ef4444", width=2, dash="dash"),
            )
            fig.add_annotation(
                x=today, y=combined_df['qty'].max() * 1.15,
                text="TODAY", showarrow=False,
                font=dict(size=12, color="#ef4444", family="Inter"),
                bgcolor="rgba(239,68,68,0.15)", bordercolor="#ef4444", borderwidth=1, borderpad=4
            )
            
            fig.update_layout(
                template='plotly_dark',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                height=400,
                xaxis=dict(showgrid=False, title=''),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='Units Sold'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # ── Forecast Table + Summary ──
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.markdown("#### 📋 Daily Forecast Breakdown")
                display = future_df[['date', 'predicted_qty']].copy()
                display.columns = ['Date', 'Projected Demand']
                display['Projected Demand'] = display['Projected Demand'].astype(int)
                st.dataframe(display, hide_index=True, use_container_width=True)
            
            with col_right:
                total_predicted = int(future_df['predicted_qty'].sum())
                avg_daily = int(future_df['predicted_qty'].mean())
                peak_day = future_df.loc[future_df['predicted_qty'].idxmax()]
                
                st.markdown("#### 🧠 AI Insights")
                st.metric("Total Predicted Demand", f"{total_predicted} units")
                st.metric("Avg Daily Demand", f"{avg_daily} units/day")
                st.metric("Peak Day", f"{peak_day['date'].strftime('%b %d') if hasattr(peak_day['date'], 'strftime') else peak_day['date']}")
                
                st.markdown("---")
                st.info(f"💡 **Recommendation:** Ensure you have **{total_predicted}+ units** of {selected_product_name} in stock to avoid stockouts over the next {forecast_days} days.")
