import sqlite3

def init_db():
    conn = sqlite3.connect('foodiq.db')
    c = conn.cursor()

    # 1. MENU (The Reference)
    c.execute('''CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')

    # 2. THRESHOLD RULES (The Logic)
    # If we have more than 'warn_limit' kgs, 'auto_notify' turns on.
    c.execute('''CREATE TABLE IF NOT EXISTS threshold_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT REFERENCES menu_items(name),
        warn_limit REAL NOT NULL, 
        auto_notify BOOLEAN DEFAULT 1,
        UNIQUE(item_name)
    )''')

    # 3. SURPLUS LISTINGS (The Output)
    c.execute('''CREATE TABLE IF NOT EXISTS surplus_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        qty_kg REAL,
        lat REAL, 
        lng REAL,
        is_urgent BOOLEAN DEFAULT 0,
        status TEXT DEFAULT 'AVAILABLE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Seed Data
    c.execute("INSERT OR IGNORE INTO menu_items (name) VALUES ('Rice')")
    c.execute("INSERT OR IGNORE INTO menu_items (name) VALUES ('Dal')")
    
    # DEFAULT RULE: If Rice > 10kg, it is Urgent.
    c.execute("INSERT OR IGNORE INTO threshold_configs (item_name, warn_limit) VALUES ('Rice', 10)")

    conn.commit()
    conn.close()
    print("✅ Database Architected.")

if __name__ == '__main__':
    init_db()