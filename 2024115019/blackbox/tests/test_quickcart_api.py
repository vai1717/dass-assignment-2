import requests
import pytest

BASE_URL = "http://localhost:8080/api/v1/products"
HEADERS = {"X-Roll-Number": "123"}

# 1. Valid request
def test_valid_request():
    response = requests.get(BASE_URL, headers=HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for product in response.json():
        assert "id" in product and "name" in product and "price" in product

# 2. Missing X-Roll-Number header
def test_missing_roll_number():
    response = requests.get(BASE_URL)
    assert response.status_code == 401

# 3. Invalid X-Roll-Number (non-integer)
def test_invalid_roll_number():
    response = requests.get(BASE_URL, headers={"X-Roll-Number": "abc"})
    assert response.status_code == 400

# 4. Boundary value: Large X-Roll-Number
def test_large_roll_number():
    response = requests.get(BASE_URL, headers={"X-Roll-Number": "9999999999"})
    assert response.status_code in (200, 400)

# 5. Filter by category
def test_filter_by_category():
    response = requests.get(BASE_URL + "?category=Electronics", headers=HEADERS)
    assert response.status_code == 200
    for product in response.json():
        assert product.get("category") == "Electronics"

# 6. Search by name
def test_search_by_name():
    response = requests.get(BASE_URL + "?search=phone", headers=HEADERS)
    assert response.status_code == 200
    for product in response.json():
        assert "phone" in product.get("name", "").lower()

# 7. Sort by price ascending
def test_sort_price_asc():
    response = requests.get(BASE_URL + "?sort=price_asc", headers=HEADERS)
    assert response.status_code == 200
    prices = [product["price"] for product in response.json()]
    assert prices == sorted(prices)

# 8. Sort by price descending
def test_sort_price_desc():
    response = requests.get(BASE_URL + "?sort=price_desc", headers=HEADERS)
    assert response.status_code == 200
    prices = [product["price"] for product in response.json()]
    assert prices == sorted(prices, reverse=True)

# 9. Wrong data type for category
def test_wrong_category_type():
    response = requests.get(BASE_URL + "?category=12345", headers=HEADERS)
    assert response.status_code in (200, 400)

# 10. Boundary value: Empty search string
def test_empty_search():
    response = requests.get(BASE_URL + "?search=", headers=HEADERS)
    assert response.status_code == 200

# 11. Boundary value: Very long search string
def test_long_search():
    long_search = "a" * 1001
    response = requests.get(BASE_URL + f"?search={long_search}", headers=HEADERS)
    assert response.status_code in (200, 400)
