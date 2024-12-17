# import os
# from Entities.Stock import Stock
# from Entities.StocksRealValue import fetch_stock_real_price
# from flask import Flask, request, jsonify, abort

# app = Flask(__name__)

# @app.route('/stocks', methods=['POST', 'GET'])
# def manage_stocks():
#     if request.method == 'POST':
#         if not request.is_json:
#             abort(415)

#         data: dict = request.json

#         try:
#             stock = Stock(data)
#             Stock.stocks[stock.id] = stock
#             return jsonify({"id": stock.id}), 201
#         except ValueError as e:
#             abort(400)
#         except Exception as e:
#             abort(500, description=str(e))

#     elif request.method == 'GET':
#         try:
#             query_params = request.args.to_dict()
#             filtered_stocks = [
#                 stock.to_dict() for stock in Stock.stocks.values()
#                 if all(str(stock.to_dict().get(k)).lower() == v.lower() for k, v in query_params.items())
#             ]
#             return jsonify(filtered_stocks), 200
#         except Exception as e:
#             abort(500, description=str(e))

# @app.route('/stocks/<stock_id>', methods=['GET', 'PUT', 'DELETE'])
# def manage_stock(stock_id):
#     Stock.check_stock_exists(stock_id)
#     stock = Stock.stocks[stock_id]
#     if request.method == 'GET':
#         return jsonify(stock.to_dict()), 200

#     elif request.method == 'DELETE':
#         try:
#             Stock.delete_stock(stock_id)
#             return "", 204
#         except Exception as e:
#             abort(500, description=str(e))

#     elif request.method == 'PUT':
#         if not request.is_json:
#             abort(415)

#         data = request.json
#         if not data:
#             abort(400)

#         try:
#             Stock.validate_put_stock_fields(data)
#             stock.name = data["name"]
#             stock.symbol = data["symbol"].upper()
#             stock.purchase_price = round(float(data["purchase price"]), 2)
#             stock.purchase_date = data["purchase date"]
#             stock.shares = int(data["shares"])
#             return jsonify({"id": stock_id}), 200
#         except ValueError as e:
#             abort(400)
#         except Exception as e:
#             abort(500, description=str(e))

# @app.route('/stock-value/<stock_id>', methods=['GET'])
# def get_stock_value(stock_id):
#     stock = Stock.stocks.get(stock_id)
#     if not stock:
#         abort(404)

#     try:
#         ticker_price = fetch_stock_real_price(stock.symbol)
#         stock_value = round(ticker_price * stock.shares, 2)
#         return jsonify({
#             "symbol": stock.symbol,
#             "ticker": ticker_price,
#             "stock value": stock_value
#         }), 200
#     except Exception as e:
#         abort(500, description=str(e))

# @app.route('/portfolio-value', methods=['GET'])
# def get_portfolio_value():
#     try:
#         total_value = 0
#         for stock in Stock.stocks.values():
#             ticker_price = fetch_stock_real_price(stock.symbol)
#             total_value += ticker_price * stock.shares

#         return jsonify({
#             "date": request.args.get("date", "Today"),
#             "portfolio value": round(total_value, 2)
#         }), 200
#     except Exception as e:
#         abort(500, description=str(e))

# @app.errorhandler(400)
# def bad_request(error):
#     return jsonify({"error": "Malformed data"}), 400

# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({"error": "Not found"}), 404

# @app.errorhandler(415)
# def unsupported_media_type(error):
#     return jsonify({"error": "Expected application/json media type"}), 415

# @app.errorhandler(500)
# def internal_server_error(error):
#     description = error.description if error.description else "Internal server error"
#     return jsonify({"server error": description}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5001)))
##########################################################################################################


# import os
# from flask import Flask, request, jsonify, abort
# import requests
# from Entities.Stock import Stock  # Importing the Stock class
# from Entities.StocksRealValue import fetch_stock_real_price

# app = Flask(__name__)

# # MongoDB Service URL
# MONGO_DB_SERVICE_URL = "http://localhost:5002/stocks"

# # Collection name from the environment variable
# COLLECTION_NAME = os.getenv("COLLECTION_NAME", "default_collection")


# @app.route('/stocks', methods=['POST', 'GET'])
# def manage_stocks():
#     if request.method == 'POST':
#         if not request.is_json:
#             abort(415)

#         data: dict = request.json

