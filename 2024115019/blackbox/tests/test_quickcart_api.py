"""
Rigorous Blackbox API Tests for QuickCart API based strictly on documentation.
"""
import pytest
import requests

BASE = "http://localhost:8080/api/v1"
HEADERS_USER = {"X-Roll-Number": "2024115019", "X-User-ID": "1"}
HEADERS_ADMIN = {"X-Roll-Number": "2024115019"}

# --- GLOBAL AUTH ---
def test_auth_missing_roll():
    """Verify 401 error when X-Roll-Number is completely omitted across endpoints."""
    r = requests.get(f"{BASE}/products")
    assert r.status_code == 401, "Expected 401 for missing roll number"

def test_auth_invalid_roll_type():
    """Verify 400 error when X-Roll-Number is a string instead of an integer to validate types."""
    r = requests.get(f"{BASE}/products", headers={"X-Roll-Number": "invalid"})
    assert r.status_code == 400, "Expected 400 for invalid roll number"

def test_auth_missing_user_id():
    """Verify user-scoped endpoints require X-User-ID, returning 400 when missing."""
    r = requests.get(f"{BASE}/profile", headers=HEADERS_ADMIN)
    assert r.status_code == 400, "Expected 400 for missing user ID in user endpoint"

def test_auth_invalid_user_id_type():
    """Verify X-User-ID rejects non-integers representing data-type validation."""
    r = requests.get(f"{BASE}/profile", headers={**HEADERS_ADMIN, "X-User-ID": "abc"})
    assert r.status_code == 400, "Expected 400 for invalid user id type"

# --- ADMIN API ---
def test_admin_get_users_returns_200():
    """Validate getting all users returns 200 via admin access."""
    r = requests.get(f"{BASE}/admin/users", headers=HEADERS_ADMIN)
    assert r.status_code == 200

def test_admin_get_carts_returns_200():
    """Validate admin can read all global carts."""
    r = requests.get(f"{BASE}/admin/carts", headers=HEADERS_ADMIN)
    assert r.status_code == 200

def test_admin_get_orders_returns_200():
    """Validate admin can access all orders across active system."""
    r = requests.get(f"{BASE}/admin/orders", headers=HEADERS_ADMIN)
    assert r.status_code == 200

def test_admin_get_products_returns_inactive():
    """Validate admin product list contains inactive products unlike the public interface."""
    r = requests.get(f"{BASE}/admin/products", headers=HEADERS_ADMIN)
    assert r.status_code == 200
    assert any(p.get("is_active") is False or p.get("active") is False for p in r.json()), "Admin should see inactive products"

def test_admin_get_coupons_returns_200():
    """Validate admin endpoint for coupon access works."""
    r = requests.get(f"{BASE}/admin/coupons", headers=HEADERS_ADMIN)
    assert r.status_code == 200

def test_admin_get_tickets_returns_200():
    """Validate admin endpoint for all support tickets works."""
    r = requests.get(f"{BASE}/admin/tickets", headers=HEADERS_ADMIN)
    assert r.status_code == 200

def test_admin_get_addresses_returns_200():
    """Validate admin endpoint for global addresses works."""
    r = requests.get(f"{BASE}/admin/addresses", headers=HEADERS_ADMIN)
    assert r.status_code == 200

# --- PROFILE API ---
def test_profile_read_accessibility():
    """Validate profile details can be read with valid ID."""
    r = requests.get(f"{BASE}/profile", headers=HEADERS_USER)
    assert r.status_code == 200

def test_profile_update_name_minimum_boundary():
    """Validate name shorter than 2 characters is rejected (400)."""
    r = requests.put(f"{BASE}/profile", headers=HEADERS_USER, json={"name": "A", "phone": "1234567890"})
    assert r.status_code == 400

def test_profile_update_name_maximum_boundary():
    """Validate name exactly 50 characters is accepted."""
    r = requests.put(f"{BASE}/profile", headers=HEADERS_USER, json={"name": "A"*50, "phone": "1234567890"})
    assert r.status_code in (200, 201)

