import MongoDBService.MongoDBService as mongo_service
import os

# Collection name from the environment variable
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "stocks1")


class Stock:
    @classmethod
    def validate_stock_fields(cls, data: dict, is_new: bool = True, id_when_not_new: str = None):
        """
        Validate stock data fields with different requirements for new and existing stocks.

        :param data: Dictionary containing stock data
        :param is_new: Boolean indicating if this is a new stock creation
        :raises ValueError: If validation fails
        """
        # Define required fields based on whether it's a new stock or an update
        required_fields = ["symbol", "purchase price", "shares"] if is_new \
            else ["id", "symbol", "name", "purchase price", "purchase date", "shares"]

        # Validate required fields are present
        if not all(field in data for field in required_fields):
            raise ValueError("Missing required fields")

        # Validate symbol not already in stocks
        # if is_new, we need to go through all stocks to check for duplicates
        # if not is_new, we need to make sure the id is the same as the one we're updating
        if is_new:
            found = False
            
            try:
                if mongo_service.get_stock_by_symbol(COLLECTION_NAME, data["symbol"]):
                    found = True
            except ValueError:
                # The stock symbol does not exist, so we can move on without raising an error
                pass
            
            if found:
                raise ValueError("Stock with symbol already exists")
        else:
            stock = mongo_service.get_stock(COLLECTION_NAME, id_when_not_new)
            # if we reach this point, the stock exists
            if id_when_not_new != data["id"]:
                raise ValueError("Cannot change stock ID")
            # if we reach this point, the stock ID is the same
            if stock["symbol"] != data["symbol"]:
                found = False
                try:
                    if mongo_service.get_stock_by_symbol(COLLECTION_NAME, data["symbol"]):
                        found = True
                except ValueError:
                    # The new stock symbol does not exist, so we can update without raising an error
                    pass
                
                if found:
                    raise ValueError("Stock with symbol already exists")

        # Validate purchase price
        try:
            float(data["purchase price"])
        except ValueError as e:
            raise ValueError(f"Invalid purchase price - {e}")

        # Validate purchase date (if present)
        if data.get("purchase date"):
            try:
                day, month, year = map(int, data["purchase date"].split("-"))
                if not (1 <= day <= 31 and 1 <= month <= 12 and year > 0):
                    raise ValueError("Invalid purchase date")
            except ValueError as e:
                raise ValueError(f"Invalid purchase date - {e}")

        # Validate shares
        try:
            int(data["shares"])
        except ValueError as e:
            raise ValueError(f"Invalid shares - {e}")

    @classmethod
    def prepare_stock_data(cls, data: dict, is_new: bool = True, id_when_not_new: str = None):
        """
        Validate and prepare stock data for database insertion or update.

        :param data: Dictionary containing stock data
        :param is_new: Boolean indicating if this is a new stock creation
        :return: Prepared stock data dictionary
        """
        # Validate the data first
        cls.validate_stock_fields(data, is_new, id_when_not_new)

        # Prepare the data for storage
        prepared_data = data.copy()

        # Normalize certain fields
        if "symbol" in prepared_data:
            prepared_data["symbol"] = prepared_data["symbol"].upper()

        if "purchase price" in prepared_data:
            prepared_data["purchase price"] = round(
                float(prepared_data["purchase price"]), 2)

        if "shares" in prepared_data:
            prepared_data["shares"] = int(prepared_data["shares"])

        # Handle optional fields with "NA" as default
        if is_new:
            prepared_data.setdefault('name', 'NA')
            prepared_data.setdefault('purchase date', 'NA')

        return prepared_data