import os
from flask import Blueprint, jsonify, current_app
from business_stats import load_transactions_from_db, load_expenses_from_db, compute_business_stats

business_bp = Blueprint("business", __name__)

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "pos_system.db")   # ensure pos_system.db is here

@business_bp.route("/api/business_stats")
def api_business_stats():
    """
    Returns the same JSON structure the UI expects.
    """
    if not os.path.exists(DB_PATH):
        current_app.logger.error("pos_system.db not found at %s", DB_PATH)
        return jsonify({"error": "pos_system.db not found", "details": f"Expected at {DB_PATH}"}), 500

    try:
        transactions = load_transactions_from_db(DB_PATH)
    except Exception as e:
        current_app.logger.exception("Failed to load transactions from DB")
        return jsonify({"error": "Failed to load transactions from DB", "details": str(e)}), 500

    try:
        expenses = load_expenses_from_db(DB_PATH)
    except Exception:
        expenses = []

    stats = compute_business_stats(transactions, expenses)
    return jsonify(stats)
