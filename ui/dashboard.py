import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.database import get_connection

def fetch_stock_overview():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT p.name as Item, p.category as Category, p.price as Price, s.current_qty as Stock
        FROM stock s
        JOIN products p ON s.product_id = p.id
    """, conn)
    conn.close()
    return df

def fetch_recent_transactions(limit=15):
    conn = get_connection()
    df = pd.read_sql_query(f"""
        SELECT t.id, p.name as Item, t.qty as Quantity, t.type as Type, t.date as Date
        FROM transactions t
        JOIN products p ON t.product_id = p.id
        ORDER BY t.id DESC LIMIT {limit}
    """, conn)
    conn.close()
    return df

def fetch_daily_sales_trend():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT t.date as Date, SUM(t.qty) as TotalSales
        FROM transactions t
        WHERE t.type = 'sale' AND t.date IS NOT NULL
        GROUP BY t.date
        ORDER BY t.date DESC
        LIMIT 60
    """, conn)
    conn.close()
    return df

def render_dashboard():
    stock_df = fetch_stock_overview()
    txns_df = fetch_recent_transactions()
    trend_df = fetch_daily_sales_trend()
    
    # ── Top Metrics Row ──
    total_items = stock_df.shape[0] if not stock_df.empty else 0
    low_stock = stock_df[stock_df['Stock'] < 20].shape[0] if not stock_df.empty else 0
    total_stock_value = (stock_df['Stock'] * stock_df['Price']).sum() if not stock_df.empty else 0
    total_units = stock_df['Stock'].sum() if not stock_df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Products Tracked", total_items)
    col2.metric("⚠️ Low Stock Alerts", low_stock)
    col3.metric("💰 Inventory Value", f"₹{int(total_stock_value):,}")
    col4.metric("📊 Total Units", f"{int(total_units):,}")

    st.markdown("")  # spacer

    # ── Two-column layout ──
    left, right = st.columns([3, 2])
    
    with left:
        st.markdown('<div class="section-title">📈 Sales Trend (Last 60 Days)</div>', unsafe_allow_html=True)
        if not trend_df.empty:
            trend_df = trend_df.sort_values('Date')
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_df['Date'], y=trend_df['TotalSales'],
                mode='lines+markers',
                fill='tozeroy',
                fillcolor='rgba(99, 102, 241, 0.1)',
                line=dict(color='#818cf8', width=2.5),
                marker=dict(size=4, color='#c084fc'),
                name='Daily Sales'
            ))
            fig.update_layout(
                template='plotly_dark',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                height=320,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data yet — head to Input Data to get started!")

    with right:
        st.markdown('<div class="section-title">🕐 Recent Activity</div>', unsafe_allow_html=True)
        if not txns_df.empty:
            styled = txns_df[['Item', 'Quantity', 'Type', 'Date']].copy()
            styled['Type'] = styled['Type'].map(lambda x: f"🟢 {x}" if x == "restock" else (f"🔴 {x}" if x == "sale" else f"🔵 {x}"))
            st.dataframe(styled, hide_index=True, use_container_width=True, height=320)
        else:
            st.info("No transactions yet.")

    st.markdown("---")
    
    # ── Stock Overview Bar Chart ──
    st.markdown('<div class="section-title">📦 Current Stock Levels by Product</div>', unsafe_allow_html=True)
    if not stock_df.empty:
        # Color-code by status
        stock_df['Status'] = stock_df['Stock'].apply(lambda x: '🔴 Critical' if x < 10 else ('🟡 Low' if x < 50 else '🟢 Healthy'))
        color_map = {'🔴 Critical': '#ef4444', '🟡 Low': '#f59e0b', '🟢 Healthy': '#22c55e'}
        
        fig = px.bar(
            stock_df, x='Item', y='Stock', color='Status', text_auto=True,
            color_discrete_map=color_map
        )
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            height=350,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_traces(textposition='outside', textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)
    
    # ── Stock Table ──
    st.markdown('<div class="section-title">📋 Detailed Stock Table</div>', unsafe_allow_html=True)
    if not stock_df.empty:
        display_df = stock_df[['Item', 'Category', 'Price', 'Stock', 'Status']].copy()
        display_df['Price'] = display_df['Price'].apply(lambda x: f"₹{x:.0f}" if x > 0 else "—")
        st.dataframe(display_df, hide_index=True, use_container_width=True)
