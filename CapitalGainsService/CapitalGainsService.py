import os
from Entities.Stock import Stock
from Entities.StocksRealValue import fetch_stock_real_price

from flask import Flask, request, jsonify, abort
import requests

app = Flask(__name__)

def fetch_stocks_based_on_query_params(query_params: dict) -> dict:
    # Fetch stocks from Stocks1 and Stocks2 services using query parameters
    services = [
        "http://Stocks1:5002/stocks",  # Example endpoint for Stocks1 using the name in the docker compose file
        "http://Stocks2:5003/stocks"   # Example endpoint for Stocks2 using the name in the docker compose file
    ]
    stocks = {}
    for service in services:
        try:
            response = requests.get(service, params=query_params)
            if response.status_code == 200:
                stocks.update({stock["id"]: stock for stock in response.json()})
        except Exception as e:
            print(f"Failed to fetch stocks from {service}: {e}")
    return stocks


def calculate_capital_gains(stocks: dict = None) -> float:
    total_capital_gain = 0
    if not stocks:
        #! When MongoDB is built, retrieve ALL stocks from the database (Stocks1 and Stocks2)
        stocks = Stock.stocks

    for stock in Stock.stocks.values():
        try:
            current_price = fetch_stock_real_price(stock.symbol)
            current_value = stock.shares * current_price
            capital_gain = current_value - stock.purchase_price
            total_capital_gain += capital_gain
        except Exception as e:
            print(f"Error processing stock {stock.symbol}: {e}") #! Change to the right abort function
    return total_capital_gain


@app.route('/capital-gains', methods=['GET'])
def manage_stocks():
    try:
        query_params = request.args.to_dict()
        if not query_params:
            total_capital_gains = calculate_capital_gains()
            return jsonify({"total capital gains": total_capital_gains}), 200
        else:
            stocks = fetch_stocks_based_on_query_params(query_params)
            total_capital_gains = calculate_capital_gains(stocks)
            return jsonify({"total capital gains": total_capital_gains}), 200
    except Exception as e:
        abort(500, description=str(e)) #! Change to the right abort function

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Malformed data"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(415)
def unsupported_media_type(error):
    return jsonify({"error": "Expected application/json media type"}), 415

@app.errorhandler(500)
def internal_server_error(error):
    description = error.description if error.description else "Internal server error"
    return jsonify({"server error": description}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5001)))