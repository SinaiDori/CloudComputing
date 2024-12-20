import os
from flask import Flask, request, jsonify, abort
from Entities.Stock import Stock  # Importing the Stock class
from Entities.StocksRealValue import fetch_stock_real_price
from Core.exceptions import StocksRealValueError

# Import the new MongoDB module functions
import MongoDBService.MongoDBService as mongo_service

app = Flask(__name__)

# Collection name from the environment variable
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "stocks1")


@app.route('/stocks', methods=['POST', 'GET'])
def manage_stocks():
    if request.method == 'POST':
        if not request.is_json:
            abort(415)

        data: dict = request.json

        try:
            # Validate and prepare the stock data
            prepared_stock_data = Stock.prepare_stock_data(data)

            # Create stock in MongoDB
            inserted_id = mongo_service.create_stock(
                COLLECTION_NAME, prepared_stock_data)

            return jsonify({"status": "success", "id": inserted_id}), 201
        except ValueError as e:
            abort(400)
        except Exception as e:
            abort(500, description=f"Error creating stock: {e}")

    elif request.method == 'GET':
        try:
            # Get stocks from MongoDB with optional query parameters
            stocks = mongo_service.get_stocks(
                COLLECTION_NAME, request.args.to_dict())
            return jsonify(stocks), 200
        except Exception as e:
            abort(500, description=f"Error retrieving stocks: {e}")


@app.route('/stocks/<stock_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_stock(stock_id):
    if request.method == 'GET':
        try:
            # Retrieve specific stock
            stock = mongo_service.get_stock(COLLECTION_NAME, stock_id)
            return jsonify(stock), 200
        except ValueError:
            abort(404)
        except Exception as e:
            abort(500, description=f"Error retrieving stock: {e}")

    elif request.method == 'PUT':
        if not request.is_json:
            abort(415)

        data = request.json
        try:
            # Validate and prepare the updated stock data
            prepared_stock_data = Stock.prepare_stock_data(
                data, is_new=False, id_when_not_new=stock_id)

            # Update stock in MongoDB
            success = mongo_service.update_stock(
                COLLECTION_NAME, stock_id, prepared_stock_data)
            if not success:
                abort(404)

            return jsonify({"status": "success"}), 200
        except ValueError as e:
            abort(400)
        except Exception as e:
            abort(500, description=f"Error updating stock: {e}")

    elif request.method == 'DELETE':
        try:
            # Delete stock from MongoDB
            success = mongo_service.delete_stock(COLLECTION_NAME, stock_id)
            if not success:
                abort(404)

            return "", 204
        except Exception as e:
            abort(500, description=f"Error deleting stock: {e}")


@app.route('/stock-value/<stock_id>', methods=['GET'])
def get_stock_value(stock_id):
    try:
        # Fetch stock from MongoDB
        stock = mongo_service.get_stock(COLLECTION_NAME, stock_id)

        # Fetch real-time stock price
        ticker_price = fetch_stock_real_price(stock["symbol"])
        stock_value = round(ticker_price * stock["shares"], 2)

        return jsonify({
            "symbol": stock["symbol"],
            "ticker": ticker_price,
            "stock value": stock_value
        }), 200
    except StocksRealValueError as e:
        abort(500, description=f"API response code {e}")
    except KeyError as e:
        abort(500, description=f"Missing field in stock data: {e}")


@app.route('/portfolio-value', methods=['GET'])
def get_portfolio_value():
    try:
        # Fetch all stocks from MongoDB
        stocks = mongo_service.get_stocks(
            COLLECTION_NAME, request.args.to_dict())

        # Calculate total portfolio value
        total_value = 0
        for stock in stocks:
            ticker_price = fetch_stock_real_price(stock["symbol"])
            total_value += ticker_price * stock["shares"]

        return jsonify({
            "date": request.args.get("date", "Today"),
            "portfolio value": round(total_value, 2)
        }), 200
    except KeyError as e:
        abort(500, description=f"Missing field in stock data: {e}")


@app.route('/kill', methods=['GET'])
def kill_service():
    """Simulate a crash for testing container restart."""
    os._exit(1)

# Error handlers remain the same as in the original file


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
    app.run(host='0.0.0.0', port=8000)
