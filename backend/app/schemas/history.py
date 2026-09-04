"""Historical farm record schemas.

Aggregates a farmer's past and present data across crops, bookings, and
payments into a single response for the frontend dashboard.
"""
from typing import List

from pydantic import BaseModel

from app.schemas.crop import CropOut
from app.schemas.payment import PaymentOut
from app.schemas.slot import SlotBookingOut


class FarmHistoryOut(BaseModel):
    """Aggregated historical record for a farmer."""

    crops: List[CropOut] = []
    bookings: List[SlotBookingOut] = []
    payments: List[PaymentOut] = []

    model_config = {"from_attributes": True}
