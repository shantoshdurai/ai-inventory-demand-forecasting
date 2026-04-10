import sqlite3
import os

from config import DB_PATH

def get_connection():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Enable row factory to access columns by name
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = get_connection()
    c = conn.cursor()
    
    # Create products table
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT,
            unit TEXT,
            price REAL
        )
    ''')
    
    # Create stock table
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            product_id INTEGER,
            current_qty REAL DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    
    # Create transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            qty REAL,
            type TEXT, -- 'sale', 'restock', 'initial'
            date TEXT,
            source TEXT, -- 'voice', 'photo', 'csv', 'manual'
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    
    # Create forecasts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            predicted_qty REAL,
            date TEXT,
            confidence REAL,
            explanation TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def is_database_empty():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products")
    count = c.fetchone()[0]
    conn.close()
    return count == 0


def auto_seed_demo_data():
    if not is_database_empty():
        return
    try:
        from core.generate_demo_data import generate_medical_shop_data, seed_database_with_demo_data
        df = generate_medical_shop_data(days=180)
        seed_database_with_demo_data(df)
    except Exception:
        pass


# Initialize DB on import
setup_database()
# Auto-seed demo data if DB is empty (for recruiter demos)
auto_seed_demo_data()