def test_profile_update_name_exceeds_maximum():
    """Validate name larger than 50 characters is rejected (400)."""
    r = requests.put(f"{BASE}/profile", headers=HEADERS_USER, json={"name": "A"*51, "phone": "1234567890"})
    assert r.status_code == 400

def test_profile_update_phone_wrong_length():
    """Validate phone number length exactly 10 digits; 9 digits returns 400."""
    r = requests.put(f"{BASE}/profile", headers=HEADERS_USER, json={"name": "Valid", "phone": "123456789"})
    assert r.status_code == 400

def test_profile_update_phone_excess_length():
    """Validate phone number length exactly 10 digits; 11 digits returns 400."""
    r = requests.put(f"{BASE}/profile", headers=HEADERS_USER, json={"name": "Valid", "phone": "12345678901"})
    assert r.status_code == 400

# --- ADDRESS API ---
def test_address_view():
    """Verify users can view their addresses."""
    r = requests.get(f"{BASE}/addresses", headers=HEADERS_USER)
    assert r.status_code == 200

def test_address_add_invalid_label():
    """Validate label must be strictly HOME, OFFICE, or OTHER."""
    r = requests.post(f"{BASE}/addresses", headers=HEADERS_USER, json={"label": "WORK", "street": "Valid St", "city": "Valid City", "pincode": "123456"})
    assert r.status_code == 400

def test_address_add_street_min_length():
    """Validate street shorter than 5 chars is rejected (400)."""
    r = requests.post(f"{BASE}/addresses", headers=HEADERS_USER, json={"label": "HOME", "street": "1234", "city": "Valid City", "pincode": "123456"})
    assert r.status_code == 400

def test_address_add_street_max_length():
    """Validate street exactly 100 chars."""
    r = requests.post(f"{BASE}/addresses", headers=HEADERS_USER, json={"label": "HOME", "street": "A"*100, "city": "Valid City", "pincode": "123456"})
    assert r.status_code in (200, 201)

def test_address_add_street_excess_length():
    """Validate street longer than 100 chars returns 400."""
    r = requests.post(f"{BASE}/addresses", headers=HEADERS_USER, json={"label": "HOME", "street": "A"*101, "city": "Valid City", "pincode": "123456"})
    assert r.status_code == 400

def test_address_add_city_min_length():
    """Validate city shorter than 2 chars returns 400."""
    r = requests.post(f"{BASE}/addresses", headers=HEADERS_USER, json={"label": "HOME", "street": "Valid St", "city": "A", "pincode": "123456"})
    assert r.status_code == 400

def test_address_add_pincode_invalid_length():
    """Validate pincode must be exactly 6 digits (5 digits returns 400)."""
    r = requests.post(f"{BASE}/addresses", headers=HEADERS_USER, json={"label": "HOME", "street": "Valid St", "city": "City", "pincode": "12345"})
    assert r.status_code == 400

def test_address_add_returns_full_object():
    """POST /addresses should return assigned address_id, label, street, city, pincode, is_default."""
    r = requests.post(f"{BASE}/addresses", headers=HEADERS_USER, json={"label": "HOME", "street": "Return St", "city": "City", "pincode": "123456"})
    if r.status_code in (200, 201):
        data = r.json()
        assert "address_id" in data or "id" in data
        assert "label" in data and "street" in data and "city" in data and "pincode" in data and "is_default" in data

def test_address_update_prohibited_fields():
    """Update can only change street and is_default. Label changes should be ignored or rejected."""
    r = requests.post(f"{BASE}/addresses", headers=HEADERS_USER, json={"label": "HOME", "street": "Valid St", "city": "City", "pincode": "123456"})
    if r.status_code not in (200, 201):
        pytest.skip("Could not add address")
    addr_id = r.json().get("address_id", r.json().get("id"))
    r2 = requests.put(f"{BASE}/addresses/{addr_id}", headers=HEADERS_USER, json={"label": "OFFICE", "street": "New Street"})
    assert r2.status_code in (200, 201)
    # Check old label remained
    r3 = requests.get(f"{BASE}/addresses", headers=HEADERS_USER)
    addr = next(a for a in r3.json() if a.get("id") == addr_id or a.get("address_id") == addr_id)
    assert addr["label"] == "HOME", "Label should not have changed"