#         try:
#             # Validate and create the Stock object
#             stock = Stock(data)

#             # Forward POST request to MongoDBService
#             response = requests.post(
#                 f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}", json=stock.to_dict())
#             response.raise_for_status()

#             return jsonify(response.json()), response.status_code
#         except ValueError as e:
#             abort(400, description=f"Invalid data: {e}")
#         except requests.exceptions.RequestException as e:
#             abort(
#                 500, description=f"Error communicating with MongoDBService: {e}")

#     elif request.method == 'GET':
#         try:
#             # Forward GET request to MongoDBService
#             response = requests.get(
#                 f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}", params=request.args)
#             response.raise_for_status()

#             return jsonify(response.json()), response.status_code
#         except requests.exceptions.RequestException as e:
#             abort(
#                 500, description=f"Error communicating with MongoDBService: {e}")


# @app.route('/stocks/<stock_id>', methods=['GET', 'PUT', 'DELETE'])
# def manage_stock(stock_id):
#     if request.method == 'GET':
#         try:
#             # Forward GET request to MongoDBService
#             response = requests.get(
#                 f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}/{stock_id}")
#             response.raise_for_status()

#             return jsonify(response.json()), response.status_code
#         except requests.exceptions.RequestException as e:
#             abort(
#                 500, description=f"Error communicating with MongoDBService: {e}")

#     elif request.method == 'PUT':
#         if not request.is_json:
#             abort(415)

#         data = request.json
#         try:
#             # Validate updated fields with the Stock class
#             Stock.validate_put_stock_fields(data)

#             # Forward PUT request to MongoDBService
#             response = requests.put(
#                 f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}/{stock_id}", json=data)
#             response.raise_for_status()

#             return jsonify(response.json()), response.status_code
#         except ValueError as e:
#             abort(400, description=f"Invalid data: {e}")
#         except requests.exceptions.RequestException as e:
#             abort(
#                 500, description=f"Error communicating with MongoDBService: {e}")

#     elif request.method == 'DELETE':
#         try:
#             # Forward DELETE request to MongoDBService
#             response = requests.delete(
#                 f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}/{stock_id}")
#             response.raise_for_status()

#             return "", response.status_code
#         except requests.exceptions.RequestException as e:
#             abort(
#                 500, description=f"Error communicating with MongoDBService: {e}")


# @app.route('/stock-value/<stock_id>', methods=['GET'])
# def get_stock_value(stock_id):
#     try:
#         # Fetch stock from MongoDBService
#         stock_response = requests.get(
#             f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}/{stock_id}")
#         stock_response.raise_for_status()
#         stock = stock_response.json()

#         # Fetch real-time stock price
#         ticker_price = fetch_stock_real_price(stock["symbol"])
#         stock_value = round(ticker_price * stock["shares"], 2)

#         return jsonify({
#             "symbol": stock["symbol"],
#             "ticker": ticker_price,
#             "stock value": stock_value
#         }), 200
#     except requests.exceptions.RequestException as e:
#         abort(500, description=f"Error communicating with MongoDBService: {e}")
#     except KeyError as e:
#         abort(500, description=f"Missing field in stock data: {e}")


# @app.route('/portfolio-value', methods=['GET'])
# def get_portfolio_value():
#     try:
#         # Fetch all stocks from MongoDBService
#         stocks_response = requests.get(
#             f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}", params=request.args)
#         stocks_response.raise_for_status()
#         stocks = stocks_response.json()

#         # Calculate total portfolio value
#         total_value = 0
#         for stock in stocks:
#             ticker_price = fetch_stock_real_price(stock["symbol"])
#             total_value += ticker_price * stock["shares"]

#         return jsonify({
#             "date": request.args.get("date", "Today"),
#             "portfolio value": round(total_value, 2)
#         }), 200
#     except requests.exceptions.RequestException as e:
#         abort(500, description=f"Error communicating with MongoDBService: {e}")
#     except KeyError as e:
#         abort(500, description=f"Missing field in stock data: {e}")


# @app.route('/kill', methods=['GET'])
# def kill_service():
#     """Simulate a crash for testing container restart."""
#     os._exit(1)


# @app.errorhandler(400)
# def bad_request(error):
#     return jsonify({"error": "Malformed data"}), 400


# @app.errorhandler(404)
# def not_found(error):
#     return jsonify({"error": "Not found"}), 404


