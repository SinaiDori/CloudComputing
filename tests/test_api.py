import pytest
import requests

BASE_URL = "http://127.0.0.1:5001"

# Predefined list of known stock symbols
KNOWN_SYMBOLS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
    "NFLX", "NVDA", "INTC", "ORCL", "CSCO", "DIS", "PYPL"
]

symbol_counter = 0  # Global counter to track which symbol to use next

def get_known_symbol():
    """Retrieve the next stock symbol from the predefined list."""
    global symbol_counter
    symbol = KNOWN_SYMBOLS[symbol_counter % len(KNOWN_SYMBOLS)]
    symbol_counter += 1
    return symbol

@pytest.fixture
def create_stock():
    # Set up: Create a new stock with a known symbol
    url = f"{BASE_URL}/stocks"
    headers = {"Content-Type": "application/json"}
    symbol = get_known_symbol()  # Use the next symbol in the list
    data = {
        "symbol": symbol,
        "name": "Test Stock",
        "purchase price": 100.00,
        "purchase date": "01-01-2024",
        "shares": 10
    }
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 201
    stock_id = response.json().get("id")

    yield stock_id, symbol  # Provide stock_id and symbol to test functions

    # Teardown: Delete the created stock after the test completes
    requests.delete(f"{BASE_URL}/stocks/{stock_id}")

def test_post_stocks():
    url = f"{BASE_URL}/stocks"
    headers = {"Content-Type": "application/json"}
    symbol = get_known_symbol()  # Use the second symbol in the list

    # Valid data
    data = {
        "symbol": symbol,
        "name": "Test Inc",
        "purchase price": 150.00,
        "purchase date": "01-01-2024",
        "shares": 10
    }
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 201
    assert "id" in response.json()
    stock_id = response.json()["id"]

    # Cleanup: delete the created stock
    requests.delete(f"{BASE_URL}/stocks/{stock_id}")

def test_post_duplicate_symbol():
    url = f"{BASE_URL}/stocks"
    headers = {"Content-Type": "application/json"}
    symbol = get_known_symbol()  # Use the third symbol in the list

    # First POST request to add a stock
    data_1 = {
        "symbol": symbol,
        "name": "Test Inc",
        "purchase price": 150.00,
        "purchase date": "01-01-2024",
        "shares": 10
    }
    response_1 = requests.post(url, headers=headers, json=data_1)
    assert response_1.status_code == 201
    stock_id_1 = response_1.json().get("id")

    # Second POST request with the same symbol
    data_2 = {
        "symbol": symbol,  # Duplicate symbol
        "name": "Another Inc",
        "purchase price": 200.00,
        "purchase date": "02-01-2024",
        "shares": 5
    }
    response_2 = requests.post(url, headers=headers, json=data_2)
    assert response_2.status_code == 400
    assert "Malformed data" in response_2.json().get("error", "")

    # Cleanup: delete the created stock
    requests.delete(f"{BASE_URL}/stocks/{stock_id_1}")

def test_get_stocks(create_stock):
    stock_id, symbol = create_stock
    url = f"{BASE_URL}/stocks"

    # Get all stocks
    response = requests.get(url)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Get stocks with query parameters
    response = requests.get(url, params={"symbol": symbol})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == symbol  # Ensure symbols match exactly

def test_put_stock(create_stock):
    stock_id, symbol = create_stock
    url = f"{BASE_URL}/stocks/{stock_id}"
    headers = {"Content-Type": "application/json"}

    # Update stock with valid data
    data = {
        "id": stock_id,
        "symbol": symbol,
        "name": "Updated Stock",
        "purchase price": 155.00,
        "purchase date": "01-02-2024",
        "shares": 15
    }
    response = requests.put(url, headers=headers, json=data)
    assert response.status_code == 200
    assert response.json().get("id") == stock_id

    # Update with missing fields (should return 400)
    data = {
        "id": stock_id,
        "symbol": symbol
    }
    response = requests.put(url, headers=headers, json=data)
    assert response.status_code == 400

    # Invalid content type
    response = requests.put(url, headers={"Content-Type": "text/plain"}, json=data)
    assert response.status_code == 415

def test_get_stock(create_stock):
    stock_id, symbol = create_stock
    url = f"{BASE_URL}/stocks/{stock_id}"

    # Valid GET request
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json().get("id") == stock_id

    # Invalid stock ID
    response = requests.get(f"{BASE_URL}/stocks/9999")
    assert response.status_code == 404

def test_delete_stock(create_stock):
    stock_id, symbol = create_stock
    url = f"{BASE_URL}/stocks/{stock_id}"

    # Valid DELETE request
    response = requests.delete(url)
    assert response.status_code == 204

    # Deleting a non-existent stock
    response = requests.delete(url)
    assert response.status_code == 404

def test_get_stock_value(create_stock):
    stock_id, symbol = create_stock
    url = f"{BASE_URL}/stock-value/{stock_id}"

    # Valid stock value request
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data and "ticker" in data and "stock value" in data

    # Invalid stock ID
    response = requests.get(f"{BASE_URL}/stock-value/9999")
    assert response.status_code == 404

def test_get_portfolio_value():
    url = f"{BASE_URL}/portfolio-value"

    # Valid portfolio value request
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "date" in data and "portfolio value" in data

def test_post_invalid_json():
    url = f"{BASE_URL}/stocks"
    headers = {"Content-Type": "application/json"}
    
    # Malformed JSON
    data = "not a valid JSON"
    response = requests.post(url, headers=headers, data=data)
    assert response.status_code == 400
    
    # Wrong fields
    data = {
        "wrong_field": "value"
    }
    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 400


def test_get_stocks_multiple_filters(create_stock):
    stock_id, symbol = create_stock
    url = f"{BASE_URL}/stocks"
    
    # Valid multiple filters
    response = requests.get(url, params={"symbol": symbol, "name": "Test Stock"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["symbol"] == symbol

def test_put_stock_non_json(create_stock):
    stock_id, symbol = create_stock
    url = f"{BASE_URL}/stocks/{stock_id}"
    
    # Non-JSON input
    data = "not a json"
    response = requests.put(url, headers={"Content-Type": "application/json"}, data=data)
    assert response.status_code == 400

def test_delete_nonexistent_stock():
    url = f"{BASE_URL}/stocks/nonexistent-id"
    response = requests.delete(url)
    assert response.status_code == 404