from datetime import datetime
from pydantic import Field
from typing import List, Optional
from uuid import uuid4

from .base import BaseModel


class Return(BaseModel):
    """Model for product returns"""
    return_id: str = Field(default_factory=lambda: str(uuid4()))
    order_id: str = Field(..., description="Reference to the original order")
    product_ids: List[int] = Field(..., description="Products being returned")
    reason: str = Field(..., description="Reason for return")
    status: str = Field(default="requested", description="Current status of the return")
    refund_amount: float = Field(..., description="Amount to be refunded")
    requested_at: datetime = Field(default_factory=datetime.now, avro_type="timestamp-millis")
    processed_at: Optional[datetime] = Field(None, avro_type="timestamp-millis", description="When return was processed")
    notes: Optional[str] = Field(None, description="Additional notes about the return")