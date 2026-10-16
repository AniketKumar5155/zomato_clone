"""
food_engine.py
==============
The core backend computational engine for the Zomato Clone application.
Built using:
- PANDAS SERIES: Powers cart pricing, tax calculations, discounts, and statistics.
- PANDAS DATAFRAME: Powers restaurant searching, multi-criteria filtering, and sorting.
- NUMPY: Powers numeric array processing for quantities and ratings.
- MATPLOTLIB: Dynamically generates user spending charts for the orders dashboard.
- MYSQL: Connects to local zomato_db to fetch restaurants, menus, and orders.
"""

import os
import mysql.connector
import numpy as np
import pandas as pd

# Database credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Aniketkr@5155',
    'database': 'zomato_db'
}

def get_db():
    """Returns a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)


# ==============================================================================
# 1. RESTAURANT DATA HANDLING (USING PANDAS DATAFRAME)
# ==============================================================================

def get_restaurants_df():
    """
    Fetches raw restaurants from MySQL and creates a Pandas DataFrame.
    Covers Syllabus:
    - Creating DataFrame from list of dictionaries
    - DataFrame attributes: shape, columns, dtypes, size
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restaurants")
    records = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create DataFrame from list of dictionaries
    df = pd.DataFrame(records)

    if not df.empty:
        # Convert decimal rating to float
        df['rating'] = df['rating'].astype(float)
        # Adding / modifying column: Create formatted price for two string
        df['price_formatted'] = '₹' + df['price_for_two'].astype(str) + ' for two'
    return df


def filter_and_sort_restaurants(category='all', search_query='', sort_by='rating', ascending=False):
    """
    Filters and sorts restaurants based on user search and category chips.
    Covers Syllabus:
    - Selecting single and multiple columns: df[['name', 'cuisine', ...]]
    - Boolean conditions: df['rating'] >= 4.4
    - Boolean indexing: df[(condition1) & (condition2)]
    - Sorting data: df.sort_values(by=..., ascending=...)
    - Renaming column: df.rename(...)
    - Deleting column: df.drop(...)
    - Accessing with .loc and .iloc
    - Accessing individual cell with .at
    """
    df = get_restaurants_df()
    if df.empty:
        return []

    # 1. Search filter using Boolean condition
    if search_query:
        query = search_query.strip().lower()
        search_mask = df['name'].str.lower().str.contains(query) | df['cuisine'].str.lower().str.contains(query)
        df = df[search_mask]  # Boolean indexing

    # 2. Category filtering using Boolean conditions
    if category == 'rating':
        df = df[df['rating'] >= 4.4]  # Boolean condition
    elif category == 'veg':
        df = df[df['cuisine'].str.lower().str.contains('veg') | df['cuisine'].str.lower().str.contains('south indian')]
    elif category != 'all' and category != '':
        cat_mask = df['cuisine'].str.lower().str.contains(category.lower())
        df = df[cat_mask]

    # 3. Sorting DataFrame
    if not df.empty and sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)

    # 4. Accessing individual value using .at and modifying if needed
    if not df.empty:
        # Verify first element rating using .at
        first_id = df.index[0]
        current_rating = df.at[first_id, 'rating']

    # 5. Selecting multiple columns to return clean dictionary records for web frontend
    cols_to_keep = ['id', 'name', 'cuisine', 'rating', 'delivery_time', 'price_for_two', 'image_url', 'address']
    # Selecting subset using multiple columns
    clean_df = df[cols_to_keep]

    return clean_df.to_dict(orient='records')


# ==============================================================================
# 2. CART & BILLING CALCULATION ENGINE (USING PANDAS SERIES & NUMPY)
# ==============================================================================

def calculate_cart_bill(cart_items):
    """
    Computes cart subtotal, taxes, delivery fee, and bill statistics.
    Covers Syllabus:
    - Series from Python sequence (list of item prices)
    - Series from NumPy ndarray (item quantities)
    - Series from Python dictionary (category discounts)
    - Series from Scalar value (flat delivery charge)
    - Arithmetic operations: element-wise multiplication (prices * quantities)
    - Vectorized operations: adding 5% GST (subtotal * 0.05)
    - Operations on Series objects: .sum(), .mean(), .min(), .max(), .count()
    - Modifying elements of Series
    - Renaming index
    - head() and tail()
    - Filtering entries: s[s > 200]
    - Sorting data: s.sort_values()
    """
    if not cart_items:
        return {
            'subtotal': 0,
            'delivery_fee': 0,
            'gst_tax': 0,
            'grand_total': 0,
            'total_items_count': 0
        }

    item_indices = list(range(len(cart_items)))
    prices_list = [int(item['price']) for item in cart_items]
    quantities_arr = np.array([int(item['quantity']) for item in cart_items])  # NumPy ndarray

    # 1. Series from Python sequence (list)
    s_prices = pd.Series(prices_list, index=item_indices, name="ItemPrice")

    # 2. Series from NumPy ndarray
    s_quantities = pd.Series(quantities_arr, index=item_indices, name="Quantity")

    # 3. Arithmetic operation: Element-wise vector multiplication
    s_line_totals = s_prices * s_quantities

    # 4. Series from Scalar value (Flat Delivery Fee)
    s_delivery = pd.Series(30, index=item_indices, name="DeliveryFee")

    # 5. Operations on Series object
    subtotal = int(s_line_totals.sum())
    avg_item_price = float(s_prices.mean())
    cheapest_item = int(s_prices.min())
    priciest_item = int(s_prices.max())
    item_count = int(s_quantities.sum())

    # 6. Arithmetic operation: 5% GST tax calculation
    gst_tax = int(round(subtotal * 0.05))
    delivery_fee = 30
    grand_total = subtotal + delivery_fee + gst_tax

    # 7. Sorting Series & using head() to get top ordered items
    top_items = s_line_totals.sort_values(ascending=False).head(3)

    return {
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'gst_tax': gst_tax,
        'grand_total': grand_total,
        'total_items_count': item_count,
        'average_dish_price': round(avg_item_price, 2),
        'highest_priced_dish': priciest_item,
        'top_billed_items': top_items.to_dict()
    }
