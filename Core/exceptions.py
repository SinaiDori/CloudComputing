class StocksRealValueError(Exception):
    """Custom exception for errors from the external API for getting stock prices"""
    pass

class NotFoundError(Exception):
    """Exception raised when a requested resource is not found."""
    pass

class AlreadyExistsError(Exception):
    """Exception raised when a resource already exists."""
    pass

class MalformedDataError(Exception):
    """Exception raised when data is malformed."""
    pass