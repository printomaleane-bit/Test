import sqlite3
import os

DB_NAME = "pos_system.db"

# The Master Menu Data (Hardcoded here for safety)
MENU_ITEMS = [
    # BREAKFAST
    (101, "Vada Pav", 20, "breakfast"), (102, "Samosa Pav", 22, "breakfast"),
    (103, "Kanda Poha", 25, "breakfast"), (104, "Upma", 25, "breakfast"),
    (105, "Sheera", 30, "breakfast"), (106, "Idli Sambar", 40, "breakfast"),
    (107, "Medu Vada", 45, "breakfast"), (108, "Misal Pav", 60, "breakfast"),
    (109, "Usal Pav", 50, "breakfast"), (110, "Batata Vada", 20, "breakfast"),
    (111, "Sabudana Vada", 45, "breakfast"), (112, "Sabudana Khichdi", 50, "breakfast"),
    (113, "Bun Maska", 30, "breakfast"), (114, "Masala Dosa", 70, "breakfast"),
    (115, "Sada Dosa", 50, "breakfast"), (116, "Mysore Masala", 80, "breakfast"),
    (117, "Uttapam", 70, "breakfast"), (118, "Egg Bhurji Pav", 70, "breakfast"),
    (119, "Omelette Pav", 60, "breakfast"), (120, "Bread Pakoda", 25, "breakfast"),
    (121, "Toast Sandwich", 50, "breakfast"), (122, "Veg Sandwich", 40, "breakfast"),
    (123, "Cheese Sandwich", 60, "breakfast"), (124, "Maggi", 40, "breakfast"),
    (125, "Cutting Chai", 15, "breakfast"),
    
    # LUNCH
    (201, "Veg Thali", 100, "lunch"), (202, "Chicken Thali", 150, "lunch"),
    (203, "Mini Meal", 80, "lunch"), (204, "Dal Khichdi", 90, "lunch"),
    (205, "Rajma Chawal", 100, "lunch"), (206, "Chole Bhature", 120, "lunch"),
    (207, "Veg Biryani", 120, "lunch"), (208, "Chicken Biryani", 160, "lunch"),
    (209, "Egg Biryani", 130, "lunch"), (210, "Fried Rice", 100, "lunch"),
    (211, "Schezwan Rice", 110, "lunch"), (212, "Hakka Noodles", 100, "lunch"),
    (213, "Triple Rice", 150, "lunch"), (214, "Manchurian Rice", 110, "lunch"),
    (215, "Paneer Chilli", 130, "lunch"), (216, "Chicken Chilli", 150, "lunch"),
    (217, "Puri Bhaji", 80, "lunch"), (218, "Chapati Bhaji", 60, "lunch"),
    (219, "Aloo Paratha", 70, "lunch"), (220, "Paneer Paratha", 90, "lunch"),
    (221, "Curd Rice", 80, "lunch"), (222, "Chicken Curry", 140, "lunch"),
    (223, "Egg Curry", 110, "lunch"), (224, "Veg Kadai", 120, "lunch"),
    (225, "Masala Taak", 20, "lunch"),

    # DINNER
    (301, "Pav Bhaji", 100, "dinner"), (302, "Tawa Pulao", 110, "dinner"),
    (303, "Masala Pav", 50, "dinner"), (304, "Veg Frankie", 60, "dinner"),
    (305, "Chicken Frankie", 90, "dinner"), (306, "Cheese Frankie", 80, "dinner"),
    (307, "Paneer Frankie", 80, "dinner"), (308, "Veg Burger", 70, "dinner"),
    (309, "Chicken Burger", 90, "dinner"), (310, "Veg Pizza", 120, "dinner"),
    (311, "Chicken Pizza", 150, "dinner"), (312, "Red Pasta", 130, "dinner"),
    (313, "White Pasta", 130, "dinner"), (314, "Manchow Soup", 80, "dinner"),
    (315, "Corn Soup", 80, "dinner"), (316, "Chinese Bhel", 70, "dinner"),
    (317, "Sev Puri", 50, "dinner"), (318, "Dahi Puri", 60, "dinner"),
    (319, "Ragda Pattice", 60, "dinner"), (320, "Samosa Chaat", 60, "dinner"),
    (321, "Chicken Lollipop", 140, "dinner"), (322, "Veg Crispy", 110, "dinner"),
    (323, "Cold Coffee", 60, "dinner"), (324, "Milkshake", 80, "dinner"),
    (325, "Ice Cream", 40, "dinner")
]

def seed_data():
    if not os.path.exists(DB_NAME):
        print(f"❌ Error: Database '{DB_NAME}' not found. Run setup_db.py first.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    count = 0
    print("🌱 Seeding data...")
    
    for item in MENU_ITEMS:
        item_id, name, price, category = item
        
        # Convert Rupees to Paise (Integer)
        price_in_paise = int(price * 100)
        initial_stock = 50 

        cursor.execute("""
            INSERT OR REPLACE INTO menu_items (id, name, price_in_paise, category, stock, is_available)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (item_id, name, price_in_paise, category, initial_stock))
        count += 1

    conn.commit()
    conn.close()
    print(f"✅ Success: {count} menu items loaded. Stocks reset to 50.")

if __name__ == "__main__":
    seed_data()