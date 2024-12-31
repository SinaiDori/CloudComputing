import os
from Core.exceptions import NotFoundError, MalformedDataError
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import Dict, List, Any, Optional

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
db = client["stocks"]


def get_stocks(collection: str, query_params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Retrieve stocks from a specified collection based on optional query parameters.

    Args:
        collection (str): Name of the collection to query
        query_params (dict, optional): Query parameters to filter stocks

    Returns:
        List of stock dictionaries
    """
    try:
        stocks: List[Dict[str, Any]] = list(db[collection].find(query_params or {}))
        for stock in stocks:
            # copy stock id to a key "id" and convert ObjectId to string
            stock["id"] = str(stock.pop("_id"))
        return stocks
    except Exception as e:
        raise RuntimeError(f"Error retrieving stocks: {str(e)}")


def create_stock(collection: str, data: Dict[str, Any]) -> str:
    """
    Create a new stock in the specified collection.

    Args:
        collection (str): Name of the collection to insert into
        data (dict): Stock data to insert

    Returns:
        Inserted document's ID as a string
    """
    if not data:
        raise MalformedDataError("Missing stock data")

    try:
        result = db[collection].insert_one(data)
        return str(result.inserted_id)
    except Exception as e:
        raise RuntimeError(f"Error creating stock: {str(e)}")


def get_stock(collection: str, stock_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific stock by its ID.

    Args:
        collection (str): Name of the collection
        stock_id (str): ID of the stock to retrieve

    Returns:
        Stock document as a dictionary
    """
    try:
        stock: Dict[str, Any] = db[collection].find_one({"_id": ObjectId(stock_id)})
    except Exception as e:
        raise RuntimeError(f"Error retrieving stock: {str(e)}")
    if not stock:
        raise NotFoundError("Stock not found")
    stock["id"] = str(stock.pop("_id"))
    return stock


def get_stock_by_symbol(collection: str, symbol: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific stock by its symbol.

    Args:
        collection (str): Name of the collection
        symbol (str): Symbol of the stock to retrieve

    Returns:
        Stock document as a dictionary or None if not found
    """
    try:
        stock: Dict[str, Any] = db[collection].find_one({"symbol": symbol})
    except Exception as e:
        raise RuntimeError(f"Error retrieving stock: {str(e)}")
    
    if not stock:
        raise NotFoundError("Stock not found")
    stock["id"] = str(stock.pop("_id"))
    return stock


def update_stock(collection: str, stock_id: str, data: Dict[str, Any]) -> bool:
    """
    Update a specific stock in the collection.

    Args:
        collection (str): Name of the collection
        stock_id (str): ID of the stock to update
        data (dict): Updated stock data

    Returns:
        Boolean indicating success of update
    """
    if not data:
        raise MalformedDataError("Missing update data")

    # check if stock exists
    get_stock(collection, stock_id)

    try:
        result = db[collection].update_one(
            {"_id": ObjectId(stock_id)}, {"$set": data})
        return result.matched_count > 0
    except Exception as e:
        raise RuntimeError(f"Error updating stock: {str(e)}")


def delete_stock(collection: str, stock_id: str) -> bool:
    """
    Delete a specific stock from the collection.

    Args:
        collection (str): Name of the collection
        stock_id (str): ID of the stock to delete

    Returns:
        Boolean indicating success of deletion
    """

    # check if stock exists
    get_stock(collection, stock_id)

    try:
        result = db[collection].delete_one({"_id": ObjectId(stock_id)})
        return result.deleted_count > 0
    except Exception as e:
        raise RuntimeError(f"Error deleting stock: {str(e)}")
