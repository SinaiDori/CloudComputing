import os
from core.exceptions import NotFoundError, MalformedDataError
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import Dict, List, Any, Optional

# MongoDB Setup
MONGO_URI = "mongodb://mongodb-service:27017"
COLLECTION_NAME = "stocks"

client = MongoClient(MONGO_URI)
db = client[COLLECTION_NAME]


def get_stocks(query_params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Retrieve stocks from the "stocks" collection based on optional query parameters.

    Args:
        query_params (dict, optional): Query parameters to filter stocks

    Returns:
        List of stock dictionaries
    """
    try:
        stocks: List[Dict[str, Any]] = list(db[COLLECTION_NAME].find(query_params or {}))
        for stock in stocks:
            stock["id"] = str(stock.pop("_id"))
        return stocks
    except Exception as e:
        raise RuntimeError(f"Error retrieving stocks: {str(e)}")


def create_stock(data: Dict[str, Any]) -> str:
    """
    Create a new stock in the "stocks" collection.

    Args:
        data (dict): Stock data to insert

    Returns:
        Inserted document's ID as a string
    """
    if not data:
        raise MalformedDataError("Missing stock data")

    try:
        result = db[COLLECTION_NAME].insert_one(data)
        return str(result.inserted_id)
    except Exception as e:
        raise RuntimeError(f"Error creating stock: {str(e)}")


def get_stock(stock_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific stock by its ID.

    Args:
        stock_id (str): ID of the stock to retrieve

    Returns:
        Stock document as a dictionary
    """
    try:
        stock: Dict[str, Any] = db[COLLECTION_NAME].find_one({"_id": ObjectId(stock_id)})
    except Exception as e:
        raise RuntimeError(f"Error retrieving stock: {str(e)}")
    if not stock:
        raise NotFoundError("Stock not found")
    stock["id"] = str(stock.pop("_id"))
    return stock


def get_stock_by_symbol(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific stock by its symbol.

    Args:
        symbol (str): Symbol of the stock to retrieve

    Returns:
        Stock document as a dictionary or None if not found
    """
    try:
        stock: Dict[str, Any] = db[COLLECTION_NAME].find_one({"symbol": symbol})
    except Exception as e:
        raise RuntimeError(f"Error retrieving stock: {str(e)}")

    if not stock:
        raise NotFoundError("Stock not found")
    stock["id"] = str(stock.pop("_id"))
    return stock


def update_stock(stock_id: str, data: Dict[str, Any]) -> bool:
    """
    Update a specific stock in the "stocks" collection.

    Args:
        stock_id (str): ID of the stock to update
        data (dict): Updated stock data

    Returns:
        Boolean indicating success of update
    """
    if not data:
        raise MalformedDataError("Missing update data")

    try:
        result = db[COLLECTION_NAME].update_one(
            {"_id": ObjectId(stock_id)}, {"$set": data})
        if result.matched_count == 0:
            raise NotFoundError("Stock not found")
        return True
    except NotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error updating stock: {str(e)}")


def delete_stock(stock_id: str) -> bool:
    """
    Delete a specific stock from the "stocks" collection.

    Args:
        stock_id (str): ID of the stock to delete

    Returns:
        Boolean indicating success of deletion
    """
    try:
        result = db[COLLECTION_NAME].delete_one({"_id": ObjectId(stock_id)})
        if result.deleted_count == 0:
            raise NotFoundError("Stock not found")
        return True
    except NotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error deleting stock: {str(e)}")