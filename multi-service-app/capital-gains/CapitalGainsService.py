from entities.StocksRealValue import fetch_stock_real_price
from flask import Flask, jsonify, abort, request
import requests
from core.exceptions import StocksRealValueError

app = Flask(__name__)

def fetch_stocks(query_params: dict = {}) -> dict:
    service = "http://stock-service:8000/stocks"

    stocks = {}

    try:
        response = requests.get(service)
        if response.status_code == 200:
            for stock in response.json():
                stocks[stock["symbol"]] = stock
    except Exception as e:
        print(f"Failed to fetch stocks from {service}: {e}")

    if "numsharesgt" in query_params or "numshareslt" in query_params:
        if query_params.get("numsharesgt"):
            min_shares = int(query_params.get("numsharesgt"))
        else:
            min_shares = float('-inf')

        if query_params.get("numshareslt"):
            max_shares = int(query_params.get("numshareslt"))
        else:
            max_shares = float('inf')

        stocks = {
            stock_id: stock_data
            for stock_id, stock_data in stocks.items()
            if min_shares < stock_data["shares"] < max_shares
        }

    return stocks


@app.route('/capital-gains', methods=['GET'])
def capital_gains():

    total_capital_gains = 0
    query_params = request.args.to_dict()
    stocks = fetch_stocks(query_params)

    for stock in stocks.values():
        try:
            current_price = fetch_stock_real_price(stock["symbol"])
            capital_gain = (current_price - stock["purchase_price"]) * stock["shares"]
            total_capital_gains += capital_gain
        except StocksRealValueError as e:
            abort(500, description="API response code " + e)

    return str(total_capital_gains), 200


@app.errorhandler(500)
def internal_server_error(error):
    description = error.description if error.description else "Internal server error"
    return jsonify({"server error": description}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
