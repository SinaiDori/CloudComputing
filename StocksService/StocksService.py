# import os
# from flask import Flask, request, jsonify, abort
# import requests
# from Entities.Stock import Stock  # Importing the Stock class
# from Entities.StocksRealValue import fetch_stock_real_price
# from Core.exceptions import StocksRealValueError
# import socket

# # Add hostname resolution debug code here
# try:
#     ip = socket.gethostbyname('mongodb-service')
#     print(f"Resolved mongodb-service to IP: {ip}")
# except socket.gaierror as e:
#     print(f"Hostname resolution failed: {e}")

# app = Flask(__name__)

# MONGO_DB_CONTAINER_PORT = os.getenv("MONGO_DB_CONTAINER_PORT", 27017)

# # MongoDB Service URL
# MONGO_DB_SERVICE_URL = f"http://mongodb-service:{MONGO_DB_CONTAINER_PORT}"

# # Collection name from the environment variable
# COLLECTION_NAME = os.getenv("COLLECTION_NAME", "stocks1")


# @app.route('/stocks', methods=['POST', 'GET'])
# def manage_stocks():
#     if request.method == 'POST':
#         if not request.is_json:
#             abort(415)

#         data: dict = request.json

#         try:
#             # Validate and prepare the stock data
#             prepared_stock_data = Stock.prepare_stock_data(data)

#             # Forward POST request to MongoDBService
#             response = requests.post(
#                 f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}", json=prepared_stock_data)
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
#             # Validate and prepare the updated stock data
#             prepared_stock_data = Stock.prepare_stock_data(data, is_new=False)

#             # Forward PUT request to MongoDBService
#             response = requests.put(
#                 f"{MONGO_DB_SERVICE_URL}/{COLLECTION_NAME}/{stock_id}", json=prepared_stock_data)
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
#         print(stock)

#         # Fetch real-time stock price
#         ticker_price = fetch_stock_real_price(stock["symbol"])
#         stock_value = round(ticker_price * stock["shares"], 2)

#         return jsonify({
#             "symbol": stock["symbol"],
#             "ticker": ticker_price,
#             "stock value": stock_value
#         }), 200
#     except StocksRealValueError as e:
#         abort(500, description=f"API response code {e}")
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
#     # stocks_port = 5001 if COLLECTION_NAME == "stocks1" else 5002
#     # app.run(host='0.0.0.0', port=int(
#     #     os.getenv('STOCKS_SERVICE_PORT', stocks_port)))
#     app.run(host='0.0.0.0', port=8000)

import os
from flask import Flask, request, jsonify, abort
import requests
from Entities.Stock import Stock  # Importing the Stock class
from Entities.StocksRealValue import fetch_stock_real_price
from Core.exceptions import StocksRealValueError
import socket

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
