from .user import User, Address
from .product import Product
from .order import Order
from .payment import Payment
from .returns import Return

# Central list of all models for registration and processing
ALL_MODELS = [User, Product, Order, Payment, Return]

__all__ = [
    "User",
    "Address", 
    "Product",
    "Order",
    "Payment",
    "Return",
    "ALL_MODELS"
]