import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Entities.Stock import Stock
from Entities.StocksRealValue import fetch_stock_real_price

from flask import Flask, request, jsonify, abort
import requests

app = Flask(__name__)

@app.route('/stocks', methods=['POST', 'GET'])
def manage_stocks():
    if request.method == 'POST':
        if not request.is_json:
            abort(415)

        data: dict = request.json

        try:
            stock = Stock(data)
            Stock.stocks[stock.id] = stock
            return jsonify({"id": stock.id}), 201
        except ValueError as e:
            abort(400)
        except Exception as e:
            abort(500, description=str(e))

    elif request.method == 'GET':
        try:
            query_params = request.args.to_dict()
            filtered_stocks = [
                stock.to_dict() for stock in Stock.stocks.values()
                if all(str(stock.to_dict().get(k)).lower() == v.lower() for k, v in query_params.items())
            ]
            return jsonify(filtered_stocks), 200
        except Exception as e:
            abort(500, description=str(e))

@app.route('/stocks/<stock_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_stock(stock_id):
    Stock.check_stock_exists(stock_id)
    stock = Stock.stocks[stock_id]
    if request.method == 'GET':
        return jsonify(stock.to_dict()), 200

    elif request.method == 'DELETE':
        try:
            Stock.delete_stock(stock_id)
            return "", 204
        except Exception as e:
            abort(500, description=str(e))

    elif request.method == 'PUT':
        if not request.is_json:
            abort(415)

        data = request.json
        if not data:
            abort(400)

        try:
            Stock.validate_put_stock_fields(data)
            stock.name = data["name"]
            stock.symbol = data["symbol"].upper()
            stock.purchase_price = round(float(data["purchase price"]), 2)
            stock.purchase_date = data["purchase date"]
            stock.shares = int(data["shares"])
            return jsonify({"id": stock_id}), 200
        except ValueError as e:
            abort(400)
        except Exception as e:
            abort(500, description=str(e))

@app.route('/stock-value/<stock_id>', methods=['GET'])
def get_stock_value(stock_id):
    stock = Stock.stocks.get(stock_id)
    if not stock:
        abort(404)

    try:
        ticker_price = fetch_stock_real_price(stock.symbol)
        stock_value = round(ticker_price * stock.shares, 2)
        return jsonify({
            "symbol": stock.symbol,
            "ticker": ticker_price,
            "stock value": stock_value
        }), 200
    except Exception as e:
        abort(500, description=str(e))

@app.route('/portfolio-value', methods=['GET'])
def get_portfolio_value():
    try:
        total_value = 0
        for stock in Stock.stocks.values():
            ticker_price = fetch_stock_real_price(stock.symbol)
            total_value += ticker_price * stock.shares

        return jsonify({
            "date": request.args.get("date", "Today"),
            "portfolio value": round(total_value, 2)
        }), 200
    except Exception as e:
        abort(500, description=str(e))

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