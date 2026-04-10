import pandas as pd
from core.database import get_connection
from config import GEMINI_API_KEY


def _get_inventory_context():
    conn = get_connection()
    stock_df = pd.read_sql_query("""
        SELECT p.name, p.category, p.price, s.current_qty
        FROM stock s JOIN products p ON s.product_id = p.id
    """, conn)
    sales_df = pd.read_sql_query("""
        SELECT p.name, t.qty, t.date, t.type
        FROM transactions t JOIN products p ON t.product_id = p.id
        WHERE t.type = 'sale' AND t.date IS NOT NULL
        ORDER BY t.date DESC
    """, conn)
    conn.close()
    return stock_df, sales_df


def get_inventory_summary_text():
    stock_df, sales_df = _get_inventory_context()
    if stock_df.empty:
        return "No inventory data available."

    lines = ["PRODUCT INVENTORY:"]
    for _, r in stock_df.iterrows():
        lines.append(f"- {r['name']} ({r['category']}): {int(r['current_qty'])} units @ ₹{r['price']:.0f}")

    if not sales_df.empty:
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        recent = sales_df[sales_df['date'] >= sales_df['date'].max() - pd.Timedelta(days=7)]
        if not recent.empty:
            lines.append("\nLAST 7 DAYS SALES:")
            weekly = recent.groupby('name')['qty'].sum().sort_values(ascending=False)
            for name, qty in weekly.items():
                lines.append(f"- {name}: {int(qty)} units sold")

        last_30 = sales_df[sales_df['date'] >= sales_df['date'].max() - pd.Timedelta(days=30)]
        prev_30 = sales_df[
            (sales_df['date'] < sales_df['date'].max() - pd.Timedelta(days=30)) &
            (sales_df['date'] >= sales_df['date'].max() - pd.Timedelta(days=60))
        ]
        if not last_30.empty and not prev_30.empty:
            lines.append("\n30-DAY TRENDS (vs prior 30 days):")
            cur = last_30.groupby('name')['qty'].sum()
            prev = prev_30.groupby('name')['qty'].sum()
            for name in cur.index:
                cur_val = cur[name]
                prev_val = prev.get(name, 0)
                if prev_val > 0:
                    change = ((cur_val - prev_val) / prev_val) * 100
                    lines.append(f"- {name}: {change:+.0f}%")

    return "\n".join(lines)


def generate_rule_based_insights():
    stock_df, sales_df = _get_inventory_context()
    if stock_df.empty:
        return []

    insights = []

    # Critical stock alerts
    critical = stock_df[stock_df['current_qty'] < 10]
    for _, r in critical.iterrows():
        insights.append({
            "title": f"{r['name']} critically low",
            "detail": f"Only {int(r['current_qty'])} units remaining. Reorder immediately to avoid stockouts.",
            "severity": "critical",
            "metric": f"{int(r['current_qty'])} left"
        })

    # Low stock warnings
    low = stock_df[(stock_df['current_qty'] >= 10) & (stock_df['current_qty'] < 30)]
    for _, r in low.iterrows():
        insights.append({
            "title": f"{r['name']} running low",
            "detail": f"{int(r['current_qty'])} units in stock. Consider restocking within the week.",
            "severity": "warning",
            "metric": f"{int(r['current_qty'])} units"
        })

    if not sales_df.empty:
        sales_df['date'] = pd.to_datetime(sales_df['date'])
        max_date = sales_df['date'].max()

        # Stockout risk - estimate days remaining
        recent_7 = sales_df[sales_df['date'] >= max_date - pd.Timedelta(days=7)]
        if not recent_7.empty:
            daily_avg = recent_7.groupby('name')['qty'].sum() / 7
            for _, r in stock_df.iterrows():
                avg = daily_avg.get(r['name'], 0)
                if avg > 0:
                    days_left = r['current_qty'] / avg
                    if days_left < 5 and r['current_qty'] >= 10:
                        insights.append({
                            "title": f"{r['name']} stockout risk",
                            "detail": f"At current sales rate ({avg:.0f}/day), stock runs out in ~{days_left:.0f} days. Order {int(avg * 14):.0f} units for 2-week cover.",
                            "severity": "critical",
                            "metric": f"~{days_left:.0f} days"
                        })

        # Trending products
        last_30 = sales_df[sales_df['date'] >= max_date - pd.Timedelta(days=30)]
        prev_30 = sales_df[
            (sales_df['date'] < max_date - pd.Timedelta(days=30)) &
            (sales_df['date'] >= max_date - pd.Timedelta(days=60))
        ]
        if not last_30.empty and not prev_30.empty:
            cur = last_30.groupby('name')['qty'].sum()
            prev = prev_30.groupby('name')['qty'].sum()
            for name in cur.index:
                cur_val = cur[name]
                prev_val = prev.get(name, 0)
                if prev_val > 0:
                    change = ((cur_val - prev_val) / prev_val) * 100
                    if change > 20:
                        insights.append({
                            "title": f"{name} demand surging",
                            "detail": f"Sales up {change:.0f}% vs last month ({int(cur_val)} vs {int(prev_val)} units). Increase next order accordingly.",
                            "severity": "info",
                            "metric": f"+{change:.0f}%"
                        })
                    elif change < -20:
                        insights.append({
                            "title": f"{name} demand declining",
                            "detail": f"Sales down {abs(change):.0f}% vs last month. Avoid over-ordering to prevent dead stock.",
                            "severity": "warning",
                            "metric": f"{change:.0f}%"
                        })

        # Top seller highlight
        if not last_30.empty:
            top = last_30.groupby('name')['qty'].sum().idxmax()
            top_qty = int(last_30.groupby('name')['qty'].sum().max())
            insights.append({
                "title": f"{top} is your top seller",
                "detail": f"{top_qty} units sold in the last 30 days. Ensure consistent supply.",
                "severity": "info",
                "metric": f"{top_qty} units"
            })

    # Sort: critical first, then warning, then info
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    insights.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return insights[:6]


def get_smart_insights():
    rule_insights = generate_rule_based_insights()

    if GEMINI_API_KEY:
        try:
            from core.gemini_engine import generate_ai_insights
            context = get_inventory_summary_text()
            ai_insights = generate_ai_insights(context)
            if ai_insights:
                seen_titles = {i["title"].lower() for i in rule_insights}
                for ai in ai_insights:
                    if ai.get("title", "").lower() not in seen_titles:
                        rule_insights.append(ai)
        except Exception:
            pass

    return rule_insights[:6]