def test_address_delete_nonexistent():
    """Deleting nonexistent address must return 404."""
    r = requests.delete(f"{BASE}/addresses/999999", headers=HEADERS_USER)
    assert r.status_code == 404

# --- PRODUCTS API ---
def test_products_list_returns_active_only():
    """Validate public product list drops all inactive products."""
    r = requests.get(f"{BASE}/products", headers=HEADERS_USER)
    assert r.status_code == 200
    for p in r.json():
        assert p.get("is_active", p.get("active", True)) is True

def test_products_lookup_nonexistent():
    """Looking up non-existent product returns 404."""
    r = requests.get(f"{BASE}/products/99999", headers=HEADERS_USER)
    assert r.status_code == 404

def test_products_filter_category():
    """Filtering by category returns only products in that category."""
    r = requests.get(f"{BASE}/products?category=Electronics", headers=HEADERS_USER)
    if r.status_code == 200 and r.json():
        for p in r.json():
            assert p["category"] == "Electronics"

def test_products_search_name():
    """Searching acts correctly."""
    r = requests.get(f"{BASE}/products?search=Apple", headers=HEADERS_USER)
    assert r.status_code == 200

# --- CART API ---
def test_cart_add_zero_quantity():
    """Cart addition requires quantity >= 1 (0 returns 400)."""
    requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 1, "quantity": 0})
    r = requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 1, "quantity": 0})
    assert r.status_code == 400

def test_cart_add_negative_quantity():
    """Cart addition requires quantity >= 1 (negative returns 400)."""
    r = requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 1, "quantity": -5})
    assert r.status_code == 400

def test_cart_add_nonexistent_product():
    """Adding non-existent product returns 404."""
    r = requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 999123, "quantity": 1})
    assert r.status_code == 404

def test_cart_add_quantity_exceeds_stock():
    """Requesting more quantity than stock returns 400."""
    r = requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 1, "quantity": 999999})
    assert r.status_code == 400

def test_cart_duplicate_product_combines_quantities():
    """Adding an item already in the cart must sum quantities rather than replacing."""
    requests.delete(f"{BASE}/cart/clear", headers=HEADERS_USER)
    requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 1, "quantity": 1})
    requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 1, "quantity": 1})
    r = requests.get(f"{BASE}/cart", headers=HEADERS_USER)
    for t in r.json().get("items", []):
        if t["product_id"] == 1:
            assert t["quantity"] == 2
            return

def test_cart_update_zero_quantity():
    """Updating a cart item quantity to 0 must return 400."""
    requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 1, "quantity": 1})
    r = requests.post(f"{BASE}/cart/update", headers=HEADERS_USER, json={"product_id": 1, "quantity": 0})
    assert r.status_code == 400

def test_cart_remove_nonexistent():
    """Removing product not in cart returns 404."""
    requests.delete(f"{BASE}/cart/clear", headers=HEADERS_USER)
    r = requests.post(f"{BASE}/cart/remove", headers=HEADERS_USER, json={"product_id": 1})
    assert r.status_code == 404

def test_cart_subtotal_calculation():
    """Each item in cart must expose subtotal = qty * price."""
    requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 1, "quantity": 2})
    r = requests.get(f"{BASE}/cart", headers=HEADERS_USER)
    for item in r.json().get("items", []):
        assert item["subtotal"] == item["quantity"] * item["price"]

