"""Payment tracking schemas.

Covers the "Payment Tracking" feature from the project brief. Represents
post-procurement payments made to farmers. Since actual banking integrations
require RBI-licensed partners, this schema supports a mock gateway webhook
pattern that can be swapped for a real signature-verified gateway later.
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    """Status of a procurement payment."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class PaymentCreate(BaseModel):
    """Schema for recording a payment against a booking (simulating a gateway webhook)."""

    booking_id: str = Field(..., min_length=1, description="The slot booking ID being paid for")
    amount: float = Field(..., gt=0, description="Payment amount in INR")
    transaction_ref: str = Field(..., min_length=5, description="Gateway transaction reference ID")


class PaymentOut(BaseModel):
    """Schema for payment records returned to the farmer."""

    payment_id: str
    farmer_id: str
    booking_id: str
    amount: float
    transaction_ref: str
    status: PaymentStatus
    processed_at: datetime

    model_config = {"from_attributes": True}
