"""Farmer identity & profile schemas.

Covers the "Farmer ID / Aadhaar-linked identification" feature from the
project brief. `farmer_id` is the Firebase Auth UID (identity itself is
Infra's domain); this module only handles the *profile* data attached to
that identity, which is Backend's responsibility.

Security note: we never accept or return a full Aadhaar number in any
response. Only the last 4 digits are stored/exposed (`aadhaar_last4`),
mirroring how Aadhaar is handled in real e-KYC flows. The full number is
validated on input, hashed, and the plaintext is discarded - see
app/services/farmer_service.py.
"""
import re
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# Keep this list in sync with what the AI/ML and Frontend teams support for
# the "regional language capability" requirement. Extend as needed.
SUPPORTED_LANGUAGES = {"en", "hi", "mr", "pa", "gu", "ta", "te", "kn", "bn", "or", "ml"}

_AADHAAR_RE = re.compile(r"^\d{12}$")
_PHONE_RE = re.compile(r"^[6-9]\d{9}$")  # Indian mobile numbers


class FarmerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone_number: str = Field(description="10-digit Indian mobile number, no country code")
    aadhaar_number: str = Field(description="12-digit Aadhaar number; never stored or returned in full")
    village: str = Field(min_length=1, max_length=120)
    district: str = Field(min_length=1, max_length=120)
    state: str = Field(min_length=1, max_length=120)
    preferred_language: str = Field(default="en")

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not _PHONE_RE.match(v):
            raise ValueError("phone_number must be a 10-digit Indian mobile number")
        return v

    @field_validator("aadhaar_number")
    @classmethod
    def validate_aadhaar(cls, v: str) -> str:
        if not _AADHAAR_RE.match(v):
            raise ValueError("aadhaar_number must be exactly 12 digits")
        return v

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"preferred_language must be one of {sorted(SUPPORTED_LANGUAGES)}")
        return v


class FarmerUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    village: Optional[str] = Field(default=None, min_length=1, max_length=120)
    district: Optional[str] = Field(default=None, min_length=1, max_length=120)
    state: Optional[str] = Field(default=None, min_length=1, max_length=120)
    preferred_language: Optional[str] = None

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"preferred_language must be one of {sorted(SUPPORTED_LANGUAGES)}")
        return v


class FarmerOut(BaseModel):
    farmer_id: str
    full_name: str
    phone_number: str
    aadhaar_last4: str
    village: str
    district: str
    state: str
    preferred_language: str
    created_at: datetime

    model_config = {"from_attributes": True}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