# @app.errorhandler(415)
# def unsupported_media_type(error):
#     return jsonify({"error": "Expected application/json media type"}), 415


# @app.errorhandler(500)
# def internal_server_error(error):
#     description = error.description if error.description else "Internal server error"
#     return jsonify({"server error": description}), 500


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=int(os.getenv('FLASK_RUN_PORT', 5001)))
#############################################################################################################

import os
from flask import Flask, request, jsonify, abort
import requests
from Entities.Stock import Stock  # Importing the Stock class
from Entities.StocksRealValue import fetch_stock_real_price
from Core.exceptions import StocksRealValueError

app = Flask(__name__)

# MongoDB Service URL
MONGO_DB_SERVICE_URL = "http://localhost:5002/stocks"

# Collection name from the environment variable
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "default_collection")


@app.route('/stocks', methods=['POST', 'GET'])
def manage_stocks():
    if request.method == 'POST':
        if not request.is_json:
            abort(415)

        data: dict = request.json

        try:
            # Validate and prepare the stock data
            prepared_stock_data = Stock.prepare_stock_data(data)

            # Forward POST request to MongoDBService
            response = requests.post(
                f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}", json=prepared_stock_data)
            response.raise_for_status()

            return jsonify(response.json()), response.status_code
        except ValueError as e:
            abort(400, description=f"Invalid data: {e}")
        except requests.exceptions.RequestException as e:
            abort(
                500, description=f"Error communicating with MongoDBService: {e}")

    elif request.method == 'GET':
        try:
            # Forward GET request to MongoDBService
            response = requests.get(
                f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}", params=request.args)
            response.raise_for_status()

            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            abort(
                500, description=f"Error communicating with MongoDBService: {e}")


@app.route('/stocks/<stock_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_stock(stock_id):
    if request.method == 'GET':
        try:
            # Forward GET request to MongoDBService
            response = requests.get(
                f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}/{stock_id}")
            response.raise_for_status()

            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            abort(
                500, description=f"Error communicating with MongoDBService: {e}")

    elif request.method == 'PUT':
        if not request.is_json:
            abort(415)

        data = request.json
        try:
            # Validate and prepare the updated stock data
            prepared_stock_data = Stock.prepare_stock_data(data, is_new=False)

            # Forward PUT request to MongoDBService
            response = requests.put(
                f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}/{stock_id}", json=prepared_stock_data)
            response.raise_for_status()

            return jsonify(response.json()), response.status_code
        except ValueError as e:
            abort(400, description=f"Invalid data: {e}")
        except requests.exceptions.RequestException as e:
            abort(
                500, description=f"Error communicating with MongoDBService: {e}")

    elif request.method == 'DELETE':
        try:
            # Forward DELETE request to MongoDBService
            response = requests.delete(
                f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}/{stock_id}")
            response.raise_for_status()

            return "", response.status_code
        except requests.exceptions.RequestException as e:
            abort(
                500, description=f"Error communicating with MongoDBService: {e}")


@app.route('/stock-value/<stock_id>', methods=['GET'])
def get_stock_value(stock_id):
    try:
        # Fetch stock from MongoDBService
        stock_response = requests.get(
            f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}/{stock_id}")
        stock_response.raise_for_status()
        stock = stock_response.json()
        print(stock)

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
    except requests.exceptions.RequestException as e:
        abort(500, description=f"Error communicating with MongoDBService: {e}")
    except KeyError as e:
        abort(500, description=f"Missing field in stock data: {e}")


@app.route('/portfolio-value', methods=['GET'])
def get_portfolio_value():
    try:
        # Fetch all stocks from MongoDBService
        stocks_response = requests.get(
            f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}", params=request.args)
        stocks_response.raise_for_status()
        stocks = stocks_response.json()

        # Calculate total portfolio value
        total_value = 0
        for stock in stocks:
            ticker_price = fetch_stock_real_price(stock["symbol"])
            total_value += ticker_price * stock["shares"]

        return jsonify({
            "date": request.args.get("date", "Today"),
            "portfolio value": round(total_value, 2)
        }), 200
    except requests.exceptions.RequestException as e:
        abort(500, description=f"Error communicating with MongoDBService: {e}")
    except KeyError as e:
        abort(500, description=f"Missing field in stock data: {e}")


@app.route('/kill', methods=['GET'])
def kill_service():
    """Simulate a crash for testing container restart."""
    os._exit(1)


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
