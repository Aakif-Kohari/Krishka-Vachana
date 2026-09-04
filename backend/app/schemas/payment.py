"""Payment tracking schemas.

Covers the "Payment Tracking" feature from the project brief. Represents
post-procurement payments made to farmers. Since actual banking integrations
require RBI-licensed partners, this schema supports a mock gateway webhook
pattern that can be swapped for a real signature-verified gateway later.
"""
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    """Status of a procurement payment."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class PaymentCreate(BaseModel):
    """Schema for recording a development-only mock payment against a booking."""

    booking_id: str = Field(..., min_length=1, description="The slot booking ID being paid for")
    amount_paise: int = Field(..., gt=0, strict=True, description="Payment amount in paise")
    transaction_ref: str = Field(..., min_length=5, description="Gateway transaction reference ID")


class PaymentWebhookPayload(PaymentCreate):
    """Signature-verified successful-payment event sent by the gateway."""

    event: Literal["payment.success"]


class PaymentOut(BaseModel):
    """Schema for payment records returned to the farmer."""

    payment_id: str
    farmer_id: str
    booking_id: str
    amount_paise: int
    transaction_ref: str
    status: PaymentStatus
    processed_at: datetime

    model_config = {"from_attributes": True}
