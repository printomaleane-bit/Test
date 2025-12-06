import logging
import sqlite3
import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# LOGGING
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("Ironclad_POS")

DB_NAME = "pos_system.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    # Enforce foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ==========================================
# 1. READ MENU (With Stock Levels)
# ==========================================
@app.route('/api/menu', methods=['GET'])
def get_menu():
    conn = get_db()
    try:
        cursor = conn.cursor()
        # We send price back as Rupees (float) for display, but keep logic internal as integers
        cursor.execute("SELECT id, name, price_in_paise, category, stock FROM menu_items WHERE is_available = 1")
        rows = cursor.fetchall()
        
        menu_list = []
        for row in rows:
            menu_list.append({
                "id": row['id'],
                "name": row['name'],
                "price": row['price_in_paise'] / 100.0, # Convert back to Float for UI
                "category": row['category'],
                "stock": row['stock'] # UI needs to know if sold out
            })
        return jsonify(menu_list)
    except Exception as e:
        logger.error(f"Menu Fetch Error: {e}")
        return jsonify({"error": "System Error"}), 500
    finally:
        conn.close()

# ==========================================
# 2. IRONCLAD CHECKOUT (Atomic Transaction)
# ==========================================
@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    cart = data.get('cart', [])
    payment_mode = data.get('paymentMode', 'Cash')
    
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    conn = get_db()
    
    try:
        # START TRANSACTION (Exclusive Lock)
        # This prevents other writes while we are calculating
        conn.execute("BEGIN IMMEDIATE") 
        cursor = conn.cursor()

        total_paise = 0
        order_uuid = str(uuid.uuid4())
        
        # 1. CREATE ORDER HEADER FIRST (Pending)
        cursor.execute("""
            INSERT INTO orders (order_uuid, total_amount_in_paise, payment_mode, order_status)
            VALUES (?, 0, ?, 'PENDING')
        """, (order_uuid, payment_mode))
        
        order_db_id = cursor.lastrowid

        # 2. PROCESS ITEMS & DEDUCT STOCK
        for item in cart:
            p_id = item['id']
            qty = int(item['qty'])
            
            if qty <= 0: continue

            # CHECK STOCK & PRICE ATOMICALLY
            cursor.execute("SELECT name, price_in_paise, stock FROM menu_items WHERE id = ?", (p_id,))
            product = cursor.fetchone()

            if not product:
                raise Exception(f"Item ID {p_id} invalid.")
            
            if product['stock'] < qty:
                # ROLLBACK TRIGGER
                raise Exception(f"Stock Error: Only {product['stock']} left for {product['name']}")

            # DEDUCT STOCK
            cursor.execute("UPDATE menu_items SET stock = stock - ? WHERE id = ?", (qty, p_id))

            # CALCULATE
            line_total = product['price_in_paise'] * qty
            total_paise += line_total

            # INSERT LINE ITEM
            cursor.execute("""
                INSERT INTO order_items (order_id, menu_item_id, item_name, quantity, price_at_sale_in_paise)
                VALUES (?, ?, ?, ?, ?)
            """, (order_db_id, p_id, product['name'], qty, product['price_in_paise']))

        # 3. UPDATE ORDER TOTAL & FINALIZE
        cursor.execute("UPDATE orders SET total_amount_in_paise = ?, order_status = 'COMPLETED' WHERE id = ?", (total_paise, order_db_id))

        conn.commit() # ALL CHANGES SAVED HERE
        logger.info(f"Order #{order_db_id} processed. Total: {total_paise/100}")
        
        return jsonify({
            "success": True,
            "orderId": order_db_id,
            "total": total_paise / 100.0
        }), 201

    except Exception as e:
        conn.rollback() # UNDO EVERYTHING IF ERROR
        logger.error(f"Transaction Failed: {e}")
        return jsonify({"error": str(e)}), 409 # 409 = Conflict
    finally:
        conn.close()

if __name__ == '__main__':
    # In production, use Gunicorn. For dev, this is fine.
    app.run(host='0.0.0.0', port=5000, debug=True)