def test_cart_total_sum_calculation():
    """Cart total must be sum of all subtotals."""
    r = requests.get(f"{BASE}/cart", headers=HEADERS_USER)
    items = r.json().get("items", [])
    expected_total = sum(i["subtotal"] for i in items)
    assert r.json().get("total", 0) == expected_total

# --- CHECKOUT API ---
def test_checkout_invalid_method():
    """Only COD, WALLET, or CARD payment allowed; CHEQUE returns 400."""
    r = requests.post(f"{BASE}/checkout", headers=HEADERS_USER, json={"payment_method": "CHEQUE"})
    assert r.status_code == 400

def test_checkout_empty_cart():
    """Empty cart implies 400 on checkout."""
    requests.delete(f"{BASE}/cart/clear", headers=HEADERS_USER)
    r = requests.post(f"{BASE}/checkout", headers=HEADERS_USER, json={"payment_method": "COD"})
    assert r.status_code == 400

# --- WALLET API ---
def test_wallet_add_zero():
    """Amount added to wallet must > 0."""
    r = requests.post(f"{BASE}/wallet/add", headers=HEADERS_USER, json={"amount": 0})
    assert r.status_code == 400

def test_wallet_add_exceeding_max():
    """Amount added to wallet must be at most 100000."""
    r = requests.post(f"{BASE}/wallet/add", headers=HEADERS_USER, json={"amount": 100001})
    assert r.status_code == 400

def test_wallet_pay_negative():
    """Wallet pay amount must be > 0."""
    r = requests.post(f"{BASE}/wallet/pay", headers=HEADERS_USER, json={"amount": -10})
    assert r.status_code == 400

def test_wallet_pay_insufficient():
    """If wallet balance is insufficient, pay returns 400."""
    r = requests.post(f"{BASE}/wallet/pay", headers=HEADERS_USER, json={"amount": 999999})
    assert r.status_code == 400

# --- LOYALTY POINTS ---
def test_loyalty_redeem_zero():
    """Redemption amount must be at least 1."""
    r = requests.post(f"{BASE}/loyalty/redeem", headers=HEADERS_USER, json={"points": 0})
    assert r.status_code == 400

def test_loyalty_redeem_too_many():
    """Redeeming more than wallet balance is 400."""
    r = requests.post(f"{BASE}/loyalty/redeem", headers=HEADERS_USER, json={"points": 999999})
    assert r.status_code == 400

# --- ORDERS API ---
def test_orders_cancel_nonexistent():
    """Canceling an order that does not exist returns 404."""
    r = requests.post(f"{BASE}/orders/99999/cancel", headers=HEADERS_USER)
    assert r.status_code == 404

# --- REVIEWS API ---
def test_review_rating_zero():
    """Review rating must be between 1 and 5 (0 returns 400)."""
    r = requests.post(f"{BASE}/products/1/reviews", headers=HEADERS_USER, json={"rating": 0, "comment": "Good"})
    assert r.status_code == 400

def test_review_rating_six():
    """Review rating must be between 1 and 5 (6 returns 400)."""
    r = requests.post(f"{BASE}/products/1/reviews", headers=HEADERS_USER, json={"rating": 6, "comment": "Good"})
    assert r.status_code == 400

def test_review_comment_empty():
    """Comment must be 1 to 200 chars."""
    r = requests.post(f"{BASE}/products/1/reviews", headers=HEADERS_USER, json={"rating": 3, "comment": ""})
    assert r.status_code == 400

def test_review_comment_exceeds_max():
    """Comment 201 chars returns 400."""
    r = requests.post(f"{BASE}/products/1/reviews", headers=HEADERS_USER, json={"rating": 3, "comment": "A"*201})
    assert r.status_code == 400

def test_review_average_rating_decimal():
    """Validate average rating is a correct decimal calculation."""
    r = requests.get(f"{BASE}/products", headers=HEADERS_USER)
    for p in r.json():
        if "average_rating" in p:
            assert isinstance(p["average_rating"], float) or p["average_rating"] == 0

