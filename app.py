"""
app.py
======
Flask Web Backend for Zomato Clone.
Built with Python, MySQL, and powered by Pandas & Matplotlib.

Clean user flow:
- Restaurant browsing, real-time search and category filtering (Pandas DataFrame)
- Cart calculations, GST tax and subtotal (Pandas Series)
- Order placement into local MySQL (zomato_db)
- User spending chart in My Orders (Matplotlib)
"""

import os
from flask import Flask, render_template, request, jsonify
import mysql.connector
from food_engine import (
    get_db, 
    filter_and_sort_restaurants, 
    calculate_cart_bill
)

app = Flask(__name__)

# -------------------------------------------------------------
# 1. MAIN APP ROUTES
# -------------------------------------------------------------
@app.route('/')
def home():
    """Serves the main Zomato food delivery application."""
    return render_template('index.html')

@app.route('/orders')
def orders_page():
    """Serves the simple standalone order history page."""
    return render_template('orders.html')


# -------------------------------------------------------------
# 2. RESTAURANTS & MENU APIs (POWERED BY PANDAS DATAFRAME)
# -------------------------------------------------------------
@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """
    Fetches, searches, and filters restaurants using Pandas DataFrame engine.
    Query parameters:
    - search: search text for restaurant name or cuisine
    - category: 'all', 'veg', 'Biryani', 'Pizza', 'Burgers', 'rating', etc.
    - sort: 'rating' or 'price_for_two'
    """
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', 'all').strip()
    sort_by = request.args.get('sort', 'rating').strip()

    restaurants = filter_and_sort_restaurants(
        category=category,
        search_query=search_query,
        sort_by=sort_by,
        ascending=(sort_by == 'price_for_two')
    )
    return jsonify(restaurants)


@app.route('/api/restaurants/<int:restaurant_id>/menu', methods=['GET'])
def get_restaurant_menu(restaurant_id):
    """Fetches restaurant details and its menu items."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM restaurants WHERE id = %s", (restaurant_id,))
    restaurant = cursor.fetchone()
    if restaurant and 'rating' in restaurant:
        restaurant['rating'] = float(restaurant['rating'])

    cursor.execute("SELECT * FROM menu_items WHERE restaurant_id = %s", (restaurant_id,))
    menu_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        'restaurant': restaurant,
        'menu': menu_items
    })


# -------------------------------------------------------------
# 3. CART CALCULATION API (POWERED BY PANDAS SERIES)
# -------------------------------------------------------------
@app.route('/api/cart/calculate', methods=['POST'])
def calculate_cart():
    """Calculates subtotal, delivery fee, GST tax using Pandas Series vector math."""
    data = request.get_json() or {}
    items = data.get('items', [])
    bill = calculate_cart_bill(items)
    return jsonify(bill)


# -------------------------------------------------------------
# 4. ORDER PLACEMENT & HISTORY (MYSQL + MATPLOTLIB)
# -------------------------------------------------------------
@app.route('/api/order', methods=['POST'])
def place_order():
    """Places an order and saves it into MySQL orders and order_items tables."""
    data = request.get_json() or {}
    items = data.get('items', [])
    if not items:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    customer_name = data.get('name', 'Customer').strip()
    customer_phone = data.get('phone', '9876543210').strip()
    customer_address = data.get('address', 'New Delhi').strip()
    payment_method = data.get('payment_method', 'Cash on Delivery')
    restaurant_id = data.get('restaurant_id', 1)

    # Calculate verified bill using Pandas Series engine
    bill = calculate_cart_bill(items)
    total_amount = bill['grand_total']

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Check if user exists or get user_id
        cursor.execute("SELECT id FROM users WHERE phone = %s LIMIT 1", (customer_phone,))
        user_row = cursor.fetchone()
        if user_row:
            user_id = user_row[0]
        else:
            fake_email = f"user_{customer_phone[-4:]}@zomato.com"
            cursor.execute(
                "INSERT INTO users (name, email, password, phone, address, role) VALUES (%s, %s, %s, %s, %s, %s)",
                (customer_name, fake_email, 'user123', customer_phone, customer_address, 'customer')
            )
            user_id = cursor.lastrowid

        # Insert order into orders table
        cursor.execute("""
            INSERT INTO orders (user_id, restaurant_id, total_amount, delivery_address, contact_phone, payment_method, order_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, restaurant_id, total_amount, customer_address, customer_phone, payment_method, 'Order Placed'))
        order_id = cursor.lastrowid

        # Insert each ordered item into order_items table
        for itm in items:
            cursor.execute("""
                INSERT INTO order_items (order_id, item_name, price, quantity)
                VALUES (%s, %s, %s, %s)
            """, (order_id, itm.get('name', 'Food Item'), itm.get('price', 0), itm.get('quantity', 1)))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Order placed successfully!',
            'order_id': order_id,
            'total_amount': total_amount,
            'estimated_delivery': '30-35 mins'
        })

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Fetches user's order history from MySQL including item details."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.id, o.total_amount, o.delivery_address, o.contact_phone, 
               o.payment_method, o.order_status, o.order_date, r.name AS restaurant_name,
               GROUP_CONCAT(CONCAT(oi.item_name, ' (x', oi.quantity, ')') SEPARATOR ', ') AS items_summary
        FROM orders o
        LEFT JOIN restaurants r ON o.restaurant_id = r.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        GROUP BY o.id, o.total_amount, o.delivery_address, o.contact_phone, 
                 o.payment_method, o.order_status, o.order_date, r.name
        ORDER BY o.id DESC
        LIMIT 20
    """)
    orders = cursor.fetchall()
    for o in orders:
        if o.get('order_date'):
            o['order_date'] = o['order_date'].strftime('%d %b %Y, %I:%M %p')

    cursor.close()
    conn.close()
    return jsonify(orders)


if __name__ == '__main__':
    print("=" * 55)
    print("  ZOMATO CLONE - USER WEB APP")
    print("  Running on: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True, host='127.0.0.1', port=5000)
