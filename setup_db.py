import sqlite3
import os

DB_NAME = "pos_system.db"

def init_db():
    # 1. DESTROY THE OLD WORLD (Critical Step)
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"♻️  Old '{DB_NAME}' removed. Starting fresh.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Enable Foreign Keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 2. CREATE THE NEW WORLD (New Columns)
    # Note: price_in_paise and stock are NEW columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price_in_paise INTEGER NOT NULL CHECK (price_in_paise >= 0),
        category TEXT,
        stock INTEGER NOT NULL DEFAULT 50 CHECK (stock >= 0),
        is_available INTEGER DEFAULT 1
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_uuid TEXT UNIQUE, 
        total_amount_in_paise INTEGER NOT NULL,
        payment_mode TEXT NOT NULL,
        order_status TEXT DEFAULT 'COMPLETED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        menu_item_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        price_at_sale_in_paise INTEGER NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id)
    );
    """)

    conn.commit()
    conn.close()
    print(f"✅ Ironclad Database '{DB_NAME}' initialized successfully.")

if __name__ == "__main__":
    init_db()