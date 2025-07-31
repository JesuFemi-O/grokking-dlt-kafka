from datetime import datetime
from pydantic import Field

from .base import BaseModel


class Product(BaseModel):
    product_id: int = Field(..., avro_type="long")
    name: str
    category: str
    price: float
    stock: int
    created_at: datetime = Field(default_factory=datetime.now, avro_type="timestamp-millis")