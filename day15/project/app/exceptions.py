from typing import Any


class AppException(Exception):
    pass


class ProductNotFoundError(AppException):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} not found")


class InsufficientStockError(AppException):
    def __init__(self, product_id: int, requested: int, available: int):
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for product {product_id}. "
            f"Requested: {requested}, Available: {available}"
        )


class RepositoryError(AppException):
    pass