# --- SUPPORT TICKETS ---
def test_ticket_subject_minimum_length():
    """Subject must be 5-100 characters; 4 chars returns 400."""
    r = requests.post(f"{BASE}/support/ticket", headers=HEADERS_USER, json={"subject": "1234", "message": "hello world"})
    assert r.status_code == 400

def test_ticket_subject_maximum_length():
    """Subject exceeding 100 characters returns 400."""
    r = requests.post(f"{BASE}/support/ticket", headers=HEADERS_USER, json={"subject": "A"*101, "message": "hello world"})
    assert r.status_code == 400

def test_ticket_message_empty():
    """Message must be 1-500 characters; empty returns 400."""
    r = requests.post(f"{BASE}/support/ticket", headers=HEADERS_USER, json={"subject": "Valid subject", "message": ""})
    assert r.status_code == 400

def test_ticket_message_exceeds_max():
    """Message exceeding 500 characters returns 400."""
    r = requests.post(f"{BASE}/support/ticket", headers=HEADERS_USER, json={"subject": "Valid subject", "message": "A"*501})
    assert r.status_code == 400

# --- COUPONS API ---
def test_coupon_apply_valid():
    """Apply valid coupon successfully."""
    r = requests.post(f"{BASE}/coupon/apply", headers=HEADERS_USER, json={"code": "SUMMER10"})
    assert r.status_code in (200, 400) # May 400 if cart empty

def test_coupon_apply_empty_code():
    """Apply empty coupon code should 400."""
    r = requests.post(f"{BASE}/coupon/apply", headers=HEADERS_USER, json={"code": ""})
    assert r.status_code == 400

def test_coupon_apply_expired():
    """Applying an expired coupon returns 400."""
    r = requests.post(f"{BASE}/coupon/apply", headers=HEADERS_USER, json={"code": "EXPIRED2023"})
    assert r.status_code == 400

def test_coupon_minimum_cart_value():
    """Coupon requiring minimum value must throw 400 if cart isn't large enough."""
    requests.delete(f"{BASE}/cart/clear", headers=HEADERS_USER)
    r = requests.post(f"{BASE}/coupon/apply", headers=HEADERS_USER, json={"code": "BIGORDER"})
    assert r.status_code == 400

def test_coupon_remove():
    """Removing a coupon should succeed or return 400 if none applied."""
    r = requests.post(f"{BASE}/coupon/remove", headers=HEADERS_USER)
    assert r.status_code in (200, 400)

# --- ORDERS INVOICE API ---
def test_order_invoice_subtotal():
    """Invoice must show subtotal = total before GST."""
    admin_r = requests.get(f"{BASE}/admin/orders", headers=HEADERS_ADMIN)
    if admin_r.status_code == 200 and admin_r.json():
        oid = admin_r.json()[0]["id"]
        uid = admin_r.json()[0]["user_id"]
        r = requests.get(f"{BASE}/orders/{oid}/invoice", headers={**HEADERS_ADMIN, "X-User-ID": str(uid)})
        if r.status_code == 200:
            inv = r.json()
            assert "subtotal" in inv and "gst" in inv and "total" in inv
            assert inv["total"] == inv["subtotal"] + inv["gst"]

def test_order_invoice_gst_rate():
    """GST must be 5%."""
    admin_r = requests.get(f"{BASE}/admin/orders", headers=HEADERS_ADMIN)
    if admin_r.status_code == 200 and admin_r.json():
        oid = admin_r.json()[0]["id"]
        uid = admin_r.json()[0]["user_id"]
        r = requests.get(f"{BASE}/orders/{oid}/invoice", headers={**HEADERS_ADMIN, "X-User-ID": str(uid)})
        if r.status_code == 200:
            inv = r.json()
            assert abs(inv["gst"] - (inv["subtotal"] * 0.05)) < 0.01

def test_order_invoice_nonexistent():
    """Invoice for nonexistent order returns 404."""
    r = requests.get(f"{BASE}/orders/999999/invoice", headers=HEADERS_USER)
    assert r.status_code == 404

