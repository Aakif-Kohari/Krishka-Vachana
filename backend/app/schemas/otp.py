"""Phone-number OTP verification schemas.

Covers the "SMS/OTP integration" half of Phase 3 (see backend README
roadmap and team_work_division.md's Backend responsibility "Integrate SMS
gateway for OTP/notifications"). This is independent of Firebase
Authentication (Database & Infrastructure's domain, used for farmer
login/identity) - it verifies that the phone_number a farmer registered
actually belongs to them, via a one-time code sent through app/core/sms.py.
"""
from pydantic import BaseModel, Field


class OtpVerifyRequest(BaseModel):
    """Schema for submitting an OTP code for verification."""

    otp_code: str = Field(min_length=4, max_length=8, description="The code received by SMS")


class OtpRequestOut(BaseModel):
    """Response after requesting an OTP be sent."""

    message: str
    expires_in_seconds: int


class OtpVerifyOut(BaseModel):
    """Response after a successful OTP verification."""

    phone_verified: bool
