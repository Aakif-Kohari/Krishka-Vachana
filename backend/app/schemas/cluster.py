"""Village Cluster Booking schemas.

Covers the "Village Cluster Booking" feature from the project brief: group
scheduling for farmers from the same village to coordinate transport to a
procurement centre. Validates that all farmers in the request share the
same village and atomically reserves capacity for the entire group.
"""
from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field


class ClusterBookingCreate(BaseModel):
    """Schema for requesting a bulk slot booking for a village cluster."""

    centre_id: str = Field(..., min_length=1)
    slot_date: date = Field(..., description="Date of the procurement slot")
    slot_window: str = Field(..., min_length=1, description="Time window (e.g., '08:00-10:00')")
    village: str = Field(..., min_length=1, max_length=120, description="Claimed village name for the cluster")
    farmer_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of farmer UIDs in the cluster; all must belong to the claimed village",
    )


class ClusterBookingOut(BaseModel):
    """Schema for the result of a successful cluster booking."""

    cluster_id: str
    village: str
    booking_ids: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}
