import os
from Entities.StocksRealValue import fetch_stock_real_price
from flask import Flask, jsonify, abort
import requests
from Core.exceptions import StocksRealValueError

app = Flask(__name__)

def fetch_stocks(query_params: dict = None) -> dict:
    services = {
        "stocks1": "http://Stocks1:5001/stocks",
        "stocks2": "http://Stocks2:5002/stocks"
    }

    stocks = {}

    portfolios = query_params.get("portfolio")
    portfolios = [portfolios] if portfolios else ["stocks1", "stocks2"]

    for portfolio in portfolios:
        try:
            response = requests.get(services[portfolio])
            if response.status_code == 200:
                for stock in response.json():
                    stocks[stock["symbol"]] = stock
        except Exception as e:
            print(f"Failed to fetch stocks from {services[0]}: {e}")

    
    if "numsharesgt" in query_params or "numshareslt" in query_params:
        min_shares = int(query_params.get("numsharesgt", float('-inf')))
        max_shares = int(query_params.get("numshareslt", float('inf')))
        stocks = {
            stock_id: stock_data
            for stock_id, stock_data in stocks.items()
            if min_shares < stock_data["shares"] < max_shares
        }
    
    return stocks


@app.route('/capital-gains', methods=['GET'])
def capital_gains():
    
    total_capital_gains = 0
    if not stocks:
        stocks = fetch_stocks()

    for stock in stocks.values():
        try:
            current_price = fetch_stock_real_price(stock.symbol)
            current_value = stock.shares * current_price
            capital_gain = current_value - stock.purchase_price
            total_capital_gains += capital_gain
        except StocksRealValueError as e:
            abort(500, description="API response code " + e)
    
    return jsonify({"total capital gains": total_capital_gains}), 200


@app.errorhandler(500)
def internal_server_error(error):
    description = error.description if error.description else "Internal server error"
    return jsonify({"server error": description}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('CAPITAL_GAIN_SERVICE_PORT', 5003)))