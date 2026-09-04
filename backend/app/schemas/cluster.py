"""Village Cluster Booking schemas.

Covers the "Village Cluster Booking" feature from the project brief: group
scheduling for farmers from the same village to coordinate transport to a
procurement centre. Validates that all farmers in the request share the
same village and atomically reserves capacity for the entire group.
"""
from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field, field_validator


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

    @field_validator("village", mode="before")
    @classmethod
    def strip_and_require_village(cls, village: object) -> object:
        """Strip the claimed village and reject whitespace-only values."""
        if isinstance(village, str):
            village = village.strip()
            if not village:
                raise ValueError("village must not be empty after trimming whitespace")
        return village

    @field_validator("farmer_ids")
    @classmethod
    def require_unique_farmer_ids(cls, farmer_ids: List[str]) -> List[str]:
        """Reject duplicate members before attempting an atomic reservation."""
        if len(farmer_ids) != len(set(farmer_ids)):
            raise ValueError("farmer_ids must contain unique farmer IDs")
        return farmer_ids


class ClusterBookingOut(BaseModel):
    """Schema for the result of a successful cluster booking."""

    cluster_id: str
    village: str
    booking_ids: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}
