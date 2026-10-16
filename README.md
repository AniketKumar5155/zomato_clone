# Zomato Clone

A clean, responsive food delivery web application built with **HTML, CSS, JavaScript**, **Python (Flask)**, and **MySQL**, powered under the hood by **Pandas (Series & DataFrame)**, **NumPy**, and **Matplotlib**.

---

## 📁 Project Architecture

```
b:\Catastrophy\zomato_clone_3\
├── app.py               # Flask application & REST API routes
├── food_engine.py       # Core computational engine (Pandas DataFrame, Series & Matplotlib)
├── database_setup.py    # MySQL database setup and seed data script
├── templates/
│   ├── index.html       # Clean Zomato food delivery user interface
│   └── orders.html      # Simple standalone order history page
├── static/
│   ├── css/
│   │   └── style.css    # Responsive styling & Zomato branding
│   └── js/
│       └── app.js       # Client interaction, cart management & checkout
└── README.md
```

---

## 🔧 How the Technologies are Used

### 1. Pandas DataFrame (in `food_engine.py`)
- **Data Loading**: Loads restaurant records from MySQL into a structured DataFrame (`df_restaurants`).
- **Searching & Filtering**: Uses **Boolean Indexing** and compound boolean conditions (`df[(df['rating'] >= 4.4) & (...)]`) to filter restaurants by cuisine, pure veg, and ratings.
- **Sorting**: Powers multi-column sorting (e.g., sorting by rating descending or price for two ascending).
- **Column Operations**: Selects single/multiple columns, adds formatted pricing columns, uses `.at` for fast cell access, and `.loc` / `.iloc` for slicing.

### 2. Pandas Series (in `food_engine.py`)
- **Cart Calculations**: Takes cart item prices as a **Series from Python sequence**, and quantities as a **Series from NumPy ndarray**.
- **Vectorized Math**: Calculates line item subtotals (`s_prices * s_quantities`) and applies 5% GST taxes (`subtotal * 0.05`).
- **Statistical Aggregation**: Computes order statistics using `.sum()`, `.mean()`, `.min()`, and `.max()`.
- **Top Dishes Ranking**: Uses `.sort_values()` and `.head()` to identify top ordered dishes.

### 3. MySQL Database (`zomato_db`)
- Stores 12 restaurants, 57 menu items, user profiles, and records orders with itemized breakdowns.

---

## 🚀 How to Run

1. **Start the Flask Server**:
   ```bash
   python app.py
   ```

2. **Open in Browser**:
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)
