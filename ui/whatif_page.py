import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from core.database import get_connection
from ml.feature_engineering import prepare_time_series_data
from ml.forecaster import train_xgboost

def fetch_product_details():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT p.id, p.name, p.price, p.category, s.current_qty 
        FROM products p
        LEFT JOIN stock s ON s.product_id = p.id
    """, conn)
    conn.close()
    return df

def render_whatif_page():
    st.markdown('<div class="section-title">🎛️ What-If Simulator</div>', unsafe_allow_html=True)
    st.write("Test pricing scenarios to see how discounts impact demand, revenue, and stock levels.")

    prod_df = fetch_product_details()
    if prod_df.empty:
        st.warning("No products available.")
        return

    prod_map = dict(zip(prod_df['name'], prod_df['id']))
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ⚙️ Simulation Setup")
        selected_prod = st.selectbox("🏷️ Product", list(prod_map.keys()))
        prod_id = prod_map[selected_prod]
        
        row = prod_df[prod_df['name'] == selected_prod].iloc[0]
        current_price = float(row['price']) if row['price'] else 0.0
        current_stock = float(row['current_qty']) if row['current_qty'] else 0.0
        
        # Show current product info
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:0.85rem; color:#94a3b8;">CURRENT PRICE</div>
            <div style="font-size:1.5rem; font-weight:700; color:#818cf8;">₹{current_price:.0f}</div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:8px;">STOCK ON HAND</div>
            <div style="font-size:1.5rem; font-weight:700; color:#22c55e;">{int(current_stock)} units</div>
        </div>
        """, unsafe_allow_html=True)
        
        discount_percent = st.slider("💸 Apply Discount (%)", 0, 50, 10, step=5)
        new_price = current_price * (1 - discount_percent/100)
        st.markdown(f"🏷️ **New Price:** ₹{new_price:.2f}")
        
        simulation_days = st.slider("📅 Days to Simulate", 7, 30, 14)

    with col2:
        st.markdown("### 📊 Projected Impact")
        
        if st.button("🚀 Run Simulation", type="primary"):
            if current_price <= 0:
                st.error("Product does not have a set price. Cannot simulate.")
                return
                
            with st.spinner("Running price elasticity model..."):
                # Baseline ML Forecast
                df = prepare_time_series_data(product_id=prod_id)
                if df.empty or len(df) < 30:
                    st.error("Not enough historical data to simulate (need 30+ days).")
                    return
                    
                _, base_forecast = train_xgboost(df, steps=simulation_days)
                if base_forecast.empty:
                    st.error("Forecasting model failed.")
                    return
                    
                base_demand = base_forecast['predicted_qty'].sum()
                base_revenue = base_demand * current_price
                
                # Price Elasticity of Demand = -1.5 (industry standard for pharma consumer goods)
                elasticity = 1.5
                demand_multiplier = 1 + ((discount_percent/100) * elasticity)
                
                sim_forecast = base_forecast.copy()
                sim_forecast['simulated_qty'] = (sim_forecast['predicted_qty'] * demand_multiplier).round()
                sim_demand = sim_forecast['simulated_qty'].sum()
                sim_revenue = sim_demand * new_price
                
                profit_base = base_revenue * 0.25  # Assume 25% margin
                profit_sim = sim_revenue * 0.25
                
                # ── Results Cards ──
                st.markdown("---")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("📦 Baseline Sales", f"{int(base_demand)} units")
                m2.metric("📦 Simulated Sales", f"{int(sim_demand)} units", delta=f"+{int(sim_demand - base_demand)}")
                m3.metric("📊 Demand Uplift", f"+{((demand_multiplier - 1)*100):.0f}%")
                
                r1, r2, r3 = st.columns(3)
                r1.metric("💰 Baseline Revenue", f"₹{int(base_revenue):,}")
                r2.metric("💰 Sim Revenue", f"₹{int(sim_revenue):,}", delta=f"₹{int(sim_revenue - base_revenue):,}")
                r3.metric("🏦 Profit Change", f"₹{int(profit_sim - profit_base):,}", 
                          delta=f"{'📈' if profit_sim > profit_base else '📉'}")
                
                st.markdown("---")
                
                # ── Comparison Chart ──
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Baseline', 'With Discount'],
                    y=[int(base_demand), int(sim_demand)],
                    name='Units Sold',
                    marker_color=['#6366f1', '#22c55e'],
                    text=[int(base_demand), int(sim_demand)],
                    textposition='outside'
                ))
                fig.update_layout(
                    template='plotly_dark',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=300,
                    title_text="Units Sold: Baseline vs Discount Scenario",
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # ── Stockout Warning ──
                if sim_demand > current_stock:
                    shortage = int(sim_demand - current_stock)
                    days_until_stockout = int(current_stock / (sim_demand / simulation_days)) if sim_demand > 0 else simulation_days
                    st.error(f"""
                    ⚠️ **STOCKOUT RISK!**  
                    Running this {discount_percent}% discount will deplete your stock in ~**{days_until_stockout} days**.  
                    You need **{shortage} more units** to sustain the full promotion period.  
                    📞 **Action:** Contact your distributor and order now!
                    """)
                else:
                    surplus = int(current_stock - sim_demand)
                    st.success(f"""
                    ✅ **All Clear!** You have enough stock to run this promotion.  
                    Estimated surplus of **{surplus} units** after the sale period.
                    """)
