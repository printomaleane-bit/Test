import sqlite3
import math
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db():
    conn = sqlite3.connect('foodiq.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- LOGIC UTILITY: HAVERSINE DISTANCE ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- ENDPOINT 1: THE DECISION ENGINE ---
@app.route('/api/wastage', methods=['POST'])
def report_wastage():
    # Input: { "item": "Rice", "qty": 15, "lat": 19.1, "lng": 72.8 }
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    try:
        # STEP 1: CHECK THE RULE
        # We look up if this item has a threshold configuration
        cursor.execute("SELECT warn_limit, auto_notify FROM threshold_configs WHERE item_name = ?", (data['item'],))
        rule = cursor.fetchone()

        is_urgent = False
        message = "Surplus Logged."

        # STEP 2: EVALUATE CONDITION
        if rule:
            limit = rule['warn_limit']
            # LOGIC: If input qty is greater than limit, Trigger Alert
            if float(data['qty']) >= limit and rule['auto_notify']:
                is_urgent = True
                message = f"URGENT: {data['item']} exceeds {limit}kg limit. NGOs notified."

        # STEP 3: EXECUTE ACTION (Save to DB)
        cursor.execute('''
            INSERT INTO surplus_listings (item_name, qty_kg, lat, lng, is_urgent)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['item'], data['qty'], data.get('lat', 19.1), data.get('lng', 72.8), is_urgent))

        conn.commit()
        
        # Return the decision to the frontend so it knows what happened
        return jsonify({
            "success": True,
            "decision": "BROADCAST" if is_urgent else "LOG_ONLY",
            "message": message
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# --- ENDPOINT 2: THE NGO FEED (FILTERED BY DISTANCE) ---
@app.route('/api/ngo/feed', methods=['GET'])
def get_feed():
    # Input params: ?lat=19.2&lng=72.9 (NGO's location)
    ngo_lat = float(request.args.get('lat', 19.1))
    ngo_lng = float(request.args.get('lng', 72.8))

    conn = get_db()
    # Get all available food
    rows = conn.execute("SELECT * FROM surplus_listings WHERE status='AVAILABLE' ORDER BY is_urgent DESC, created_at DESC").fetchall()
    conn.close()

    results = []
    for row in rows:
        item = dict(row)
        # Calculate Distance dynamically
        dist = calculate_distance(ngo_lat, ngo_lng, item['lat'], item['lng'])
        
        # LOGIC: Only show items within 10km radius (Optional constraint)
        if dist <= 15: 
            item['distance_km'] = round(dist, 1)
            results.append(item)

    return jsonify(results)

# --- ENDPOINT 3: SET THRESHOLDS (Manager Config) ---
@app.route('/api/thresholds', methods=['POST'])
def set_threshold():
    # Input: { "item": "Rice", "limit": 20 }
    data = request.json
    conn = get_db()
    conn.execute('''
        INSERT INTO threshold_configs (item_name, warn_limit) 
        VALUES (?, ?)
        ON CONFLICT(item_name) DO UPDATE SET warn_limit=excluded.warn_limit
    ''', (data['item'], data['limit']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    print("⚡ Ironclad Backend Logic Active on Port 5000")
    app.run(debug=True, port=5000)

    import sqlite3
import math
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enables the HTML to talk to Python

def get_db():
    conn = sqlite3.connect('foodiq.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- 1. SET RULES (Thresholds) ---
@app.route('/api/thresholds', methods=['POST'])
def set_threshold():
    data = request.json
    conn = get_db()
    # Upsert: Create rule if new, update if exists
    conn.execute('''
        INSERT INTO threshold_configs (item_name, warn_limit) 
        VALUES (?, ?)
        ON CONFLICT(item_name) DO UPDATE SET warn_limit=excluded.warn_limit
    ''', (data['item'], data['limit']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# --- 2. REPORT WASTAGE (The Decision Engine) ---
@app.route('/api/wastage', methods=['POST'])
def report_wastage():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    # A. Check if Rule Exists
    cursor.execute("SELECT warn_limit, auto_notify FROM threshold_configs WHERE item_name = ?", (data['item'],))
    rule = cursor.fetchone()

    is_urgent = False
    message = "Standard Listing Created."

    # B. Compare Quantity vs Threshold
    if rule:
        limit = rule['warn_limit']
        if float(data['qty']) >= limit:
            is_urgent = True
            message = f"URGENT ALERT: {data['item']} exceeds {limit}kg limit!"

    # C. Save to Database
    cursor.execute('''
        INSERT INTO surplus_listings (item_name, qty_kg, lat, lng, is_urgent)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['item'], data['qty'], data.get('lat', 19.1), data.get('lng', 72.8), is_urgent))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True, 
        "decision": "BROADCAST" if is_urgent else "LOG_ONLY",
        "message": message
    })

# --- 3. NGO FEED (View Data) ---
@app.route('/api/ngo/feed', methods=['GET'])
def get_feed():
    conn = get_db()
    # Fetch all items, sort Urgent ones to the top
    rows = conn.execute("SELECT * FROM surplus_listings WHERE status='AVAILABLE' ORDER BY is_urgent DESC, id DESC").fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append(dict(row)) # Convert DB row to JSON object

    return jsonify(results)

# --- 4. CLAIM FOOD ---
@app.route('/api/ngo/claim', methods=['POST'])
def claim_food():
    data = request.json
    conn = get_db()
    conn.execute("UPDATE surplus_listings SET status='CLAIMED' WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "pickup_code": "PICK-99"})

if __name__ == '__main__':
    print("🚀 Server Running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)