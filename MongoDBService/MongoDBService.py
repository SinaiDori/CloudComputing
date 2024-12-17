import os
from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
stocks1_collection = client["stocks1"]
stocks2_collection = client["stocks2"]
stocks_collections = {
    "stocks1": stocks1_collection,
    "stocks2": stocks2_collection
}


@app.route('/<collection>', methods=['POST', 'GET'])
def manage_stocks(collection):
    stocks_collection = stocks_collections.get(collection)

    if request.method == 'POST':
        data = request.json
        if not data:
            abort(400, "Missing JSON body")

        try:
            # Insert the data and retrieve the generated _id
            result = stocks_collection.insert_one(data)
            inserted_id = str(result.inserted_id)  # Convert ObjectId to string
            return jsonify({"status": "success", "id": inserted_id}), 201
        except Exception as e:
            abort(500, description=str(e))

    elif request.method == 'GET':
        query_params = request.args.to_dict()
        try:
            stocks = list(stocks_collection.find(query_params))
            for stock in stocks:
                stock["_id"] = str(stock["_id"])  # Convert ObjectId to string
            return jsonify(stocks), 200
        except Exception as e:
            abort(500, description=str(e))


@app.route('/<collection>/<stock_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_stock(collection, stock_id):
    stocks_collection = stocks_collections.get(collection)

    if request.method == 'GET':
        stock = stocks_collection.find_one({"_id": ObjectId(stock_id)})
        if not stock:
            abort(404)
        stock["_id"] = str(stock["_id"])
        return jsonify(stock), 200

    elif request.method == 'PUT':
        data = request.json
        if not data:
            abort(400, "Missing JSON body")

        result = stocks_collection.update_one(
            {"_id": ObjectId(stock_id)}, {"$set": data})
        if result.matched_count == 0:
            abort(404)
        return jsonify({"status": "success"}), 200

    elif request.method == 'DELETE':
        result = stocks_collection.delete_one({"_id": ObjectId(stock_id)})
        if result.deleted_count == 0:
            abort(404)
        return "", 204


@app.route('/db-structure', methods=['GET'])
def fetch_db_structure():
    try:
        structure = {}
        databases = client.list_database_names()
        for database_name in databases:
            database = client[database_name]
            collections = database.list_collection_names()
            structure[database_name] = {}
            for collection_name in collections:
                collection = database[collection_name]
                structure[database_name][collection_name] = list(
                    collection.find())
                for doc in structure[database_name][collection_name]:
                    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        return jsonify(structure), 200
    except Exception as e:
        abort(500, description=str(e))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(
        os.getenv("MONGO_DB_CONTAINER_PORT", 27017)))
