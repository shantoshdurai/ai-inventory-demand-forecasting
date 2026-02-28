from .database import get_connection

def add_product(name, category=None, unit="pcs", price=0.0):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO products (name, category, unit, price) VALUES (?, ?, ?, ?)", 
              (name, category, unit, price))
    conn.commit()
    conn.close()

def update_product_price(name, price):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE products SET price = ? WHERE name = ?", (price, name))
    conn.commit()
    conn.close()

def log_transaction(product_name, qty, txn_type="sale", date=None, source="manual", price=None, category=None):
    conn = get_connection()
    c = conn.cursor()
    
    # Get product ID or create
    c.execute("SELECT id FROM products WHERE name = ?", (product_name,))
    row = c.fetchone()
    if not row:
        add_product(product_name, category=category, price=price or 0.0)
        c.execute("SELECT id FROM products WHERE name = ?", (product_name,))
        row = c.fetchone()
    product_id = row['id']
    
    # Update price if provided
    if price is not None and price > 0:
        c.execute("UPDATE products SET price = ? WHERE id = ? AND (price IS NULL OR price = 0)", (price, product_id))
    
    # Update category if provided
    if category:
        c.execute("UPDATE products SET category = ? WHERE id = ? AND (category IS NULL OR category = '')", (category, product_id))
    
    # Insert transaction
    if not date:
        c.execute("INSERT INTO transactions (product_id, qty, type, source) VALUES (?, ?, ?, ?)",
                  (product_id, qty, txn_type, source))
    else:
        c.execute("INSERT INTO transactions (product_id, qty, type, date, source) VALUES (?, ?, ?, ?, ?)",
                  (product_id, qty, txn_type, date, source))
        
    # Update stock
    c.execute("SELECT current_qty FROM stock WHERE product_id = ?", (product_id,))
    stock_row = c.fetchone()
    current_qty = stock_row['current_qty'] if stock_row else 0
    
    new_qty = current_qty
    if txn_type == "sale":
        new_qty -= qty
    elif txn_type in ["restock", "initial"]:
        new_qty += qty
        
    if stock_row is None:
        c.execute("INSERT INTO stock (product_id, current_qty) VALUES (?, ?)", (product_id, new_qty))
    else:
        c.execute("UPDATE stock SET current_qty = ?, last_updated = CURRENT_TIMESTAMP WHERE product_id = ?",
                  (new_qty, product_id))
                  
    conn.commit()
    conn.close()
