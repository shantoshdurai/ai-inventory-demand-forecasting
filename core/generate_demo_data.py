import os
import random
import pandas as pd
from datetime import datetime, timedelta
from core.database import get_connection
from core.stock_tracker import log_transaction

PRODUCTS = [
    # Staples
    {"name": "Toor Dal", "category": "Pulses & Grains", "base_price": 160, "base_daily_demand": 8, "unit": "kg"},
    {"name": "Basmati Rice (5kg)", "category": "Pulses & Grains", "base_price": 450, "base_daily_demand": 6, "unit": "pcs"},
    {"name": "Aashirvaad Atta (10kg)", "category": "Pulses & Grains", "base_price": 520, "base_daily_demand": 5, "unit": "pcs"},
    {"name": "Sugar", "category": "Pulses & Grains", "base_price": 45, "base_daily_demand": 10, "unit": "kg"},
    # Cooking
    {"name": "Fortune Sunflower Oil (1L)", "category": "Cooking", "base_price": 180, "base_daily_demand": 7, "unit": "pcs"},
    {"name": "MDH Garam Masala", "category": "Cooking", "base_price": 85, "base_daily_demand": 4, "unit": "pcs"},
    {"name": "Saffola Gold Oil (1L)", "category": "Cooking", "base_price": 220, "base_daily_demand": 3, "unit": "pcs"},
    # Snacks & Packaged
    {"name": "Maggi Noodles", "category": "Snacks", "base_price": 14, "base_daily_demand": 25, "unit": "pcs"},
    {"name": "Parle-G Biscuits", "category": "Snacks", "base_price": 10, "base_daily_demand": 30, "unit": "pcs"},
    {"name": "Lays Chips (Small)", "category": "Snacks", "base_price": 20, "base_daily_demand": 15, "unit": "pcs"},
    {"name": "Britannia Bread", "category": "Bakery", "base_price": 45, "base_daily_demand": 12, "unit": "pcs"},
    # Beverages
    {"name": "Tata Tea Gold (500g)", "category": "Beverages", "base_price": 280, "base_daily_demand": 4, "unit": "pcs"},
    {"name": "Nescafe Classic (50g)", "category": "Beverages", "base_price": 160, "base_daily_demand": 3, "unit": "pcs"},
    {"name": "Amul Milk (500ml)", "category": "Dairy", "base_price": 30, "base_daily_demand": 35, "unit": "pcs"},
    # Personal Care & Household
    {"name": "Surf Excel (1kg)", "category": "Household", "base_price": 250, "base_daily_demand": 4, "unit": "pcs"},
    {"name": "Vim Dishwash Bar", "category": "Household", "base_price": 35, "base_daily_demand": 6, "unit": "pcs"},
    {"name": "Lux Soap", "category": "Personal Care", "base_price": 48, "base_daily_demand": 5, "unit": "pcs"},
    {"name": "Colgate Toothpaste", "category": "Personal Care", "base_price": 95, "base_daily_demand": 4, "unit": "pcs"},
    # Eggs & Daily
    {"name": "Eggs (dozen)", "category": "Daily Essentials", "base_price": 80, "base_daily_demand": 10, "unit": "pcs"},
    {"name": "Amul Butter (100g)", "category": "Dairy", "base_price": 56, "base_daily_demand": 6, "unit": "pcs"},
]


def generate_medical_shop_data(days=180):
    """
    Generates realistic 6-month historical data for a Kirana (Indian grocery) shop.
    """
    print("Generating Kirana shop demo data for 6 months...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    transactions = []

    # Generate initial stock
    for product in PRODUCTS:
        transactions.append({
            "item": product["name"],
            "category": product["category"],
            "price": product["base_price"],
            "qty": product["base_daily_demand"] * 30,
            "type": "initial",
            "date": start_date.strftime("%Y-%m-%d"),
            "source": "demo_script"
        })

    # Generate daily sales and restocks
    current_date = start_date
    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5
        date_str = current_date.strftime("%Y-%m-%d")
        month = current_date.month

        for product in PRODUCTS:
            demand = product["base_daily_demand"]

            # Weekend boost (families shop more)
            if is_weekend:
                demand *= 1.35

            # Random daily noise
            noise = random.uniform(0.65, 1.35)
            actual_sales = max(0, int(demand * noise))

            # Festival/seasonal effects for India
            # Diwali season (Oct-Nov) — huge spike in snacks, sweets, gifts
            if month in [10, 11] and product["category"] in ["Snacks", "Cooking", "Dairy"]:
                actual_sales = int(actual_sales * 1.6)
            # Summer (Apr-Jun) — more beverages, less cooking oil
            if month in [4, 5, 6] and product["category"] == "Beverages":
                actual_sales = int(actual_sales * 1.4)
            # Monsoon (Jul-Sep) — more tea, Maggi, comfort food
            if month in [7, 8, 9] and product["name"] in ["Tata Tea Gold (500g)", "Maggi Noodles", "Britannia Bread"]:
                actual_sales = int(actual_sales * 1.5)
            # Winter (Dec-Jan) — more dairy, tea
            if month in [12, 1] and product["category"] in ["Dairy", "Beverages"]:
                actual_sales = int(actual_sales * 1.3)
            # Month-end effect — people buy staples
            if current_date.day >= 25 and product["category"] == "Pulses & Grains":
                actual_sales = int(actual_sales * 1.3)

            if actual_sales > 0:
                transactions.append({
                    "item": product["name"],
                    "category": product["category"],
                    "price": product["base_price"],
                    "qty": actual_sales,
                    "type": "sale",
                    "date": date_str,
                    "source": "demo_script"
                })

            # Restock logic: every ~10-14 days, restock about 14 days worth
            if current_date.day in [1, 10, 20] or (current_date.day == 15 and is_weekend):
                restock_amount = product["base_daily_demand"] * 14 * random.uniform(0.9, 1.2)
                transactions.append({
                    "item": product["name"],
                    "category": product["category"],
                    "price": product["base_price"],
                    "qty": int(restock_amount),
                    "type": "restock",
                    "date": date_str,
                    "source": "demo_script"
                })

        current_date += timedelta(days=1)

    df = pd.DataFrame(transactions)

    os.makedirs('data', exist_ok=True)
    df.to_csv('data/demo_data.csv', index=False)

    print(f"Generated {len(df)} transactions for {len(PRODUCTS)} Kirana products. Saved to data/demo_data.csv")
    return df


def seed_database_with_demo_data(df):
    """Clears current tables and seeds with the new demo data."""
    print("Clearing existing database and importing Kirana shop demo data...")
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM forecasts")
    c.execute("DELETE FROM transactions")
    c.execute("DELETE FROM stock")
    c.execute("DELETE FROM products")
    try:
        c.execute("DELETE FROM sqlite_sequence")
    except Exception:
        pass
    conn.commit()
    conn.close()

    df_sorted = df.sort_values(by="date")

    count = 0
    for _, row in df_sorted.iterrows():
        log_transaction(
            product_name=row['item'],
            qty=row['qty'],
            txn_type=row['type'],
            date=row['date'],
            source=row['source'],
            price=row.get('price', 0),
            category=row.get('category', None)
        )
        count += 1
        if count % 500 == 0:
            print(f"  Inserted {count} rows...")

    print(f"Successfully seeded database with {count} Kirana shop records!")


if __name__ == "__main__":
    df = generate_medical_shop_data(days=180)
    seed_database_with_demo_data(df)
