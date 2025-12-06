# setup_database.py
import sqlite3
import os

DB_PATH = "pos_system.db"

def setup_database():
    print(f"Setting up database at: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("DROP TABLE IF EXISTS expenses")
    
    # Create transactions table (EXACT structure your code expects)
    cursor.execute("""
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        item TEXT NOT NULL,
        category TEXT,
        price REAL NOT NULL,
        cost REAL NOT NULL,
        customer TEXT
    )
    """)
    
    # Create expenses table (optional)
    cursor.execute("""
    CREATE TABLE expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        expense REAL NOT NULL
    )
    """)
    
    # Insert sample transaction data
    sample_transactions = [
        ('2024-01-15', 'Pizza Margherita', 'Food', 499.99, 200.50, 'John Smith'),
        ('2024-01-15', 'Garlic Bread', 'Food', 199.99, 80.00, 'John Smith'),
        ('2024-01-16', 'Burger Deluxe', 'Food', 349.99, 150.00, 'Jane Doe'),
        ('2024-01-16', 'French Fries', 'Food', 149.99, 50.00, 'Jane Doe'),
        ('2024-01-17', 'Cappuccino', 'Drinks', 129.99, 40.00, 'Bob Wilson'),
        ('2024-01-17', 'Chocolate Cake', 'Desserts', 249.99, 100.00, 'Bob Wilson'),
        ('2024-01-18', 'Grilled Chicken', 'Food', 399.99, 180.00, 'Alice Johnson'),
        ('2024-01-19', 'Mineral Water', 'Drinks', 49.99, 15.00, 'Mike Brown'),
        ('2024-01-19', 'Pasta Alfredo', 'Food', 299.99, 120.00, 'Sarah Davis'),
    ]
    
    cursor.executemany("""
    INSERT INTO transactions (date, item, category, price, cost, customer)
    VALUES (?, ?, ?, ?, ?, ?)
    """, sample_transactions)
    
    # Insert sample expenses
    sample_expenses = [
        ('2024-01-15', 5000.00),  # Rent
        ('2024-01-15', 2000.00),  # Utilities
        ('2024-01-16', 1500.00),  # Supplies
        ('2024-01-17', 800.00),   # Marketing
    ]
    
    cursor.executemany("""
    INSERT INTO expenses (date, expense)
    VALUES (?, ?)
    """, sample_expenses)
    
    conn.commit()
    
    # Verify the data
    cursor.execute("SELECT COUNT(*) as count FROM transactions")
    trans_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as count FROM expenses")
    exp_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(price) as total_revenue FROM transactions")
    revenue = cursor.fetchone()[0]
    
    print(f"\n✅ Database setup complete!")
    print(f"   - Transactions inserted: {trans_count}")
    print(f"   - Expenses inserted: {exp_count}")
    print(f"   - Total revenue: ₹{revenue:,.2f}")
    
    # Show table structure
    print(f"\n📊 Table structure:")
    cursor.execute("PRAGMA table_info(transactions)")
    print("   transactions table columns:")
    for col in cursor.fetchall():
        print(f"     - {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    setup_database()