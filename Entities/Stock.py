# import uuid
# from flask import abort

# class Stock:
#     _used_ids = set()
#     stocks = {}

#     def __init__(self, data: dict):
#         self.validate_new_stock_fields(data)
#         # If we reach this line, the data is valid
#         self.id = self._generate_unique_id()
#         self.name = data.get("name", "NA")
#         self.symbol = data["symbol"].upper()
#         self.purchase_price = round(float(data["purchase price"]), 2)
#         self.purchase_date = data.get("purchase date", "NA")
#         self.shares = data["shares"]

#     @classmethod
#     def _generate_unique_id(cls) -> str:
#         while True:
#             new_id = str(uuid.uuid4())
#             if new_id not in cls._used_ids:
#                 cls._used_ids.add(new_id)
#                 return new_id

#     @classmethod
#     def check_stock_exists(cls, stock_id):
#         if stock_id not in cls.stocks:
#             abort(404)

#     @classmethod
#     def delete_stock(cls, stock_id):
#         del cls.stocks[stock_id]
#         cls.remove_id_from_used_ids(stock_id)

#     @classmethod
#     def remove_id_from_used_ids(cls, stock_id):
#         cls._used_ids.discard(stock_id)

#     @classmethod
#     def validate_new_stock_fields(cls, data: dict):
#         required_fields = ["symbol", "purchase price", "shares"]

#         # Validate required fields
#         if not all(field in data for field in required_fields):
#             raise ValueError("Missing required fields")

#         # Validate symbol not already in stocks
#         for stock in cls.stocks.values():
#             if stock.symbol == data["symbol"].upper():
#                 raise ValueError("Stock with symbol already exists")

#         # Validate purchase price
#         try:
#             float(data["purchase price"])
#         except ValueError as e:
#             raise ValueError("Invalid purchase price - " + str(e))

#         # Validate purchase date
#         if data.get("purchase date"):
#             try:
#                 day, month, year = map(int, data["purchase date"].split("-"))
#                 if not (1 <= day <= 31 and 1 <= month <= 12 and year > 0):
#                     raise ValueError("Invalid purchase date")
#             except ValueError as e:
#                 raise ValueError("Invalid purchase date - " + str(e))

#         # Validate shares
#         try:
#             int(data["shares"])
#         except ValueError as e:
#             raise ValueError("Invalid shares - " + str(e))

#     @classmethod
#     def validate_put_stock_fields(cls, data: dict):
#         required_fields = ["id", "symbol", "name", "purchase price", "purchase date", "shares"]

#         # Validate required fields
#         if not all(field in data for field in required_fields):
#             raise ValueError("Missing required fields")

#         # Validate purchase price
#         try:
#             float(data["purchase price"])
#         except ValueError as e:
#             raise ValueError("Invalid purchase price - " + str(e))

#         # Validate purchase date
#         if data.get("purchase date"):
#             try:
#                 day, month, year = map(int, data["purchase date"].split("-"))
#                 if not (1 <= day <= 31 and 1 <= month <= 12 and year > 0):
#                     raise ValueError("Invalid purchase date")
#             except ValueError as e:
#                 raise ValueError("Invalid purchase date - " + str(e))

#         # Validate shares
#         try:
#             int(data["shares"])
#         except ValueError as e:
#             raise ValueError("Invalid shares - " + str(e))

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "symbol": self.symbol,
#             "purchase price": self.purchase_price,
#             "purchase date": self.purchase_date,
#             "shares": self.shares,
#         }

class Stock:
    @classmethod
    def validate_stock_fields(cls, data: dict, is_new: bool = True):
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
    def prepare_stock_data(cls, data: dict, is_new: bool = True):
        """
        Validate and prepare stock data for database insertion or update.

        :param data: Dictionary containing stock data
        :param is_new: Boolean indicating if this is a new stock creation
        :return: Prepared stock data dictionary
        """
        # Validate the data first
        cls.validate_stock_fields(data, is_new)

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
