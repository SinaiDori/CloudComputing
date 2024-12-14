import os
import uuid
from flask import Flask, request, jsonify, abort
import requests

app = Flask(__name__)

API_KEY = "MybMJ/yhrKNKH7YJVCSfZg==pW9iG0vqEIjkRpnn"
API_URL = "https://api.api-ninjas.com/v1/stockprice"

stocks = {}

class Stock:
    _used_ids = set()

    def __init__(self, data: dict):
        self.validate_new_stock_fields(data)
        # If we reach this line, the data is valid
        self.id = self._generate_unique_id()
        self.name = data.get("name", "NA")
        self.symbol = data["symbol"].upper()
        self.purchase_price = round(float(data["purchase price"]), 2)
        self.purchase_date = data.get("purchase date", "NA")
        self.shares = data["shares"]

    @classmethod
    def _generate_unique_id(cls) -> str:
        while True:
            new_id = str(uuid.uuid4())
            if new_id not in cls._used_ids:
                cls._used_ids.add(new_id)
                return new_id

    @classmethod
    def check_stock_exists(cls, stock_id):
        if stock_id not in stocks:
            abort(404)

    @classmethod
    def delete_stock(cls, stock_id):
        del stocks[stock_id]
        cls.remove_id_from_used_ids(stock_id)

    @classmethod
    def remove_id_from_used_ids(cls, stock_id):
        cls._used_ids.discard(stock_id)

    @classmethod
    def validate_new_stock_fields(self, data: dict):
        required_fields = ["symbol", "purchase price", "shares"]
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")

        # Validate symbol not already in stocks
        for stock in stocks.values():
            if stock.symbol == data["symbol"].upper():
                raise ValueError("Stock with symbol already exists")
        
        # Validate purchase price
        try:
            float(data["purchase price"])
        except ValueError as e:
            raise ValueError("Invalid purchase price - " + str(e))

        # Validate purchase date
        if data.get("purchase date"):
            try:
                day, month, year = map(int, data["purchase date"].split("-"))
                if not (1 <= day <= 31 and 1 <= month <= 12 and year > 0):
                    raise ValueError("Invalid purchase date")
            except ValueError as e:
                raise ValueError("Invalid purchase date - " + str(e))

        # Validate shares
        try:
            int(data["shares"])
        except ValueError as e:
            raise ValueError("Invalid shares - " + str(e))

    @classmethod
    def validate_put_stock_fields(self, data: dict):
        required_fields = ["id", "symbol", "name", "purchase price", "purchase date", "shares"]
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")

        # Validate purchase price
        try:
            float(data["purchase price"])
        except ValueError as e:
            raise ValueError("Invalid purchase price - " + str(e))

        # Validate purchase date
        if data.get("purchase date"):
            try:
                day, month, year = map(int, data["purchase date"].split("-"))
                if not (1 <= day <= 31 and 1 <= month <= 12 and year > 0):
                    raise ValueError("Invalid purchase date")
            except ValueError as e:
                raise ValueError("Invalid purchase date - " + str(e))

        # Validate shares
        try:
            int(data["shares"])
        except ValueError as e:
            raise ValueError("Invalid shares - " + str(e))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "purchase price": self.purchase_price,
            "purchase date": self.purchase_date,
            "shares": self.shares,
        }

# Fetch stock price from external API
def fetch_stock_price(symbol):
    headers = {"X-Api-Key": API_KEY}
    response = requests.get(f"{API_URL}?ticker={symbol}", headers=headers)
    if response.status_code == 200:
        return response.json().get("price")
    else:
        abort(500, description="API response code " + str(response.status_code))

@app.route('/stocks', methods=['POST', 'GET'])
def manage_stocks():
    if request.method == 'POST':
        if not request.is_json:
            abort(415)

        data: dict = request.json

        try:
            stock = Stock(data)
            stocks[stock.id] = stock
            return jsonify({"id": stock.id}), 201
        except ValueError as e:
            abort(400)
        except Exception as e:
            abort(500, description=str(e))

    elif request.method == 'GET':
        try:
            query_params = request.args.to_dict()
            filtered_stocks = [
                stock.to_dict() for stock in stocks.values()
                if all(str(stock.to_dict().get(k)).lower() == v.lower() for k, v in query_params.items())
            ]
            return jsonify(filtered_stocks), 200
        except Exception as e:
            abort(500, description=str(e))

@app.route('/stocks/<stock_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_stock(stock_id):
    Stock.check_stock_exists(stock_id)
    stock = stocks[stock_id]
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
    stock = stocks.get(stock_id)
    if not stock:
        abort(404)

    try:
        ticker_price = fetch_stock_price(stock.symbol)
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
        for stock in stocks.values():
            ticker_price = fetch_stock_price(stock.symbol)
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