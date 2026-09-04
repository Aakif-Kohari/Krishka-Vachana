"""Phone-number OTP verification business logic (see app/schemas/otp.py).

The OTP challenge (hash, expiry, attempt count) is stored as extra fields
on the farmer's own repository record via FarmerRepository.update - the
same repository Phase 1 already provides - rather than a new collection,
since there is at most one pending challenge per farmer at a time. These
fields are never part of FarmerOut (see app/schemas/farmer.py), so they
never leak in API responses, the same way aadhaar_hash already doesn't.
"""
import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import Settings
from app.core.exceptions import ConflictError, NotFoundError, ValidationAppError
from app.core.sms import send_sms
from app.repositories.base import FarmerRepository
from app.schemas.otp import OtpRequestOut, OtpVerifyOut

logger = logging.getLogger("app.otp")


def _hash_code(code: str) -> str:
    """Hash an OTP code using SHA-256 for secure storage."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def utcnow() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


def request_otp(settings: Settings, farmer_repo: FarmerRepository, farmer_id: str) -> OtpRequestOut:
    """Generate and send a phone-verification OTP to the farmer's registered number."""
    farmer = farmer_repo.get(farmer_id)
    if farmer is None:
        raise NotFoundError("Farmer profile not found - register first")
    phone_number = farmer.get("phone_number")
    if not phone_number:
        raise ConflictError("No phone number on file for this profile")

    code = f"{secrets.randbelow(10 ** settings.otp_length):0{settings.otp_length}d}"
    expires_at = utcnow() + timedelta(seconds=settings.otp_ttl_seconds)
    farmer_repo.update(
        farmer_id,
        {
            "phone_otp_hash": _hash_code(code),
            "phone_otp_expires_at": expires_at,
            "phone_otp_attempts": 0,
        },
    )

    sent = send_sms(
        settings,
        phone_number,
        f"KisanSetu: your verification code is {code}. "
        f"It expires in {settings.otp_ttl_seconds // 60} minutes.",
    )
    if not sent:
        # Dry-run/local-dev visibility only (see app/core/sms.py) - the code
        # itself is never returned in the API response.
        logger.info("OTP for farmer %s (dry run, SMS gateway unset): %s", farmer_id, code)

    return OtpRequestOut(message="Verification code sent", expires_in_seconds=settings.otp_ttl_seconds)


def verify_otp(settings: Settings, farmer_repo: FarmerRepository, farmer_id: str, otp_code: str) -> OtpVerifyOut:
    """Verify a submitted OTP code against the farmer's pending challenge."""
    farmer = farmer_repo.get(farmer_id)
    if farmer is None:
        raise NotFoundError("Farmer profile not found - register first")

    stored_hash = farmer.get("phone_otp_hash")
    expires_at = farmer.get("phone_otp_expires_at")
    attempts = farmer.get("phone_otp_attempts", 0)

    if not stored_hash or not expires_at:
        raise ConflictError("No verification code was requested, or it already expired")
    if utcnow() > expires_at:
        _clear_otp(farmer_repo, farmer_id)
        raise ConflictError("Verification code expired - request a new one")
    if attempts >= settings.otp_max_attempts:
        _clear_otp(farmer_repo, farmer_id)
        raise ConflictError("Too many incorrect attempts - request a new code")

    if _hash_code(otp_code) != stored_hash:
        farmer_repo.update(farmer_id, {"phone_otp_attempts": attempts + 1})
        raise ValidationAppError("Incorrect verification code")

    farmer_repo.update(farmer_id, {"phone_verified": True})
    _clear_otp(farmer_repo, farmer_id)
    return OtpVerifyOut(phone_verified=True)


def _clear_otp(farmer_repo: FarmerRepository, farmer_id: str) -> None:
    """Clear the OTP challenge fields from a farmer's record."""
    farmer_repo.update(
        farmer_id,
        {"phone_otp_hash": None, "phone_otp_expires_at": None, "phone_otp_attempts": 0},
    )
