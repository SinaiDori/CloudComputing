import requests
from Core.exceptions import StocksRealValueError

API_KEY = "MybMJ/yhrKNKH7YJVCSfZg==pW9iG0vqEIjkRpnn"
API_URL = "https://api.api-ninjas.com/v1/stockprice"

# Fetch stock price from external API
def fetch_stock_real_price(symbol):
    headers = {"X-Api-Key": API_KEY}
    response = requests.get(f"{API_URL}?ticker={symbol}", headers=headers)
    if response.status_code == 200:
        return response.json().get("price")
    else:
        raise StocksRealValueError(str(response.status_code))