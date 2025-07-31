from datetime import datetime
from pydantic import Field
from uuid import uuid4

from .base import BaseModel


class Payment(BaseModel):
    payment_id: str = Field(default_factory=lambda: str(uuid4()))
    order_id: str  # Reference to order
    amount: float
    method: str  # Using string for flexibility
    successful: bool
    processed_at: datetime = Field(default_factory=datetime.now, avro_type="timestamp-millis")