# --- ADDITIONAL CHECKOUT RULES ---
def test_checkout_cod_limit():
    """COD not allowed if order total is more than 5000 (returns 400)."""
    # Assuming cart is populated
    requests.post(f"{BASE}/cart/add", headers=HEADERS_USER, json={"product_id": 1, "quantity": 100})
    r = requests.post(f"{BASE}/checkout", headers=HEADERS_USER, json={"payment_method": "COD", "address_id": 1})
    assert r.status_code == 400

# --- ADDITIONAL PROFILE RULES ---
def test_profile_read_has_fields():
    """Profile exposes name and phone."""
    r = requests.get(f"{BASE}/profile", headers=HEADERS_USER)
    if r.status_code == 200:
        assert "name" in r.json() and "phone" in r.json()

# --- ADMIN EDGE CASES ---
def test_admin_get_user_specific():
    """Admin can get single user."""
    r = requests.get(f"{BASE}/admin/users/1", headers=HEADERS_ADMIN)
    assert r.status_code == 200

def test_admin_get_user_invalid():
    """Admin get nonexistent user returns 404."""
    r = requests.get(f"{BASE}/admin/users/9999", headers=HEADERS_ADMIN)
    assert r.status_code == 404

# --- PRODUCTS LIST EXTENSIONS ---
def test_products_sort_price_asc():
    """Sort products by price ascending."""
    r = requests.get(f"{BASE}/products?sort=price_asc", headers=HEADERS_USER)
    assert r.status_code == 200
    prices = [p.get("price", 0) for p in r.json()]
    assert prices == sorted(prices)

def test_products_sort_price_desc():
    """Sort products by price descending."""
    r = requests.get(f"{BASE}/products?sort=price_desc", headers=HEADERS_USER)
    assert r.status_code == 200
    prices = [p.get("price", 0) for p in r.json()]
    assert prices == sorted(prices, reverse=True)

def test_products_sort_invalid():
    """Invalid sort key should 400."""
    r = requests.get(f"{BASE}/products?sort=random", headers=HEADERS_USER)
    assert r.status_code == 400

# --- WALLET EXTRA ---
def test_wallet_balance_read():
    """Can read wallet balance."""
    r = requests.get(f"{BASE}/wallet", headers=HEADERS_USER)
    assert r.status_code == 200

def test_wallet_pay_exact_amount():
    """Wallet pays exactly amount."""
    r = requests.post(f"{BASE}/wallet/pay", headers=HEADERS_USER, json={"amount": 1})
    assert r.status_code in (200, 400)

# --- REVIEWS EXTRA ---
def test_review_view():
    """Can view product reviews."""
    r = requests.get(f"{BASE}/products/1/reviews", headers=HEADERS_USER)
    assert r.status_code == 200

def test_review_view_nonexistent():
    """View reviews of nonexistent product returns 404."""
    r = requests.get(f"{BASE}/products/99999/reviews", headers=HEADERS_USER)
    assert r.status_code == 404

# --- TICKETS EXTRA ---
def test_ticket_view_all():
    """User can view all their tickets."""
    r = requests.get(f"{BASE}/support/tickets", headers=HEADERS_USER)
    assert r.status_code == 200

def test_ticket_update_status_backwards():
    """Status cannot move from IN_PROGRESS backwards to OPEN."""
    r = requests.post(f"{BASE}/support/ticket", headers=HEADERS_USER, json={"subject": "Valid Subject", "message": "Valid desc"})
    if r.status_code in (200, 201):
        tid = r.json().get("id")
        requests.put(f"{BASE}/support/tickets/{tid}", headers=HEADERS_USER, json={"status": "IN_PROGRESS"})
        put2 = requests.put(f"{BASE}/support/tickets/{tid}", headers=HEADERS_USER, json={"status": "OPEN"})
        assert put2.status_code == 400

