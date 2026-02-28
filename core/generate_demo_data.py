import os
import random
import pandas as pd
from datetime import datetime, timedelta
from core.database import get_connection
from core.stock_tracker import log_transaction

PRODUCTS = [
    {"name": "Dolo 650", "category": "Fever", "base_price": 30, "base_daily_demand": 15},
    {"name": "Crocin Advance", "category": "Fever", "base_price": 25, "base_daily_demand": 8},
    {"name": "Amoxicillin 500mg", "category": "Antibiotic", "base_price": 85, "base_daily_demand": 5},
    {"name": "Volini Spray", "category": "Pain Relief", "base_price": 120, "base_daily_demand": 3},
    {"name": "Digene Tablets", "category": "Digestion", "base_price": 20, "base_daily_demand": 10},
    {"name": "Cetirizine", "category": "Allergy", "base_price": 15, "base_daily_demand": 12},
    {"name": "Vicks VapoRub", "category": "Cold", "base_price": 45, "base_daily_demand": 4},
    {"name": "Band-Aid", "category": "First Aid", "base_price": 5, "base_daily_demand": 20},
]

def generate_medical_shop_data(days=180):
    """
    Generates realistic 6-month historical data for a medical shop.
    Returns a pandas DataFrame and saves it to a CSV.
    """
    print("Generating demo data for 6 months...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    transactions = []
    
    # Generate initial stock
    for product in PRODUCTS:
        transactions.append({
            "item": product["name"],
            "category": product["category"],
            "price": product["base_price"],
            "qty": product["base_daily_demand"] * 30, # 1 month initial buffer
            "type": "initial",
            "date": start_date.strftime("%Y-%m-%d"),
            "source": "demo_script"
        })
    
    # Generate daily sales and restocks
    current_date = start_date
    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5
        date_str = current_date.strftime("%Y-%m-%d")
        
        for product in PRODUCTS:
            demand = product["base_daily_demand"]
            
            # Weekend effect
            if is_weekend:
                demand *= 1.3
                
            # Random noise
            noise = random.uniform(0.7, 1.3)
            actual_sales = max(0, int(demand * noise))
            
            # Season effects
            if "Cold" in product["category"] and current_date.month in [11, 12, 1, 2]:
                actual_sales = int(actual_sales * 1.5) # Winter spike
            if "Allergy" in product["category"] and current_date.month in [3, 4, 5]:
                actual_sales = int(actual_sales * 1.4) # Spring allergy spike
            if "Fever" in product["category"] and current_date.month in [6, 7, 8]:
                actual_sales = int(actual_sales * 1.3) # Monsoon spike
            
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
                
            # Restock logic: Every 14 days or so, restock about 14 days worth
            if current_date.day in [1, 14, 28] or (current_date.day == 15 and is_weekend):
                 restock_amount = product["base_daily_demand"] * 15 * random.uniform(0.9, 1.2)
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
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/demo_data.csv', index=False)
    
    print(f"Generated {len(df)} transactions. Saved to data/demo_data.csv")
    return df

def seed_database_with_demo_data(df):
    """
    Clears current tables and seeds with the new demo data.
    """
    print("Clearing existing database and importing demo data...")
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
    
    # Iterate chronologically
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
            print(f"Inserted {count} rows...")
            
    print(f"Successfully seeded database with {count} records!")

if __name__ == "__main__":
    df = generate_medical_shop_data(days=180)
    seed_database_with_demo_data(df)
