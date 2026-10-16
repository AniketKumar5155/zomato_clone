"""
database_setup.py
------------------
Sets up the MySQL database 'zomato_db' and creates sample tables:
1. restaurants
2. food_items
3. orders

Run this script once to initialize or reset your database.
"""

import mysql.connector
from mysql.connector import Error

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Aniketkr@5155'
}

DB_NAME = 'zomato_db'

def get_connection(use_database=True):
    config = DB_CONFIG.copy()
    if use_database:
        config['database'] = DB_NAME
    return mysql.connector.connect(**config)

def setup_database():
    try:
        # Step 1: Connect to MySQL server and create database if not exists
        conn = get_connection(use_database=False)
        cursor = conn.cursor()
        print(f"[*] Connecting to MySQL Server...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"[+] Database '{DB_NAME}' created or verified successfully.")
        cursor.close()
        conn.close()

        # Step 2: Connect to zomato_db and create tables
        conn = get_connection(use_database=True)
        cursor = conn.cursor()

        # 1. Restaurants table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            cuisine VARCHAR(100) NOT NULL,
            rating FLOAT NOT NULL,
            delivery_time VARCHAR(20) NOT NULL,
            cost_for_two INT NOT NULL,
            image_url VARCHAR(255),
            address VARCHAR(150)
        )
        """)
        print("[+] 'restaurants' table ready.")

        # 2. Food Items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            restaurant_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            price INT NOT NULL,
            is_veg TINYINT(1) DEFAULT 1,
            rating FLOAT NOT NULL,
            description VARCHAR(255),
            image_url VARCHAR(255),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
        )
        """)
        print("[+] 'food_items' table ready.")

        # 3. Orders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            customer_phone VARCHAR(20) NOT NULL,
            delivery_address VARCHAR(200) NOT NULL,
            items_summary TEXT NOT NULL,
            total_amount INT NOT NULL,
            payment_mode VARCHAR(50) DEFAULT 'Cash on Delivery',
            order_status VARCHAR(50) DEFAULT 'Delivered',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("[+] 'orders' table ready.")

        # Step 3: Populate sample restaurants if empty
        cursor.execute("SELECT COUNT(*) FROM restaurants")
        restaurant_count = cursor.fetchone()[0]

        if restaurant_count == 0:
            print("[*] Inserting sample restaurants and menu items...")
            restaurants_data = [
                ("Biryani By Kilo", "Biryani, North Indian", 4.4, "30-35 mins", 600,
                 "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=500&auto=format&fit=crop&q=60", "Connaught Place, New Delhi"),
                ("Pizza Hut", "Pizza, Fast Food, Italian", 4.2, "25-30 mins", 450,
                 "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60", "Sector 18, Noida"),
                ("Haldiram's Sweets & Thali", "North Indian, Street Food, Mithai", 4.5, "20-25 mins", 350,
                 "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500&auto=format&fit=crop&q=60", "Lajpat Nagar, New Delhi"),
                ("Burger King", "Burgers, Fast Food, Beverages", 4.1, "20-30 mins", 300,
                 "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60", "Mall Road, Delhi"),
                ("Sagar Ratna", "South Indian, Dosa, Filter Coffee", 4.3, "25-35 mins", 400,
                 "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=500&auto=format&fit=crop&q=60", "Defence Colony, New Delhi"),
                ("Keventers - Milkshakes", "Beverages, Desserts, Shakes", 4.6, "15-20 mins", 250,
                 "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&auto=format&fit=crop&q=60", "Saket, New Delhi")
            ]

            cursor.executemany("""
            INSERT INTO restaurants (name, cuisine, rating, delivery_time, cost_for_two, image_url, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, restaurants_data)
            conn.commit()

            # Food items mapping (restaurant_id 1 to 6)
            food_items_data = [
                # Biryani By Kilo (ID 1)
                (1, "Hyderabadi Dum Biryani", "Biryani", 320, 0, 4.6, "Aromatic basmati rice cooked with spiced chicken in handi.", "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop&q=60"),
                (1, "Paneer Dum Biryani", "Biryani", 280, 1, 4.3, "Fresh paneer marinated in royal spices layered with saffron rice.", "https://images.unsplash.com/photo-1642821373181-696a54913e9a?w=500&auto=format&fit=crop&q=60"),
                (1, "Galouti Kebab (4 pcs)", "Starters", 290, 0, 4.5, "Melt-in-mouth spiced kebabs served with mint chutney.", "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=500&auto=format&fit=crop&q=60"),

                # Pizza Hut (ID 2)
                (2, "Margherita Cheese Pizza", "Pizza", 220, 1, 4.2, "Classic mozzarella cheese and fresh basil tomato sauce.", "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?w=500&auto=format&fit=crop&q=60"),
                (2, "Farmhouse Veg Delight", "Pizza", 340, 1, 4.4, "Capsicum, onion, grilled mushrooms, and fresh paneer.", "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60"),
                (2, "Garlic Breadsticks", "Sides", 140, 1, 4.1, "Freshly baked breadsticks seasoned with garlic butter.", "https://images.unsplash.com/photo-1619535860434-ba1d8fa12536?w=500&auto=format&fit=crop&q=60"),

                # Haldiram's (ID 3)
                (3, "Special Chole Bhature", "North Indian", 160, 1, 4.7, "2 fluffy bhature served with pindi chole and tangy pickle.", "https://images.unsplash.com/photo-1626132647523-66f5bf380027?w=500&auto=format&fit=crop&q=60"),
                (3, "Pav Bhaji Deluxe", "Street Food", 150, 1, 4.5, "Spicy mashed butter vegetables served with toasted butter pav.", "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=500&auto=format&fit=crop&q=60"),
                (3, "Gulab Jamun (2 pcs)", "Mithai", 80, 1, 4.8, "Hot soft gulab jamun soaked in cardamom flavored sugar syrup.", "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop&q=60"),

                # Burger King (ID 4)
                (4, "Crispy Veg Whopper", "Burgers", 170, 1, 4.2, "Crispy sesame bun, crunchy patty, lettuce, mayo and onions.", "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60"),
                (4, "Crispy Chicken Burger", "Burgers", 199, 0, 4.3, "Juicy fried chicken patty with smoked chili sauce.", "https://images.unsplash.com/photo-1550547660-d9450f859349?w=500&auto=format&fit=crop&q=60"),
                (4, "Peri Peri French Fries", "Sides", 110, 1, 4.0, "Golden french fries tossed in spicy peri-peri mix.", "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=500&auto=format&fit=crop&q=60"),

                # Sagar Ratna (ID 5)
                (5, "Masala Dosa with Sambar", "South Indian", 180, 1, 4.6, "Crispy golden crepe with potato masala and fresh coconut chutney.", "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=500&auto=format&fit=crop&q=60"),
                (5, "Steamed Idli (2 pcs)", "South Indian", 100, 1, 4.3, "Steamed rice cakes served piping hot with lentil stew.", "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop&q=60"),
                (5, "South Indian Filter Coffee", "Beverages", 70, 1, 4.8, "Authentic decoction brewed filter coffee with frothy milk.", "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500&auto=format&fit=crop&q=60"),

                # Keventers (ID 6)
                (6, "Chocolate Oreo Milkshake", "Beverages", 210, 1, 4.7, "Rich thick shake made with crushed Oreos and dairy cream.", "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=500&auto=format&fit=crop&q=60"),
                (6, "Strawberry Delight Shake", "Beverages", 190, 1, 4.4, "Sweet strawberry thick shake served in signature glass bottle.", "https://images.unsplash.com/photo-1541658016709-82535e94bc69?w=500&auto=format&fit=crop&q=60")
            ]

            cursor.executemany("""
            INSERT INTO food_items (restaurant_id, name, category, price, is_veg, rating, description, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, food_items_data)
            conn.commit()

        # Step 4: Populate sample orders if empty (needed for Pandas DataFrame & Series analysis!)
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]

        if order_count == 0:
            print("[*] Inserting sample orders for Data Analysis and Matplotlib...")
            sample_orders = [
                ("Rohan Sharma", "9876543210", "A-12, Green Park, New Delhi", "Hyderabadi Dum Biryani (x2)", 640, "UPI", "Delivered"),
                ("Priya Verma", "9811223344", "Flat 402, Mayur Vihar, Delhi", "Margherita Cheese Pizza (x1), Garlic Breadsticks (x1)", 360, "Credit Card", "Delivered"),
                ("Amit Patel", "9822334455", "H-15, Rajouri Garden, Delhi", "Special Chole Bhature (x2), Gulab Jamun (x1)", 400, "Cash on Delivery", "Delivered"),
                ("Sneha Roy", "9833445566", "B-7, Saket, New Delhi", "Crispy Veg Whopper (x2), Peri Peri French Fries (x1)", 450, "UPI", "Delivered"),
                ("Vikram Singh", "9844556677", "Pocket 2, Dwarka, Delhi", "Masala Dosa with Sambar (x2), Filter Coffee (x2)", 500, "Cash on Delivery", "Delivered"),
                ("Ananya Gupta", "9855667788", "C-33, Noida Sector 62", "Chocolate Oreo Milkshake (x2)", 420, "UPI", "Delivered"),
                ("Karan Kapoor", "9866778899", "Villa 9, Greater Kailash, Delhi", "Hyderabadi Dum Biryani (x1), Galouti Kebab (x1)", 610, "Debit Card", "Delivered"),
                ("Pooja Nair", "9877889900", "Tower 3, Gurugram Phase 5", "Farmhouse Veg Delight (x1), Peri Peri French Fries (x1)", 450, "UPI", "Delivered"),
                ("Rahul Mehta", "9888990011", "D-4, Model Town, Delhi", "Pav Bhaji Deluxe (x2), Gulab Jamun (x2)", 460, "Cash on Delivery", "Delivered"),
                ("Divya Joshi", "9899001122", "Flat 101, Indirapuram, Ghaziabad", "Crispy Chicken Burger (x2), Chocolate Oreo Milkshake (x1)", 608, "UPI", "Delivered")
            ]

            cursor.executemany("""
            INSERT INTO orders (customer_name, customer_phone, delivery_address, items_summary, total_amount, payment_mode, order_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, sample_orders)
            conn.commit()

        cursor.close()
        conn.close()
        print("[SUCCESS] MySQL database 'zomato_db' setup completed successfully!")

    except Error as e:
        print(f"[!] Error setting up database: {e}")

if __name__ == '__main__':
    setup_database()
