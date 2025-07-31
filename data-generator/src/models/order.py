from datetime import datetime
from pydantic import Field
from typing import List

from .base import BaseModel


class Order(BaseModel):
    order_id: int = Field(..., avro_type="long")
    user_id: int = Field(..., avro_type="long")
    product_ids: List[int]
    total_amount: float
    status: str  # Using string instead of enum for flexibility
    created_at: datetime = Field(default_factory=datetime.now, avro_type="timestamp-millis")