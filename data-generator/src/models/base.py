from datetime import datetime
from pydantic import Field
from pydantic_avro.base import AvroBase
from typing import List, Optional
from uuid import uuid4
from enum import Enum


# Common enums used across models
class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentMethodEnum(str, Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class ReturnStatusEnum(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ReturnReasonEnum(str, Enum):
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    NOT_AS_DESCRIBED = "not_as_described"
    CHANGED_MIND = "changed_mind"
    DAMAGED_IN_SHIPPING = "damaged_in_shipping"
    SIZE_ISSUE = "size_issue"


# Base model class that all our models inherit from
class BaseModel(AvroBase):
    """Base model with common functionality"""
    pass