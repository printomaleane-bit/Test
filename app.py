# unified_app.py
from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
from collections import defaultdict
from statistics import mean

app = Flask(__name__)
CORS(app)

# ========== BUSINESS STATS FUNCTIONS ==========
def _ensure_date(value):
    """Convert various date formats to date object"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except:
                continue
    return None

def load_transactions_from_db(db_path: str):
    """Load transactions from SQLite database"""
    transactions = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(transactions)")
        cols = [r["name"] for r in cur.fetchall()]
        
        required = ["date", "item", "category", "price", "cost", "customer"]
        select_cols = [(c if c in cols else f"NULL as {c}") for c in required]
        
        q = f"SELECT {', '.join(select_cols)} FROM transactions ORDER BY date ASC"
        
        for r in cur.execute(q):
            raw_date = r["date"]
            d = _ensure_date(raw_date)
            if d is None:
                continue
            
            transactions.append({
                "date": d,
                "item": (r["item"] or "").strip(),
                "category": (r["category"] or "Uncategorized").strip(),
                "price": float(r["price"] or 0),
                "cost": float(r["cost"] or 0),
                "customer": (r["customer"] or "Anonymous").strip()
            })
        conn.close()
    except Exception as e:
        print(f"Error loading transactions: {e}")
    
    return transactions

def load_expenses_from_db(db_path: str):
    """Load expenses from SQLite database"""
    expenses = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(expenses)")
        cols = [r["name"] for r in cur.fetchall()]
        if not cols:
            conn.close()
            return []
        
        select_cols = [(c if c in cols else f"NULL as {c}") for c in ("date", "expense")]
        q = f"SELECT {', '.join(select_cols)} FROM expenses ORDER BY date ASC"
        
        for r in cur.execute(q):
            d = _ensure_date(r["date"])
            if d is None:
                continue
            expenses.append({"date": d, "expense": float(r["expense"] or 0)})
        conn.close()
    except Exception:
        return []
    
    return expenses

def compute_business_stats(transactions, expenses):
    """Compute business statistics"""
    total_revenue = sum(t["price"] for t in transactions)
    total_cost = sum(t["cost"] for t in transactions)
    total_expenses = sum(e.get("expense", 0) for e in expenses)

    net_profit = total_revenue - total_cost - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue else 0.0
    avg_order_value = mean([t["price"] for t in transactions]) if transactions else 0.0

    # revenue over time (monthly)
    monthly = defaultdict(float)
    for t in transactions:
        key = t["date"].strftime("%Y-%m")
        monthly[key] += t["price"]
    period_labels = sorted(monthly.keys())
    period_values = [monthly[k] for k in period_labels]

    # revenue by category
    revenue_by_category = defaultdict(float)
    for t in transactions:
        revenue_by_category[t["category"]] += t["price"]

    # top products by profit
    product_map = defaultdict(lambda: {"rev": 0.0, "cost": 0.0})
    for t in transactions:
        product_map[t["item"]]["rev"] += t["price"]
        product_map[t["item"]]["cost"] += t["cost"]

    top_products = []
    for name, d in product_map.items():
        rev = d["rev"]
        cost = d["cost"]
        profit = rev - cost
        margin = (profit / rev * 100) if rev else 0.0
        top_products.append({
            "name": name,
            "revenue": rev,
            "profit": profit,
            "margin": margin
        })
    top_products = sorted(top_products, key=lambda x: x["profit"], reverse=True)[:20]

    # top customers by spend
    customer_map = defaultdict(float)
    for t in transactions:
        customer_map[t["customer"]] += t["price"]
    top_customers = [{"name": n, "spend": s} for n, s in customer_map.items()]
    top_customers = sorted(top_customers, key=lambda x: x["spend"], reverse=True)[:12]

    return {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "profit_margin": profit_margin,
        "avg_order_value": avg_order_value,
        "period_labels": period_labels,
        "period_values": period_values,
        "revenue_by_category": dict(revenue_by_category),
        "top_products": top_products,
        "top_customers": top_customers
    }

# ========== ROUTES ==========
DB_PATH = "pos_system.db"

@app.route("/api/business_stats")
def api_business_stats():
    """Business stats API endpoint"""
    if not os.path.exists(DB_PATH):
        return jsonify({"error": "Database not found", "path": DB_PATH}), 500
    
    try:
        transactions = load_transactions_from_db(DB_PATH)
        expenses = load_expenses_from_db(DB_PATH)
        stats = compute_business_stats(transactions, expenses)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    """Serve the dashboard HTML"""
    if os.path.exists("business_dashboard.html"):
        return send_file("business_dashboard.html")
    else:
        return f"""
        <h1>Business Dashboard</h1>
        <p>HTML file not found. Testing API:</p>
        <p><a href="/api/business_stats">/api/business_stats</a></p>
        """

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "api": "http://127.0.0.1:5500/api/business_stats",
        "dashboard": "http://127.0.0.1:5500/",
        "database_exists": os.path.exists(DB_PATH)
    })

if __name__ == "__main__":
    print("Starting unified business dashboard on port 5000")
    print("Dashboard: http://127.0.0.1:5400/")
    print("API: http://127.0.0.1:5500/api/business_stats")
    print("Health: http://127.0.0.1:5400/health")
    app.run(debug=True, host="0.0.0.0", port=5000)