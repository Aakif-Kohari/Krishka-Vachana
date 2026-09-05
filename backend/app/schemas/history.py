"""Historical farm record schemas.

Aggregates a farmer's past and present data across crops, bookings, and
payments into a single response for the frontend dashboard.
"""
import base64
import binascii
import json
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.crop import CropOut
from app.schemas.payment import PaymentOut
from app.schemas.slot import SlotBookingOut


class FarmHistoryCursor(BaseModel):
    """Positions for each independently paginated history collection."""

    crops: Optional[str] = Field(default=None, min_length=1)
    bookings: Optional[str] = Field(default=None, min_length=1)
    payments: Optional[str] = Field(default=None, min_length=1)

    model_config = {"extra": "forbid"}

    @classmethod
    def from_token(cls, token: str) -> "FarmHistoryCursor":
        """Decode and validate an opaque URL-safe history cursor."""
        try:
            padding = "=" * (-len(token) % 4)
            payload = base64.b64decode(
                token + padding, altchars=b"-_", validate=True
            )
            cursor = cls.model_validate(json.loads(payload))
        except (ValueError, TypeError, UnicodeError, binascii.Error) as exc:
            raise ValueError("invalid history cursor") from exc
        if not any((cursor.crops, cursor.bookings, cursor.payments)):
            raise ValueError("invalid history cursor")
        return cursor

    def to_token(self) -> str:
        """Encode cursor positions into an opaque URL-safe token."""
        payload = json.dumps(
            self.model_dump(exclude_none=True), separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
        return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


class FarmHistoryQuery(BaseModel):
    """Validated query parameters for a bounded history page."""

    page_size: int = Field(default=20, ge=1, le=100)
    cursor: Optional[str] = Field(default=None, min_length=1, max_length=1024)

    @field_validator("cursor")
    @classmethod
    def validate_cursor(cls, value: Optional[str]) -> Optional[str]:
        """Reject malformed cursor tokens at the API boundary."""
        if value is not None:
            FarmHistoryCursor.from_token(value)
        return value

    def decoded_cursor(self) -> FarmHistoryCursor:
        """Return the decoded positions, or initial empty positions."""
        return FarmHistoryCursor.from_token(self.cursor) if self.cursor else FarmHistoryCursor()


class FarmHistoryPageInfo(BaseModel):
    """Metadata needed to request the next bounded history page."""

    page_size: int
    next_cursor: Optional[str] = None


class FarmHistoryOut(BaseModel):
    """Aggregated historical record for a farmer."""

    crops: List[CropOut] = Field(default_factory=list)
    bookings: List[SlotBookingOut] = Field(default_factory=list)
    payments: List[PaymentOut] = Field(default_factory=list)
    page: FarmHistoryPageInfo

    model_config = {"from_attributes": True}
