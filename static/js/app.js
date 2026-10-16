/**
 * Zomato Clone - Frontend JavaScript
 * Simple, clean vanilla JS for restaurant browsing, cart, checkout, and orders.
 */

// Global State
let currentCategory = 'all';
let currentSearch = '';
let currentSort = 'rating';
let cart = []; // Array of { id, name, price, quantity, restaurant_id }
let currentRestaurant = null;

// ----------------------------------------------------------------
// 1. INITIAL LOAD & EVENT LISTENERS
// ----------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    fetchAndRenderRestaurants();
    setupEventListeners();
});

function setupEventListeners() {
    // Search input filtering (debounced)
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let timeout = null;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                currentSearch = e.target.value.trim();
                fetchAndRenderRestaurants();
            }, 250);
        });
    }

    // Category filter chips
    const filterChips = document.querySelectorAll('.filter-chip');
    filterChips.forEach(chip => {
        chip.addEventListener('click', () => {
            filterChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            currentCategory = chip.getAttribute('data-category');
            fetchAndRenderRestaurants();
        });
    });

    // Checkout form submission
    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', handleCheckoutSubmit);
    }
}

function applySorting(sortVal) {
    currentSort = sortVal;
    fetchAndRenderRestaurants();
}

// ----------------------------------------------------------------
// 2. FETCH & RENDER RESTAURANTS (POWERED BY PANDAS DATAFRAME)
// ----------------------------------------------------------------
async function fetchAndRenderRestaurants() {
    const grid = document.getElementById('restaurantGrid');
    if (!grid) return;

    try {
        const url = `/api/restaurants?category=${encodeURIComponent(currentCategory)}&search=${encodeURIComponent(currentSearch)}&sort=${encodeURIComponent(currentSort)}`;
        const response = await fetch(url);
        const restaurants = await response.json();

        if (restaurants.length === 0) {
            grid.innerHTML = '<p style="grid-column: 1/-1; text-align:center; padding: 40px; color:#888;">No restaurants found matching your criteria.</p>';
            return;
        }

        grid.innerHTML = restaurants.map(r => `
            <div class="restaurant-card" onclick="openRestaurantMenu(${r.id})">
                <div class="card-img-wrapper">
                    <img src="${r.image_url || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500'}" alt="${r.name}" loading="lazy">
                    <span class="delivery-badge">${r.delivery_time || '25-30 mins'}</span>
                </div>
                <div class="card-content">
                    <div class="card-header">
                        <h3 class="card-title">${r.name}</h3>
                        <span class="rating-badge">${parseFloat(r.rating).toFixed(1)} ★</span>
                    </div>
                    <p class="cuisine-text">${r.cuisine}</p>
                    <div class="card-footer">
                        <span>₹${r.price_for_two || 350} for two</span>
                        <span style="color:#24963F; font-weight:600;">Free Delivery</span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error fetching restaurants:', error);
        grid.innerHTML = '<p style="color:red; text-align:center;">Failed to load restaurants.</p>';
    }
}

// ----------------------------------------------------------------
// 3. RESTAURANT MENU MODAL
// ----------------------------------------------------------------
async function openRestaurantMenu(restaurantId) {
    try {
        const response = await fetch(`/api/restaurants/${restaurantId}/menu`);
        const data = await response.json();
        currentRestaurant = data.restaurant;

        document.getElementById('menuRestaurantName').textContent = currentRestaurant.name;
        document.getElementById('menuRestaurantCuisine').textContent = currentRestaurant.cuisine;
        document.getElementById('menuRestaurantRating').textContent = `${parseFloat(currentRestaurant.rating).toFixed(1)} ★`;

        const menuListContainer = document.getElementById('menuItemsList');
        if (!data.menu || data.menu.length === 0) {
            menuListContainer.innerHTML = '<p style="padding:20px; color:#777;">No dishes currently listed for this restaurant.</p>';
        } else {
            menuListContainer.innerHTML = data.menu.map(item => {
                const inCart = cart.find(c => c.id === item.id);
                const qty = inCart ? inCart.quantity : 0;
                
                return `
                <div class="menu-item-row">
                    <div class="item-info">
                        <span class="${item.is_veg ? 'veg-icon' : 'non-veg-icon'}"></span>
                        <h4 class="item-name">${item.item_name}</h4>
                        <div class="item-price">₹${item.price}</div>
                        <p class="item-desc">${item.description || 'Delicious freshly prepared specialty dish.'}</p>
                    </div>
                    <div class="item-action">
                        ${item.image_url ? `<img src="${item.image_url}" alt="${item.item_name}">` : ''}
                        <div id="btn-wrap-${item.id}">
                            ${qty > 0 ? `
                                <div class="qty-control">
                                    <button class="qty-btn" onclick="updateItemQty(${item.id}, -1)">−</button>
                                    <span class="qty-num">${qty}</span>
                                    <button class="qty-btn" onclick="updateItemQty(${item.id}, 1)">+</button>
                                </div>
                            ` : `
                                <button class="add-btn" onclick="addItemToCart(${item.id}, '${escapeQuotes(item.item_name)}', ${item.price}, ${restaurantId})">+ ADD</button>
                            `}
                        </div>
                    </div>
                </div>
                `;
            }).join('');
        }

        document.getElementById('menuModal').style.display = 'flex';
    } catch (error) {
        console.error('Error opening menu:', error);
        alert('Could not fetch menu items.');
    }
}

function closeMenuModal() {
    document.getElementById('menuModal').style.display = 'none';
}

function escapeQuotes(str) {
    return str.replace(/'/g, "\\'");
}

// ----------------------------------------------------------------
// 4. CART & QUANTITY MANAGEMENT
// ----------------------------------------------------------------
function addItemToCart(id, name, price, restaurantId) {
    if (cart.length > 0 && cart[0].restaurant_id !== restaurantId) {
        if (!confirm('Your cart contains items from a different restaurant. Would you like to reset your cart to order from this restaurant?')) {
            return;
        }
        cart = [];
    }

    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ id, name, price, quantity: 1, restaurant_id: restaurantId });
    }

    updateCartBadge();
    refreshItemButton(id);
}

function updateItemQty(id, delta) {
    const itemIndex = cart.findIndex(i => i.id === id);
    if (itemIndex > -1) {
        cart[itemIndex].quantity += delta;
        if (cart[itemIndex].quantity <= 0) {
            cart.splice(itemIndex, 1);
        }
    }
    updateCartBadge();
    refreshItemButton(id);
    renderCartModalItems();
}

function refreshItemButton(id) {
    const wrap = document.getElementById(`btn-wrap-${id}`);
    if (!wrap) return;

    const inCart = cart.find(c => c.id === id);
    const qty = inCart ? inCart.quantity : 0;

    if (qty > 0) {
        wrap.innerHTML = `
            <div class="qty-control">
                <button class="qty-btn" onclick="updateItemQty(${id}, -1)">−</button>
                <span class="qty-num">${qty}</span>
                <button class="qty-btn" onclick="updateItemQty(${id}, 1)">+</button>
            </div>
        `;
    } else {
        const itemRow = wrap.closest('.menu-item-row');
        const name = itemRow.querySelector('.item-name').textContent;
        const priceText = itemRow.querySelector('.item-price').textContent.replace('₹', '');
        const price = parseInt(priceText, 10);
        const restId = currentRestaurant ? currentRestaurant.id : 1;

        wrap.innerHTML = `
            <button class="add-btn" onclick="addItemToCart(${id}, '${escapeQuotes(name)}', ${price}, ${restId})">+ ADD</button>
        `;
    }
}

function updateCartBadge() {
    const totalQty = cart.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
    const subtotal = cart.reduce((sum, item) => sum + (Number(item.price || 0) * Number(item.quantity || 0)), 0);
    const deliveryFee = totalQty > 0 ? 30 : 0;
    const gstTax = Math.round(subtotal * 0.05);
    const grandTotal = subtotal + deliveryFee + gstTax;

    // Update navbar Cart button
    const cartNavBtn = document.getElementById('cartNavBtn');
    if (cartNavBtn) {
        if (totalQty > 0) {
            cartNavBtn.innerHTML = `🛒 Cart <span class="cart-badge">${totalQty}</span> <span style="font-weight:700; margin-left:6px; background:rgba(255,255,255,0.2); padding:2px 7px; border-radius:6px;">₹${grandTotal}</span>`;
        } else {
            cartNavBtn.innerHTML = `🛒 Cart <span class="cart-badge">0</span>`;
        }
    } else {
        const badge = document.getElementById('cartBadge');
        if (badge) badge.textContent = totalQty;
    }

    // Update bottom floating cart bar
    const floatBar = document.getElementById('floatingCartBar');
    const floatText = document.getElementById('floatCartText');
    if (floatBar && floatText) {
        if (totalQty > 0) {
            floatText.textContent = `${totalQty} item${totalQty > 1 ? 's' : ''} added • ₹${grandTotal}`;
            floatBar.style.display = 'flex';
        } else {
            floatBar.style.display = 'none';
        }
    }
}

// ----------------------------------------------------------------
// 5. CART MODAL & BILL CALCULATIONS (POWERED BY PANDAS SERIES API)
// ----------------------------------------------------------------
function openCartModal() {
    renderCartModalItems();
    document.getElementById('cartModal').style.display = 'flex';
}

function closeCartModal() {
    document.getElementById('cartModal').style.display = 'none';
}

async function renderCartModalItems() {
    const container = document.getElementById('cartItemsContainer');
    const emptyMsg = document.getElementById('cartEmptyMsg');
    const billBox = document.getElementById('billDetailsBox');
    const formBox = document.getElementById('checkoutForm');

    if (cart.length === 0) {
        if (container) container.innerHTML = '';
        if (emptyMsg) emptyMsg.style.display = 'block';
        if (billBox) billBox.style.display = 'none';
        if (formBox) formBox.style.display = 'none';
        return;
    }

    if (emptyMsg) emptyMsg.style.display = 'none';
    if (billBox) billBox.style.display = 'block';
    if (formBox) formBox.style.display = 'block';

    // 1. Render item rows with line amounts
    container.innerHTML = cart.map(item => {
        const itemPrice = Number(item.price || 0);
        const itemQty = Number(item.quantity || 1);
        const lineTotal = itemPrice * itemQty;
        return `
            <div class="cart-item-row">
                <div>
                    <strong style="color:#1C1C1C;">${item.name}</strong>
                    <div style="font-size:12px; color:#777;">₹${itemPrice} each</div>
                </div>
                <div class="qty-control">
                    <button class="qty-btn" onclick="updateItemQty(${item.id}, -1)">−</button>
                    <span class="qty-num">${itemQty}</span>
                    <button class="qty-btn" onclick="updateItemQty(${item.id}, 1)">+</button>
                </div>
                <div style="font-weight:700; width:80px; text-align:right; font-size:15px; color:#1C1C1C;">₹${lineTotal}</div>
            </div>
        `;
    }).join('');

    // 2. Immediate synchronous calculation for instant accurate amounts
    const subtotal = cart.reduce((sum, item) => sum + (Number(item.price) * Number(item.quantity)), 0);
    const deliveryFee = 30;
    const gstTax = Math.round(subtotal * 0.05);
    const grandTotal = subtotal + deliveryFee + gstTax;

    const subtotalEl = document.getElementById('billSubtotal');
    const deliveryEl = document.getElementById('billDeliveryFee');
    const taxEl = document.getElementById('billTax');
    const totalEl = document.getElementById('billGrandTotal');

    if (subtotalEl) subtotalEl.textContent = `₹${subtotal}`;
    if (deliveryEl) deliveryEl.textContent = `₹${deliveryFee}`;
    if (taxEl) taxEl.textContent = `₹${gstTax}`;
    if (totalEl) totalEl.textContent = `₹${grandTotal}`;

    // 3. Server-side Pandas Series computation
    try {
        const response = await fetch('/api/cart/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ items: cart })
        });
        if (response.ok) {
            const bill = await response.json();
            if (subtotalEl && bill.subtotal !== undefined) subtotalEl.textContent = `₹${bill.subtotal}`;
            if (deliveryEl && bill.delivery_fee !== undefined) deliveryEl.textContent = `₹${bill.delivery_fee}`;
            if (taxEl && bill.gst_tax !== undefined) taxEl.textContent = `₹${bill.gst_tax}`;
            if (totalEl && bill.grand_total !== undefined) totalEl.textContent = `₹${bill.grand_total}`;
        }
    } catch (e) {
        console.warn('API cart calculation fallback:', e);
    }
}

// ----------------------------------------------------------------
// 6. CHECKOUT & ORDER PLACEMENT
// ----------------------------------------------------------------
async function handleCheckoutSubmit(e) {
    e.preventDefault();
    if (cart.length === 0) {
        alert('Cart is empty!');
        return;
    }

    const payload = {
        name: document.getElementById('custName').value,
        phone: document.getElementById('custPhone').value,
        address: document.getElementById('custAddress').value,
        payment_method: document.getElementById('custPayment').value,
        restaurant_id: cart[0].restaurant_id,
        items: cart
    };

    try {
        const response = await fetch('/api/order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        if (result.success) {
            closeCartModal();
            cart = [];
            updateCartBadge();

            // Show Confirmation
            document.getElementById('confirmOrderId').textContent = `#${result.order_id}`;
            document.getElementById('confirmTotal').textContent = `₹${result.total_amount}`;
            document.getElementById('confirmModal').style.display = 'flex';
        } else {
            alert('Order failed: ' + result.message);
        }
    } catch (err) {
        console.error('Order error:', err);
        alert('Could not connect to server.');
    }
}

function closeConfirmModal() {
    document.getElementById('confirmModal').style.display = 'none';
}
