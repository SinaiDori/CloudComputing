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
