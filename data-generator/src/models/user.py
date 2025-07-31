from datetime import datetime
from pydantic import Field
from typing import List, Optional

from .base import BaseModel, StatusEnum


class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: Optional[str] = None


class User(BaseModel):
    id: int = Field(..., avro_type="long", description="User ID")
    name: str
    email: str
    age: Optional[int] = Field(None, avro_type="long")
    status: StatusEnum = StatusEnum.ACTIVE
    addresses: List[Address] = []
    created_at: datetime = Field(default_factory=datetime.now, avro_type="timestamp-millis")
    is_verified: bool = False