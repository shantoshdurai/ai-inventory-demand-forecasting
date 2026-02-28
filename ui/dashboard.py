import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.database import get_connection

def fetch_stock_overview():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT p.name as Item, p.category as Category, p.price as Price, s.current_qty as Stock
        FROM stock s JOIN products p ON s.product_id = p.id
    """, conn)
    conn.close()
    return df

def fetch_recent_transactions(limit=8):
    conn = get_connection()
    df = pd.read_sql_query(f"""
        SELECT p.name as Item, t.qty as Qty, t.type as Type, t.date as Date
        FROM transactions t JOIN products p ON t.product_id = p.id
        ORDER BY t.id DESC LIMIT {limit}
    """, conn)
    conn.close()
    return df

def fetch_daily_sales_trend():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT t.date as Date, SUM(t.qty) as Sales
        FROM transactions t
        WHERE t.type = 'sale' AND t.date IS NOT NULL
        GROUP BY t.date ORDER BY t.date DESC LIMIT 60
    """, conn)
    conn.close()
    return df

def render_dashboard():
    # ── Title ──
    st.markdown("""
    <div class="page-title">Dashboard</div>
    <div class="page-desc">Real-time overview of your inventory, sales trends, and stock health.</div>
    """, unsafe_allow_html=True)
    
    stock_df = fetch_stock_overview()
    txns_df = fetch_recent_transactions()
    trend_df = fetch_daily_sales_trend()
    
    total_items = stock_df.shape[0] if not stock_df.empty else 0
    low_stock = stock_df[stock_df['Stock'] < 20].shape[0] if not stock_df.empty else 0
    total_value = int((stock_df['Stock'] * stock_df['Price']).sum()) if not stock_df.empty else 0
    total_units = int(stock_df['Stock'].sum()) if not stock_df.empty else 0

    # ── Stats Grid (HTML) ──
    st.markdown(f"""
    <div class="grid-4">
        <div class="card">
            <div class="card-stat-label">Products</div>
            <div class="card-stat-value">{total_items}</div>
        </div>
        <div class="card">
            <div class="card-stat-label">Low Stock Alerts</div>
            <div class="card-stat-value amber">{low_stock}</div>
        </div>
        <div class="card">
            <div class="card-stat-label">Inventory Value</div>
            <div class="card-stat-value accent">₹{total_value:,}</div>
        </div>
        <div class="card">
            <div class="card-stat-label">Total Units</div>
            <div class="card-stat-value">{total_units:,}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two columns: Chart + Activity ──
    col_chart, col_activity = st.columns([5, 3], gap="large")
    
    with col_chart:
        st.markdown('<div class="sh">Sales Trend · 60 Days</div>', unsafe_allow_html=True)
        if not trend_df.empty:
            trend_df = trend_df.sort_values('Date')
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_df['Date'], y=trend_df['Sales'],
                mode='lines',
                line=dict(color='#7c6ef0', width=2.5, shape='spline'),
                fill='tozeroy',
                fillcolor='rgba(124, 110, 240, 0.08)',
                hovertemplate='%{x}<br><b>%{y}</b> units<extra></extra>'
            ))
            fig.update_layout(
                template='plotly_dark',
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0), height=300,
                xaxis=dict(showgrid=False, color='#666', tickfont=dict(size=11, family='Plus Jakarta Sans')),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', color='#666', tickfont=dict(size=11)),
                hoverlabel=dict(bgcolor='#1a1a2e', bordercolor='#7c6ef0', font=dict(family='Plus Jakarta Sans', size=13, color='white'))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data yet.")

    with col_activity:
        st.markdown('<div class="sh">Recent Transactions</div>', unsafe_allow_html=True)
        if not txns_df.empty:
            # Build as HTML table for full control
            rows_html = ""
            for _, r in txns_df.iterrows():
                type_color = "#4ade80" if r['Type'] == 'restock' else ("#f87171" if r['Type'] == 'sale' else "#60a5fa")
                type_icon = "↙" if r['Type'] == 'restock' else ("↗" if r['Type'] == 'sale' else "●")
                rows_html += f"""
                <tr>
                    <td style="font-weight:500; color:#f0eff5;">{r['Item']}</td>
                    <td style="font-family:'JetBrains Mono'; font-size:13px; color:#ccc;">{int(r['Qty'])}</td>
                    <td><span style="color:{type_color}; font-size:13px;">{type_icon} {r['Type']}</span></td>
                </tr>"""
            
            st.markdown(f"""
            <table style="width:100%; border-collapse:collapse; font-size:14px;">
                <thead>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                        <th style="text-align:left; padding:10px 0; color:rgba(240,238,250,0.4); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">Item</th>
                        <th style="text-align:left; padding:10px 0; color:rgba(240,238,250,0.4); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">Qty</th>
                        <th style="text-align:left; padding:10px 0; color:rgba(240,238,250,0.4); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">Type</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.info("No transactions.")

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    
    # ── Stock Levels — Horizontal Bar ──
    st.markdown('<div class="sh">Stock Levels by Product</div>', unsafe_allow_html=True)
    if not stock_df.empty:
        sdf = stock_df.sort_values('Stock', ascending=True)
        colors = ['#f87171' if s < 10 else '#fbbf24' if s < 50 else '#7c6ef0' for s in sdf['Stock']]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=sdf['Item'], x=sdf['Stock'], orientation='h',
            marker=dict(color=colors, cornerradius=6),
            text=sdf['Stock'].astype(int), textposition='outside',
            textfont=dict(size=13, color='#ccc', family='JetBrains Mono'),
            hovertemplate='%{y}: <b>%{x}</b> units<extra></extra>'
        ))
        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=50, t=0, b=0), height=280,
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', color='#666', tickfont=dict(size=10)),
            yaxis=dict(showgrid=False, color='#ccc', tickfont=dict(size=13, family='Plus Jakarta Sans')),
            hoverlabel=dict(bgcolor='#1a1a2e', bordercolor='#7c6ef0', font=dict(family='Plus Jakarta Sans'))
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Product Table ──
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sh">All Products</div>', unsafe_allow_html=True)
    if not stock_df.empty:
        tbl = stock_df.sort_values('Item')
        rows = ""
        for _, r in tbl.iterrows():
            status_color = "#f87171" if r['Stock'] < 10 else ("#fbbf24" if r['Stock'] < 50 else "#4ade80")
            status_text = "Critical" if r['Stock'] < 10 else ("Low" if r['Stock'] < 50 else "Healthy")
            rows += f"""
            <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                <td style="padding:14px 0; font-weight:600; color:#f0eff5;">{r['Item']}</td>
                <td style="color:#999;">{r['Category']}</td>
                <td style="font-family:'JetBrains Mono'; color:#ccc;">₹{r['Price']:.0f}</td>
                <td style="font-family:'JetBrains Mono'; color:#f0eff5; font-weight:600;">{int(r['Stock'])}</td>
                <td><span style="display:inline-block; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600; 
                    background:{status_color}15; color:{status_color};">{status_text}</span></td>
            </tr>"""
        
        st.markdown(f"""
        <table style="width:100%; border-collapse:collapse; font-size:14px;">
            <thead>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.08);">
                    <th style="text-align:left; padding:12px 0; color:rgba(240,238,250,0.4); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">Product</th>
                    <th style="text-align:left; padding:12px 0; color:rgba(240,238,250,0.4); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">Category</th>
                    <th style="text-align:left; padding:12px 0; color:rgba(240,238,250,0.4); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">Price</th>
                    <th style="text-align:left; padding:12px 0; color:rgba(240,238,250,0.4); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">Stock</th>
                    <th style="text-align:left; padding:12px 0; color:rgba(240,238,250,0.4); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">Status</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """, unsafe_allow_html=True)
